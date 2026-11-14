from pathlib import Path

import pandas as pd


PROJECT_ROOT = Path(__file__).resolve().parent.parent

PROCESSED_DIR = PROJECT_ROOT / "data" / "processed"

MODIS_FILE = PROCESSED_DIR / "modis_punjab_haryana.csv"
VIIRS_FILE = PROCESSED_DIR / "viirs_punjab_haryana.csv"

GRID_RESOLUTIONS_KM = [1, 2, 5]


def load_sensor_data(file_path: Path) -> pd.DataFrame:
    """Load and validate a sensor dataset containing projected coordinates."""

    if not file_path.exists():
        raise FileNotFoundError(f"File not found: {file_path}")

    data = pd.read_csv(file_path)

    required_columns = [
        "latitude",
        "x_m",
        "y_m",
        "acq_date_utc",
        "state",
    ]

    missing = set(required_columns) - set(data.columns)

    if missing:
        raise ValueError(f"Missing columns: {missing}")

    if data[required_columns].isnull().any().any():
        raise ValueError("Required columns contain missing values.")

    if not data["x_m"].map(lambda x: pd.notna(x) and abs(x) != float("inf")).all():
        raise ValueError("Invalid projected X coordinates.")

    if not data["y_m"].map(lambda y: pd.notna(y) and abs(y) != float("inf")).all():
        raise ValueError("Invalid projected Y coordinates.")

    return data


def create_cell_days(
    data: pd.DataFrame,
    resolution_km: int
) -> pd.DataFrame:
    """Assign detections to a common grid and aggregate by cell and date."""

    cell_size_m = resolution_km * 1000

    data = data.copy()

    # A common grid origin is used for both sensors.
    data["grid_x"] = (
        data["x_m"] // cell_size_m
    ).astype("int64")

    data["grid_y"] = (
        data["y_m"] // cell_size_m
    ).astype("int64")

    cell_days = (
        data.groupby(
            ["state", "acq_date_utc", "grid_x", "grid_y"],
            as_index=False
        )
        .agg(detection_count=("latitude", "size"))
    )

    return cell_days


def compare_sensors(
    modis: pd.DataFrame,
    viirs: pd.DataFrame,
    resolution_km: int
) -> dict:
    """Compare sensor detections using cell-day presence."""

    modis_cells = create_cell_days(modis, resolution_km)

    viirs_cells = create_cell_days(viirs, resolution_km)

    comparison = modis_cells.merge(
        viirs_cells,
        on=["state", "acq_date_utc", "grid_x", "grid_y"],
        how="outer",
        suffixes=("_modis", "_viirs"),
        indicator=True
    )

    comparison["category"] = comparison["_merge"].map({
        "both": "co_detected",
        "left_only": "modis_only",
        "right_only": "viirs_only"
    })

    summary = {
        "resolution_km": resolution_km,
        "modis_cell_days": len(modis_cells),
        "viirs_cell_days": len(viirs_cells),
        "co_detected_cell_days": (
            comparison["category"] == "co_detected"
        ).sum(),
        "modis_only_cell_days": (
            comparison["category"] == "modis_only"
        ).sum(),
        "viirs_only_cell_days": (
            comparison["category"] == "viirs_only"
        ).sum(),
    }

    output_file = (
        PROCESSED_DIR
        / f"grid_comparison_{resolution_km}km.csv"
    )

    comparison.drop(columns="_merge").to_csv(
        output_file,
        index=False
    )

    return summary


def main() -> None:

    modis = load_sensor_data(MODIS_FILE)
    viirs = load_sensor_data(VIIRS_FILE)

    print("\nSPATIAL GRID SENSITIVITY ANALYSIS")
    print("=" * 55)

    results = []

    for resolution in GRID_RESOLUTIONS_KM:

        summary = compare_sensors(
            modis,
            viirs,
            resolution
        )

        results.append(summary)

        print(f"\nGRID RESOLUTION: {resolution} km")

        for key, value in summary.items():
            if key != "resolution_km":
                print(f"{key}: {value:,}")

    summary_df = pd.DataFrame(results)

    summary_file = (
        PROCESSED_DIR / "grid_sensitivity_summary.csv"
    )

    summary_df.to_csv(summary_file, index=False)

    print("\n" + "=" * 55)
    print("GRID SENSITIVITY ANALYSIS COMPLETED")
    print(f"Summary saved to: {summary_file}")


if __name__ == "__main__":
    main()