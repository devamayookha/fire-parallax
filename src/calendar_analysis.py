from pathlib import Path

import pandas as pd


PROJECT_ROOT = Path(__file__).resolve().parent.parent

PROCESSED_DIR = PROJECT_ROOT / "data" / "processed"

MODIS_FILE = PROCESSED_DIR / "modis_punjab_haryana.csv"
VIIRS_FILE = PROCESSED_DIR / "viirs_punjab_haryana.csv"

GRID_RESOLUTION_KM = 2


def load_sensor_data(file_path: Path) -> pd.DataFrame:
    """Load clipped sensor data."""

    if not file_path.exists():
        raise FileNotFoundError(f"File not found: {file_path}")

    data = pd.read_csv(file_path)

    required = [
        "x_m",
        "y_m",
        "acq_date_utc",
        "state",
    ]

    missing = set(required) - set(data.columns)

    if missing:
        raise ValueError(f"Missing columns: {missing}")

    return data


def create_weekly_calendar(
    data: pd.DataFrame,
    sensor_name: str
) -> pd.DataFrame:
    """Aggregate sensor detections into weekly spatial activity."""

    data = data.copy()

    cell_size_m = GRID_RESOLUTION_KM * 1000

    data["grid_x"] = (
        data["x_m"] // cell_size_m
    ).astype("int64")

    data["grid_y"] = (
        data["y_m"] // cell_size_m
    ).astype("int64")

    data["date"] = pd.to_datetime(
        data["acq_date_utc"],
        utc=True
    )

    # Monday is the beginning of each calendar week.
    data["week_start"] = (
        data["date"]
        .dt.tz_convert(None)
        .dt.to_period("W-SUN")
        .dt.start_time
        .dt.strftime("%Y-%m-%d")
    )

    # First count detections within each cell and day.
    cell_days = (
        data.groupby(
            [
                "state",
                "week_start",
                "acq_date_utc",
                "grid_x",
                "grid_y",
            ],
            as_index=False
        )
        .agg(
            detection_count=("latitude", "size")
        )
    )

    # Then aggregate cell-days and detections by state and week.
    weekly = (
        cell_days.groupby(
            ["state", "week_start"],
            as_index=False
        )
        .agg(
            active_cell_days=("detection_count", "size"),
            detection_count=("detection_count", "sum")
        )
    )

    weekly["sensor"] = sensor_name

    # Calculate weekly share within each sensor and state.
    weekly["weekly_share_pct"] = (
        weekly["active_cell_days"]
        / weekly.groupby("state")["active_cell_days"].transform("sum")
        * 100
    )

    return weekly

def complete_calendar(calendar: pd.DataFrame) -> pd.DataFrame:
    """Add zero-activity weeks and record the number of covered days."""

    states = ["Punjab", "Haryāna"]
    sensors = ["MODIS Aqua", "VIIRS NOAA-20"]

    weeks = pd.date_range(
        start="2022-09-26",
        end="2022-11-28",
        freq="7D"
    ).strftime("%Y-%m-%d")

    complete_index = pd.MultiIndex.from_product(
        [states, weeks, sensors],
        names=["state", "week_start", "sensor"]
    )

    complete = (
        calendar
        .set_index(["state", "week_start", "sensor"])
        .reindex(complete_index)
        .reset_index()
    )

    complete["active_cell_days"] = (
        complete["active_cell_days"].fillna(0).astype(int)
    )

    complete["detection_count"] = (
        complete["detection_count"].fillna(0).astype(int)
    )

    # Number of days from the requested study period
    # falling inside each Monday-Sunday calendar week.
    week_dates = pd.to_datetime(complete["week_start"])

    week_end = week_dates + pd.Timedelta(days=6)

    study_start = pd.Timestamp("2022-10-01")
    study_end = pd.Timestamp("2022-11-30")

    overlap_start = week_dates.where(
        week_dates >= study_start,
        study_start
    )

    overlap_end = week_end.where(
        week_end <= study_end,
        study_end
    )

    complete["coverage_days"] = (
        (overlap_end - overlap_start).dt.days + 1
    )

    complete["weekly_share_pct"] = (
        complete["active_cell_days"]
        / complete.groupby(
            ["state", "sensor"]
        )["active_cell_days"].transform("sum")
        * 100
    )

    return complete

def validate_calendar(calendar: pd.DataFrame) -> None:
    """Check the calendar's basic structural and numerical consistency."""

    assert len(calendar) == 40, "Expected 40 state-week-sensor records."

    assert calendar["active_cell_days"].ge(0).all()
    assert calendar["detection_count"].ge(0).all()

    # Each state-sensor combination should account for 100% of its
    # active cell-days across the selected study period.
    share_totals = (
        calendar.groupby(["state", "sensor"])["weekly_share_pct"].sum()
    )

    assert share_totals.between(99.99, 100.01).all(), (
        "Weekly shares do not sum to approximately 100%."
    )

    # The calendar should cover the complete study period.
    assert set(calendar["coverage_days"].unique()) == {2, 3, 7}

    print("\nCALENDAR VALIDATION")
    print("=" * 40)
    print("Record count: PASS")
    print("Non-negative counts: PASS")
    print("Weekly shares sum to 100%: PASS")
    print("Partial-week coverage: PASS")


def main() -> None:

    modis = load_sensor_data(MODIS_FILE)
    viirs = load_sensor_data(VIIRS_FILE)

    modis_weekly = create_weekly_calendar(
        modis,
        "MODIS Aqua"
    )

    viirs_weekly = create_weekly_calendar(
        viirs,
        "VIIRS NOAA-20"
    )

    calendar = pd.concat(
        [modis_weekly, viirs_weekly],
        ignore_index=True
    )

    calendar = complete_calendar(calendar)
    validate_calendar(calendar)

    calendar = calendar.sort_values(
        ["state", "week_start", "sensor"]
    )

    output_file = (
        PROCESSED_DIR / "weekly_activity_calendar.csv"
    )

    calendar.to_csv(output_file, index=False)

    print("\nWEEKLY BURNING ACTIVITY CALENDAR")
    print("=" * 55)

    print(f"Grid resolution: {GRID_RESOLUTION_KM} km")
    print(f"Total weekly records: {len(calendar)}")

    print("\nWeekly results:")
    print(calendar.to_string(index=False))

    print(f"\nSaved: {output_file}")


if __name__ == "__main__":
    main()