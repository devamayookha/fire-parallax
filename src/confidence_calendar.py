from pathlib import Path

import pandas as pd

PROJECT_ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = PROJECT_ROOT / "data" / "processed"

MODIS_FILE = DATA_DIR / "modis_punjab_haryana.csv"
VIIRS_FILE = DATA_DIR / "viirs_punjab_haryana.csv"

START_DATE = "2022-09-26"
END_DATE = "2022-11-28"

GRID_RESOLUTION_KM = 2


def prepare_modis(data):
    data = data.copy()

    data["confidence_class"] = pd.cut(
        data["confidence"],
        bins=[-1, 29, 79, 100],
        labels=["Low", "Nominal", "High"]
    )

    return data


def prepare_viirs(data):
    data = data.copy()

    class_mapping = {
        "l": "Low",
        "n": "Nominal",
        "h": "High"
    }

    data["confidence_class"] = (
        data["confidence"].map(class_mapping)
    )

    return data


def create_class_calendar(data, sensor):

    cell_size = GRID_RESOLUTION_KM * 1000

    data = data.copy()

    data["grid_x"] = (
        data["x_m"] // cell_size
    ).astype("int64")

    data["grid_y"] = (
        data["y_m"] // cell_size
    ).astype("int64")

    dates = pd.to_datetime(data["acq_date_utc"])

    data["week_start"] = (
        dates.dt.to_period("W-SUN")
        .dt.start_time.dt.strftime("%Y-%m-%d")
    )

    cell_days = (
        data.groupby(
            [
                "state",
                "week_start",
                "acq_date_utc",
                "grid_x",
                "grid_y",
                "confidence_class"
            ],
            observed=True,
            as_index=False
        )
        .agg(
            detection_count=("latitude", "size")
        )
    )

    weekly = (
        cell_days.groupby(
            ["state", "week_start", "confidence_class"],
            observed=True,
            as_index=False
        )
        .agg(
            active_cell_days=("detection_count", "size"),
            detection_count=("detection_count", "sum")
        )
    )

    weekly["sensor"] = sensor

    return weekly


def complete_calendar(calendar):

    states = ["Punjab", "Haryāna"]
    sensors = ["MODIS Aqua", "VIIRS NOAA-20"]
    classes = ["Low", "Nominal", "High"]

    weeks = pd.date_range(
        START_DATE,
        END_DATE,
        freq="7D"
    ).strftime("%Y-%m-%d")

    index = pd.MultiIndex.from_product(
        [states, weeks, sensors, classes],
        names=[
            "state",
            "week_start",
            "sensor",
            "confidence_class"
        ]
    )

    complete = (
        calendar
        .set_index([
            "state",
            "week_start",
            "sensor",
            "confidence_class"
        ])
        .reindex(index)
        .reset_index()
    )

    for column in ["active_cell_days", "detection_count"]:
        complete[column] = (
            complete[column].fillna(0).astype(int)
        )

    # Share within each state, sensor and confidence class.
    totals = complete.groupby(
        ["state", "sensor", "confidence_class"]
    )["active_cell_days"].transform("sum")

    complete["weekly_share_pct"] = (
        complete["active_cell_days"]
        .div(totals.where(totals != 0))
        .mul(100)
        .fillna(0)
    )

    return complete


def main():

    modis = pd.read_csv(MODIS_FILE)
    viirs = pd.read_csv(VIIRS_FILE)

    modis = prepare_modis(modis)
    viirs = prepare_viirs(viirs)

    print("\nCONFIDENCE CLASS VALIDATION")
    print("=" * 50)

    print("\nMODIS:")
    print(modis["confidence_class"].value_counts())

    print("\nVIIRS:")
    print(viirs["confidence_class"].value_counts())
    modis_weekly = create_class_calendar(
        modis,
        "MODIS Aqua"
    )

    viirs_weekly = create_class_calendar(
        viirs,
        "VIIRS NOAA-20"
    )

    calendar = pd.concat(
        [modis_weekly, viirs_weekly],
        ignore_index=True
    )

    calendar = complete_calendar(calendar)

    output_file = DATA_DIR / "confidence_class_calendar.csv"

    calendar.to_csv(output_file, index=False)

    print("\nCONFIDENCE CLASS CALENDAR")
    print("=" * 50)
    print("Total records:", len(calendar))

    print("\nWeekly results:")
    print(calendar.to_string(index=False))

    print("\nSaved:", output_file)


if __name__ == "__main__":
    main()