# Data-quality profile — occurrence.txt

Records: **80,896**  ·  Columns: 50

## Records by collection

| collectionCode   |   count |
|:-----------------|--------:|
| Mammalogy        |   80896 |

## Checks

| Check | Records | % | Notes |
|---|---:|---:|---|
| eventDate missing | 27,982 | 34.6% |  |
| decimalLatitude missing | 14,196 | 17.5% |  |
| decimalLongitude missing | 14,196 | 17.5% |  |
| locality blank | 80,896 | 100.0% |  |
| stateProvince blank | 28,950 | 35.8% |  |
| country blank | 12,243 | 15.1% |  |
| recordedBy blank | 18,574 | 23.0% |  |
| coordinateUncertainty missing | 71,169 | 88.0% |  |
| eventDate not ISO-like | 0 | 0.0% |  |
| eventDate present but not a valid date | 9,010 | 11.1% |  |
| eventDate in the future | 0 | 0.0% |  |
| eventDate before 1800 | 0 | 0.0% |  |
| year blank while eventDate present | 2,001 | 2.5% |  |
| coordinates out of range | 0 | 0.0% |  |
| coordinates exactly 0,0 | 1 | 0.0% |  |
| only one of lat/lon present | 0 | 0.0% |  |
| country = Australia but coordinates outside AU bounding box | 525 | 0.6% | check for swapped sign / swapped lat-lon |
| coordinates with <= 2 decimal places | 17,791 | 22.0% | low precision |
| duplicate catalogNumber | 0 | 0.0% | 0 duplicated within the same collectionCode |
| distinct catalogNumber patterns | 19 | 0.0% | see table below |
| stateProvince: spelling / case variants | 0 | 0.0% |  |
| country: spelling / case variants | 0 | 0.0% |  |
| scientificName with stray whitespace | 0 | 0.0% |  |
| scientificName with lowercase genus | 0 | 0.0% |  |
| scientificName with sp. / cf. / ? | 0 | 0.0% | open identifications, not errors |

## GBIF issue flags (top 15)

| issue                              |   count |
|:-----------------------------------|--------:|
| INSTITUTION_MATCH_FUZZY            |   80896 |
| COLLECTION_MATCH_FUZZY             |   80896 |
| TAXON_CONCEPT_ID_NOT_FOUND         |   80890 |
| CONTINENT_DERIVED_FROM_COORDINATES |   65969 |
| TAXON_MATCH_HIGHERRANK             |    1187 |
| COUNTRY_DERIVED_FROM_COORDINATES   |     272 |
| COUNTRY_COORDINATE_MISMATCH        |     172 |
| RECORDED_DATE_MISMATCH             |      99 |
| TAXON_MATCH_FUZZY                  |      67 |
| COUNTRY_INVALID                    |      63 |
| RECORDED_DATE_INVALID              |      26 |
| PRESUMED_NEGATED_LATITUDE          |      17 |
| RECORDED_DATE_UNLIKELY             |      14 |
| TAXON_MATCH_NONE                   |       6 |
| ZERO_COORDINATE                    |       1 |

## catalogNumber patterns (9 = digit, A = letter)

| catalogNumber   |   count |
|:----------------|--------:|
| A.99999.999     |   43583 |
| A.99999         |   23329 |
| A.9999.999      |    6530 |
| A.9999          |    4970 |
| A.999.999       |     640 |
| A.999           |     472 |
| AA.999.999      |     433 |
| AA.9999.999     |     338 |