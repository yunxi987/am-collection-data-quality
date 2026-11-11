# Quick data-quality profile for a GBIF occurrence export (Australian Museum / OZCAM).
# Reads the simple-format occurrence.txt, runs a set of completeness / validity /
# consistency checks and writes a markdown summary.
#
#   python am_data_quality_profile.py occurrence.txt --out am_report.md

import argparse
import pandas as pd

AUS_LAT = (-44.5, -9.0)      # rough bounding box for Australia incl. Tasmania
AUS_LON = (112.0, 154.5)


def load(path):
    sep = "\t" if path.lower().endswith((".txt", ".tsv")) else None
    df = pd.read_csv(path, sep=sep, engine="python", dtype=str,
                     on_bad_lines="skip", quoting=3 if sep == "\t" else 0)
    df.columns = [c.strip() for c in df.columns]
    return df


def pick(df, *candidates):
    """Return the first column name that exists (case-insensitive), else None."""
    lookup = {c.lower(): c for c in df.columns}
    for name in candidates:
        if name.lower() in lookup:
            return lookup[name.lower()]
    return None


def blank(series):
    return series.isna() | (series.astype(str).str.strip() == "")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("path")
    ap.add_argument("--out", default="am_report.md")
    args = ap.parse_args()

    df = load(args.path)
    n = len(df)

    cat = pick(df, "catalogNumber")
    sci = pick(df, "scientificName")
    lat = pick(df, "decimalLatitude", "latitude")
    lon = pick(df, "decimalLongitude", "longitude")
    unc = pick(df, "coordinateUncertaintyInMeters")
    date = pick(df, "eventDate")
    year = pick(df, "year")
    country = pick(df, "countryCode", "country")
    state = pick(df, "stateProvince", "state")
    locality = pick(df, "locality")
    coll = pick(df, "collectionCode")
    recby = pick(df, "recordedBy", "collector")
    issue = pick(df, "issue")

    rows = []

    def add(check, count, note=""):
        rows.append((check, int(count), f"{count / n * 100:.1f}%" if n else "-", note))

    # --- completeness -------------------------------------------------------
    for c, label in [(date, "eventDate missing"), (lat, "decimalLatitude missing"),
                     (lon, "decimalLongitude missing"), (locality, "locality blank"),
                     (state, "stateProvince blank"), (country, "country blank"),
                     (recby, "recordedBy blank"), (unc, "coordinateUncertainty missing")]:
        if c:
            add(label, blank(df[c]).sum())

    # --- dates --------------------------------------------------------------
    if date:
        d = df[date].dropna().astype(str)
        not_iso = ~d.str.match(r"^\d{4}(-\d{2}(-\d{2})?)?")
        add("eventDate not ISO-like", not_iso.sum())
        parsed = pd.to_datetime(d.str[:10], errors="coerce")
        bad = parsed.isna().sum()
        add("eventDate present but not a valid date", bad - not_iso.sum() if bad >= not_iso.sum() else bad)
        add("eventDate in the future", (parsed > pd.Timestamp.today()).sum())
        add("eventDate before 1800", (parsed < pd.Timestamp("1800-01-01")).sum())
    if year:
        y = pd.to_numeric(df[year], errors="coerce")
        add("year blank while eventDate present", (y.isna() & df[date].notna()).sum() if date else y.isna().sum())

    # --- coordinates --------------------------------------------------------
    if lat and lon:
        la = pd.to_numeric(df[lat], errors="coerce")
        lo = pd.to_numeric(df[lon], errors="coerce")
        add("coordinates out of range", ((la.abs() > 90) | (lo.abs() > 180)).sum())
        add("coordinates exactly 0,0", ((la == 0) & (lo == 0)).sum())
        add("only one of lat/lon present", (la.notna() ^ lo.notna()).sum())
        if country:
            is_aus = df[country].astype(str).str.upper().isin(["AU", "AUSTRALIA"])
            outside = (is_aus & la.notna() & ~la.between(*AUS_LAT)) | (is_aus & lo.notna() & ~lo.between(*AUS_LON))
            add("country = Australia but coordinates outside AU bounding box", outside.sum(),
                "check for swapped sign / swapped lat-lon")
        low_prec = df[lat].astype(str).str.contains(r"^-?\d+(?:\.\d{1,2})?$", na=False)
        add("coordinates with <= 2 decimal places", low_prec.sum(), "low precision")

    # --- catalogue numbers --------------------------------------------------
    top_formats = None
    if cat:
        c = df[cat].astype(str).str.strip()
        c = c[c.ne("") & c.ne("nan")]
        note = ""
        if coll:
            within = df[[coll, cat]].dropna().duplicated(keep=False).sum()
            note = f"{within:,} duplicated within the same collectionCode"
        add("duplicate catalogNumber", c.duplicated(keep=False).sum(), note)
        shape = c.str.replace(r"\d", "9", regex=True).str.replace(r"[A-Za-z]", "A", regex=True)
        add("distinct catalogNumber patterns", shape.nunique(), "see table below")
        top_formats = shape.value_counts().head(8)

    # --- controlled values: same value spelt differently --------------------
    def spelling_variants(col, label):
        if not col:
            return
        s = df[col].dropna().astype(str).str.strip()
        s = s[s != ""]
        key = s.str.lower().str.replace(r"[^a-z]", "", regex=True)
        groups = s.groupby(key).agg(lambda x: sorted(set(x)))
        multi = groups[groups.apply(len) > 1]
        add(f"{label}: spelling / case variants", len(multi),
            "; ".join(" / ".join(v[:4]) for v in multi.head(5)))

    spelling_variants(state, "stateProvince")
    spelling_variants(country, "country")

    # --- scientific names ---------------------------------------------------
    if sci:
        s = df[sci].dropna().astype(str)
        add("scientificName with stray whitespace", (s.str.contains("  ") | (s != s.str.strip())).sum())
        add("scientificName with lowercase genus", s.str.match(r"^[a-z]").sum())
        add("scientificName with sp. / cf. / ?", s.str.contains(r"\bsp\.|\bcf\.|\?", regex=True).sum(),
            "open identifications, not errors")

    # --- write report -------------------------------------------------------
    out = [f"# Data-quality profile — {args.path}", "",
           f"Records: **{n:,}**  ·  Columns: {len(df.columns)}", ""]
    if coll:
        out += ["## Records by collection", "",
                df[coll].fillna("(blank)").value_counts().head(15).to_markdown(), ""]
    out += ["## Checks", "", "| Check | Records | % | Notes |", "|---|---:|---:|---|"]
    out += [f"| {a} | {b:,} | {p} | {note} |" for a, b, p, note in rows]
    if issue:
        flags = df[issue].dropna().astype(str).str.split(";").explode().str.strip()
        flags = flags[flags != ""]
        out += ["", "## GBIF issue flags (top 15)", "", flags.value_counts().head(15).to_markdown()]
    if top_formats is not None:
        out += ["", "## catalogNumber patterns (9 = digit, A = letter)", "", top_formats.to_markdown()]

    text = "\n".join(out)
    with open(args.out, "w", encoding="utf-8") as f:
        f.write(text)
    print(text)
    print(f"\nwritten to {args.out}")


if __name__ == "__main__":
    main()
