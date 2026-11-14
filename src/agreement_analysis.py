from pathlib import Path

import pandas as pd


PROJECT_ROOT = Path(__file__).resolve().parent.parent

DATA_FILE = (
    PROJECT_ROOT
    / "data"
    / "processed"
    / "grid_sensitivity_summary.csv"
)

OUTPUT_FILE = (
    PROJECT_ROOT
    / "data"
    / "processed"
    / "agreement_metrics.csv"
)


def calculate_agreement(data: pd.DataFrame) -> pd.DataFrame:
    """Calculate spatial overlap metrics for each grid resolution."""

    data = data.copy()

    union = (
        data["modis_cell_days"]
        + data["viirs_cell_days"]
        - data["co_detected_cell_days"]
    )

    data["jaccard_overlap_pct"] = (
        data["co_detected_cell_days"] / union * 100
    )

    data["modis_overlap_pct"] = (
        data["co_detected_cell_days"]
        / data["modis_cell_days"] * 100
    )

    data["viirs_overlap_pct"] = (
        data["co_detected_cell_days"]
        / data["viirs_cell_days"] * 100
    )

    return data


def main() -> None:

    if not DATA_FILE.exists():
        raise FileNotFoundError(
            f"Sensitivity file not found: {DATA_FILE}"
        )

    data = pd.read_csv(DATA_FILE)

    required_columns = [
        "resolution_km",
        "modis_cell_days",
        "viirs_cell_days",
        "co_detected_cell_days",
    ]

    missing = set(required_columns) - set(data.columns)

    if missing:
        raise ValueError(f"Missing columns: {missing}")

    results = calculate_agreement(data)

    results.to_csv(
        OUTPUT_FILE,
        index=False
    )

    print("\nSPATIAL AGREEMENT ANALYSIS")
    print("=" * 55)

    print(
        results[
            [
                "resolution_km",
                "jaccard_overlap_pct",
                "modis_overlap_pct",
                "viirs_overlap_pct",
            ]
        ].to_string(index=False)
    )

    print(f"\nSaved: {OUTPUT_FILE}")


if __name__ == "__main__":
    main()