<div align="center">

# 🔥 FIRE PARALLAX

### A SENSOR-AWARE BURNING ACTIVITY CALENDAR

**Two sensors. One region. A clearer picture of detected burning activity.**

<br>

[![NASA Space Apps Challenge 2026](https://img.shields.io/badge/NASA%20Space%20Apps-2026-0B3D91?style=for-the-badge&logo=nasa&logoColor=white)](https://www.spaceappschallenge.org/)
[![Python](https://img.shields.io/badge/Python-3.13-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://www.python.org/)
[![Streamlit](https://img.shields.io/badge/Streamlit-Dashboard-FF4B4B?style=for-the-badge&logo=streamlit&logoColor=white)](https://streamlit.io/)
[![License: MIT](https://img.shields.io/badge/License-MIT-green?style=for-the-badge)](LICENSE)

<br>

**Built by TEAM ROCHE DOMINION**

</div>

---

## 🌌 THE IDEA

What happens when two different satellite instruments observe the same region?

Do they record similar patterns of burning activity? Do their observations overlap? How does the seasonal picture change depending on the sensor?

**Fire Parallax** explores these questions by comparing active-fire observations from NASA's MODIS Aqua and VIIRS NOAA-20 instruments across Punjab and Haryana, India.

Rather than treating every satellite detection as an individual fire, the project harmonizes observations using a common spatial grid and temporal framework to explore where and when the sensors record activity.

> Our goal is not simply to count hotspots. It is to understand how satellite observation differences shape the picture of detected burning activity.

## 🛰️ THE SATELLITES

<div align="center">

| MODIS Aqua | VIIRS NOAA-20 |
|:---:|:---:|
| Moderate Resolution Imaging Spectroradiometer | Visible Infrared Imaging Radiometer Suite |
| Approximately 1 km nominal resolution | 375 m nominal resolution |
| NASA Aqua satellite | NOAA-20 satellite |

</div>

Different instruments have different spatial resolutions, observation characteristics and confidence systems. Comparing their raw hotspot counts directly can therefore be misleading.

Fire Parallax makes these differences part of the analysis.

## 🎯 EXPLORE THE PROJECT

| Feature | What it does |
|:---|:---|
| 📊 **Burning Activity Calendar** | Explore weekly activity patterns and seasonal distributions. |
| 🗺️ **Spatial Explorer** | Visualize co-detected, MODIS-only and VIIRS-only cell-days. |
| 📈 **Sensor Comparison** | Compare activity across Punjab and Haryana. |
| 🔬 **Confidence Explorer** | Examine the confidence categories reported by each sensor. |
| 📖 **Methodology** | Understand the processing rules, comparison framework and limitations. |
| 📉 **Sensitivity Analysis** | Examine how spatial resolution affects sensor agreement. |

## 📍 STUDY REGION

**Punjab and Haryana, India**

| Parameter | Configuration |
|:---|:---|
| Observation period | 1 October – 30 November 2022 |
| MODIS dataset | Collection 6.1 – Aqua |
| VIIRS dataset | Collection 2 – NOAA-20 |
| Detection type | Type 0 |
| Primary spatial grid | 2 km |
| Additional grid tests | 1 km and 5 km |
| Temporal aggregation | Weekly |
| Coordinate reference system | EPSG:32643 |

The region and observation period provide a focused case study for examining seasonal active-fire detection patterns.

## 🧬 HOW IT WORKS

```text
                 NASA FIRMS DATA
                        |
             +----------+----------+
             |                     |
         MODIS Aqua           VIIRS NOAA-20
             |                     |
             +----------+----------+
                        |
               DATA PREPROCESSING
                        |
                SENSOR SELECTION
                  AND FILTERING
                        |
                 REGIONAL CLIPPING
                        |
                  COMMON SPATIAL
                      GRID
                        |
                 CELL-DAY MATCHING
                        |
             +----------+----------+
             |          |          |
          BOTH       MODIS       VIIRS
         SENSORS      ONLY        ONLY
             |          |          |
             +----------+----------+
                        |
              TEMPORAL & SPATIAL
                    ANALYSIS
                        |
                 INTERACTIVE
                   DASHBOARD
```

### What is a cell-day?

A cell-day represents a spatial grid cell with at least one qualifying detection on a particular UTC date.

We classify cell-days into three groups:

- 🟢 **Co-detected:** Both sensors recorded at least one qualifying detection in the same cell on the same UTC date.
- 🔵 **MODIS-only:** MODIS recorded a detection, but VIIRS did not under the selected matching rule.
- 🟠 **VIIRS-only:** VIIRS recorded a detection, but MODIS did not under the selected matching rule.

These are observation-comparison categories, not reconstructed physical fire events.

## 📊 SENSITIVITY ANALYSIS

Spatial resolution can strongly influence apparent agreement between satellite observations.

Our analysis tests three grid sizes:

| Grid size | Co-detected cell-days | Jaccard agreement |
|:---:|---:|---:|
| 1 km | 1,849 | 3.33% |
| 2 km | 3,406 | 7.37% |
| 5 km | 5,166 | 19.16% |

The increasing overlap demonstrates why spatial scale matters when comparing sensors.

The 2 km grid is our primary working configuration, not a universally optimal resolution.

We also examine grid-origin shifts and temporal matching tolerances to understand how comparison choices affect the results.

## 🧰 TECHNOLOGY STACK

<div align="center">

![Python](https://img.shields.io/badge/Python-3776AB?style=flat-square&logo=python&logoColor=white)
![Pandas](https://img.shields.io/badge/Pandas-150458?style=flat-square&logo=pandas&logoColor=white)
![NumPy](https://img.shields.io/badge/NumPy-013243?style=flat-square&logo=numpy&logoColor=white)
![GeoPandas](https://img.shields.io/badge/GeoPandas-139C5A?style=flat-square)
![Shapely](https://img.shields.io/badge/Shapely-3776AB?style=flat-square)
![Plotly](https://img.shields.io/badge/Plotly-3F4F75?style=flat-square&logo=plotly&logoColor=white)
![Streamlit](https://img.shields.io/badge/Streamlit-FF4B4B?style=flat-square&logo=streamlit&logoColor=white)

</div>

- **Data processing:** Pandas, NumPy
- **Geospatial analysis:** GeoPandas, Shapely, PyProj
- **Visualization:** Plotly
- **Interactive application:** Streamlit
- **Testing and validation:** Pytest and project-specific integrity checks
- **Data source:** NASA FIRMS

## 📂 PROJECT STRUCTURE

```text
fire-parallax/
│
├── app/
│   └── main.py
│
├── assets/
│   └── screenshots/
│
├── data/
│   ├── raw/
│   ├── processed/
│   └── sample/
│
├── docs/
│   └── RESULTS.md
│
├── src/
│   ├── preprocess.py
│   ├── boundaries.py
│   ├── clip_region.py
│   ├── spatial.py
│   ├── grid_analysis.py
│   ├── calendar_analysis.py
│   ├── confidence_calendar.py
│   ├── confidence_summary.py
│   ├── agreement_analysis.py
│   ├── high_confidence_analysis.py
│   ├── date_overlap_analysis.py
│   ├── temporal_tolerance.py
│   ├── grid_origin_sensitivity.py
│   ├── validate_project.py
│   └── visualization modules
│
├── tests/
├── requirements.txt
├── README.md
├── LICENSE
└── .gitignore
```

## 🚀 RUN LOCALLY

### 1. Clone the repository

```cmd
git clone https://github.com/devamayookha/fire-parallax.git
cd fire-parallax
```

### 2. Create a virtual environment

```cmd
python -m venv .venv
```

Activate it in Windows CMD:

```cmd
.venv\Scripts\activate
```

### 3. Install dependencies

```cmd
pip install -r requirements.txt
```

### 4. Obtain the datasets

Download historical active-fire data from [NASA FIRMS](https://firms.modaps.eosdis.nasa.gov/).

Use the following study configuration:

- **Date range:** 2022-10-01 to 2022-11-30
- **Geographical bounding box:** West 73.7, South 27.5, East 77.9, North 32.6
- **MODIS:** Collection 6.1, Aqua observations
- **VIIRS:** Collection 2, NOAA-20 observations
- **Format:** CSV

Extract the downloaded files into the following locations:

```text
data/
└── raw/
    ├── modis/
    │   └── fire_archive_M-C61_846582.csv
    │
    └── viirs_noaa20/
        └── fire_archive_J1V-C2_846583.csv
```

The filenames above correspond to the datasets used in this project's analysis. If you download new FIRMS requests, update the filenames or corresponding input paths in the source modules.

The administrative boundary data is retrieved by the boundary-processing module.

**Important:** Raw and processed datasets are excluded from this GitHub repository. They must be obtained and generated locally.

### 5. Generate the analysis outputs

Run these commands from the repository root, in the following order.

**Core preprocessing and analysis:**

```cmd
python -m src.preprocess
python -m src.boundaries
python -m src.clip_region
python -m src.spatial
python -m src.grid_analysis
python -m src.calendar_analysis
python -m src.confidence_calendar
python -m src.confidence_summary
```

**Additional comparison and sensitivity analyses:**

```cmd
python -m src.agreement_analysis
python -m src.high_confidence_analysis
python -m src.date_overlap_analysis
python -m src.temporal_tolerance
python -m src.grid_origin_sensitivity
```

**Validate the generated outputs:**

```cmd
python -m src.validate_project
```

The validation module checks expected record counts, calendar dimensions, confidence summaries and spatial comparison totals.

### 6. Launch the application

```cmd
streamlit run app/main.py
```

The application reads the generated processed datasets from `data/processed/`.

## 📚 DOCUMENTATION

For detailed methodology, data processing decisions, numerical results, sensitivity analysis and scientific limitations, see:

**[📖 Detailed Results and Methodology](docs/RESULTS.md)**

## ⚠️ SCIENTIFIC LIMITATIONS

We believe responsible interpretation is just as important as visualization.

- Active-fire hotspots are satellite thermal detections, not verified physical fire events.
- Type 0 detections are not proof of agricultural burning.
- MODIS and VIIRS have different resolutions, observation times and detection characteristics.
- Their confidence systems are not directly equivalent.
- A missing satellite detection does not establish that no fire occurred.
- Spatial co-detection does not prove that both sensors observed the same physical fire.
- The analysis covers a limited geographical region and observation period.
- Confidence-class-specific active cell-days can overlap when multiple confidence classes occur in the same cell-day. They should not be summed as unique activity totals.

**Fire Parallax compares satellite observations. It does not claim to reconstruct every real-world fire event.**

---

# 👥 MEET THE TEAM

<div align="center">

## ROCHE DOMINION

*Curiosity beyond the visible. Analysis beyond the obvious.*

<br>

| Team Member | GitHub |
|:---:|:---:|
| **B R Devamayookha** | [@devamayookha](https://github.com/devamayookha) |
| **Kanisha M** | [@kanisha0729](https://github.com/kanisha0729) |

<br>

**NASA SPACE APPS CHALLENGE 2026**

</div>

---

## 🌠 OUR MISSION

To explore how Earth-observing satellites reveal patterns that may not be obvious from a single instrument's observations.

**Because the way we observe Earth matters just as much as what we observe.**

<div align="center">

### 🔥 FIRE PARALLAX

**TEAM ROCHE DOMINION**

[View Repository](https://github.com/devamayookha/fire-parallax) · [Report an Issue](https://github.com/devamayookha/fire-parallax/issues)

<br>

*Built with curiosity, satellite data and a passion for Earth observation.*

</div>