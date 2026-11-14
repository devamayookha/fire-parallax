from pathlib import Path

import pandas as pd

from src.grid_analysis import create_cell_days

PROJECT_ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = PROJECT_ROOT / "data" / "processed"

DATASETS = {
    "Baseline": (
        "modis_punjab_haryana.csv",
        "viirs_punjab_haryana.csv",
    ),
    "High-confidence": (
        "modis_punjab_haryana_high.csv",
        "viirs_punjab_haryana_high.csv",
    ),
}

GRID_RESOLUTION_KM = 2
TOLERANCE_DAYS = [0, 1, 2]


def load_cell_days(filename):
    data = pd.read_csv(DATA_DIR / filename)

    cell_days = create_cell_days(
        data,
        GRID_RESOLUTION_KM
    )

    cell_days["date"] = pd.to_datetime(
        cell_days["acq_date_utc"]
    )

    return cell_days


def compare_with_tolerance(modis, viirs, tolerance):
    """Calculate directional cell-day matching within a date tolerance."""

    keys = ["state", "grid_x", "grid_y"]

    pairs = modis[
        keys + ["date"]
    ].merge(
        viirs[keys + ["date"]],
        on=keys,
        suffixes=("_modis", "_viirs")
    )

    pairs["day_difference"] = (
        pairs["date_modis"] - pairs["date_viirs"]
    ).dt.days.abs()

    matched_pairs = pairs[
        pairs["day_difference"] <= tolerance
    ]

    matched_modis = (
        matched_pairs["date_modis"]
        .groupby(
            [
                matched_pairs["state"],
                matched_pairs["grid_x"],
                matched_pairs["grid_y"],
            ]
        )
        .size()
    )

    # Count unique MODIS cell-days that have a VIIRS match.
    matched_modis_keys = matched_pairs[
        ["state", "grid_x", "grid_y", "date_modis"]
    ].drop_duplicates()

    matched_viirs_keys = matched_pairs[
        ["state", "grid_x", "grid_y", "date_viirs"]
    ].drop_duplicates()

    modis_matched_count = len(matched_modis_keys)
    viirs_matched_count = len(matched_viirs_keys)

    modis_total = len(modis)
    viirs_total = len(viirs)

    return {
        "tolerance_days": tolerance,
        "modis_cell_days": modis_total,
        "viirs_cell_days": viirs_total,
        "matched_modis_cell_days": modis_matched_count,
        "matched_viirs_cell_days": viirs_matched_count,
        "modis_match_rate_pct": (
            modis_matched_count / modis_total * 100
            if modis_total else 0
        ),
        "viirs_match_rate_pct": (
            viirs_matched_count / viirs_total * 100
            if viirs_total else 0
        ),
    }


def main():

    all_results = []

    for dataset_name, filenames in DATASETS.items():

        modis = load_cell_days(filenames[0])
        viirs = load_cell_days(filenames[1])

        print(f"\n{dataset_name.upper()}")
        print("=" * 75)

        for tolerance in TOLERANCE_DAYS:

            result = compare_with_tolerance(
                modis,
                viirs,
                tolerance
            )

            result["dataset"] = dataset_name
            all_results.append(result)

            print(
                f"\nTolerance: ±{tolerance} day(s)"
            )

            for key, value in result.items():
                if key not in ["dataset", "tolerance_days"]:
                    if "pct" in key:
                        print(f"{key}: {value:.2f}%")
                    else:
                        print(f"{key}: {value:,}")

    results = pd.DataFrame(all_results)

    output_file = (
        DATA_DIR / "temporal_tolerance_summary.csv"
    )

    results.to_csv(output_file, index=False)

    print("\n" + "=" * 75)
    print("TEMPORAL TOLERANCE ANALYSIS COMPLETED")
    print("Saved:", output_file)


if __name__ == "__main__":
    main()