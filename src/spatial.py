from pathlib import Path

import pandas as pd
from pyproj import Transformer


PROJECT_ROOT = Path(__file__).resolve().parent.parent

PROCESSED_DIR = PROJECT_ROOT / "data" / "processed"

MODIS_FILE = PROCESSED_DIR / "modis_aqua_type0.csv"
VIIRS_FILE = PROCESSED_DIR / "viirs_noaa20_type0.csv"

OUTPUT_DIR = PROCESSED_DIR

# WGS84 latitude/longitude to UTM Zone 43N
TRANSFORMER = Transformer.from_crs(
    "EPSG:4326",
    "EPSG:32643",
    always_xy=True
)


def add_projected_coordinates(data: pd.DataFrame) -> pd.DataFrame:
    """Convert longitude and latitude into projected coordinates in metres."""

    data = data.copy()

    x, y = TRANSFORMER.transform(
        data["longitude"].to_numpy(),
        data["latitude"].to_numpy()
    )

    data["x_m"] = x
    data["y_m"] = y

    return data


def process_sensor(file_path: Path, sensor_name: str) -> None:
    """Add projected coordinates and save the dataset."""

    data = pd.read_csv(file_path)

    data = add_projected_coordinates(data)

    output_file = OUTPUT_DIR / file_path.name

    data.to_csv(output_file, index=False)

    print(f"\n{sensor_name}")
    print(f"Records: {len(data)}")
    print(f"X range (km): {data['x_m'].min() / 1000:.2f} to {data['x_m'].max() / 1000:.2f}")
    print(f"Y range (km): {data['y_m'].min() / 1000:.2f} to {data['y_m'].max() / 1000:.2f}")
    print(f"Missing projected coordinates: {data[['x_m', 'y_m']].isna().sum().sum()}")


def main() -> None:
    process_sensor(MODIS_FILE, "MODIS AQUA")
    process_sensor(VIIRS_FILE, "VIIRS NOAA-20")


if __name__ == "__main__":
    main()