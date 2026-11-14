from pathlib import Path

import geopandas as gpd
import pandas as pd


PROJECT_ROOT = Path(__file__).resolve().parent.parent

PROCESSED_DIR = PROJECT_ROOT / "data" / "processed"

BOUNDARY_FILE = (
    PROJECT_ROOT
    / "data"
    / "raw"
    / "admin_boundaries"
    / "india_adm1.geojson"
)

TARGET_STATES = ["Punjab", "Haryāna"]


def clip_sensor_data(file_path: Path, sensor_name: str) -> None:
    """Retain detections falling inside Punjab and Haryana."""

    data = pd.read_csv(file_path)

    boundaries = gpd.read_file(BOUNDARY_FILE)

    target_boundaries = boundaries[
        boundaries["shapeName"].isin(TARGET_STATES)
    ].copy()

    if len(target_boundaries) != 2:
        raise ValueError(
            "Could not find both Punjab and Haryāna boundaries."
        )

    # Create geographical points from the original coordinates.
    points = gpd.GeoDataFrame(
        data,
        geometry=gpd.points_from_xy(
            data["longitude"],
            data["latitude"]
        ),
        crs="EPSG:4326"
    )

    # Match each detection to its administrative state.
    matched = gpd.sjoin(
        points,
        target_boundaries[["shapeName", "geometry"]],
        how="left",
        predicate="within"
    )

    # Keep detections assigned to either target state.
    inside = matched[
        matched["shapeName"].notna()
    ].copy()

    inside = inside.rename(
        columns={"shapeName": "state"}
    )

    inside = inside.drop(
        columns=["geometry", "index_right"],
        errors="ignore"
    )

    output_file = (
        PROCESSED_DIR
        / f"{sensor_name.lower()}_punjab_haryana.csv"
    )

    inside.to_csv(output_file, index=False)

    print(f"\n{sensor_name}")
    print("-" * 40)
    print(f"Original detections: {len(data):,}")
    print(f"Inside Punjab-Haryana: {len(inside):,}")
    print(f"Outside target states: {len(data) - len(inside):,}")

    print("\nState-wise detections:")
    print(inside["state"].value_counts())

    print(f"\nSaved: {output_file}")


def main() -> None:

    clip_sensor_data(
        PROCESSED_DIR / "modis_aqua_type0.csv",
        "MODIS"
    )

    clip_sensor_data(
        PROCESSED_DIR / "viirs_noaa20_type0.csv",
        "VIIRS"
    )

    print("\nREGIONAL CLIPPING COMPLETED")


if __name__ == "__main__":
    main()