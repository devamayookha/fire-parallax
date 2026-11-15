from pathlib import Path

import pandas as pd

import plotly.express as px

import plotly.graph_objects as go

import streamlit as st

from pyproj import Transformer

# Ensure indented HTML strings are rendered as HTML, not Markdown code blocks.
_original_st_markdown = st.markdown

def _render_markdown_dedented(body, *args, **kwargs):
    if kwargs.get("unsafe_allow_html", False) and isinstance(body, str):
        body = "\n".join(line.lstrip() for line in body.splitlines()).strip()
    return _original_st_markdown(body, *args, **kwargs)

st.markdown = _render_markdown_dedented

# ---------------------------------------------------------------------

# FIRE PARALLAX — mission-control dashboard

# Data-driven UI for MODIS Aqua and VIIRS NOAA-20 comparisons.

# ---------------------------------------------------------------------

st.set_page_config(

          page_title="Fire Parallax | Earth Observation Intelligence",

          page_icon="🔥",

          layout="wide",

          initial_sidebar_state="expanded",

)

PROJECT_ROOT = Path(__file__).resolve().parent.parent

DATA_DIR = PROJECT_ROOT / "data" / "processed"

COLORS = {

          "bg": "#080E1B",

          "panel": "#111C2F",

          "panel2": "#16243A",

          "border": "#263852",

          "text": "#E8EEF8",

          "muted": "#91A3BC",

          "blue": "#57A6FF",

          "cyan": "#55D6D2",

          "orange": "#FF9B5C",

          "red": "#FF6B6B",

          "green": "#75D69C",

          "purple": "#A99BFF",

}

SENSOR_COLORS = {"MODIS Aqua": COLORS["blue"], "VIIRS NOAA-20": COLORS["orange"]}

CATEGORY_LABELS = {

          "co_detected": "Co-detected",

          "modis_only": "MODIS-only",

          "viirs_only": "VIIRS-only",

}

CATEGORY_COLORS = {

          "co_detected": COLORS["green"],

          "modis_only": COLORS["blue"],

          "viirs_only": COLORS["orange"],

}

# ---------------------------------------------------------------------

# Styling

# ---------------------------------------------------------------------

st.markdown(

          f"""

          <style>

          @import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;600;700&family=Space+Grotesk:wght@500;600;700&display=swap');

          :root {{

               --fp-bg: {COLORS["bg"]};

               --fp-panel: {COLORS["panel"]};

               --fp-border: {COLORS["border"]};

               --fp-text: {COLORS["text"]};

               --fp-muted: {COLORS["muted"]};

          }}

          html, body, [class*="css"] {{

               font-family: 'DM Sans', sans-serif;

          }}

          .stApp {{

               background:

                    radial-gradient(ellipse at 78% 0%, rgba(43,91,153,.17), transparent 34%),

                    linear-gradient(180deg, #080E1B 0%, #0A1221 100%);

               color: var(--fp-text);

          }}

          [data-testid="stHeader"] {{

               background: rgba(8,14,27,.82);

          }}

          [data-testid="stSidebar"] {{

               background: linear-gradient(180deg, #101B2D 0%, #0B1423 100%);

               border-right: 1px solid #263852;

          }}

          [data-testid="stSidebar"] > div:first-child {{

               padding-top: 1.3rem;

          }}

          [data-testid="stSidebar"] [data-testid="stRadio"] label {{

               padding: .35rem .55rem;

               border-radius: 8px;

          }}

          [data-testid="stSidebar"] [data-testid="stRadio"] label:hover {{

               background: rgba(87,166,255,.10);

          }}

          h1, h2, h3 {{

               font-family: 'Space Grotesk', sans-serif !important;

               letter-spacing: -.025em;

               color: #F5F8FF;

          }}

          h1 {{ font-size: 2.35rem !important; }}

          h2 {{ font-size: 1.55rem !important; }}

          h3 {{ font-size: 1.12rem !important; }}

          p, li, label {{ color: #D7E1F0; }}

          .block-container {{

               max-width: 1500px;

               padding-top: 1.6rem;

               padding-bottom: 3rem;

          }}

          .eyebrow {{

               color: {COLORS["cyan"]};

               font-size: .73rem;

               font-weight: 700;

               letter-spacing: .17em;

               text-transform: uppercase;

               margin-bottom: .55rem;

          }}

          .hero {{

               position: relative;

               overflow: hidden;

               padding: 2.1rem 2.25rem;

               border: 1px solid #29466A;

               border-radius: 22px;

               background:

                    radial-gradient(circle at 85% 20%, rgba(85,214,210,.17), transparent 26%),

                    radial-gradient(circle at 70% 110%, rgba(87,166,255,.22), transparent 40%),

                    linear-gradient(115deg, #12223A 0%, #142C4A 55%, #18264B 100%);

               box-shadow: 0 18px 50px rgba(0,0,0,.22);

               margin-bottom: 1.35rem;

          }}

          .hero {{

               min-height: 300px;

               display: flex;

               flex-direction: column;

               justify-content: center;

               isolation: isolate;

          }}

          .hero::before {{

               content: "";

               position: absolute;

               z-index: -1;

               width: 430px;

               height: 430px;

               right: -55px;

               top: -105px;

               border-radius: 50%;

               background:

                    radial-gradient(circle at 34% 34%, rgba(112,190,255,.95) 0 2%, transparent 3%),

                    radial-gradient(circle at 42% 38%, rgba(52,139,207,.95) 0 12%, transparent 13%),

                    radial-gradient(circle at 65% 62%, rgba(13,57,102,.96) 0 30%, transparent 31%),

                    radial-gradient(circle at 40% 38%, #1b5c91 0%, #0c2949 48%, #061324 72%);

               box-shadow: inset -28px -22px 55px rgba(0,0,0,.48), 0 0 75px rgba(63,151,224,.28);

               opacity: .92;

          }}

          .hero::after {{

               content: "";

               position: absolute;

               z-index: -1;

               width: 570px;

               height: 170px;

               right: -95px;

               top: 18px;

               border: 1px solid rgba(112,205,255,.40);

               border-radius: 50%;

               transform: rotate(-19deg);

               box-shadow: 0 0 22px rgba(82,183,255,.12);

          }}

          .hero h1 {{

               margin: 0 0 .45rem 0;

               font-size: 2.9rem !important;

               max-width: 650px;

          }}

          .hero .hero-copy {{

               max-width: 680px;

               position: relative;

               z-index: 2;

          }}

          .mission-strip {{

               display:flex; flex-wrap:wrap; gap:.55rem; align-items:center;

               margin-top:1.05rem; color:#9FB9D5; font-size:.72rem;

               letter-spacing:.08em; text-transform:uppercase;

          }}

          .mission-strip span {{

               border:1px solid rgba(128,190,235,.28);

               background:rgba(4,16,31,.38); border-radius:999px;

               padding:.38rem .68rem;

          }}

          .hero p {{

               max-width: 760px;

               color: #C1D1E5;

               font-size: 1.04rem;

               line-height: 1.65;

               margin-bottom: .8rem;

          }}

          .hero-tag {{

               display: inline-block;

               color: #BFEFEB;

               border: 1px solid rgba(85,214,210,.38);

               background: rgba(85,214,210,.08);

               padding: .32rem .65rem;

               border-radius: 999px;

               font-size: .72rem;

               letter-spacing: .08em;

               text-transform: uppercase;

               margin-right: .35rem;

          }}

          .metric-card {{

               background: linear-gradient(145deg, #15243A, #101B2D);

               border: 1px solid #2A3D58;

               border-radius: 16px;

               padding: 1.05rem 1.15rem;

               min-height: 112px;

               box-shadow: 0 8px 24px rgba(0,0,0,.12);

          }}

          .metric-label {{

               color: #91A8C4;

               font-size: .73rem;

               font-weight: 700;

               letter-spacing: .09em;

               text-transform: uppercase;

          }}

          .metric-value {{

               color: #F4F8FF;

               font-family: 'Space Grotesk', sans-serif;

               font-size: 1.8rem;

               font-weight: 700;

               margin-top: .32rem;

          }}

          .metric-note {{

               color: #8FA3BD;

               font-size: .76rem;

               margin-top: .15rem;

          }}

          .section-kicker {{

               color: {COLORS["cyan"]};

               font-size: .72rem;

               font-weight: 700;

               letter-spacing: .14em;

               text-transform: uppercase;

               margin: 1.35rem 0 .25rem 0;

          }}

          .panel {{

               background: linear-gradient(145deg, rgba(21,36,58,.96), rgba(14,25,42,.96));

               border: 1px solid #273B56;

               border-radius: 16px;

               padding: 1.05rem 1.2rem;

               margin-bottom: .7rem;

          }}

          .panel-title {{

               color: #F2F6FC;

               font-weight: 700;

               font-size: 1.02rem;

               margin-bottom: .35rem;

          }}

          .panel-copy {{

               color: #9FB0C7;

               line-height: 1.55;

               font-size: .9rem;

          }}

          .notice {{

               background: rgba(255,181,71,.09);

               border: 1px solid rgba(255,181,71,.32);

               border-left: 4px solid #FFB547;

               border-radius: 10px;

               padding: .9rem 1rem;

               color: #F8DDA8;

               line-height: 1.55;

          }}

          .science-note {{

               background: rgba(87,166,255,.08);

               border: 1px solid rgba(87,166,255,.25);

               border-left: 4px solid {COLORS["blue"]};

               border-radius: 10px;

               padding: .9rem 1rem;

               color: #C9DDF6;

               line-height: 1.55;

          }}

          .sensor-chip {{

               display: inline-block;

               padding: .28rem .6rem;

               border-radius: 999px;

               font-size: .72rem;

               font-weight: 700;

               background: rgba(87,166,255,.12);

               color: #A9D2FF;

               border: 1px solid rgba(87,166,255,.25);

          }}

          div[data-testid="stMetric"] {{

               background: #142238;

               border: 1px solid #2A3D58;

               padding: .85rem 1rem;

               border-radius: 13px;

          }}

          div[data-testid="stMetric"] label {{

               color: #9FB0C7 !important;

          }}

          div[data-testid="stMetric"] [data-testid="stMetricValue"] {{

               color: #F4F8FF !important;

               font-family: 'Space Grotesk', sans-serif;

          }}

          .stButton button, .stDownloadButton button {{

               border-radius: 9px;

               border: 1px solid #3C638D;

          }}

          hr {{

               border-color: #263852;

          }}

          [data-testid="stDataFrame"] {{

               border: 1px solid #263852;

               border-radius: 10px;

          }}

          footer {{ visibility: hidden; }}

          </style>

          """,

          unsafe_allow_html=True,

)

# ---------------------------------------------------------------------

# Data helpers

# ---------------------------------------------------------------------

@st.cache_data(show_spinner=False)

def load_csv(filename: str) -> pd.DataFrame:

          path = DATA_DIR / filename

          if not path.exists():

                    raise FileNotFoundError(f"Required dataset not found: {path}")

          return pd.read_csv(path)

def try_load(filename: str):

          try:

                    return load_csv(filename), None

          except Exception as exc:

                    return None, str(exc)

def normalize_state(series: pd.Series) -> pd.Series:

          return series.replace({"Haryāna": "Haryana", "Haryana ": "Haryana"})

def moneyless_num(value) -> str:

          try:

                    return f"{int(value):,}"

          except (TypeError, ValueError):

                    return "—"

def metric_card(label: str, value: str, note: str = ""):

          st.markdown(

                    f"""

                    <div class="metric-card">

                         <div class="metric-label">{label}</div>

                         <div class="metric-value">{value}</div>

                         <div class="metric-note">{note}</div>

                    </div>

                    """,

                    unsafe_allow_html=True,

          )

def section_header(kicker: str, title: str, subtitle: str = ""):

          st.markdown(f'<div class="section-kicker">{kicker}</div>', unsafe_allow_html=True)

          st.subheader(title)

          if subtitle:

                    st.caption(subtitle)

def chart_layout(fig, height=390, legend=True):

          fig.update_layout(

                    template="plotly_dark",

                    paper_bgcolor="rgba(0,0,0,0)",

                    plot_bgcolor="rgba(0,0,0,0)",

                    font=dict(family="DM Sans, sans-serif", color="#D7E1F0"),

                    height=height,

                    margin=dict(l=12, r=12, t=48, b=12),

                    legend=dict(

                              orientation="h",

                              yanchor="bottom",

                              y=1.02,

                              xanchor="right",

                              x=1,

                              bgcolor="rgba(0,0,0,0)",

                    ) if legend else None,

                    xaxis=dict(gridcolor="rgba(145,163,188,.12)", zerolinecolor="rgba(145,163,188,.12)"),

                    yaxis=dict(gridcolor="rgba(145,163,188,.12)", zerolinecolor="rgba(145,163,188,.12)"),

          )

          return fig

def show_missing(filename: str):

          st.error(f"Dataset unavailable: `{filename}`")

          st.caption("Check that the file exists under `data/processed/` and has been extracted from the team's processed ZIP.")

          st.stop()

# ---------------------------------------------------------------------

# Sidebar

# ---------------------------------------------------------------------

with st.sidebar:

          st.markdown(

                    """

                    <div style="padding:.15rem 0 .9rem 0">

                         <div style="font-size:2rem">🔥</div>

                         <div style="font-family:'Space Grotesk';font-size:1.35rem;font-weight:700;color:#F5F8FF">FIRE PARALLAX</div>

                         <div style="color:#8FA3BD;font-size:.78rem;line-height:1.4;margin-top:.2rem">EARTH OBSERVATION INTELLIGENCE</div>

                    </div>

                    <div style="height:1px;background:#2A3D58;margin:.4rem 0 1rem 0"></div>

                    """,

                    unsafe_allow_html=True,

          )

          page = st.radio(

                    "MISSION NAVIGATION",

                    [

                              "Mission Overview",

                              "Burning Activity Calendar",

                              "Spatial Explorer",

                              "Sensor Comparison",

                              "Confidence Explorer",

                              "Sensitivity Analysis",

                              "Methodology",

                    ],

                    label_visibility="visible",

          )

          st.markdown("---")

          st.markdown("**STUDY PARAMETERS**")

          st.caption("REGION     ·     Punjab & Haryana, India")

          st.caption("PERIOD     ·     01 Oct – 30 Nov 2022")

          st.caption("GRID     ·     2 km reference")

          st.caption("SENSORS     ·     MODIS Aqua / VIIRS NOAA-20")

          st.markdown("---")

          st.caption("NASA FIRMS active-fire archive")

          st.caption("ROCHE DOMINION · Space Apps 2026")

# ---------------------------------------------------------------------

# Mission Overview

# ---------------------------------------------------------------------

if page == "Mission Overview":

          weekly, weekly_err = try_load("weekly_activity_calendar.csv")

          agreement, agreement_err = try_load("agreement_metrics.csv")

          if weekly is None:

                    show_missing("weekly_activity_calendar.csv")

          weekly["state"] = normalize_state(weekly["state"])

          weekly["week_start"] = pd.to_datetime(weekly["week_start"])

          total_modis = int(weekly.loc[weekly["sensor"] == "MODIS Aqua", "detection_count"].sum())

          total_viirs = int(weekly.loc[weekly["sensor"] == "VIIRS NOAA-20", "detection_count"].sum())

          jaccard = None

          if agreement is not None and not agreement.empty:

                    row2 = agreement.loc[agreement["resolution_km"] == 2]

                    if not row2.empty:

                              jaccard = float(row2.iloc[0]["jaccard_overlap_pct"])

          st.markdown(

                    """

                    <div class="hero">

                         <div class="hero-copy">

                              <div class="eyebrow">EARTH OBSERVATION · SATELLITE COMPARISON STUDY</div>

                              <h1>Fire Parallax</h1>

                              <p><b>Two sensors. One region. Different observations.</b><br>

                              Explore how MODIS Aqua and VIIRS NOAA-20 record active-fire detections

                              across Punjab and Haryana, and how spatial and temporal choices change

                              the measured overlap.</p>

                              <div class="mission-strip">

                                   <span>MODIS Aqua · ~1 km</span>

                                   <span>VIIRS NOAA-20 · 375 m</span>

                                   <span>01 Oct — 30 Nov 2022</span>

                                   <span>Punjab + Haryana</span>

                              </div>

                         </div>

                    </div>

                    """,

                    unsafe_allow_html=True,

          )

          st.markdown('<div class="section-kicker">MISSION SNAPSHOT</div>', unsafe_allow_html=True)

          cols = st.columns(4)

          with cols[0]:

                    metric_card("MODIS DETECTION RECORDS", moneyless_num(total_modis), "Aqua · Type 0 regional dataset")

          with cols[1]:

                    metric_card("VIIRS DETECTION RECORDS", moneyless_num(total_viirs), "NOAA-20 · Type 0 regional dataset")

          with cols[2]:

                    metric_card("REFERENCE GRID", "2 km", "Common projected grid")

          with cols[3]:

                    metric_card("JACCARD OVERLAP", f"{jaccard:.2f}%" if jaccard is not None else "—", "2 km · same cell + UTC date")

          st.markdown("")

          left, right = st.columns([1.35, 1])

          with left:

                    section_header("01 / TEMPORAL PICTURE", "Weekly activity across the study")

                    trend = weekly.groupby(["week_start", "sensor"], as_index=False)["active_cell_days"].sum()

                    fig = px.area(

                              trend, x="week_start", y="active_cell_days", color="sensor",

                              color_discrete_map=SENSOR_COLORS, markers=True,

                              labels={"week_start": "Week beginning (UTC)", "active_cell_days": "Active cell-days", "sensor": "Satellite"},

                    )

                    st.plotly_chart(chart_layout(fig, 370), width="stretch")

          with right:

                    section_header("02 / RESEARCH QUESTION", "What changes between sensors?")

                    st.markdown(

                              """

                              <div class="panel">

                                   <div class="panel-title">Compare observations, not assumed fire events</div>

                                   <div class="panel-copy">The platform places detections on a shared 2 km grid and UTC date,

                                   then classifies each cell-day as co-detected, MODIS-only or VIIRS-only.</div>

                              </div>

                              <div class="panel">

                                   <div class="panel-title">Why does this matter?</div>

                                   <div class="panel-copy">The instruments differ in native resolution, overpass timing,

                                   detection characteristics and confidence reporting. Their raw counts

                                   are not interchangeable.</div>

                              </div>

                              """,

                              unsafe_allow_html=True,

                    )

          section_header("03 / INTERPRETATION", "A critical scientific distinction")

          st.markdown(

                    """

                    <div class="notice">

                         Active-fire hotspots are satellite thermal detections. They are not confirmed

                         physical fire events, verified agricultural residue burning, or measurements

                         of burned area. A co-detected cell-day does not prove that both instruments

                         observed the same physical fire.

                    </div>

                    """,

                    unsafe_allow_html=True,

          )

          st.markdown("")

          a, b = st.columns(2)

          with a:

                    st.markdown(

                              f"""

                              <div class="panel">

                                   <span class="sensor-chip">SENSOR 01</span>

                                   <h3 style="margin-top:.7rem">🛰️ MODIS Aqua</h3>

                                   <div class="panel-copy">NASA MODIS Collection 6.1 · approximately 1 km nominal spatial resolution.

                                   Confidence is reported numerically in the source product.</div>

                              </div>

                              """,

                              unsafe_allow_html=True,

                    )

          with b:

                    st.markdown(

                              f"""

                              <div class="panel">

                                   <span class="sensor-chip" style="color:#FFC18F;border-color:#80502F;background:rgba(255,155,92,.10)">SENSOR 02</span>

                                   <h3 style="margin-top:.7rem">🛰️ VIIRS NOAA-20</h3>

                                   <div class="panel-copy">NASA FIRMS VIIRS 375 m product · nominal 375 m spatial resolution.

                                   Confidence is reported categorically as Low, Nominal or High.</div>

                              </div>

                              """,

                              unsafe_allow_html=True,

                    )

# ---------------------------------------------------------------------

# Burning Activity Calendar

# ---------------------------------------------------------------------

elif page == "Burning Activity Calendar":

          section_header("01 / TEMPORAL ANALYSIS", "Burning Activity Calendar", "Weekly active cell-day patterns across the two study states.")

          data, err = try_load("weekly_activity_calendar.csv")

          if data is None:

                    show_missing("weekly_activity_calendar.csv")

          data["state"] = normalize_state(data["state"])

          data["week_start"] = pd.to_datetime(data["week_start"])

          c1, c2 = st.columns(2)

          with c1:

                    state = st.selectbox("Study state", sorted(data["state"].unique()), key="calendar_state")

          with c2:

                    sensor = st.selectbox("Satellite sensor", sorted(data["sensor"].unique()), key="calendar_sensor")

          filtered = data[(data["state"] == state) & (data["sensor"] == sensor)].sort_values("week_start")

          if filtered.empty:

                    st.warning("No records for the selected filters.")

          else:

                    peak = filtered.loc[filtered["active_cell_days"].idxmax()]

                    m = st.columns(3)

                    m[0].metric("Active cell-days", moneyless_num(filtered["active_cell_days"].sum()))

                    m[1].metric("Peak week", peak["week_start"].strftime("%d %b %Y"))

                    m[2].metric("Peak weekly share", f'{peak["weekly_share_pct"]:.1f}%')

                    fig = px.bar(

                              filtered, x="week_start", y="active_cell_days",

                              color_discrete_sequence=[SENSOR_COLORS.get(sensor, COLORS["blue"])],

                              labels={"week_start": "Week beginning", "active_cell_days": "Active cell-days"},

                              hover_data={"detection_count": True, "weekly_share_pct": ":.2f", "coverage_days": True},

                    )

                    st.plotly_chart(chart_layout(fig, 380, legend=False), width="stretch")

                    fig2 = px.line(

                              filtered, x="week_start", y="weekly_share_pct", markers=True,

                              color_discrete_sequence=[COLORS["cyan"]],

                              labels={"week_start": "Week beginning", "weekly_share_pct": "Share of sensor activity (%)"},

                    )

                    st.plotly_chart(chart_layout(fig2, 310, legend=False), width="stretch")

                    with st.expander("Inspect weekly records"):

                              st.dataframe(filtered, width="stretch", hide_index=True)

          st.markdown('<div class="science-note">Active cell-days are spatial grid cells with at least one qualifying detection on a UTC date. They are not counts of unique physical fires. Weekly shares are calculated within each state and sensor.</div>', unsafe_allow_html=True)

# ---------------------------------------------------------------------

# Spatial Explorer

# ---------------------------------------------------------------------

elif page == "Spatial Explorer":

          section_header(

                    "02 / SPATIAL INTELLIGENCE",

                    "Spatial Explorer",

                    "Map the shared-grid observations across Punjab and Haryana.",

          )

          data, err = try_load("grid_comparison_2km.csv")

          if data is None:

                    show_missing("grid_comparison_2km.csv")

          required = {"state", "grid_x", "grid_y", "category"}

          if not required.issubset(data.columns):

                    st.error(f"Spatial dataset is missing columns: {sorted(required - set(data.columns))}")

                    st.stop()

          data["state"] = normalize_state(data["state"])

          spatial = (

                    data.groupby(["state", "grid_x", "grid_y", "category"], as_index=False)

                    .size()

                    .rename(columns={"size": "active_cell_days"})

          )

          # The grid coordinates are cell indices in EPSG:32643. Convert cell centres

          # to geographic coordinates for display; this does not alter the analysis.

          transformer = Transformer.from_crs("EPSG:32643", "EPSG:4326", always_xy=True)

          spatial["x_m"] = (spatial["grid_x"] + 0.5) * 2000

          spatial["y_m"] = (spatial["grid_y"] + 0.5) * 2000

          spatial["longitude"], spatial["latitude"] = transformer.transform(

                    spatial["x_m"].to_numpy(), spatial["y_m"].to_numpy()

          )

          # Mission-style filter panel

          st.markdown(

                    '<div class="panel"><div class="panel-title">OBSERVATION CONTROLS</div>'

                    '<div class="panel-copy">Choose a state and the cell-day categories to display. '

                    'The map and summary values update together.</div></div>',

                    unsafe_allow_html=True,

          )

          filter_col, category_col = st.columns([0.85, 2.15], gap="large")

          states = sorted(spatial["state"].dropna().unique())

          with filter_col:

                    state = st.selectbox("OBSERVATION REGION", states, key="spatial_state")

          with category_col:

                    selected = st.multiselect(

                              "CELL-DAY CATEGORIES",

                              list(CATEGORY_LABELS.keys()),

                              default=list(CATEGORY_LABELS.keys()),

                              format_func=lambda x: CATEGORY_LABELS[x],

                              key="spatial_categories",

                    )

          state_view = spatial[spatial["state"] == state].copy()

          view = state_view[state_view["category"].isin(selected)].copy()

          # Summary totals are calculated from the full selected state, independent

          # of the map category toggles, so the three headline values stay comparable.

          sums = state_view.groupby("category")["active_cell_days"].sum().to_dict()

          st.markdown('<div class="section-kicker">OBSERVATION SUMMARY · ' + state.upper() + '</div>', unsafe_allow_html=True)

          metric_cols = st.columns(3, gap="medium")

          metric_specs = [

                    ("CO-DETECTED", "co_detected", "Both sensors · same cell + UTC date", COLORS["green"]),

                    ("MODIS-ONLY", "modis_only", "MODIS observation only", COLORS["blue"]),

                    ("VIIRS-ONLY", "viirs_only", "VIIRS observation only", COLORS["orange"]),

          ]

          for col, (label, key, note, accent) in zip(metric_cols, metric_specs):

                    with col:

                              st.markdown(

                                        f'<div class="metric-card" style="border-top:3px solid {accent};">'

                                        f'<div class="metric-label">{label}</div>'

                                        f'<div class="metric-value">{moneyless_num(sums.get(key, 0))}</div>'

                                        f'<div class="metric-note">{note}</div></div>',

                                        unsafe_allow_html=True,

                              )

          st.markdown('<div class="section-kicker">GEOGRAPHIC OBSERVATION MAP</div>', unsafe_allow_html=True)

          if view.empty:

                    st.warning("No map cells match the selected categories. Select at least one category to display observations.")

          else:

                    view["category_label"] = view["category"].map(CATEGORY_LABELS)

                    # Stable regional camera: avoids a world-scale/wrapped view
                    # if a sparse category produces a misleading coordinate extent.
                    regional_centres = {
                        "Haryana": {"lat": 29.2, "lon": 76.1},
                        "Punjab": {"lat": 31.0, "lon": 75.3},
                    }
                    center = regional_centres.get(
                        state, {"lat": 30.2, "lon": 75.7}
                    )
                    zoom = 6.2

                    fig = px.scatter_map(

                              view,

                              lat="latitude",

                              lon="longitude",

                              color="category",

                              size="active_cell_days",

                              size_max=11,

                              category_orders={"category": ["co_detected", "modis_only", "viirs_only"]},

                              color_discrete_map=CATEGORY_COLORS,

                              hover_name="category_label",

                              hover_data={

                                        "active_cell_days": ":,",

                                        "state": True,

                                        "grid_x": True,

                                        "grid_y": True,

                                        "latitude": ":.4f",

                                        "longitude": ":.4f",

                                        "category": False,

                              },

                              zoom=zoom,

                              center=center,

                              map_style="carto-darkmatter",

                              height=650,

                              labels={

                                        "category": "Observation category",

                                        "active_cell_days": "Active cell-days",

                                        "state": "State",

                                        "grid_x": "Grid X",

                                        "grid_y": "Grid Y",

                              },

                    )

                    fig.update_traces(

                              marker={"opacity": 0.82},

                              selector={"type": "scattermap"},

                    )

                    fig.update_layout(

                              paper_bgcolor="rgba(0,0,0,0)",

                              plot_bgcolor="rgba(0,0,0,0)",

                              margin=dict(l=0, r=0, t=8, b=0),
                              map=dict(center=center, zoom=zoom),
                              height=650,

                              legend=dict(

                                        title="CELL-DAY CATEGORY",

                                        orientation="h",

                                        yanchor="bottom",

                                        y=1.01,

                                        xanchor="left",

                                        x=0.01,

                                        bgcolor="rgba(8,14,27,.78)",

                                        bordercolor="rgba(145,163,188,.22)",

                                        borderwidth=1,

                                        font=dict(color="#E8EEF8", size=12),

                              ),

                              uirevision=f"spatial-{state}",

                    )

                    st.plotly_chart(fig, width="stretch", config={"displaylogo": False, "scrollZoom": True})

          st.markdown(

                    '<div class="science-note"><b>HOW TO INTERPRET THIS MAP</b><br>'

                    'Each marker represents the centre of a 2 km reference-grid cell. Marker size represents '

                    'the number of cell-days in that category over the study period. Colours identify the '

                    'comparison category; they do not represent fire intensity. Markers are not individual '

                    'fire locations or reconstructed fire events.</div>',

                    unsafe_allow_html=True,

          )

          with st.expander("Category definitions and map notes"):

                    st.markdown("""

                    - **Co-detected:** both sensors have one or more qualifying detections in the same grid cell and UTC date.

                    - **MODIS-only:** MODIS has a qualifying detection, but VIIRS does not under the same matching rule.

                    - **VIIRS-only:** VIIRS has a qualifying detection, but MODIS does not under the same matching rule.

                    The map uses the 2 km comparison grid in EPSG:32643, with cell centres transformed to WGS84 for display.

                    """)

# ---------------------------------------------------------------------

# Sensor Comparison

# ---------------------------------------------------------------------

elif page == "Sensor Comparison":

          section_header("03 / CROSS-SENSOR ANALYSIS", "Sensor Comparison", "Compare weekly activity distributions without treating raw sensor counts as equivalent.")

          data, err = try_load("weekly_activity_calendar.csv")

          if data is None:

                    show_missing("weekly_activity_calendar.csv")

          data["state"] = normalize_state(data["state"])

          data["week_start"] = pd.to_datetime(data["week_start"])

          state = st.selectbox("Study state", sorted(data["state"].unique()), key="comparison_state")

          view = data[data["state"] == state].copy()

          summary = view.groupby("sensor", as_index=False).agg(

                    active_cell_days=("active_cell_days", "sum"),

                    detection_records=("detection_count", "sum"),

          )

          cols = st.columns(2)

          for i, row in summary.iterrows():

                    with cols[i]:

                              st.metric(f'{row["sensor"]} · active cell-days', moneyless_num(row["active_cell_days"]))

                              st.caption(f'{moneyless_num(row["detection_records"])} detection records')

          fig = px.bar(

                    view, x="week_start", y="active_cell_days", color="sensor", barmode="group",

                    color_discrete_map=SENSOR_COLORS,

                    labels={"week_start": "Week beginning", "active_cell_days": "Active cell-days", "sensor": "Sensor"},

                    hover_data={"detection_count": True, "coverage_days": True},

          )

          st.plotly_chart(chart_layout(fig, 410), width="stretch")

          fig2 = px.line(

                    view, x="week_start", y="weekly_share_pct", color="sensor",

                    markers=True, color_discrete_map=SENSOR_COLORS,

                    labels={"week_start": "Week beginning", "weekly_share_pct": "Within-sensor weekly share (%)", "sensor": "Sensor"},

          )

          st.plotly_chart(chart_layout(fig2, 360), width="stretch")

          with st.expander("View weekly comparison table"):

                    st.dataframe(view.sort_values(["week_start", "sensor"]), width="stretch", hide_index=True)

          st.markdown('<div class="notice">Weekly share describes the timing of activity within each sensor and state. It does not make MODIS and VIIRS detection counts directly comparable and is not a sensor-accuracy metric.</div>', unsafe_allow_html=True)

# ---------------------------------------------------------------------

# Confidence Explorer

# ---------------------------------------------------------------------

elif page == "Confidence Explorer":

          section_header("04 / CONFIDENCE ANALYSIS", "Confidence Explorer", "Explore each sensor's native confidence categories as separate reporting systems.")

          data, err = try_load("confidence_class_calendar.csv")

          if data is None:

                    show_missing("confidence_class_calendar.csv")

          data["state"] = normalize_state(data["state"])

          data["week_start"] = pd.to_datetime(data["week_start"])

          c1, c2 = st.columns(2)

          with c1:

                    state = st.selectbox("Study state", sorted(data["state"].unique()), key="confidence_state")

          with c2:

                    conf = st.selectbox("Confidence class", ["Low", "Nominal", "High"], key="confidence_level")

          view = data[(data["state"] == state) & (data["confidence_class"] == conf)].copy()

          summary = view.groupby("sensor", as_index=False).agg(

                    active_cell_days=("active_cell_days", "sum"),

                    detection_records=("detection_count", "sum"),

          )

          cols = st.columns(max(1, len(summary)))

          for i, row in summary.iterrows():

                    with cols[i]:

                              st.metric(f'{row["sensor"]} · {conf}', moneyless_num(row["active_cell_days"]))

                              st.caption(f'{moneyless_num(row["detection_records"])} detection records')

          fig = px.bar(

                    view, x="week_start", y="active_cell_days", color="sensor", barmode="group",

                    color_discrete_map=SENSOR_COLORS,

                    labels={"week_start": "Week beginning", "active_cell_days": "Active cell-days", "sensor": "Sensor"},

          )

          st.plotly_chart(chart_layout(fig, 390), width="stretch")

          fig2 = px.line(

                    view, x="week_start", y="weekly_share_pct", color="sensor",

                    markers=True, color_discrete_map=SENSOR_COLORS,

                    labels={"week_start": "Week beginning", "weekly_share_pct": "Within-class weekly share (%)", "sensor": "Sensor"},

          )

          st.plotly_chart(chart_layout(fig2, 330), width="stretch")

          with st.expander("View confidence-class records"):

                    st.dataframe(view.sort_values(["week_start", "sensor"]), width="stretch", hide_index=True)

          st.markdown('<div class="notice">MODIS numeric confidence thresholds and VIIRS categorical confidence labels are sensor-specific. Low, Nominal and High are shown for exploration, not as equivalent probabilities or accuracy levels. A cell-day may occur in more than one class if multiple detections with different confidence values occur in that cell-day.</div>', unsafe_allow_html=True)

# ---------------------------------------------------------------------

# Sensitivity Analysis

# ---------------------------------------------------------------------

elif page == "Sensitivity Analysis":

          section_header("05 / ROBUSTNESS TESTS", "Sensitivity Analysis", "See how spatial and temporal analytical choices change the measured overlap.")

          grid, grid_err = try_load("grid_sensitivity_summary.csv")

          origin, origin_err = try_load("grid_origin_sensitivity.csv")

          temporal, temporal_err = try_load("temporal_tolerance_summary.csv")

          high, high_err = try_load("high_confidence_cross_sensor_summary.csv")

          if grid is None:

                    show_missing("grid_sensitivity_summary.csv")

          agreement, _ = try_load("agreement_metrics.csv")

          if agreement is not None and "jaccard_overlap_pct" in agreement.columns:

                    grid = grid.merge(agreement[["resolution_km", "jaccard_overlap_pct"]], on="resolution_km", how="left")

          else:

                    union = grid["modis_cell_days"] + grid["viirs_cell_days"] - grid["co_detected_cell_days"]

                    grid["jaccard_overlap_pct"] = grid["co_detected_cell_days"].div(union.where(union > 0)).mul(100)

          st.markdown("#### A · Grid resolution sensitivity")

          fig = px.line(

                    grid, x="resolution_km", y="jaccard_overlap_pct", markers=True,

                    color_discrete_sequence=[COLORS["cyan"]],

                    labels={"resolution_km": "Grid resolution (km)", "jaccard_overlap_pct": "Jaccard overlap (%)"},

          )

          st.plotly_chart(chart_layout(fig, 300, legend=False), width="stretch")

          st.dataframe(grid, width="stretch", hide_index=True)

          st.caption("Larger grid cells make spatial coincidence less restrictive. Higher overlap at a coarser resolution does not establish better sensor accuracy.")

          if origin is not None:

                    st.markdown("#### B · Grid origin sensitivity")

                    fig2 = px.bar(

                              origin, x="grid_origin", y="jaccard_overlap_pct",

                              color="grid_origin", color_discrete_sequence=[COLORS["blue"], COLORS["cyan"], COLORS["purple"]],

                              labels={"grid_origin": "Grid origin", "jaccard_overlap_pct": "Jaccard overlap (%)"},

                              hover_data=["origin_x_m", "origin_y_m", "co_detected_cell_days"],

                    )

                    st.plotly_chart(chart_layout(fig2, 300, legend=False), width="stretch")

                    st.dataframe(origin, width="stretch", hide_index=True)

          else:

                    st.warning("Grid-origin results are unavailable: grid_origin_sensitivity.csv was not found.")

          if temporal is not None:

                    st.markdown("#### C · Temporal tolerance")

                    tview = temporal.copy()

                    if "dataset" in tview.columns:

                              fig3 = px.line(

                                        tview, x="tolerance_days", y="modis_match_rate_pct",

                                        color="dataset", markers=True,

                                        labels={"tolerance_days": "Date tolerance (days)", "modis_match_rate_pct": "MODIS matched cell-days (%)", "dataset": "Dataset"},

                              )

                              st.plotly_chart(chart_layout(fig3, 330), width="stretch")

                              fig4 = px.line(

                                        tview, x="tolerance_days", y="viirs_match_rate_pct",

                                        color="dataset", markers=True,

                                        labels={"tolerance_days": "Date tolerance (days)", "viirs_match_rate_pct": "VIIRS matched cell-days (%)", "dataset": "Dataset"},

                              )

                              st.plotly_chart(chart_layout(fig4, 330), width="stretch")

                    st.dataframe(tview, width="stretch", hide_index=True)

                    st.caption("Tolerance matching is a relaxed cell-and-date matching rule. It does not prove one-to-one physical fire-event correspondence.")

          else:

                    st.warning("Temporal tolerance results are unavailable.")

          if high is not None:

                    st.markdown("#### D · Directional high-confidence to any-confidence matching")

                    hview = high[high["resolution_km"] == 2].copy()

                    fig5 = px.bar(

                              hview, x="direction", y="matched_high_cell_days_pct",

                              color="direction", color_discrete_sequence=[COLORS["blue"], COLORS["orange"]],

                              labels={"direction": "Matching direction", "matched_high_cell_days_pct": "Matched high-confidence cell-days (%)"},

                              hover_data=["high_sensor_cell_days", "matched_high_cell_days", "unmatched_high_cell_days"],

                    )

                    st.plotly_chart(chart_layout(fig5, 320, legend=False), width="stretch")

                    st.dataframe(hview, width="stretch", hide_index=True)

                    st.caption("These are directional matching rates, not detection probabilities, accuracy estimates or symmetric agreement scores.")

          else:

                    st.warning("High-confidence cross-sensor results are unavailable.")

# ---------------------------------------------------------------------

# Methodology

# ---------------------------------------------------------------------

elif page == "Methodology":

          section_header("06 / SCIENTIFIC FRAMEWORK", "Methodology & responsible interpretation", "The processing and comparison rules behind the dashboard.")

          st.markdown("### Research question")

          st.write("How does the temporal and spatial picture of active-fire detections change when the same region is observed by MODIS and VIIRS, and how can users explore those differences without confusing sensor detections with actual fire events?")

          st.markdown("### Study configuration")

          cols = st.columns(4)

          cols[0].metric("Study region", "Punjab + Haryana")

          cols[1].metric("Observation period", "61 days")

          cols[2].metric("Primary grid", "2 km")

          cols[3].metric("Projection", "EPSG:32643")

          st.markdown("### Processing pipeline")

          steps = [

                    ("01", "FIRMS source data", "Historical MODIS Aqua Collection 6.1 and VIIRS NOAA-20 Collection 2 active-fire records."),

                    ("02", "Platform and type filtering", "Select the target platforms and Type 0 presumed vegetation-fire detections."),

                    ("03", "Regional clipping", "Restrict detections to Punjab and Haryana administrative boundaries."),

                    ("04", "Coordinate transformation", "Transform geographic coordinates to UTM Zone 43N (EPSG:32643)."),

                    ("05", "Common spatial grid", "Assign detections to a shared grid at 1 km, 2 km or 5 km resolution."),

                    ("06", "Cell-day comparison", "Compare state, UTC date, grid X and grid Y; classify co-detected, MODIS-only and VIIRS-only."),

                    ("07", "Temporal aggregation", "Summarize cell-day activity into weekly state and sensor records."),

          ]

          for num, title, detail in steps:

                    st.markdown(

                              f'<div class="panel"><span style="color:{COLORS["cyan"]};font-weight:700">{num}</span> &nbsp; <span class="panel-title">{title}</span><div class="panel-copy">{detail}</div></div>',

                              unsafe_allow_html=True,

                    )

          left, right = st.columns(2)

          with left:

                    st.markdown("### MODIS Aqua")

                    st.write("NASA MODIS Collection 6.1 · nominal spatial resolution approximately 1 km · numeric confidence field.")

                    st.markdown("### VIIRS NOAA-20")

                    st.write("VIIRS 375 m active-fire product · categorical confidence values: Low, Nominal and High.")

          with right:

                    st.markdown("### Cell-day definition")

                    st.write("One spatial grid cell with at least one qualifying detection on a particular UTC acquisition date.")

                    st.markdown("### Jaccard overlap")

                    st.latex(r"J(A,B)=\frac{|A\cap B|}{|A\cup B|}\times100")

                    st.write("A and B are the MODIS and VIIRS cell-day sets under the selected grid and date-matching rule.")

          st.markdown("### Confidence interpretation")

          st.warning("MODIS numeric confidence thresholds and VIIRS categorical confidence labels are sensor-specific. They are not equivalent probability scales. Confidence-class cell-days can overlap when multiple detections with different confidence values occur in the same cell-day.")

          st.markdown("### Scientific limitations")

          st.markdown("""

          - Active-fire detections are not confirmed counts of physical fire events.

          - Type 0 indicates presumed vegetation-fire detections; it does not prove agricultural residue burning.

          - Different spatial resolutions, overpass timing and detection algorithms affect recorded counts.

          - A cell-day without a detection does not establish the absence of fire.

          - Spatial or temporal coincidence does not establish that two detections represent the same physical fire.

          - The study covers one region and one two-month period; findings should not be generalized to all locations or seasons.

          - The analysis does not forecast future burning activity or independently verify agricultural burning.

          """)

          st.markdown('<div class="notice">Fire Parallax is an exploratory satellite-observation comparison platform. It makes differences between sensor products visible and measurable; it does not reconstruct physical fire events or rank sensor accuracy.</div>', unsafe_allow_html=True)

# ---------------------------------------------------------------------

# Footer

# ---------------------------------------------------------------------

st.markdown("---")

st.caption("FIRE PARALLAX     ·     ROCHE DOMINION     ·     SPACE APPS PROJECT     ·     Data: NASA FIRMS active-fire products")
