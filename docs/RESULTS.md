# Fire Parallax
## Scientific Results and Methodology

**Project:** Fire Parallax — A Sensor-Aware Burning Activity Calendar  
**Challenge:** Harmonization of MODIS and VIIRS Hot Spots  
**Study region:** Punjab and Haryana, India  
**Study period:** 1 October – 30 November 2022  
**Team:** ROCHE DOMINION

---

## 1. Research Question

How does the temporal and spatial picture of active-fire detections change when the same region is observed by MODIS and VIIRS, and how can users explore those differences without confusing sensor detections with actual fire events?

Fire Parallax investigates the spatial and temporal differences between two NASA FIRMS active-fire products. It presents a sensor-aware weekly burning activity calendar and makes the comparison rules, assumptions, and limitations explicit.

The project focuses on transparent comparison rather than treating either sensor as ground truth.

## 2. Study Area and Data

The study focuses on Punjab and Haryana, India, during October and November 2022.

Two NASA FIRMS active-fire datasets were selected:

| Dataset | Selected platform | Product |
|---|---|---|
| MODIS | Aqua | MODIS Collection 6.1 |
| VIIRS | NOAA-20 | VIIRS 375 m Collection 2 |

The downloaded extracts cover 1 October to 30 November 2022.

The initial MODIS extract contained both Terra and Aqua observations. Terra was excluded to maintain a single-platform comparison. The VIIRS extract contained NOAA-20 observations.

### 2.1 Detection filtering

The analysis retains records with `type = 0`, representing presumed vegetation fires in the FIRMS product.

These detections are not independently verified agricultural fires. They must not be presented as confirmed crop-residue burning.

### 2.2 Confidence information

The original sensor confidence fields are preserved.

- MODIS uses numeric confidence values ranging from 0 to 100.
- VIIRS uses categorical confidence values: `l`, `n`, and `h`.

The two confidence systems are not assumed to be directly equivalent.

### 2.3 Administrative boundaries

Punjab and Haryana observations were selected using state-level administrative boundaries obtained from the geoBoundaries administrative boundary dataset.

The boundary dataset used is identified as having a 2011 source vintage. The boundaries were used for spatial clipping and state-level grouping.

The boundary vintage is a limitation: the analysis does not independently verify whether the administrative geometry represents every subsequent boundary change.

## 3. Processing Methodology

The processing workflow consists of:

1. Loading and validating the original FIRMS CSV files.
2. Selecting MODIS Aqua and VIIRS NOAA-20 observations.
3. Filtering to `type = 0`.
4. Constructing UTC acquisition timestamps.
5. Projecting coordinates into UTM Zone 43N (EPSG:32643).
6. Clipping observations to Punjab and Haryana administrative boundaries.
7. Assigning observations to spatial grid cells.
8. Aggregating observations into cell-days.
9. Comparing sensor cell-day records.
10. Aggregating activity into weekly calendar records.

### 3.1 Spatial comparison

A cell-day is defined by a spatial grid cell and an acquisition date.

For each sensor, a cell-day is active when at least one qualifying detection occurs in that cell on that date.

The comparison categories are:

- **Co-detected:** Both sensors have at least one qualifying detection in the same grid cell on the same UTC date.
- **MODIS-only:** MODIS has a qualifying detection, but VIIRS does not, under the selected matching rule.
- **VIIRS-only:** VIIRS has a qualifying detection, but MODIS does not, under the selected matching rule.

These categories describe agreement between gridded sensor records. They do not identify individual physical fires.

The detection-record count represents the number of FIRMS records grouped into a cell-day. It is not a count of unique physical fires.

### 3.2 Spatial resolution

Three grid resolutions were tested:

- 1 km
- 2 km
- 5 km

The 2 km grid is used for the weekly calendar and primary spatial comparison. Its selection is a practical analytical choice, not proof that it is the objectively optimal resolution.

The grid uses a projected coordinate system (UTM Zone 43N, EPSG:32643) and a reference origin of (0 m, 0 m).

### 3.3 Weekly calendar

Weekly periods begin on Monday.

The calendar reports:

- Active cell-days.
- Detection-record counts.
- Weekly share of active cell-days.
- Number of days covered by each weekly period.

Weekly share is calculated within each state and sensor:

`weekly active cell-days / total active cell-days for that state and sensor × 100`

It represents the distribution of recorded activity across the study period, not the percentage of all fires.

The first calendar week covers only 1–2 October (two days), and the final week covers 28–30 November (three days). These partial weeks should not be compared directly with complete seven-day weeks without accounting for their shorter coverage.

## 4. Main Results

### 4.1 Spatial agreement and grid-resolution sensitivity

| Grid resolution | MODIS cell-days | VIIRS cell-days | Co-detected cell-days | Jaccard overlap |
|---|---:|---:|---:|---:|
| 1 km | 11,097 | 46,331 | 1,849 | 3.33% |
| 2 km | 9,894 | 39,726 | 3,406 | 7.37% |
| 5 km | 7,656 | 24,472 | 5,166 | 19.16% |

Jaccard overlap is calculated as:

`co-detected cell-days / (MODIS cell-days + VIIRS cell-days − co-detected cell-days)`

The measured overlap increases as the grid becomes coarser.

This demonstrates that apparent agreement depends substantially on the spatial scale used for comparison. A larger cell makes it easier for detections from different locations within that cell to be classified as co-detected.

The overlap values must not be interpreted as sensor accuracy, detection probability, or the percentage of physical fires observed by both sensors.

#### Grid-origin sensitivity

The 2 km spatial comparison was repeated using three grid origins: (0, 0), (500, 0), and (500, 500) metres in the projected coordinate system.

| Grid origin | X offset | Y offset | MODIS cell-days | VIIRS cell-days | Co-detected | Jaccard overlap |
|---|---:|---:|---:|---:|---:|---:|
| Current | 0 m | 0 m | 9,894 | 39,726 | 3,406 | 7.37% |
| Shifted East | 500 m | 0 m | 9,946 | 39,697 | 3,398 | 7.35% |
| Shifted Northeast | 500 m | 500 m | 9,924 | 39,816 | 3,378 | 7.29% |

Jaccard overlap varied from 7.29% to 7.37%, an absolute variation of 0.08 percentage points.

The small variation indicates that the observed low same-day spatial overlap is relatively stable across the three tested grid origins. This test does not establish independence from all possible grid alignments.

The reference origin (0 m, 0 m) is retained for reproducibility, rather than because it produces the highest overlap.

### 4.2 Weekly activity patterns

**Punjab**

Both sensors identify the week beginning 31 October 2022 as the peak week.

| Sensor | Peak week | Active cell-days | Weekly share |
|---|---|---:|---:|
| MODIS Aqua | 31 October | 2,933 | 31.94% |
| VIIRS NOAA-20 | 31 October | 12,254 | 34.32% |

**Haryana**

Both sensors identify the week beginning 24 October 2022 as the peak week.

| Sensor | Peak week | Active cell-days | Weekly share |
|---|---|---:|---:|
| MODIS Aqua | 24 October | 174 | 24.47% |
| VIIRS NOAA-20 | 24 October | 969 | 24.13% |

Within this particular study period, both sensors identify the same peak week in each state. The peak occurs one week earlier in Haryana than in Punjab.

This is evidence of similar peak timing under the selected processing rules. It does not establish that the sensors observed the same individual fires or that the pattern recurs annually.

### 4.3 Confidence-class observations

The clipped detection totals are:

| State | Sensor | Low | Nominal | High |
|---|---|---:|---:|---:|
| Punjab | MODIS Aqua | 449 | 8,691 | 1,348 |
| Punjab | VIIRS NOAA-20 | 1,757 | 46,856 | 1,414 |
| Haryana | MODIS Aqua | 16 | 709 | 57 |
| Haryana | VIIRS NOAA-20 | 295 | 4,395 | 86 |

MODIS numeric confidence was grouped using the thresholds documented in the MODIS Collection 6.1 Active Fire User Guide:

- Low: 0–29
- Nominal: 30–79
- High: 80–100

VIIRS native categorical values were mapped as:

- `l`: Low
- `n`: Nominal
- `h`: High

These definitions preserve the native classification of each product. The labels are similar, but the underlying confidence systems are algorithmically different.

NASA describes these confidence values as indicators intended to help users assess the quality of individual detections. They should not be interpreted as calibrated probabilities that a detection is correct.

Consequently, the class distributions support exploration within each sensor. They do not establish that one sensor has a higher proportion of accurate detections than the other.

### 4.4 High-confidence sensitivity

For this sensitivity analysis, the high-confidence subsets were defined using each product's native high-confidence designation:

- MODIS: confidence ≥ 80.
- VIIRS: confidence = `h`.

At 2 km resolution:

| Dataset | MODIS cell-days | VIIRS cell-days | Co-detected | Jaccard overlap |
|---|---:|---:|---:|---:|
| Baseline | 9,894 | 39,726 | 3,406 | 7.37% |
| High-confidence subsets | 1,303 | 1,297 | 15 | 0.58% |

The high-confidence subsets show substantially lower same-day spatial overlap than the baseline datasets.

However, the sensors use different confidence systems, and their high-confidence subsets are not equivalent statistical populations. The difference cannot be attributed to confidence filtering alone.

This result is therefore a sensitivity observation, not evidence that either sensor is more accurate or that high-confidence detections are less reliable.

### 4.5 Temporal-tolerance sensitivity

At 2 km resolution, allowing a temporal matching window increases the proportion of cell-days with at least one spatially matching record in the other sensor.

| Temporal window | MODIS directional match rate | VIIRS directional match rate |
|---|---:|---:|
| Same UTC date | 34.42% | 8.57% |
| ±1 day | 55.89% | 18.26% |
| ±2 days | 67.86% | 25.32% |

These are directional matching rates with different denominators:

- MODIS directional match rate: percentage of MODIS cell-days with at least one matching VIIRS cell-day within the selected date window.
- VIIRS directional match rate: percentage of VIIRS cell-days with at least one matching MODIS cell-day within the selected date window.

A cell-day may match multiple dates in the other sensor. These are not one-to-one matches.

The increase indicates greater spatial coincidence under a relaxed temporal rule. It does not prove that the records represent the same persistent physical fire.

## 5. Interpretation

The analysis highlights five important properties of MODIS–VIIRS comparison:

1. Spatial agreement depends strongly on the grid resolution.
2. The measured overlap is relatively stable across the three tested grid origins.
3. Weekly temporal patterns can show similar peak timing even when same-day spatial overlap is limited.
4. Confidence filtering substantially changes the measured overlap, but the two sensors' confidence systems are not equivalent.
5. Relaxing the temporal matching window increases spatial coincidence, without establishing physical fire identity.

A meaningful harmonization workflow should therefore expose its comparison assumptions instead of presenting one sensor-neutral count or agreement score without context.

## 6. Limitations

1. **Limited study period:** The analysis covers only October and November 2022. It cannot establish recurring annual patterns or long-term trends.
2. **Active-fire detections:** FIRMS hotspots are satellite thermal detections, not burned-area measurements or complete inventories of actual fires.
3. **Agricultural attribution:** The analysis does not independently verify that detections represent crop-residue burning.
4. **Sensor differences:** MODIS and VIIRS differ in spatial resolution, observation timing, viewing geometry, and detection characteristics.
5. **Confidence incompatibility:** Native confidence categories are not directly equivalent across sensors and are not calibrated probabilities of correctness.
6. **Spatial aggregation:** Coarser grids increase apparent overlap and may combine detections from distinct locations.
7. **Grid-origin testing:** Only three grid origins were tested. The results do not establish robustness to every possible grid alignment.
8. **Temporal matching:** Relaxed date windows can match records from different observation dates without establishing physical fire identity.
9. **Boundary data:** The administrative boundary dataset has a 2011 source vintage. Later boundary changes have not been independently verified.
10. **Observation gaps:** Cloud cover, satellite coverage, overpass timing, and detection limitations mean that zero recorded detections do not establish an absence of fire.
11. **Partial weeks:** The first and last calendar weeks contain fewer observation days than the complete weeks.

## 7. What the Project Does Not Claim

Fire Parallax does not:

- Identify unique physical fire events.
- Confirm agricultural burning.
- Estimate the total area burned.
- Calculate sensor detection accuracy or probability.
- Prove that one sensor is superior to the other.
- Establish that co-detected records represent the same physical fire.
- Predict future fires.
- Establish long-term seasonal trends from a single two-month period.

## 8. Project Objective

Fire Parallax aims to make historical active-fire information easier to explore while preserving the scientific distinctions between satellite products.

Its central contribution is a transparent, sensor-aware comparison framework that allows users to examine weekly activity, spatial coincidence, confidence distributions, and sensitivity to analytical choices without confusing satellite detections with verified fire events.

## 9. References and Data Sources

1. **NASA FIRMS — MODIS C6 and C6.1 Active Fire Product User Guide.** Used for MODIS confidence-class definitions and product interpretation.
2. **NASA FIRMS — VIIRS 375 m Fire/Hotspot Attribute Description.** Used for VIIRS confidence-category definitions and NOAA-20 platform identification.
3. **NASA FIRMS — Active Fire Data.** Source of the MODIS Aqua and VIIRS NOAA-20 active-fire extracts used in this analysis.
4. **geoBoundaries — India ADM1 administrative boundaries.** Source of the state boundary geometry used for clipping; source vintage identified as 2011.
5. **EPSG:32643 — WGS 84 / UTM zone 43N.** Coordinate reference system used for spatial analysis.