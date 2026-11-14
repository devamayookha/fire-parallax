from pathlib import Path

import pandas as pd


PROJECT_ROOT = Path(__file__).resolve().parent.parent

MODIS_FILE = (
    PROJECT_ROOT
    / "data"
    / "raw"
    / "modis"
    / "fire_archive_M-C61_846582.csv"
)

VIIRS_FILE = (
    PROJECT_ROOT
    / "data"
    / "raw"
    / "viirs_noaa20"
    / "fire_archive_J1V-C2_846583.csv"
)


def inspect_dataset(file_path: Path, sensor_name: str) -> None:
    """Print a basic quality report for a NASA FIRMS dataset."""

    if not file_path.exists():
        raise FileNotFoundError(f"Dataset not found: {file_path}")

    data = pd.read_csv(file_path)

    print(f"\n{'=' * 50}")
    print(f"{sensor_name} DATASET")
    print(f"{'=' * 50}")

    print(f"Total records: {len(data)}")
    print(f"Date range: {data['acq_date'].min()} to {data['acq_date'].max()}")
    print(f"Missing values: {data.isna().sum().sum()}")
    print(f"Exact duplicate rows: {data.duplicated().sum()}")

    print("\nSatellite distribution:")
    print(data["satellite"].value_counts())

    print("\nDetection type distribution:")
    print(data["type"].value_counts().sort_index())

    print("\nConfidence distribution:")
    print(data["confidence"].value_counts(dropna=False))

    vegetation_fires = data[data["type"] == 0]

    print(f"\nType-0 detections: {len(vegetation_fires)}")


def main() -> None:
    inspect_dataset(MODIS_FILE, "MODIS C6.1")
    inspect_dataset(VIIRS_FILE, "VIIRS NOAA-20")


if __name__ == "__main__":
    main()
