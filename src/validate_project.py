from pathlib import Path
import pandas as pd

DATA = Path("data/processed")

def check(condition, message):
    if not condition:
        raise AssertionError(f"FAILED: {message}")
    print(f"PASSED: {message}")


# 1. Regional datasets
modis = pd.read_csv(DATA / "modis_punjab_haryana.csv")
viirs = pd.read_csv(DATA / "viirs_punjab_haryana.csv")

check(len(modis) == 11270, "MODIS regional record count")
check(len(viirs) == 54803, "VIIRS regional record count")
# 1A. Confidence distributions (reference dataset checks)

modis_confidence = pd.to_numeric(
    modis["confidence"], errors="raise"
)

modis_counts = {
    "Low": int((modis_confidence <= 29).sum()),
    "Nominal": int(
        ((modis_confidence >= 30) & (modis_confidence <= 79)).sum()
    ),
    "High": int((modis_confidence >= 80).sum()),
}

expected_modis_counts = {
    "Low": 465,
    "Nominal": 9400,
    "High": 1405,
}

check(
    modis_counts == expected_modis_counts,
    "MODIS confidence distribution"
)


viirs_confidence = (
    viirs["confidence"].astype(str).str.strip().str.lower()
)

viirs_counts = {
    "Low": int((viirs_confidence == "l").sum()),
    "Nominal": int((viirs_confidence == "n").sum()),
    "High": int((viirs_confidence == "h").sum()),
}

expected_viirs_counts = {
    "Low": 2052,
    "Nominal": 51251,
    "High": 1500,
}

check(
    viirs_counts == expected_viirs_counts,
    "VIIRS confidence distribution"
)


# 2. Weekly activity calendar
weekly = pd.read_csv(DATA / "weekly_activity_calendar.csv")

check(len(weekly) == 40, "Weekly calendar has 40 records")

expected_weekly = {
    ("Punjab", "MODIS Aqua"): (9183, 10488),
    ("Punjab", "VIIRS NOAA-20"): (35710, 50027),
    ("Haryāna", "MODIS Aqua"): (711, 782),
    ("Haryāna", "VIIRS NOAA-20"): (4016, 4776),
}

for (state, sensor), (cells, detections) in expected_weekly.items():
    subset = weekly[
        (weekly["state"] == state) &
        (weekly["sensor"] == sensor)
    ]

    check(
        int(subset["active_cell_days"].sum()) == cells,
        f"{state} / {sensor}: active cell-days"
    )

    check(
        int(subset["detection_count"].sum()) == detections,
        f"{state} / {sensor}: detections"
    )


# 3. Confidence calendar
confidence = pd.read_csv(
    DATA / "confidence_class_calendar.csv"
)

check(len(confidence) == 120, "Confidence calendar has 120 records")

expected_confidence = {
    ("Haryāna", "MODIS Aqua", "Low"): (16, 16),
    ("Haryāna", "MODIS Aqua", "Nominal"): (658, 709),
    ("Haryāna", "MODIS Aqua", "High"): (54, 57),
    ("Haryāna", "VIIRS NOAA-20", "Low"): (281, 295),
    ("Haryāna", "VIIRS NOAA-20", "Nominal"): (3759, 4395),
    ("Haryāna", "VIIRS NOAA-20", "High"): (74, 86),

    ("Punjab", "MODIS Aqua", "Low"): (448, 449),
    ("Punjab", "MODIS Aqua", "Nominal"): (7880, 8691),
    ("Punjab", "MODIS Aqua", "High"): (1249, 1348),
    ("Punjab", "VIIRS NOAA-20", "Low"): (1678, 1757),
    ("Punjab", "VIIRS NOAA-20", "Nominal"): (34128, 46856),
    ("Punjab", "VIIRS NOAA-20", "High"): (1223, 1414),
}

for (state, sensor, category), (cells, detections) in expected_confidence.items():
    subset = confidence[
        (confidence["state"] == state) &
        (confidence["sensor"] == sensor) &
        (confidence["confidence_class"] == category)
    ]

    check(
        int(subset["active_cell_days"].sum()) == cells,
        f"{state} / {sensor} / {category}: active cell-days"
    )

    check(
        int(subset["detection_count"].sum()) == detections,
        f"{state} / {sensor} / {category}: detections"
    )


# 4. Spatial comparison
grid = pd.read_csv(DATA / "grid_comparison_2km.csv")

expected_categories = {
    "co_detected": 3406,
    "modis_only": 6488,
    "viirs_only": 36320,
}

for category, expected_count in expected_categories.items():
    actual_count = int((grid["category"] == category).sum())

    check(
        actual_count == expected_count,
        f"Spatial comparison: {category}"
    )

# 5. High-confidence spatial comparison

high_confidence = pd.read_csv(
    DATA / "high_confidence_grid_summary.csv"
)

expected_high_confidence = {
    1: (1392, 1350, 4, 1388, 1346),
    2: (1303, 1297, 15, 1288, 1282),
    5: (1168, 1127, 36, 1132, 1091),
}

expected_jaccard = {
    1: 0.146092,
    2: 0.580271,
    5: 1.593625,
}

check(
    len(high_confidence) == 3,
    "High-confidence comparison has three resolutions"
)

for resolution, expected in expected_high_confidence.items():
    row = high_confidence[
        high_confidence["resolution_km"] == resolution
    ]

    check(
        len(row) == 1,
        f"High-confidence comparison: {resolution} km resolution exists"
    )

    actual = tuple(
        int(row.iloc[0][column])
        for column in [
            "modis_cell_days",
            "viirs_cell_days",
            "co_detected_cell_days",
            "modis_only_cell_days",
            "viirs_only_cell_days",
        ]
    )

    check(
        actual == expected,
        f"High-confidence comparison: {resolution} km counts"
    )

    check(
        abs(
            float(row.iloc[0]["jaccard_overlap_pct"])
            - expected_jaccard[resolution]
          ) < 0.000001,
        f"High-confidence comparison: {resolution} km Jaccard"
    )

# 6. Grid-resolution sensitivity

sensitivity = pd.read_csv(
    DATA / "grid_sensitivity_summary.csv"
)

expected_sensitivity = {
    1: (11097, 46331, 1849, 9248, 44482),
    2: (9894, 39726, 3406, 6488, 36320),
    5: (7656, 24472, 5166, 2490, 19306),
}

check(
    len(sensitivity) == 3,
    "Grid sensitivity has three resolutions"
)

for resolution, expected in expected_sensitivity.items():
    row = sensitivity[
        sensitivity["resolution_km"] == resolution
    ]

    check(
        len(row) == 1,
        f"Grid sensitivity: {resolution} km resolution exists"
    )

    actual = tuple(
        int(row.iloc[0][column])
        for column in [
            "modis_cell_days",
            "viirs_cell_days",
            "co_detected_cell_days",
            "modis_only_cell_days",
            "viirs_only_cell_days",
        ]
    )

    check(
        actual == expected,
        f"Grid sensitivity: {resolution} km counts"
    )

# 7. High-confidence to any-confidence directional comparison

cross_sensor = pd.read_csv(
    DATA / "high_confidence_cross_sensor_summary.csv"
)

expected_cross_sensor = {
    (1, "MODIS High to any VIIRS"): (1392, 46331, 343, 1049),
    (1, "VIIRS High to any MODIS"): (1350, 11097, 32, 1318),
    (2, "MODIS High to any VIIRS"): (1303, 39726, 585, 718),
    (2, "VIIRS High to any MODIS"): (1297, 9894, 90, 1207),
    (5, "MODIS High to any VIIRS"): (1168, 24472, 904, 264),
    (5, "VIIRS High to any MODIS"): (1127, 7656, 249, 878),
}

expected_match_rates = {
    (1, "MODIS High to any VIIRS"): 24.640805,
    (1, "VIIRS High to any MODIS"): 2.370370,
    (2, "MODIS High to any VIIRS"): 44.896393,
    (2, "VIIRS High to any MODIS"): 6.939090,
    (5, "MODIS High to any VIIRS"): 77.397260,
    (5, "VIIRS High to any MODIS"): 22.094055,
}

check(
    len(cross_sensor) == 6,
    "Cross-confidence comparison has six directional results"
)

for key, expected in expected_cross_sensor.items():
    resolution, direction = key

    row = cross_sensor[
        (cross_sensor["resolution_km"] == resolution) &
        (cross_sensor["direction"] == direction)
    ]

    check(
        len(row) == 1,
        f"Cross-confidence comparison: {resolution} km / {direction}"
    )

    actual = tuple(
        int(row.iloc[0][column])
        for column in [
            "high_sensor_cell_days",
            "other_sensor_any_cell_days",
            "matched_high_cell_days",
            "unmatched_high_cell_days",
        ]
    )

    check(
        actual == expected,
        f"Cross-confidence comparison: {resolution} km counts / {direction}"
    )

    check(
        abs(
            float(row.iloc[0]["matched_high_cell_days_pct"])
            - expected_match_rates[key]
        ) < 0.000001,
        f"Cross-confidence comparison: {resolution} km match rate / {direction}"
    )

print("\n" + "=" * 45)
print("ALL DATA-INTEGRITY CHECKS PASSED")
print("=" * 45)