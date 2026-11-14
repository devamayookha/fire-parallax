from pathlib import Path

import pandas as pd


PROJECT_ROOT = Path(__file__).resolve().parent.parent
PROCESSED_DIR = PROJECT_ROOT / "data" / "processed"

MODIS_FILE = PROCESSED_DIR / "modis_punjab_haryana.csv"
VIIRS_FILE = PROCESSED_DIR / "viirs_punjab_haryana.csv"

GRID_SIZE_M = 2000

# Different spatial grid origins, in metres.
GRID_ORIGINS = [
    ("Current", 0, 0),
    ("Shifted_East", 500, 0),
    ("Shifted_NorthEast", 500, 500),
]


def load_data(file_path):
    data = pd.read_csv(file_path)

    required = [
        "x_m",
        "y_m",
        "acq_date_utc",
        "state",
        "latitude",
    ]

    missing = set(required) - set(data.columns)

    if missing:
        raise ValueError(f"Missing columns in {file_path}: {missing}")

    if data[required].isnull().any().any():
        raise ValueError(f"Missing values found in {file_path}")

    return data


def create_cell_days(data, origin_x, origin_y):
    data = data.copy()

    data["grid_x"] = (
        (data["x_m"] - origin_x) // GRID_SIZE_M
    ).astype("int64")

    data["grid_y"] = (
        (data["y_m"] - origin_y) // GRID_SIZE_M
    ).astype("int64")

    cell_days = (
        data.groupby(
            ["state", "acq_date_utc", "grid_x", "grid_y"],
            as_index=False
        )
        .agg(detection_count=("latitude", "size"))
    )

    return cell_days


def compare_origin(modis, viirs, origin_name, origin_x, origin_y):

    modis_cells = create_cell_days(
        modis, origin_x, origin_y
    )

    viirs_cells = create_cell_days(
        viirs, origin_x, origin_y
    )

    comparison = modis_cells.merge(
        viirs_cells,
        on=["state", "acq_date_utc", "grid_x", "grid_y"],
        how="outer",
        suffixes=("_modis", "_viirs"),
        indicator=True
    )

    modis_count = len(modis_cells)
    viirs_count = len(viirs_cells)

    co_detected = (
        comparison["_merge"] == "both"
    ).sum()

    modis_only = (
        comparison["_merge"] == "left_only"
    ).sum()

    viirs_only = (
        comparison["_merge"] == "right_only"
    ).sum()

    union = modis_count + viirs_count - co_detected

    jaccard = (
        co_detected / union * 100
        if union > 0 else 0
    )

    return {
        "grid_origin": origin_name,
        "origin_x_m": origin_x,
        "origin_y_m": origin_y,
        "modis_cell_days": modis_count,
        "viirs_cell_days": viirs_count,
        "co_detected_cell_days": co_detected,
        "modis_only_cell_days": modis_only,
        "viirs_only_cell_days": viirs_only,
        "jaccard_overlap_pct": jaccard,
    }


def main():

    modis = load_data(MODIS_FILE)
    viirs = load_data(VIIRS_FILE)

    results = []

    print("\nGRID ORIGIN SENSITIVITY ANALYSIS")
    print("=" * 65)

    for name, origin_x, origin_y in GRID_ORIGINS:

        result = compare_origin(
            modis,
            viirs,
            name,
            origin_x,
            origin_y
        )

        results.append(result)

        print(f"\nGRID ORIGIN: {name}")
        print(f"X offset: {origin_x} m")
        print(f"Y offset: {origin_y} m")
        print(f"MODIS cell-days: {result['modis_cell_days']:,}")
        print(f"VIIRS cell-days: {result['viirs_cell_days']:,}")
        print(f"Co-detected: {result['co_detected_cell_days']:,}")
        print(f"MODIS-only: {result['modis_only_cell_days']:,}")
        print(f"VIIRS-only: {result['viirs_only_cell_days']:,}")
        print(f"Jaccard overlap: {result['jaccard_overlap_pct']:.2f}%")

    summary = pd.DataFrame(results)

    output_file = (
        PROCESSED_DIR / "grid_origin_sensitivity.csv"
    )

    summary.to_csv(output_file, index=False)

    print("\n" + "=" * 65)
    print("GRID ORIGIN SENSITIVITY COMPLETED")
    print("Saved:", output_file)


if __name__ == "__main__":
    main()