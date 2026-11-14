from pathlib import Path

import geopandas as gpd
import requests


PROJECT_ROOT = Path(__file__).resolve().parent.parent

BOUNDARY_DIR = PROJECT_ROOT / "data" / "raw" / "admin_boundaries"

API_URL = (
    "https://www.geoboundaries.org/api/current/"
    "gbOpen/IND/ADM1/"
)


def download_india_boundaries():

    BOUNDARY_DIR.mkdir(parents=True, exist_ok=True)

    print("Requesting India ADM1 boundary metadata...")

    response = requests.get(API_URL, timeout=60)
    response.raise_for_status()

    metadata = response.json()

    if isinstance(metadata, list):
        metadata = metadata[0]

    print("Boundary dataset:", metadata["boundaryName"])
    print("Boundary level:", metadata["boundaryType"])
    print("Source year:", metadata["boundaryYearRepresented"])

    geojson_url = metadata["simplifiedGeometryGeoJSON"]

    print("\nDownloading state boundaries...")

    boundary_response = requests.get(
        geojson_url,
        timeout=120
    )
    boundary_response.raise_for_status()

    output_file = BOUNDARY_DIR / "india_adm1.geojson"

    output_file.write_bytes(boundary_response.content)

    print("Saved:", output_file)

    states = gpd.read_file(output_file)

    print("\nAvailable columns:")
    print(states.columns.tolist())

    print("\nState names:")

    if "shapeName" in states.columns:
        print(sorted(states["shapeName"].dropna().unique()))
    else:
        print("shapeName column not found. Inspect the columns above.")

    print("\nBoundary CRS:", states.crs)
    print("Total administrative units:", len(states))


if __name__ == "__main__":
    download_india_boundaries()