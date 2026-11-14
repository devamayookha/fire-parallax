import streamlit as st
import pandas as pd
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent

# --------------------------------------------------
# PAGE CONFIGURATION
# --------------------------------------------------

st.set_page_config(
    page_title="Fire Parallax | Satellite Detection Explorer",
    page_icon="🔥",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --------------------------------------------------
# CUSTOM STYLING
# --------------------------------------------------

st.markdown("""
<style>
    .stApp {
        background-color: #0b1120;
        color: #e5e7eb;
    }

    section[data-testid="stSidebar"] {
        background-color: #111827;
    }

    .hero {
        padding: 35px 30px;
        border-radius: 14px;
        background: linear-gradient(120deg, #172554, #312e81);
        margin-bottom: 25px;
    }

    .hero h1 {
        font-size: 42px;
        color: #ffffff;
        margin-bottom: 8px;
    }

    .hero p {
        color: #cbd5e1;
        font-size: 17px;
    }

    .metric-card {
        background-color: #172033;
        padding: 22px;
        border-radius: 12px;
        border: 1px solid #263449;
        min-height: 115px;
    }

    .metric-label {
        color: #94a3b8;
        font-size: 14px;
    }

    .metric-value {
        color: #ffffff;
        font-size: 27px;
        font-weight: 700;
    }

    .section-title {
        color: #f8fafc;
        font-size: 23px;
        font-weight: 600;
        margin-top: 28px;
    }

    .notice {
        background-color: #332b18;
        border-left: 4px solid #eab308;
        padding: 15px;
        border-radius: 6px;
        color: #fde68a;
    }
</style>
""", unsafe_allow_html=True)

# --------------------------------------------------
# SIDEBAR
# --------------------------------------------------

st.sidebar.title("🔥 FIRE PARALLAX")
st.sidebar.caption("Sensor-Aware Burning Activity Intelligence")

page = st.sidebar.radio(
    "NAVIGATION",
    [
        "Overview",
        "Burning Activity Calendar",
        "Spatial Explorer",
        "Sensor Comparison",
        "Confidence Explorer",
        "Methodology"
    ]
)

st.sidebar.divider()

st.sidebar.markdown("### STUDY CONFIGURATION")
st.sidebar.write("Region: Punjab & Haryana, India")
st.sidebar.write("Period: Oct – Nov 2022")
st.sidebar.write("Grid: 2 km")

st.sidebar.divider()
st.sidebar.caption("NASA FIRMS | MODIS Aqua | VIIRS NOAA-20")

# --------------------------------------------------
# OVERVIEW PAGE
# --------------------------------------------------

if page == "Overview":

    st.markdown("""
    <div class="hero">
        <h1>Fire Parallax</h1>
        <p>
        Exploring how different satellite sensors record
        active-fire detections across the same region.
        </p>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("### STUDY AT A GLANCE")

    col1, col2, col3, col4 = st.columns(4)

    metrics = [
        ("SATELLITE PRODUCTS", "02"),
        ("STUDY STATES", "02"),
        ("OBSERVATION PERIOD", "61 Days"),
        ("PRIMARY GRID", "2 km")
    ]

    for column, (label, value) in zip(
        [col1, col2, col3, col4], metrics
    ):
        with column:
            st.markdown(f"""
            <div class="metric-card">
                <div class="metric-label">{label}</div>
                <div class="metric-value">{value}</div>
            </div>
            """, unsafe_allow_html=True)

    st.markdown(
        '<div class="section-title">What is Fire Parallax?</div>',
        unsafe_allow_html=True
    )

    st.write("""
    Fire Parallax is a satellite-data exploration platform that
    compares historical active-fire detections from MODIS Aqua
    and VIIRS NOAA-20.

    It helps users investigate differences in spatial coincidence,
    weekly activity patterns and sensor-specific confidence classes.
    """)

    st.markdown(
        '<div class="section-title">The Two Satellite Sensors</div>',
        unsafe_allow_html=True
    )

    left, right = st.columns(2)

    with left:
        st.markdown("### 🛰️ MODIS Aqua")
        st.write("NASA MODIS Collection 6.1")
        st.write("Nominal spatial resolution: approximately 1 km")
        st.caption("Sensor-specific numeric confidence values.")

    with right:
        st.markdown("### 🛰️ VIIRS NOAA-20")
        st.write("NASA VIIRS Collection 2")
        st.write("Nominal spatial resolution: 375 m")
        st.caption("Sensor-specific categorical confidence values.")

    st.markdown(
        '<div class="section-title">Important Scientific Note</div>',
        unsafe_allow_html=True
    )

    st.markdown("""
    <div class="notice">
        Active-fire hotspots are satellite thermal detections.
        They are not confirmed physical fire events, verified
        agricultural burning, or measurements of burned area.
    </div>
    """, unsafe_allow_html=True)

# --------------------------------------------------
# PLACEHOLDER PAGES
# --------------------------------------------------

elif page == "Burning Activity Calendar":

    from pathlib import Path
    import pandas as pd
    import plotly.express as px

    st.title("🔥 Burning Activity Calendar")

    st.write(
        "Explore weekly active-fire detection patterns "
        "across Punjab and Haryana."
    )

    # Load processed NASA analysis results
    PROJECT_ROOT = Path(__file__).resolve().parent.parent

    DATA_FILE = (
        PROJECT_ROOT
        / "data"
        / "processed"
        / "weekly_activity_calendar.csv"
    )

    if not DATA_FILE.exists():
        st.error("Weekly calendar dataset not found.")
        st.stop()

    data = pd.read_csv(DATA_FILE)

    data["week_start"] = pd.to_datetime(data["week_start"])

    # Sidebar filters
    st.markdown("### Explore the data")

    col1, col2 = st.columns(2)

    with col1:
        selected_state = st.selectbox(
            "Select State",
            sorted(data["state"].unique())
        )

    with col2:
        selected_sensor = st.selectbox(
            "Select Satellite Sensor",
            sorted(data["sensor"].unique())
        )

    filtered = data[
        (data["state"] == selected_state)
        &
        (data["sensor"] == selected_sensor)
    ].sort_values("week_start")

    # Summary metrics
    total_cell_days = int(filtered["active_cell_days"].sum())

    peak_row = filtered.loc[
        filtered["active_cell_days"].idxmax()
    ]

    col1, col2, col3 = st.columns(3)

    col1.metric(
        "Active Cell-Days",
        f"{total_cell_days:,}"
    )

    col2.metric(
        "Peak Week",
        peak_row["week_start"].strftime("%d %b %Y")
    )

    col3.metric(
        "Peak Weekly Share",
        f"{peak_row['weekly_share_pct']:.2f}%"
    )

    st.divider()

    # Weekly activity chart
    st.markdown("### Weekly Activity Trend")

    fig = px.bar(
        filtered,
        x="week_start",
        y="active_cell_days",
        hover_data=[
            "detection_count",
            "weekly_share_pct",
            "coverage_days"
        ],
        labels={
            "week_start": "Week Beginning",
            "active_cell_days": "Active Cell-Days",
            "detection_count": "Detection Records",
            "weekly_share_pct": "Weekly Share (%)",
            "coverage_days": "Days Covered"
        },
        title=f"{selected_sensor} — {selected_state}"
    )

    fig.update_layout(
        template="plotly_dark",
        xaxis_title="Week Beginning",
        yaxis_title="Active Cell-Days"
    )

    st.plotly_chart(
        fig,
        use_container_width=True
    )

    # Weekly distribution
    st.markdown("### Weekly Distribution")

    line_fig = px.line(
        filtered,
        x="week_start",
        y="weekly_share_pct",
        markers=True,
        labels={
            "week_start": "Week Beginning",
            "weekly_share_pct": "Weekly Share (%)"
        }
    )

    line_fig.update_layout(
        template="plotly_dark"
    )

    st.plotly_chart(
        line_fig,
        use_container_width=True
    )

    # Data table
    st.markdown("### Underlying Weekly Records")

    display_data = filtered[
        [
            "week_start",
            "active_cell_days",
            "detection_count",
            "weekly_share_pct",
            "coverage_days"
        ]
    ].copy()

    display_data["week_start"] = (
        display_data["week_start"].dt.strftime("%d %b %Y")
    )

    st.dataframe(
        display_data,
        use_container_width=True,
        hide_index=True
    )

    st.caption(
        "Note: Active cell-days represent spatial grid cells with "
        "at least one qualifying detection on a UTC date. "
        "They are not counts of unique physical fires. "
        "Weekly shares are calculated within the selected state "
        "and sensor."
    )

elif page == "Spatial Explorer":
    from pyproj import Transformer
    import plotly.express as px

    st.title("Spatial Explorer")
    st.markdown(
        "Explore where MODIS Aqua and VIIRS NOAA-20 recorded "
        "overlapping and sensor-specific activity."
    )

    data_file = PROJECT_ROOT / "data" / "processed" / "grid_comparison_2km.csv"

    if not data_file.exists():
        st.error("Spatial comparison dataset not found.")
        st.stop()

    data = pd.read_csv(data_file)

    # Aggregate cell-days across the study period
    spatial_data = (
        data.groupby(["state", "grid_x", "grid_y", "category"])
        .size()
        .reset_index(name="active_cell_days")
    )

    # Convert 2 km grid-cell centres from UTM 43N to latitude/longitude
    transformer = Transformer.from_crs(
        "EPSG:32643",
        "EPSG:4326",
        always_xy=True
    )

    spatial_data["x_m"] = (spatial_data["grid_x"] + 0.5) * 2000
    spatial_data["y_m"] = (spatial_data["grid_y"] + 0.5) * 2000

    lon, lat = transformer.transform(
        spatial_data["x_m"].values,
        spatial_data["y_m"].values
    )

    spatial_data["longitude"] = lon
    spatial_data["latitude"] = lat

    # Filters
    col1, col2 = st.columns(2)

    with col1:
        selected_state = st.selectbox(
            "Select state",
            sorted(spatial_data["state"].unique())
        )

    with col2:
        categories = {
            "co_detected": "Co-detected",
            "modis_only": "MODIS-only",
            "viirs_only": "VIIRS-only"
        }

        selected_categories = st.multiselect(
            "Detection categories",
            options=list(categories.keys()),
            default=list(categories.keys()),
            format_func=lambda x: categories[x]
        )

    filtered = spatial_data[
        (spatial_data["state"] == selected_state)
        & (spatial_data["category"].isin(selected_categories))
    ].copy()

    # Summary
    st.subheader(f"Spatial activity — {selected_state}")

    if filtered.empty:
        st.warning("No map points match the selected filters.")
    else:
        summary = (
            filtered.groupby("category")["active_cell_days"]
            .sum()
            .to_dict()
        )

        c1, c2, c3 = st.columns(3)

        c1.metric(
            "Co-detected",
            f"{summary.get('co_detected', 0):,}"
        )
        c2.metric(
            "MODIS-only",
            f"{summary.get('modis_only', 0):,}"
        )
        c3.metric(
            "VIIRS-only",
            f"{summary.get('viirs_only', 0):,}"
        )

        color_map = {
            "co_detected": "green",
            "modis_only": "blue",
            "viirs_only": "red"
        }

        filtered["category_label"] = filtered["category"].map(categories)

        fig = px.scatter_map(
            filtered,
            lat="latitude",
            lon="longitude",
            color="category",
            size="active_cell_days",
            size_max=13,
            hover_name="category_label",
            hover_data={
                "active_cell_days": True,
                "latitude": False,
                "longitude": False,
                "category": False
            },
            color_discrete_map=color_map,
            zoom=6,
            center={
                "lat": 30.5,
                "lon": 75.5
            },
            map_style="open-street-map",
            height=650,
            title="MODIS–VIIRS Spatial Comparison"
        )

        fig.update_layout(
            margin={"r": 0, "t": 45, "l": 0, "b": 0},
            legend_title_text="Detection category"
        )

        st.plotly_chart(fig, use_container_width=True)

        st.caption(
            "Each point represents the centre of a 2 km grid cell. "
            "Point size represents the number of active cell-days "
            "in that category across the study period. "
            "These points do not represent individual physical fires."
        )

    st.divider()

    st.subheader("How to interpret this map")
    st.markdown("""
    - **Co-detected:** Both sensors recorded at least one qualifying
      detection in the same grid cell on the same UTC date.
    - **MODIS-only:** MODIS recorded detections, but VIIRS did not
      under the same matching rule.
    - **VIIRS-only:** VIIRS recorded detections, but MODIS did not
      under the same matching rule.

    These categories describe spatial-temporal agreement between
    sensor products. They do not establish which sensor is more
    accurate or prove that either sensor missed a physical fire.
    """)

elif page == "Sensor Comparison":
    import plotly.express as px

    st.title("Sensor Comparison")

    st.markdown("""
    Compare the weekly distribution of active cell-days recorded by
    MODIS Aqua and VIIRS NOAA-20 across Punjab and Haryana.
    """)

    data_file = (
        PROJECT_ROOT
        / "data"
        / "processed"
        / "weekly_activity_calendar.csv"
    )

    if not data_file.exists():
        st.error("Weekly activity dataset not found.")
        st.stop()

    data = pd.read_csv(data_file)
    data["week_start"] = pd.to_datetime(data["week_start"])

    # State filter
    selected_state = st.selectbox(
        "Select state",
        ["Punjab", "Haryana"]
    )

    filtered = data[data["state"].replace({
        "Haryāna": "Haryana"
    }) == selected_state].copy()

    if filtered.empty:
        st.warning("No data available for this state.")
        st.stop()

    # Sensor summary
    st.subheader("Sensor activity summary")

    summary = (
        filtered.groupby("sensor")
        .agg(
            total_cell_days=("active_cell_days", "sum"),
            total_detections=("detection_count", "sum")
        )
        .reset_index()
    )

    col1, col2 = st.columns(2)

    for index, (_, row) in enumerate(summary.iterrows()):
        target = col1 if index == 0 else col2

        with target:
            st.metric(
                label=f"{row['sensor']} — Active cell-days",
                value=f"{int(row['total_cell_days']):,}"
            )
            st.metric(
                label="Recorded detections",
                value=f"{int(row['total_detections']):,}"
            )

    # Weekly comparison
    st.divider()
    st.subheader("Weekly active cell-days")

    fig1 = px.bar(
        filtered,
        x="week_start",
        y="active_cell_days",
        color="sensor",
        barmode="group",
        hover_data=[
            "detection_count",
            "weekly_share_pct",
            "coverage_days"
        ],
        labels={
            "week_start": "Week beginning",
            "active_cell_days": "Active cell-days",
            "sensor": "Satellite sensor"
        },
        title=f"Weekly activity comparison — {selected_state}"
    )

    fig1.update_layout(height=450)
    st.plotly_chart(fig1, use_container_width=True)

    # Weekly share comparison
    st.subheader("Weekly share of sensor activity")

    fig2 = px.line(
        filtered,
        x="week_start",
        y="weekly_share_pct",
        color="sensor",
        markers=True,
        hover_data=[
            "active_cell_days",
            "detection_count",
            "coverage_days"
        ],
        labels={
            "week_start": "Week beginning",
            "weekly_share_pct": "Weekly activity share (%)",
            "sensor": "Satellite sensor"
        },
        title=f"Weekly activity distribution — {selected_state}"
    )

    fig2.update_layout(height=450)
    st.plotly_chart(fig2, use_container_width=True)

    # Peak week
    st.divider()
    st.subheader("Peak activity week")

    peak_rows = (
        filtered.loc[
            filtered.groupby("sensor")["active_cell_days"].idxmax()
        ]
        .sort_values("sensor")
    )

    for _, row in peak_rows.iterrows():
        st.write(
            f"**{row['sensor']}**: "
            f"Week beginning {row['week_start'].strftime('%d %B %Y')} — "
            f"{int(row['active_cell_days']):,} active cell-days."
        )

    # Data table
    with st.expander("View weekly comparison data"):
        display_data = filtered.sort_values(
            ["week_start", "sensor"]
        ).copy()

        display_data["week_start"] = (
            display_data["week_start"].dt.strftime("%d %b %Y")
        )

        st.dataframe(
            display_data,
            use_container_width=True,
            hide_index=True
        )

    st.info("""
    **Scientific interpretation:** Active cell-days represent
    sensor detections aggregated into spatial cells and UTC dates.
    They are not counts of unique physical fires.

    Weekly activity share is calculated separately within each
    sensor and state. It allows comparison of the distribution
    of activity over time, but does not make raw sensor counts
    directly equivalent.
    """)


elif page == "Confidence Explorer":
    import plotly.express as px

    st.title("Confidence Explorer")
    st.caption(
        "Explore how active-fire detections are distributed across "
        "each sensor's native confidence categories."
    )

    data_file = PROJECT_ROOT / "data" / "processed" / "confidence_class_calendar.csv"

    if not data_file.exists():
        st.error("Confidence calendar dataset not found.")
    else:
        data = pd.read_csv(data_file)
        data["week_start"] = pd.to_datetime(data["week_start"])
        data["state"] = data["state"].replace({"Haryāna": "Haryana"})

        col1, col2 = st.columns(2)

        with col1:
            selected_state = st.selectbox(
                "Select state",
                ["Punjab", "Haryana"],
                key="confidence_state"
            )

        with col2:
            selected_class = st.selectbox(
                "Select confidence category",
                ["Low", "Nominal", "High"],
                key="confidence_class"
            )

        filtered = data[
            (data["state"] == selected_state)
            & (data["confidence_class"] == selected_class)
        ].copy()

        if filtered.empty:
            st.warning("No records found for this selection.")
        else:
            summary = (
                filtered.groupby("sensor")
                .agg(
                    active_cell_days=("active_cell_days", "sum"),
                    detections=("detection_count", "sum")
                )
                .reset_index()
            )

            st.subheader(f"{selected_class} confidence — {selected_state}")

            metric_cols = st.columns(len(summary))

            for i, row in summary.iterrows():
                with metric_cols[i]:
                    st.metric(
                        label=f"{row['sensor']} active cell-days",
                        value=f"{int(row['active_cell_days']):,}",
                        help=f"{int(row['detections']):,} recorded detections"
                    )

            st.markdown("#### Weekly active cell-days")

            fig1 = px.bar(
                filtered,
                x="week_start",
                y="active_cell_days",
                color="sensor",
                barmode="group",
                hover_data=["detection_count", "weekly_share_pct"],
                labels={
                    "week_start": "Week beginning",
                    "active_cell_days": "Active cell-days",
                    "sensor": "Sensor"
                },
                color_discrete_map={
                    "MODIS Aqua": "#4C9BE8",
                    "VIIRS NOAA-20": "#F08A5D"
                }
            )
            fig1.update_layout(
                template="plotly_dark",
                legend_title_text="Sensor",
                xaxis_title="Week beginning",
                yaxis_title="Active cell-days"
            )
            st.plotly_chart(fig1, use_container_width=True)

            st.markdown("#### Weekly share within this confidence category")

            fig2 = px.line(
                filtered,
                x="week_start",
                y="weekly_share_pct",
                color="sensor",
                markers=True,
                hover_data=["active_cell_days", "detection_count"],
                labels={
                    "week_start": "Week beginning",
                    "weekly_share_pct": "Weekly share (%)",
                    "sensor": "Sensor"
                },
                color_discrete_map={
                    "MODIS Aqua": "#4C9BE8",
                    "VIIRS NOAA-20": "#F08A5D"
                }
            )
            fig2.update_layout(
                template="plotly_dark",
                legend_title_text="Sensor",
                xaxis_title="Week beginning",
                yaxis_title="Weekly share (%)"
            )
            st.plotly_chart(fig2, use_container_width=True)

            st.markdown("#### Weekly data")
            display_data = filtered[
                [
                    "week_start",
                    "sensor",
                    "active_cell_days",
                    "detection_count",
                    "weekly_share_pct"
                ]
            ].sort_values(["week_start", "sensor"])

            st.dataframe(
                display_data,
                use_container_width=True,
                hide_index=True
            )

            st.info(
                "Interpretation: weekly share is calculated within the "
                "selected sensor, state, and confidence category. It shows "
                "when that category's activity occurred during this dataset; "
                "it does not measure detection accuracy."
            )

            st.warning(
                "MODIS numeric confidence thresholds and VIIRS categorical "
                "confidence labels are sensor-specific. Low, Nominal, and "
                "High are displayed for exploration, not as equivalent "
                "probability or accuracy levels."
            )


elif page == "Methodology":

    st.title("Methodology")
    st.caption(
        "Scientific framework, data processing decisions, "
        "comparison rules, and limitations of Fire Parallax."
    )

    st.markdown("## 1. Research Question")

    st.write(
        "How does the seasonal picture of burning activity change when "
        "the same region is observed by MODIS and VIIRS, and how can "
        "users explore those differences without confusing sensor "
        "detections with actual fire events?"
    )

    st.markdown("## 2. Study Region and Period")

    col1, col2, col3 = st.columns(3)

    col1.metric("Study region", "Punjab & Haryana")
    col2.metric("Observation period", "Oct–Nov 2022")
    col3.metric("Spatial grid", "2 km")

    st.write(
        "Punjab and Haryana were selected as a regional case study "
        "because of their relevance to post-monsoon agricultural "
        "burning activity in northwestern India."
    )

    st.markdown("## 3. Satellite Data Sources")

    with st.expander("MODIS Aqua"):
        st.write(
            "- Source: NASA FIRMS active-fire archive"
        )
        st.write(
            "- Instrument: Moderate Resolution Imaging Spectroradiometer"
        )
        st.write("- Platform: Aqua")
        st.write("- Product: MODIS Collection 6.1")
        st.write("- Nominal spatial resolution: approximately 1 km")
        st.write(
            "- Native confidence: numeric confidence value"
        )

    with st.expander("VIIRS NOAA-20"):
        st.write("- Source: NASA FIRMS active-fire archive")
        st.write("- Instrument: Visible Infrared Imaging Radiometer Suite")
        st.write("- Platform: NOAA-20")
        st.write("- Product: VIIRS 375 m active-fire product")
        st.write("- Native confidence: Low, Nominal, High categories")
        st.write(
            "- Native spatial resolution: approximately 375 m"
        )

    st.info(
        "MODIS Aqua and VIIRS NOAA-20 have different spatial resolutions, "
        "observation characteristics, and confidence systems. Their "
        "detection counts should not be treated as directly interchangeable."
    )

    st.markdown("## 4. Data Filtering and Preprocessing")

    st.write(
        "The original FIRMS CSV files were validated before analysis. "
        "The following selection rules were applied:"
    )

    st.markdown(
        """
        - MODIS observations were restricted to Aqua.
        - VIIRS observations were restricted to NOAA-20.
        - Both datasets were filtered to `type = 0`, representing
          presumed vegetation fires.
        - Observations were restricted to Punjab and Haryana
          administrative boundaries.
        - Acquisition dates and times were retained in UTC.
        - Geographic coordinates were transformed from WGS84
          into UTM Zone 43N (EPSG:32643).
        """
    )

    st.warning(
        "The type = 0 filter does not prove that a detection represents "
        "agricultural residue burning. The analysis concerns presumed "
        "vegetation-fire detections."
    )

    st.markdown("## 5. Spatial Harmonization")

    st.write(
        "To compare observations from sensors with different native "
        "resolutions, detections were assigned to a common projected "
        "spatial grid."
    )

    st.markdown(
        """
        **Reference grid configuration**

        - Coordinate system: EPSG:32643
        - Grid cell size: 2 km × 2 km
        - Grid origin: (0, 0) metres
        - Matching dimensions: state, UTC date, grid X, grid Y
        """
    )

    st.markdown("### Cell-day definitions")

    st.write(
        "**Co-detected:** Both sensors recorded at least one qualifying "
        "detection in the same grid cell and UTC date."
    )

    st.write(
        "**MODIS-only:** MODIS recorded a detection, but VIIRS did not "
        "record one in the corresponding cell-day."
    )

    st.write(
        "**VIIRS-only:** VIIRS recorded a detection, but MODIS did not "
        "record one in the corresponding cell-day."
    )

    st.warning(
        "These categories describe spatial-temporal coincidence. "
        "They do not identify the same physical fire or establish "
        "that either sensor missed an actual fire."
    )

    st.markdown("## 6. Burning Activity Calendar")

    st.write(
        "The weekly calendar aggregates active cell-days by state, "
        "sensor, and week. Weeks begin on Monday."
    )

    st.write(
        "Weekly share is calculated as the active cell-days in a given "
        "week divided by the total active cell-days for that state and "
        "sensor across the selected observation period."
    )

    st.latex(
        r"\text{Weekly Share} = "
        r"\frac{\text{Weekly Active Cell-Days}}"
        r"{\text{Total Active Cell-Days}} \times 100"
   )

    st.write(
        "Partial weeks at the beginning and end of the observation "
        "period are retained and identified by their coverage days."
    )

    st.markdown("## 7. Confidence Classification")

    st.write("The native confidence fields were preserved.")

    st.markdown(
        """
        **MODIS Aqua**

        - Low: 0–29
        - Nominal: 30–79
        - High: 80–100

        **VIIRS NOAA-20**

        - Low: `l`
        - Nominal: `n`
        - High: `h`
        """
    )

    st.warning(
        "MODIS numeric thresholds and VIIRS categorical labels are "
        "sensor-specific. The categories are displayed separately "
        "and are not interpreted as equivalent confidence probabilities "
        "or accuracy measurements."
    )

    st.info(
    "A spatial cell-day can appear in more than one confidence "
    "category when multiple detections with different confidence "
    "values occur in that cell on the same UTC date. Therefore, "
    "class-specific active cell-days must not be added together "
    "to calculate total unique sensor activity."
   )

    st.markdown("## 8. Sensitivity Analysis")

    st.write(
        "Spatial overlap was evaluated at three grid resolutions "
        "to investigate how the choice of grid size affects "
        "sensor coincidence."
    )

    sensitivity_data = pd.DataFrame({
        "Grid size": ["1 km", "2 km", "5 km"],
        "MODIS cell-days": [11097, 9894, 7656],
        "VIIRS cell-days": [46331, 39726, 24472],
        "Co-detected": [1849, 3406, 5166],
        "Jaccard overlap (%)": [3.33, 7.37, 19.16]
    })

    st.dataframe(
        sensitivity_data,
        use_container_width=True,
        hide_index=True
    )

    st.write(
        "The Jaccard overlap increases with grid size because larger "
        "cells make spatial coincidence less restrictive. The 2 km "
        "grid was retained as a reproducible reference configuration, "
        "not because it maximizes agreement."
    )

    st.markdown("## 9. Limitations")

    st.markdown(
        """
        - The analysis covers only October and November 2022.
        - Results represent one regional case study, not all of India.
        - Active-fire detections are not equivalent to unique fire events.
        - Cloud cover and satellite observation timing can influence detections.
        - Different sensor resolutions and algorithms affect recorded counts.
        - A zero-detection cell-day does not establish the absence of fire.
        - Confidence categories are not directly comparable across sensors.
        - The analysis does not forecast future burning activity.
        - The analysis does not independently verify agricultural burning.
        """
    )

    st.markdown("## 10. Responsible Interpretation")

    st.success(
        "Fire Parallax is a sensor-aware exploratory analysis tool. "
        "Its purpose is to make differences between MODIS and VIIRS "
        "observations visible, measurable, and interpretable without "
        "claiming that satellite detections are complete records "
        "of actual fire events."
    )

    st.markdown("---")

    st.caption(
        "Fire Parallax | NASA Space Apps Challenge 2026 | "
        "Team ROCHE DOMINION"
    )