from pathlib import Path

import pandas as pd

from src.grid_analysis import create_cell_days

PROJECT_ROOT = Path(__file__).resolve().parent.parent
PROCESSED_DIR = PROJECT_ROOT / "data" / "processed"

MODIS_FILE = PROCESSED_DIR / "modis_punjab_haryana_high.csv"
VIIRS_FILE = PROCESSED_DIR / "viirs_punjab_haryana_high.csv"

GRID_RESOLUTIONS_KM = [1, 2, 5]

def compare_at_resolution(modis, viirs, resolution):
    """Compare high-confidence sensor cell-days."""

    modis_cells = create_cell_days(modis, resolution)
    viirs_cells = create_cell_days(viirs, resolution)

    comparison = modis_cells.merge(
        viirs_cells,
        on=["state", "acq_date_utc", "grid_x", "grid_y"],
        how="outer",
        suffixes=("_modis", "_viirs"),
        indicator=True
    )

    summary = {
        "resolution_km": resolution,
        "modis_cell_days": len(modis_cells),
        "viirs_cell_days": len(viirs_cells),
        "co_detected_cell_days": (comparison["_merge"] == "both").sum(),
        "modis_only_cell_days": (comparison["_merge"] == "left_only").sum(),
        "viirs_only_cell_days": (comparison["_merge"] == "right_only").sum(),
    }

    union = (
        summary["modis_cell_days"]
        + summary["viirs_cell_days"]
        - summary["co_detected_cell_days"]
    )

    summary["jaccard_overlap_pct"] = (
        summary["co_detected_cell_days"] / union * 100
    )

    return summary

def main():
    modis = pd.read_csv(MODIS_FILE)
    viirs = pd.read_csv(VIIRS_FILE)

    results = []

    for resolution in GRID_RESOLUTIONS_KM:
        results.append(
            compare_at_resolution(modis, viirs, resolution)
        )

    summary = pd.DataFrame(results)

    output_file = (
        PROCESSED_DIR / "high_confidence_grid_summary.csv"
    )

    summary.to_csv(output_file, index=False)

    print("\nHIGH-CONFIDENCE SPATIAL COMPARISON")
    print("=" * 55)
    print(summary.to_string(index=False))
    print(f"\nSaved: {output_file}")

if __name__ == "__main__":
    main()