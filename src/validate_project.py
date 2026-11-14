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


print("\n" + "=" * 45)
print("ALL DATA-INTEGRITY CHECKS PASSED")
print("=" * 45)