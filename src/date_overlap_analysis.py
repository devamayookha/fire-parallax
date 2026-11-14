from pathlib import Path

import pandas as pd

PROJECT_ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = PROJECT_ROOT / "data" / "processed"

FILES = {
    "MODIS baseline": "modis_punjab_haryana.csv",
    "VIIRS baseline": "viirs_punjab_haryana.csv",
    "MODIS high": "modis_punjab_haryana_high.csv",
    "VIIRS high": "viirs_punjab_haryana_high.csv",
}


def load_daily_activity(filename):
    data = pd.read_csv(DATA_DIR / filename)

    daily = (
        data.groupby(["state", "acq_date_utc"])
        .size()
        .reset_index(name="detection_count")
    )

    return daily


def compare_daily_activity(modis, viirs, label):

    comparison = modis.merge(
        viirs,
        on=["state", "acq_date_utc"],
        how="outer",
        suffixes=("_modis", "_viirs"),
        indicator=True
    )

    both = (comparison["_merge"] == "both").sum()
    modis_only = (comparison["_merge"] == "left_only").sum()
    viirs_only = (comparison["_merge"] == "right_only").sum()

    total = both + modis_only + viirs_only

    print(f"\n{label}")
    print("-" * 45)
    print(f"Shared state-days: {both}")
    print(f"MODIS-only state-days: {modis_only}")
    print(f"VIIRS-only state-days: {viirs_only}")
    print(f"Total state-days: {total}")

    if total:
        print(f"Date-level Jaccard: {both / total * 100:.2f}%")


def main():

    datasets = {}

    for label, filename in FILES.items():
        datasets[label] = load_daily_activity(filename)

    compare_daily_activity(
        datasets["MODIS baseline"],
        datasets["VIIRS baseline"],
        "BASELINE DATE OVERLAP"
    )

    compare_daily_activity(
        datasets["MODIS high"],
        datasets["VIIRS high"],
        "HIGH-CONFIDENCE DATE OVERLAP"
    )


if __name__ == "__main__":
    main()