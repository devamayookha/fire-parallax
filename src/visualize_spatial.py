from pathlib import Path

import pandas as pd
import plotly.express as px
from pyproj import Transformer


PROJECT_ROOT = Path(__file__).resolve().parent.parent

DATA_FILE = (
    PROJECT_ROOT
    / "data"
    / "processed"
    / "grid_comparison_2km.csv"
)

OUTPUT_DIR = PROJECT_ROOT / "assets" / "screenshots"

OUTPUT_FILE = OUTPUT_DIR / "spatial_comparison.html"

GRID_SIZE_M = 2000

TRANSFORMER = Transformer.from_crs(
    "EPSG:32643",
    "EPSG:4326",
    always_xy=True
)


def create_spatial_map() -> None:
    """Map cell-day comparison categories across the study region."""

    if not DATA_FILE.exists():
        raise FileNotFoundError(
            f"Comparison file not found: {DATA_FILE}"
        )

    data = pd.read_csv(DATA_FILE)

    required_columns = [
        "state",
        "grid_x",
        "grid_y",
        "category",
    ]

    missing = set(required_columns) - set(data.columns)

    if missing:
        raise ValueError(f"Missing columns: {missing}")

    # Recover the centre coordinates of each 2 km grid cell.
    x_m = (
        (data["grid_x"] + 0.5) * GRID_SIZE_M
    ).to_numpy()

    y_m = (
        (data["grid_y"] + 0.5) * GRID_SIZE_M
    ).to_numpy()

    longitude, latitude = TRANSFORMER.transform(
        x_m,
        y_m
    )

    data["longitude"] = longitude
    data["latitude"] = latitude

    # Count cell-days by category and location.
    spatial_summary = (
        data.groupby(
            [
                "state",
                "grid_x",
                "grid_y",
                "category",
                "longitude",
                "latitude",
            ],
            as_index=False
        )
        .size()
        .rename(columns={"size": "cell_day_count"})
    )

    fig = px.scatter_map(
        spatial_summary,
        lat="latitude",
        lon="longitude",
        color="category",
        size="cell_day_count",
        size_max=14,
        hover_name="state",
        hover_data={
            "cell_day_count": True,
            "grid_x": True,
            "grid_y": True,
            "latitude": ":.4f",
            "longitude": ":.4f",
        },
        zoom=6,
        height=750,
        title=(
            "MODIS–VIIRS Spatial Comparison"
            "<br><sup>Punjab and Haryana | October–November 2022"
            " | 2 km grid</sup>"
        )
    )

    fig.update_layout(
        map_style="open-street-map",
        title_x=0.5,
        legend_title="Cell-day category"
    )

    OUTPUT_DIR.mkdir(
        parents=True,
        exist_ok=True
    )

    fig.write_html(
        OUTPUT_FILE,
        include_plotlyjs=True
    )

    print("\nSPATIAL COMPARISON MAP CREATED")
    print("=" * 45)
    print(f"Grid cells displayed: {len(spatial_summary):,}")
    print(f"Cell-day records: {len(data):,}")
    print(f"Saved to: {OUTPUT_FILE}")


if __name__ == "__main__":
    create_spatial_map()