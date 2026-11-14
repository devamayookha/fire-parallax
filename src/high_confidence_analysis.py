from pathlib import Path

import pandas as pd

from src.grid_analysis import create_cell_days

PROJECT_ROOT = Path(__file__).resolve().parent.parent
PROCESSED_DIR = PROJECT_ROOT / "data" / "processed"

MODIS_FILE = PROCESSED_DIR / "modis_punjab_haryana.csv"
VIIRS_FILE = PROCESSED_DIR / "viirs_punjab_haryana.csv"

MODIS_HIGH_FILE = PROCESSED_DIR / "modis_punjab_haryana_high.csv"
VIIRS_HIGH_FILE = PROCESSED_DIR / "viirs_punjab_haryana_high.csv"

GRID_RESOLUTIONS_KM = [1, 2, 5]

MATCH_COLUMNS = [
    "state",
    "acq_date_utc",
    "grid_x",
    "grid_y",
]


def compare_at_resolution(modis, viirs, resolution):
    """Compare high-confidence cell-days from both sensors."""

    modis_cells = create_cell_days(modis, resolution)
    viirs_cells = create_cell_days(viirs, resolution)

    comparison = modis_cells.merge(
        viirs_cells,
        on=MATCH_COLUMNS,
        how="outer",
        suffixes=("_modis", "_viirs"),
        indicator=True
    )

    summary = {
        "resolution_km": resolution,
        "modis_cell_days": len(modis_cells),
        "viirs_cell_days": len(viirs_cells),
        "co_detected_cell_days": (
            comparison["_merge"] == "both"
        ).sum(),
        "modis_only_cell_days": (
            comparison["_merge"] == "left_only"
        ).sum(),
        "viirs_only_cell_days": (
            comparison["_merge"] == "right_only"
        ).sum(),
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


def compare_high_to_any(high_cells, any_cells, resolution, direction):
    """Match high-confidence cell-days against any-confidence detections."""

    high_grid = create_cell_days(high_cells, resolution)
    any_grid = create_cell_days(any_cells, resolution)

    matched = high_grid.merge(
        any_grid[MATCH_COLUMNS],
        on=MATCH_COLUMNS,
        how="inner"
    )

    high_count = len(high_grid)
    matched_count = len(matched)

    return {
        "resolution_km": resolution,
        "direction": direction,
        "high_sensor_cell_days": high_count,
        "other_sensor_any_cell_days": len(any_grid),
        "matched_high_cell_days": matched_count,
        "unmatched_high_cell_days": high_count - matched_count,
        "matched_high_cell_days_pct": (
            matched_count / high_count * 100
            if high_count > 0 else 0
        ),
    }


def main():
    modis = pd.read_csv(MODIS_FILE)
    viirs = pd.read_csv(VIIRS_FILE)

    modis_high = pd.read_csv(MODIS_HIGH_FILE)
    viirs_high = pd.read_csv(VIIRS_HIGH_FILE)

    # Existing high-confidence versus high-confidence analysis.

    results = []

    # New directional high-confidence versus any-confidence analysis.

    directional_results = []

    for resolution in GRID_RESOLUTIONS_KM:

        results.append(
            compare_at_resolution(
                modis_high,
                viirs_high,
                resolution
            )
        )

        directional_results.append(
            compare_high_to_any(
                modis_high,
                viirs,
                resolution,
                "MODIS High to any VIIRS"
            )
        )

        directional_results.append(
            compare_high_to_any(
                viirs_high,
                modis,
                resolution,
                "VIIRS High to any MODIS"
            )
        )

    # Save existing high-to-high results.

    summary = pd.DataFrame(results)

    output_file = (
        PROCESSED_DIR / "high_confidence_grid_summary.csv"
    )

    summary.to_csv(output_file, index=False)

    # Save new directional results.

    directional_summary = pd.DataFrame(directional_results)

    directional_output = (
        PROCESSED_DIR / "high_confidence_cross_sensor_summary.csv"
    )

    directional_summary.to_csv(
        directional_output,
        index=False
    )

    print("\nHIGH-CONFIDENCE TO HIGH-CONFIDENCE COMPARISON")
    print("=" * 60)
    print(summary.to_string(index=False))

    print("\nHIGH-CONFIDENCE TO ANY-CONFIDENCE COMPARISON")
    print("=" * 75)
    print(directional_summary.to_string(index=False))

    print(f"\nSaved: {output_file}")
    print(f"Saved: {directional_output}")


if __name__ == "__main__":
    main()