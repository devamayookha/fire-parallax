from pathlib import Path

import pandas as pd


PROJECT_ROOT = Path(__file__).resolve().parent.parent

RAW_DIR = PROJECT_ROOT / "data" / "raw"
PROCESSED_DIR = PROJECT_ROOT / "data" / "processed"

MODIS_FILE = RAW_DIR / "modis" / "fire_archive_M-C61_846582.csv"
VIIRS_FILE = RAW_DIR / "viirs_noaa20" / "fire_archive_J1V-C2_846583.csv"


REQUIRED_COLUMNS = [
    "latitude",
    "longitude",
    "acq_date",
    "acq_time",
    "satellite",
    "instrument",
    "confidence",
    "type",
]


def load_and_validate(file_path: Path) -> pd.DataFrame:
    """Load a FIRMS CSV and verify its required columns."""

    if not file_path.exists():
        raise FileNotFoundError(f"File not found: {file_path}")

    data = pd.read_csv(file_path)

    missing_columns = set(REQUIRED_COLUMNS) - set(data.columns)

    if missing_columns:
        raise ValueError(
            f"Missing required columns: {missing_columns}"
        )

    if data[REQUIRED_COLUMNS].isna().any().any():
        raise ValueError("Missing values found in required columns.")

    return data

def add_time_fields(data: pd.DataFrame) -> pd.DataFrame:
    """Create standardized UTC date and time fields."""

    data = data.copy()

    time_string = (
        data["acq_time"]
        .astype(str)
        .str.zfill(4)
    )

    datetime_string = (
        data["acq_date"].astype(str)
        + " "
        + time_string
    )

    data["acq_datetime_utc"] = pd.to_datetime(
        datetime_string,
        format="%Y-%m-%d %H%M",
        utc=True,
        errors="raise"
    )

    data["acq_date_utc"] = (
        data["acq_datetime_utc"].dt.strftime("%Y-%m-%d")
    )

    data["acq_time_utc"] = (
        data["acq_datetime_utc"].dt.strftime("%H:%M")
    )

    return data


def prepare_modis() -> pd.DataFrame:
    """Select Aqua type-0 detections from MODIS."""

    data = load_and_validate(MODIS_FILE)

    aqua = data[
        (data["satellite"] == "Aqua")
        & (data["type"] == 0)
    ].copy()

    aqua["sensor"] = "MODIS"
    aqua["platform"] = "Aqua"

    return aqua


def prepare_viirs() -> pd.DataFrame:
    """Select NOAA-20 type-0 detections from VIIRS."""

    data = load_and_validate(VIIRS_FILE)

    viirs = data[
        (data["satellite"] == "N20")
        & (data["type"] == 0)
    ].copy()

    viirs["sensor"] = "VIIRS"
    viirs["platform"] = "NOAA-20"

    return viirs


def save_dataset(data: pd.DataFrame, filename: str) -> None:
    """Save a processed dataset without changing the raw source."""

    PROCESSED_DIR.mkdir(parents=True, exist_ok=True)

    output_file = PROCESSED_DIR / filename

    data.to_csv(output_file, index=False)

    print(f"Saved: {output_file}")
    print(f"Records: {len(data)}")


def main() -> None:

    print("\nPROCESSING MODIS AQUA")

    modis = add_time_fields(prepare_modis())

    print(f"Selected detections: {len(modis)}")

    save_dataset(modis, "modis_aqua_type0.csv")

    print("\nPROCESSING VIIRS NOAA-20")

    viirs = add_time_fields(prepare_viirs())

    print(f"Selected detections: {len(viirs)}")

    save_dataset(viirs, "viirs_noaa20_type0.csv")

    print("\nPREPROCESSING COMPLETED SUCCESSFULLY")


if __name__ == "__main__":
    main()