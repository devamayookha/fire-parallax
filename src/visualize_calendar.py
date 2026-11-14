from pathlib import Path

import pandas as pd
import plotly.express as px


PROJECT_ROOT = Path(__file__).resolve().parent.parent

DATA_FILE = (
    PROJECT_ROOT
    / "data"
    / "processed"
    / "weekly_activity_calendar.csv"
)

OUTPUT_DIR = PROJECT_ROOT / "assets" / "screenshots"

OUTPUT_FILE = (
    OUTPUT_DIR / "weekly_activity_comparison.html"
)


def create_weekly_comparison() -> None:
    """Visualize weekly activity shares for both sensors and states."""

    if not DATA_FILE.exists():
        raise FileNotFoundError(
            f"Calendar file not found: {DATA_FILE}"
        )

    data = pd.read_csv(DATA_FILE)

    data["week_start"] = pd.to_datetime(
        data["week_start"]
    )

    data = data.sort_values("week_start")

    fig = px.line(
        data,
        x="week_start",
        y="weekly_share_pct",
        color="sensor",
        facet_col="state",
        markers=True,
        hover_data={
            "active_cell_days": True,
            "detection_count": True,
            "coverage_days": True,
            "week_start": "|%d %b %Y",
            "weekly_share_pct": ":.2f"
        },
        labels={
            "week_start": "Week beginning (UTC)",
            "weekly_share_pct": "Weekly share (%)",
            "sensor": "Satellite sensor",
            "state": "State"
        },
        title=(
            "Weekly Distribution of Active Cell-Days"
            "<br><sup>Punjab and Haryana | October–November 2022"
            " | 2 km grid</sup>"
        )
    )

    fig.update_layout(
        template="plotly_white",
        height=600,
        width=1200,
        hovermode="x unified",
        legend_title="Sensor",
        title_x=0.5
    )

    fig.update_xaxes(
        tickformat="%d %b",
        title_text="Week beginning"
    )

    fig.update_yaxes(
        title_text="Weekly share (%)",
        matches=None
    )

    OUTPUT_DIR.mkdir(
        parents=True,
        exist_ok=True
    )

    fig.write_html(
        OUTPUT_FILE,
        include_plotlyjs=True
    )

    print("\nWEEKLY COMPARISON CHART CREATED")
    print("=" * 45)
    print(f"Saved to: {OUTPUT_FILE}")


if __name__ == "__main__":
    create_weekly_comparison()