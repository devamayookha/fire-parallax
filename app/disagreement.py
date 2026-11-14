from pathlib import Path

import pandas as pd
import plotly.express as px
import streamlit as st

from pyproj import Transformer


PROJECT_ROOT = Path(__file__).resolve().parent.parent

DATA_FILE = (
    PROJECT_ROOT
    / "data"
    / "processed"
    / "grid_comparison_2km.csv"
)

GRID_SIZE_M = 2000

# Convert UTM Zone 43N cell centres into WGS84 coordinates.
TRANSFORMER = Transformer.from_crs(
    "EPSG:32643",
    "EPSG:4326",
    always_xy=True
)


@st.cache_data
def load_comparison_data() -> pd.DataFrame:
    """Load and prepare the 2 km cell-day comparison dataset."""

    if not DATA_FILE.exists():
        raise FileNotFoundError(
            f"Required dataset not found: {DATA_FILE}"
        )

    data = pd.read_csv(DATA_FILE)

    required_columns = [
        "state",
        "acq_date_utc",
        "grid_x",
        "grid_y",
        "detection_count_modis",
        "detection_count_viirs",
        "category",
    ]

    missing = set(required_columns) - set(data.columns)

    if missing:
        raise ValueError(
            f"Dataset is missing columns: {sorted(missing)}"
        )

    # Convert dates and remove any time component.
    data["acq_date_utc"] = pd.to_datetime(
        data["acq_date_utc"],
        errors="raise"
    ).dt.normalize()

    data["detection_count_modis"] = (
        data["detection_count_modis"].fillna(0)
    )

    data["detection_count_viirs"] = (
        data["detection_count_viirs"].fillna(0)
    )

    data["total_detections"] = (
        data["detection_count_modis"]
        + data["detection_count_viirs"]
    )

    # Reconstruct the exact centre of each 2 km grid cell.
    data["x_centre_m"] = (
        data["grid_x"] + 0.5
    ) * GRID_SIZE_M

    data["y_centre_m"] = (
        data["grid_y"] + 0.5
    ) * GRID_SIZE_M

    longitude, latitude = TRANSFORMER.transform(
        data["x_centre_m"].to_numpy(),
        data["y_centre_m"].to_numpy()
    )

    data["longitude"] = longitude
    data["latitude"] = latitude

    data["cell_id"] = (
        data["grid_x"].astype(str)
        + " / "
        + data["grid_y"].astype(str)
    )

    return data


def render_disagreement_investigator() -> None:
    """Render the date-level sensor disagreement investigation page."""

    st.title("Disagreement Investigator")

    st.markdown(
        """
        Investigate where MODIS Aqua and VIIRS NOAA-20 recorded
        different active-fire detection patterns across Punjab
        and Haryana.

        Each observation represents a **2 km grid cell on a
        particular UTC date**.
        """
    )

    try:
        data = load_comparison_data()

    except (FileNotFoundError, ValueError) as error:
        st.error(str(error))
        return

    # --------------------------------------------------
    # FILTER CONTROLS
    # --------------------------------------------------

    st.subheader("Observation controls")

    col1, col2, col3 = st.columns(3)

    states = sorted(data["state"].unique())

    with col1:
        selected_state = st.selectbox(
            "Study state",
            states
        )

    state_data = data[
        data["state"] == selected_state
    ].copy()

    available_dates = sorted(
        state_data["acq_date_utc"].unique()
    )

    with col2:
        selected_date = st.selectbox(
            "Observation date (UTC)",
            available_dates,
            format_func=lambda date: pd.Timestamp(date).strftime(
                "%d %b %Y"
            )
        )

    # Always compare normalized pandas timestamps.
    selected_date = pd.Timestamp(
        selected_date
    ).normalize()

    category_options = {
        "All categories": "all",
        "Co-detected": "co_detected",
        "MODIS-only": "modis_only",
        "VIIRS-only": "viirs_only",
    }

    with col3:
        selected_category_label = st.selectbox(
            "Detection category",
            list(category_options.keys())
        )

    selected_category = category_options[
        selected_category_label
    ]

    # --------------------------------------------------
    # FILTER DATA
    # --------------------------------------------------

    # First filter by state and date.
    date_data = state_data[
        state_data["acq_date_utc"] == selected_date
    ].copy()

    # Then apply the selected detection category.
    filtered = date_data.copy()

    if selected_category != "all":
        filtered = filtered[
            filtered["category"] == selected_category
        ].copy()

    # --------------------------------------------------
    # SUMMARY METRICS
    # --------------------------------------------------

    st.divider()

    st.subheader("Observation summary")

    total_cells = len(filtered)

    modis_detections = int(
        filtered["detection_count_modis"].sum()
    )

    viirs_detections = int(
        filtered["detection_count_viirs"].sum()
    )

    # Co-detected cells are counted across all categories
    # for the selected state and date.
    co_detected = int(
        (date_data["category"] == "co_detected").sum()
    )

    metric1, metric2, metric3, metric4 = st.columns(4)

    metric1.metric(
        "Matching grid cells",
        f"{total_cells:,}"
    )

    metric2.metric(
        "MODIS detections",
        f"{modis_detections:,}"
    )

    metric3.metric(
        "VIIRS detections",
        f"{viirs_detections:,}"
    )

    metric4.metric(
        "Co-detected cells (date)",
        f"{co_detected:,}"
    )

    st.caption(
        f"Showing {selected_category_label.lower()} observations "
        f"for {selected_state} on "
        f"{selected_date.strftime('%d %B %Y')} (UTC)."
    )

    # --------------------------------------------------
    # TEMPORAL CONTEXT
    # --------------------------------------------------

    st.divider()

    st.subheader("Seasonal context")

    st.caption(
        "Daily grid-cell counts across the study period. "
        "The vertical marker identifies the selected observation date."
    )

    daily_data = (
        state_data.groupby(
            ["acq_date_utc", "category"],
            as_index=False
        )
        .size()
        .rename(columns={"size": "cell_days"})
    )

    daily_pivot = daily_data.pivot(
        index="acq_date_utc",
        columns="category",
        values="cell_days"
    ).fillna(0)

    all_state_dates = pd.DatetimeIndex(
        state_data["acq_date_utc"].drop_duplicates()
    )

    daily_pivot = daily_pivot.reindex(
        all_state_dates
    ).fillna(0)

    daily_pivot = daily_pivot.reindex(
        columns=[
            "co_detected",
            "modis_only",
            "viirs_only"
        ],
        fill_value=0
    )

    selected_day_values = daily_pivot.loc[
        selected_date
    ]

    st.markdown(
        "**Selected day versus study-period baseline**"
    )

    baseline_columns = st.columns(3)

    category_details = [
        ("co_detected", "Co-detected"),
        ("modis_only", "MODIS-only"),
        ("viirs_only", "VIIRS-only"),
    ]

    for column, (category_key, category_name) in zip(
        baseline_columns,
        category_details
    ):
        daily_values = daily_pivot[category_key]

        current_value = int(
            selected_day_values[category_key]
        )

        median_value = float(
            daily_values.median()
        )

        percentile = (
            daily_values.rank(pct=True) * 100
        ).loc[selected_date]

        column.metric(
            category_name,
            f"{current_value:,}",
            delta=f"{current_value - median_value:+.1f} vs median",
            help=(
                f"Selected date: {current_value:,} cell-days. "
                f"Study-period median: {median_value:.1f}. "
                f"Percentile rank: {percentile:.1f}%."
            )
        )

    daily_fig = px.line(
        daily_data,
        x="acq_date_utc",
        y="cell_days",
        color="category",
        markers=True,
        labels={
            "acq_date_utc": "Observation date (UTC)",
            "cell_days": "Grid cell-days",
            "category": "Detection category",
        },
        color_discrete_map={
            "co_detected": "#38BDF8",
            "modis_only": "#F59E0B",
            "viirs_only": "#A78BFA",
        },
    )

    daily_fig.add_vline(
        x=selected_date,
        line_dash="dash",
        line_color="white",
        annotation_text="Selected date",
        annotation_position="top",
    )

    daily_fig.update_layout(
        height=380,
        margin=dict(l=10, r=10, t=35, b=10),
        legend_title_text="Detection category",
        hovermode="x unified",
    )

    st.plotly_chart(
        daily_fig,
        use_container_width=True
    )

    # --------------------------------------------------
    # EMPTY RESULT HANDLING
    # --------------------------------------------------

    if filtered.empty:
        st.warning(
            "No matching grid cells exist for this selection. "
            "The seasonal chart above still shows the full "
            "study-period context. Try another date or category."
        )
        return

    # --------------------------------------------------
    # SPATIAL INVESTIGATION
    # --------------------------------------------------

    st.divider()

    st.subheader("Spatial distribution")

    st.caption(
        "Each marker represents the centre of a 2 km grid cell, "
        "not the exact location of an individual fire detection."
    )

    filtered["category_label"] = filtered["category"].map({
        "co_detected": "Co-detected",
        "modis_only": "MODIS-only",
        "viirs_only": "VIIRS-only",
    })

    fig = px.scatter_map(
        filtered,
        lat="latitude",
        lon="longitude",
        color="category_label",
        size="total_detections",
        size_max=15,
        hover_name="cell_id",
        hover_data={
            "latitude": False,
            "longitude": False,
            "category_label": True,
            "detection_count_modis": True,
            "detection_count_viirs": True,
            "total_detections": True,
        },
        zoom=6,
        height=560,
        map_style="open-street-map",
        labels={
            "category_label": "Detection category",
            "detection_count_modis": "MODIS detections",
            "detection_count_viirs": "VIIRS detections",
            "total_detections": "Combined detections",
        },
    )

    fig.update_layout(
        margin=dict(l=0, r=0, t=10, b=0),
        legend_title_text="Detection category",
    )

    st.plotly_chart(
        fig,
        use_container_width=True
    )

    # --------------------------------------------------
    # INDIVIDUAL CELL INSPECTION
    # --------------------------------------------------

    st.divider()

    st.subheader("Inspect an individual grid cell")

    cell_options = (
        filtered.sort_values(
            "total_detections",
            ascending=False
        )["cell_id"].tolist()
    )

    selected_cell_id = st.selectbox(
        "Select a grid cell",
        cell_options
    )

    selected_cell = filtered[
        filtered["cell_id"] == selected_cell_id
    ].iloc[0]

    cell_col1, cell_col2, cell_col3 = st.columns(3)

    cell_col1.metric(
        "MODIS detections",
        int(selected_cell["detection_count_modis"])
    )

    cell_col2.metric(
        "VIIRS detections",
        int(selected_cell["detection_count_viirs"])
    )

    cell_col3.metric(
        "Combined detections",
        int(selected_cell["total_detections"])
    )

    st.write(
        f"**Grid coordinates:** "
        f"({int(selected_cell['grid_x'])}, "
        f"{int(selected_cell['grid_y'])})"
    )

    st.write(
        f"**Category:** "
        f"{selected_cell['category_label']}"
    )

    st.write(
        f"**Observation date (UTC):** "
        f"{selected_date.strftime('%Y-%m-%d')}"
    )

    # --------------------------------------------------
    # SCIENTIFIC INTERPRETATION
    # --------------------------------------------------

    st.divider()

    st.subheader("What does this observation mean?")

    category = selected_cell["category"]

    if category == "co_detected":

        st.info(
            "Both sensors recorded at least one qualifying "
            "detection within this grid cell on the same UTC date. "
            "This is spatial-temporal co-detection, not proof "
            "that both sensors observed the same physical fire."
        )

    elif category == "modis_only":

        st.warning(
            "MODIS recorded qualifying detections in this cell, "
            "while VIIRS recorded none under the same grid-cell "
            "and UTC-date matching rule. This does not establish "
            "that VIIRS missed a confirmed fire."
        )

    else:

        st.warning(
            "VIIRS recorded qualifying detections in this cell, "
            "while MODIS recorded none under the same grid-cell "
            "and UTC-date matching rule. This does not establish "
            "that MODIS missed a confirmed fire."
        )

    st.caption(
        "Important: Active-fire detections are satellite "
        "observations of thermal anomalies. They are not direct "
        "counts of unique physical fires, burned area, or "
        "independently verified agricultural burning events."
    )