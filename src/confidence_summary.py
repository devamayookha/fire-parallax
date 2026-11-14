from pathlib import Path

import pandas as pd

PROJECT_ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = PROJECT_ROOT / "data" / "processed"

INPUT_FILE = DATA_DIR / "confidence_class_calendar.csv"


def main():

    data = pd.read_csv(INPUT_FILE)

    # Find the peak week for every state, sensor and class.
    peak_indices = (
        data.groupby(
            ["state", "sensor", "confidence_class"]
        )["weekly_share_pct"].idxmax()
    )

    peaks = data.loc[
        peak_indices,
        [
            "state",
            "sensor",
            "confidence_class",
            "week_start",
            "active_cell_days",
            "detection_count",
            "weekly_share_pct",
        ]
    ].copy()

    peaks = peaks.rename(
        columns={"week_start": "peak_week"}
    )

    # Calculate total class-specific activity.
    totals = (
        data.groupby(
            ["state", "sensor", "confidence_class"]
        )
        .agg(
            total_active_cell_days=("active_cell_days", "sum"),
            total_detections=("detection_count", "sum")
        )
        .reset_index()
    )

    summary = peaks.merge(
        totals,
        on=["state", "sensor", "confidence_class"]
    )

    summary = summary.sort_values(
        ["state", "sensor", "confidence_class"]
    )

    output_file = DATA_DIR / "confidence_class_summary.csv"

    summary.to_csv(output_file, index=False)

    print("\nCONFIDENCE CLASS PEAK SUMMARY")
    print("=" * 75)

    print(
        summary.to_string(index=False)
    )

    print("\nSaved:", output_file)


if __name__ == "__main__":
    main()