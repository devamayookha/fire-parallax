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

          "bg": "#050B16",

          "panel": "#111E30",

          "panel2": "#16263B",

          "border": "#263B54",

          "text": "#EAF2FF",

          "muted": "#91A6C0",

          "blue": "#4C9AFF",

          "cyan": "#38D9E6",

          "orange": "#FF9A50",

          "red": "#FF6666",

          "green": "#52D69A",

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

          @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&family=JetBrains+Mono:wght@400;500;600&family=Space+Grotesk:wght@500;600;700&display=swap');

          :root {{

               --fp-bg: {COLORS["bg"]};

               --fp-panel: {COLORS["panel"]};

               --fp-border: {COLORS["border"]};

               --fp-text: {COLORS["text"]};

               --fp-muted: {COLORS["muted"]};

          }}

          html, body, [class*="css"] {{

               font-family: 'Inter', sans-serif;

          }}

          .stApp {{

               background:

                    radial-gradient(ellipse at 78% 0%, rgba(43,91,153,.17), transparent 34%),

                    linear-gradient(180deg, #050B16 0%, #0B1424 100%);

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

          [data-testid="stMetricValue"], .metric-value {{
               font-family: 'JetBrains Mono', monospace !important;
          }}
          [data-testid="stSidebar"] [data-testid="stRadio"] label:has(input:checked) {{
               background: rgba(56,217,230,.12);
               border-left: 2px solid #38D9E6;
          }}
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

          
          .status-bar {{
               display:flex; flex-wrap:wrap; align-items:center; gap:.4rem 1.4rem;
               font-family:'JetBrains Mono', monospace; font-size:.68rem; letter-spacing:.12em;
               text-transform:uppercase; color:#7F95B1;
               padding:.5rem .9rem; margin:-.4rem 0 1.1rem 0;
               border:1px solid #1E3149; border-radius:10px;
               background:linear-gradient(90deg, rgba(56,217,230,.07), rgba(11,20,36,.6) 40%);
          }}
          .status-bar .status-main {{ color:#38D9E6; font-weight:600; }}
          .status-bar .status-right {{ margin-left:auto; color:#52D69A; }}
          .status-dot {{
               width:8px; height:8px; border-radius:50%; background:#52D69A;
               box-shadow:0 0 8px #52D69A; display:inline-block; margin-right:.5rem;
               animation:fp-pulse 2.4s ease-in-out infinite;
          }}
          @keyframes fp-pulse {{ 0%,100% {{ opacity:1; }} 50% {{ opacity:.35; }} }}
          .orbit-logo {{
               position:relative; width:46px; height:46px; border-radius:50%; margin-bottom:.2rem;
               background:radial-gradient(circle at 35% 35%, #2F7FC0 0%, #123A63 55%, #07162A 100%);
               box-shadow:0 0 18px rgba(56,217,230,.35), inset 0 0 10px rgba(0,0,0,.5);
          }}
          .orbit-logo::before {{
               content:""; position:absolute; left:-12px; top:15px; width:70px; height:18px;
               border:1.5px solid rgba(56,217,230,.75); border-radius:50%; transform:rotate(-24deg);
          }}
          .orbit-logo span {{
               position:absolute; width:7px; height:7px; border-radius:50%; background:#FF9A50;
               box-shadow:0 0 8px #FF9A50; right:-9px; top:8px;
          }}
          .metric-card {{
               position:relative; overflow:hidden;
               background:linear-gradient(160deg, #15263D 0%, #0E1A2D 100%);
               border:1px solid #223653; transition:border-color .2s, transform .2s;
          }}
          .metric-card::before {{
               content:""; position:absolute; left:0; top:0; right:0; height:2px;
               background:linear-gradient(90deg, #38D9E6, #4C9AFF 55%, transparent);
          }}
          .metric-card:hover {{ border-color:#38D9E6; transform:translateY(-2px); }}
          .metric-label {{ font-family:'JetBrains Mono', monospace; font-size:.66rem; letter-spacing:.13em; color:#7F95B1; }}
          .metric-value {{ font-size:1.75rem; letter-spacing:-.02em; }}
          .panel {{ position:relative; border-color:#223653; }}
          .panel::before {{
               content:""; position:absolute; left:14px; top:-1px; width:34px; height:2px; background:#38D9E6;
          }}
          .section-kicker {{ font-family:'JetBrains Mono', monospace; letter-spacing:.16em; }}
          [data-testid="stPlotlyChart"] {{
               border:1px solid #1E3149; border-radius:14px; padding:.35rem;
               background:rgba(9,17,31,.62);
          }}
          [data-baseweb="select"] > div {{
               background:#0F1B2E !important; border-color:#263B54 !important; border-radius:9px !important;
          }}
          [data-baseweb="select"] > div:hover {{ border-color:#38D9E6 !important; }}
          [data-testid="stSidebar"] [data-testid="stRadio"] label {{ letter-spacing:.02em; }}
          ::-webkit-scrollbar {{ width:9px; height:9px; }}
          ::-webkit-scrollbar-thumb {{ background:#26405F; border-radius:6px; }}
          ::-webkit-scrollbar-track {{ background:#0A1322; }}
          .fp-footer {{
               font-family:'JetBrains Mono', monospace; font-size:.68rem; letter-spacing:.14em;
               text-transform:uppercase; color:#7F95B1; text-align:center; padding:.4rem 0 0 0;
          }}
          .fp-footer b {{ color:#38D9E6; font-weight:600; }}
                    /* fp-header-fix: keep content below Streamlit's fixed top header */
          .block-container, [data-testid="stMainBlockContainer"] {{
               padding-top: 4.6rem !important;
          }}
          .status-bar {{ margin: 0 0 1.1rem 0 !important; }}
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
                    hoverlabel=dict(bgcolor="#111E30", bordercolor="#38D9E6", font=dict(family="JetBrains Mono, monospace", size=12, color="#EAF2FF")),

                    paper_bgcolor="rgba(0,0,0,0)",

                    plot_bgcolor="rgba(0,0,0,0)",

                    font=dict(family="Inter, sans-serif", color="#D7E1F0"),

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

                         <div class="orbit-logo"><span></span></div>

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
                    format_func=lambda p: {"Mission Overview": "01", "Burning Activity Calendar": "02", "Spatial Explorer": "03", "Sensor Comparison": "04", "Confidence Explorer": "05", "Sensitivity Analysis": "06", "Methodology": "07"}[p] + " · " + p,

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

st.markdown(
    """<div class="status-bar"><span><span class="status-dot"></span><span class="status-main">MISSION CONTROL</span></span><span>MODIS AQUA × VIIRS NOAA-20</span><span>PUNJAB · HARYANA</span><span>01 OCT – 30 NOV 2022 · UTC</span><span class="status-right">2 KM REFERENCE GRID · EPSG:32643</span></div>""",
    unsafe_allow_html=True,
)
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

          section_header("01 / TEMPORAL ANALYSIS", "Burning Activity Calendar", "Tracking the temporal patterns of satellite active-fire observations (UTC dates).")

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

                    st.markdown('<div class="section-kicker">WEEKLY ACTIVITY HEATMAP · ALL STATES AND SENSORS</div>', unsafe_allow_html=True)
                    _hm = data.assign(row=data["state"] + " · " + data["sensor"]).pivot_table(index="row", columns="week_start", values="weekly_share_pct", aggfunc="sum")
                    _fig_hm = go.Figure(go.Heatmap(z=_hm.values, x=_hm.columns, y=_hm.index, colorscale=[[0, "#0B1424"], [1, "#38D9E6"]], hovertemplate="%{y}<br>Week beginning %{x|%d %b %Y}<br>Share of sensor activity: %{z:.1f}%<extra></extra>", colorbar=dict(title="Weekly share (%)")))
                    st.plotly_chart(chart_layout(_fig_hm, 300, legend=False), width="stretch")
                    st.caption("Each row is one state and sensor. Colour shows the share of that row's own activity in each week, so rows with very different totals can be compared by timing. Partial first and last weeks are shown as recorded.")
                    with st.expander("Inspect weekly records"):

                              st.dataframe(filtered, width="stretch", hide_index=True)

          st.markdown('<div class="science-note">Active cell-days are spatial grid cells with at least one qualifying detection on a UTC date. They are not counts of unique physical fires. Weekly shares are calculated within each state and sensor.</div>', unsafe_allow_html=True)
# ---------------------------------------------------------------------
# Spatial Explorer
# ---------------------------------------------------------------------
elif page == "Spatial Explorer":
    section_header(
        "02 / SPATIAL INTELLIGENCE",
        "Spatial Intelligence",
        "Explore the geographic distribution of shared-grid observations.",
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
    # Grid coordinates are cell indices in EPSG:32643. Cell centres are converted to WGS84 for display only.
    transformer = Transformer.from_crs("EPSG:32643", "EPSG:4326", always_xy=True)
    spatial["x_m"] = (spatial["grid_x"] + 0.5) * 2000
    spatial["y_m"] = (spatial["grid_y"] + 0.5) * 2000
    spatial["longitude"], spatial["latitude"] = transformer.transform(
        spatial["x_m"].to_numpy(), spatial["y_m"].to_numpy()
    )

    st.markdown('<div class="section-kicker">OBSERVATION CONTROLS</div>', unsafe_allow_html=True)
    states = sorted(spatial["state"].dropna().unique())
    c1, c2, c3, c4 = st.columns([0.9, 1.8, 1.1, 1.1], gap="medium")
    with c1:
        state = st.selectbox("Study state", states, key="spatial_state")
    with c2:
        selected = st.multiselect(
            "Cell-day categories",
            list(CATEGORY_LABELS.keys()),
            default=list(CATEGORY_LABELS.keys()),
            format_func=lambda x: CATEGORY_LABELS[x],
            key="spatial_categories",
        )
    with c3:
        basemap_name = st.selectbox("Basemap", ["Dark mission", "Satellite imagery", "Light"], key="spatial_basemap")
    with c4:
        display = st.radio("Display", ["Cell markers", "Density heat"], key="spatial_display")

    BASEMAPS = {
        "Dark mission": {"style": "carto-darkmatter", "layers": []},
        "Light": {"style": "carto-positron", "layers": []},
        "Satellite imagery": {
            "style": "white-bg",
            "layers": [
                {
                    "below": "traces",
                    "sourcetype": "raster",
                    "sourceattribution": "Imagery © Esri, Maxar, Earthstar Geographics",
                    "source": ["https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}"],
                }
            ],
        },
    }
    basemap = BASEMAPS[basemap_name]

    state_view = spatial[spatial["state"] == state].copy()
    view = state_view[state_view["category"].isin(selected)].copy()
    # Headline totals use the whole selected state, independent of the category toggles.
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
        centres = {"Haryana": {"lat": 29.2, "lon": 76.1}, "Punjab": {"lat": 31.0, "lon": 75.3}}
        center = centres.get(state, {"lat": 30.2, "lon": 75.7})
        zoom = 6.3
        fig = go.Figure()
        if display == "Cell markers":
            cmax = max(float(view["active_cell_days"].max()), 1.0)
            for cat in ["modis_only", "viirs_only", "co_detected"]:  # co-detected drawn last, on top
                if cat not in selected:
                    continue
                sub = view[view["category"] == cat]
                if sub.empty:
                    continue
                size = 6 + 12 * (sub["active_cell_days"] / cmax) ** 0.5
                color = CATEGORY_COLORS[cat]
                fig.add_trace(go.Scattermap(  # soft glow under each marker
                    lat=sub["latitude"], lon=sub["longitude"], mode="markers",
                    marker=dict(size=size * 2.3, color=color, opacity=0.14),
                    hoverinfo="skip", showlegend=False,
                ))
                fig.add_trace(go.Scattermap(
                    lat=sub["latitude"], lon=sub["longitude"], mode="markers",
                    name=CATEGORY_LABELS[cat],
                    marker=dict(size=size, color=color, opacity=0.88),
                    customdata=sub[["active_cell_days", "grid_x", "grid_y", "state"]].to_numpy(),
                    hovertemplate=(
                        "<b>%{fullData.name}</b><br>Active cell-days: %{customdata[0]:,}"
                        "<br>Grid cell: (%{customdata[1]}, %{customdata[2]})<br>%{customdata[3]}"
                        "<br>%{lat:.4f}°N, %{lon:.4f}°E<extra></extra>"
                    ),
                ))
        else:
            fig.add_trace(go.Densitymap(
                lat=view["latitude"], lon=view["longitude"], z=view["active_cell_days"], radius=16,
                colorscale=[[0, "rgba(56,217,230,0)"], [0.35, "rgba(56,217,230,0.55)"], [0.7, "#FFBF69"], [1, "#FF6666"]],
                colorbar=dict(title=dict(text="Cell-days", font=dict(color="#EAF2FF")), thickness=12, len=0.55,
                              tickfont=dict(color="#EAF2FF"), bgcolor="rgba(5,11,22,.6)"),
                hoverinfo="skip",
            ))
        fig.update_layout(
            map=dict(style=basemap["style"], layers=basemap["layers"], center=center, zoom=zoom),
            paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
            margin=dict(l=0, r=0, t=0, b=0), height=700,
            legend=dict(
                orientation="v", x=0.012, y=0.985, xanchor="left", yanchor="top", itemsizing="constant",
                bgcolor="rgba(5,11,22,.82)", bordercolor="rgba(56,217,230,.35)", borderwidth=1,
                font=dict(color="#EAF2FF", size=12),
            ),
            hoverlabel=dict(bgcolor="#111E30", bordercolor="#38D9E6",
                            font=dict(family="JetBrains Mono, monospace", size=12, color="#EAF2FF")),
            uirevision=f"spatial-{state}-{basemap_name}-{display}",
        )
        st.plotly_chart(fig, width="stretch", config={"displaylogo": False, "scrollZoom": True})
        if basemap_name == "Satellite imagery":
            st.caption("Satellite basemap: Imagery © Esri, Maxar, Earthstar Geographics. It needs an internet connection; if tiles do not load, switch to the Dark mission basemap.")
    st.markdown(
        '<div class="science-note"><b>HOW TO INTERPRET THIS MAP</b><br>'
        'Each marker is the centre of a 2 km reference-grid cell. Marker size grows with the number of cell-days '
        'in that cell and category over the study period (square-root scale). Colours identify the comparison '
        'category, not fire intensity. Density heat shows where selected cell-days concentrate. '
        'Markers are not individual fire locations or reconstructed fire events.</div>',
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
    section_header(
        "03 / CROSS-SENSOR ANALYSIS",
        "Sensor Comparison Lab",
        "Comparing the observation characteristics of two satellite systems.",
    )
    data, err = try_load("weekly_activity_calendar.csv")
    if data is None:
        show_missing("weekly_activity_calendar.csv")
    agreement, _ = try_load("agreement_metrics.csv")
    data["state"] = normalize_state(data["state"])
    data["week_start"] = pd.to_datetime(data["week_start"])

    totals = data.groupby("sensor").agg(
        records=("detection_count", "sum"),
        cell_days=("active_cell_days", "sum"),
    )

    def _total(sensor_name, column):
        return int(totals.loc[sensor_name, column]) if sensor_name in totals.index else None

    st.markdown('<div class="section-kicker">SENSOR PROFILES · STUDY-WIDE (PUNJAB + HARYANA)</div>', unsafe_allow_html=True)
    p1, p2 = st.columns(2, gap="medium")
    with p1:
        st.markdown(
            f'<div class="panel" style="border-top:3px solid {COLORS["blue"]}">'
            f'<span class="sensor-chip">SENSOR 01</span>'
            f'<h3 style="margin-top:.6rem">🛰️ MODIS Aqua</h3>'
            f'<div class="panel-copy">Platform: NASA Aqua · Collection 6.1<br>'
            f'Nominal resolution: approximately 1 km<br>'
            f'Confidence: numeric 0–100 (Low 0–29, Nominal 30–79, High 80–100)<br>'
            f'<b>Detection records:</b> {moneyless_num(_total("MODIS Aqua", "records"))}<br>'
            f'<b>Active cell-days (2 km):</b> {moneyless_num(_total("MODIS Aqua", "cell_days"))}</div></div>',
            unsafe_allow_html=True,
        )
    with p2:
        st.markdown(
            f'<div class="panel" style="border-top:3px solid {COLORS["orange"]}">'
            f'<span class="sensor-chip" style="color:#FFC18F;border-color:#80502F;background:rgba(255,155,92,.10)">SENSOR 02</span>'
            f'<h3 style="margin-top:.6rem">🛰️ VIIRS NOAA-20</h3>'
            f'<div class="panel-copy">Platform: NOAA-20 · Collection 2 (375 m product)<br>'
            f'Nominal resolution: 375 m<br>'
            f'Confidence: categorical (Low, Nominal, High)<br>'
            f'<b>Detection records:</b> {moneyless_num(_total("VIIRS NOAA-20", "records"))}<br>'
            f'<b>Active cell-days (2 km):</b> {moneyless_num(_total("VIIRS NOAA-20", "cell_days"))}</div></div>',
            unsafe_allow_html=True,
        )

    # Records vs cell-days (different units, shown side by side but labelled)
    compare_rows = []
    for sensor_name in ["MODIS Aqua", "VIIRS NOAA-20"]:
        if sensor_name in totals.index:
            compare_rows.append({"Measure": "Detection records", "Sensor": sensor_name, "Value": int(totals.loc[sensor_name, "records"])})
            compare_rows.append({"Measure": "Active cell-days (2 km)", "Sensor": sensor_name, "Value": int(totals.loc[sensor_name, "cell_days"])})
    st.markdown('<div class="section-kicker">RECORDS VS CELL-DAYS</div>', unsafe_allow_html=True)
    if compare_rows:
        fig_a = px.bar(
            pd.DataFrame(compare_rows), x="Measure", y="Value", color="Sensor", barmode="group",
            color_discrete_map=SENSOR_COLORS, text_auto=",.0f",
        )
        fig_a.update_traces(textposition="outside", cliponaxis=False)
        st.plotly_chart(chart_layout(fig_a, 360), width="stretch")
    st.caption("Detection records are individual FIRMS rows. Active cell-days count each grid cell once per UTC date, however many records fall in it. The two measures use different units and should not be compared with each other.")

    # Co-detection composition and overlap (2 km reference grid)
    st.markdown('<div class="section-kicker">CELL-DAY OVERLAP · 2 KM REFERENCE GRID</div>', unsafe_allow_html=True)
    row2 = None
    if agreement is not None and not agreement.empty:
        match = agreement.loc[agreement["resolution_km"] == 2]
        if not match.empty:
            row2 = match.iloc[0]
    if row2 is None:
        st.warning("Overlap metrics are unavailable: agreement_metrics.csv has no 2 km row.")
    else:
        k1, k2, k3, k4 = st.columns(4, gap="medium")
        with k1:
            metric_card("CO-DETECTED", moneyless_num(row2["co_detected_cell_days"]), "Both sensors · same cell + UTC date")
        with k2:
            metric_card("MODIS-ONLY", moneyless_num(row2["modis_only_cell_days"]), "MODIS cell-days without VIIRS")
        with k3:
            metric_card("VIIRS-ONLY", moneyless_num(row2["viirs_only_cell_days"]), "VIIRS cell-days without MODIS")
        with k4:
            metric_card("JACCARD OVERLAP", f'{float(row2["jaccard_overlap_pct"]):.2f}%', "Co-detected ÷ cell-days from either sensor")
        st.markdown("")
        comp = pd.DataFrame([
            {"Sensor": "MODIS Aqua", "Category": CATEGORY_LABELS["co_detected"], "Cell-days": int(row2["co_detected_cell_days"])},
            {"Sensor": "MODIS Aqua", "Category": CATEGORY_LABELS["modis_only"], "Cell-days": int(row2["modis_only_cell_days"])},
            {"Sensor": "VIIRS NOAA-20", "Category": CATEGORY_LABELS["co_detected"], "Cell-days": int(row2["co_detected_cell_days"])},
            {"Sensor": "VIIRS NOAA-20", "Category": CATEGORY_LABELS["viirs_only"], "Cell-days": int(row2["viirs_only_cell_days"])},
        ])
        label_colors = {CATEGORY_LABELS[key]: color for key, color in CATEGORY_COLORS.items()}
        fig_b = px.bar(
            comp, x="Sensor", y="Cell-days", color="Category", barmode="stack",
            color_discrete_map=label_colors, text_auto=",.0f",
        )
        st.plotly_chart(chart_layout(fig_b, 360), width="stretch")
        d1, d2 = st.columns(2, gap="medium")
        with d1:
            metric_card("MODIS CELL-DAYS WITH A VIIRS MATCH", f'{float(row2["modis_overlap_pct"]):.2f}%', "Directional share · denominator: MODIS cell-days")
        with d2:
            metric_card("VIIRS CELL-DAYS WITH A MODIS MATCH", f'{float(row2["viirs_overlap_pct"]):.2f}%', "Directional share · denominator: VIIRS cell-days")
        st.caption("The two directional shares use different denominators, so they are not symmetric. They are not accuracy or detection-probability estimates, and a larger count does not mean a more accurate sensor.")

    with st.expander("What is the difference between these measures?"):
        st.markdown("""
        - **Detection record:** one FIRMS thermal-detection row from a sensor.
        - **Active cell-day:** one 2 km grid cell with at least one qualifying detection on one UTC date.
        - **Co-detected cell-day:** both sensors have an active cell-day in the same cell on the same UTC date.
        - **Sensor-only cell-day:** only that sensor has an active cell-day under the same matching rule.
        """)

    # Weekly timing (existing charts, unchanged logic)
    st.markdown('<div class="section-kicker">WEEKLY TIMING BY STATE</div>', unsafe_allow_html=True)
    state = st.selectbox("Study state", sorted(data["state"].unique()), key="comparison_state")
    view = data[data["state"] == state].copy()
    summary = view.groupby("sensor", as_index=False).agg(
        active_cell_days=("active_cell_days", "sum"),
        detection_records=("detection_count", "sum"),
    )
    cols = st.columns(max(1, len(summary)))
    for i, row in summary.iterrows():
        with cols[i]:
            st.metric(f'{row["sensor"]} · active cell-days', moneyless_num(row["active_cell_days"]))
            st.caption(f'{moneyless_num(row["detection_records"])} detection records')
    fig = px.bar(
        view, x="week_start", y="active_cell_days", color="sensor", barmode="group",
        color_discrete_map=SENSOR_COLORS,
        labels={"week_start": "Week beginning (UTC)", "active_cell_days": "Active cell-days", "sensor": "Sensor"},
        hover_data={"detection_count": True, "coverage_days": True},
    )
    st.plotly_chart(chart_layout(fig, 410), width="stretch")
    fig2 = px.line(
        view, x="week_start", y="weekly_share_pct", color="sensor",
        markers=True, color_discrete_map=SENSOR_COLORS,
        labels={"week_start": "Week beginning (UTC)", "weekly_share_pct": "Within-sensor weekly share (%)", "sensor": "Sensor"},
    )
    st.plotly_chart(chart_layout(fig2, 360), width="stretch")
    with st.expander("View weekly comparison table"):
        st.dataframe(view.sort_values(["week_start", "sensor"]), width="stretch", hide_index=True)
    st.caption("The first calendar week (beginning 26 Sep) covers only 1–2 Oct and the last (28 Nov) covers 28–30 Nov, so partial weeks should not be compared directly with full seven-day weeks.")
    st.markdown('<div class="notice">Weekly share describes the timing of activity within each sensor and state. It does not make MODIS and VIIRS detection counts directly comparable and is not a sensor-accuracy measure.</div>', unsafe_allow_html=True)
# ---------------------------------------------------------------------
# Confidence Explorer
# ---------------------------------------------------------------------
elif page == "Confidence Explorer":
    section_header(
        "04 / CONFIDENCE ANALYSIS",
        "Confidence Intelligence",
        "Exploring how confidence filtering changes sensor agreement.",
    )
    data, err = try_load("confidence_class_calendar.csv")
    if data is None:
        show_missing("confidence_class_calendar.csv")
    class_summary, _ = try_load("confidence_class_summary.csv")
    cross, _ = try_load("high_confidence_cross_sensor_summary.csv")
    high_grid, _ = try_load("high_confidence_grid_summary.csv")
    data["state"] = normalize_state(data["state"])
    data["week_start"] = pd.to_datetime(data["week_start"])
    class_order = ["Low", "Nominal", "High"]

    state = st.selectbox("Study state", sorted(data["state"].unique()), key="confidence_state")

    # 1. Distribution of detection records by native confidence class
    st.markdown('<div class="section-kicker">01 / CONFIDENCE CLASS DISTRIBUTION</div>', unsafe_allow_html=True)
    if class_summary is None:
        st.warning("Confidence distribution is unavailable: confidence_class_summary.csv was not found.")
    else:
        cs = class_summary.copy()
        cs["state"] = normalize_state(cs["state"])
        cs = cs[cs["state"] == state]
        if cs.empty:
            st.warning("No confidence-class records for the selected state.")
        else:
            fig_d = px.bar(
                cs, x="confidence_class", y="total_detections", color="sensor", barmode="group",
                category_orders={"confidence_class": class_order},
                color_discrete_map=SENSOR_COLORS, text_auto=",.0f",
                labels={"confidence_class": "Native confidence class", "total_detections": "Detection records", "sensor": "Sensor"},
            )
            fig_d.update_traces(textposition="outside", cliponaxis=False)
            st.plotly_chart(chart_layout(fig_d, 380), width="stretch")
            st.caption("MODIS classes come from numeric confidence (Low 0–29, Nominal 30–79, High 80–100). VIIRS classes come from its native l / n / h categories. The class names look alike but the two systems are not equivalent.")

    # 2. High-confidence cross-sensor comparison
    st.markdown('<div class="section-kicker">02 / HIGH-CONFIDENCE CROSS-SENSOR COMPARISON · STUDY-WIDE (BOTH STATES)</div>', unsafe_allow_html=True)
    if cross is None or high_grid is None:
        st.warning("High-confidence comparison is unavailable: a required CSV was not found.")
    else:
        resolution = st.selectbox("Grid resolution (km)", sorted(cross["resolution_km"].unique()), index=1, key="confidence_resolution")
        cross_view = cross[cross["resolution_km"] == resolution]
        grid_view = high_grid[high_grid["resolution_km"] == resolution]
        modis_dir = cross_view[cross_view["direction"] == "MODIS High to any VIIRS"]
        viirs_dir = cross_view[cross_view["direction"] == "VIIRS High to any MODIS"]
        c1, c2, c3 = st.columns(3, gap="medium")
        with c1:
            if modis_dir.empty:
                metric_card("MODIS HIGH → ANY VIIRS", "—", "No record for this resolution")
            else:
                r = modis_dir.iloc[0]
                metric_card("MODIS HIGH → ANY VIIRS", f'{float(r["matched_high_cell_days_pct"]):.2f}%',
                            f'{moneyless_num(r["matched_high_cell_days"])} of {moneyless_num(r["high_sensor_cell_days"])} MODIS high-confidence cell-days')
        with c2:
            if viirs_dir.empty:
                metric_card("VIIRS HIGH → ANY MODIS", "—", "No record for this resolution")
            else:
                r = viirs_dir.iloc[0]
                metric_card("VIIRS HIGH → ANY MODIS", f'{float(r["matched_high_cell_days_pct"]):.2f}%',
                            f'{moneyless_num(r["matched_high_cell_days"])} of {moneyless_num(r["high_sensor_cell_days"])} VIIRS high-confidence cell-days')
        with c3:
            if grid_view.empty:
                metric_card("HIGH VS HIGH", "—", "No record for this resolution")
            else:
                r = grid_view.iloc[0]
                metric_card("HIGH VS HIGH · JACCARD", f'{float(r["jaccard_overlap_pct"]):.2f}%',
                            f'{moneyless_num(r["co_detected_cell_days"])} co-detected high-confidence cell-days')
        if not cross_view.empty:
            fig_c = px.bar(
                cross_view, x="direction", y="matched_high_cell_days_pct", color="direction",
                color_discrete_sequence=[COLORS["blue"], COLORS["orange"]],
                labels={"direction": "Matching direction", "matched_high_cell_days_pct": "Matched high-confidence cell-days (%)"},
                hover_data=["high_sensor_cell_days", "matched_high_cell_days", "unmatched_high_cell_days"],
            )
            fig_c.update_traces(texttemplate="%{y:.2f}%", textposition="outside", cliponaxis=False)
            st.plotly_chart(chart_layout(fig_c, 330, legend=False), width="stretch")
        st.caption("High → any compares one sensor's high-confidence cell-days with all cell-days of the other sensor. High vs high compares the two high-confidence subsets only. These are different metrics with different denominators. None is an accuracy or detection-probability estimate.")

    # 3. Weekly timing by confidence class (existing charts, unchanged logic)
    st.markdown('<div class="section-kicker">03 / WEEKLY TIMING BY CONFIDENCE CLASS</div>', unsafe_allow_html=True)
    conf = st.selectbox("Confidence class", class_order, key="confidence_level")
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
        labels={"week_start": "Week beginning (UTC)", "active_cell_days": "Active cell-days", "sensor": "Sensor"},
    )
    st.plotly_chart(chart_layout(fig, 390), width="stretch")
    fig2 = px.line(
        view, x="week_start", y="weekly_share_pct", color="sensor",
        markers=True, color_discrete_map=SENSOR_COLORS,
        labels={"week_start": "Week beginning (UTC)", "weekly_share_pct": "Within-class weekly share (%)", "sensor": "Sensor"},
    )
    st.plotly_chart(chart_layout(fig2, 330), width="stretch")
    with st.expander("View confidence-class records"):
        st.dataframe(view.sort_values(["week_start", "sensor"]), width="stretch", hide_index=True)
    st.markdown('<div class="notice">MODIS numeric confidence thresholds and VIIRS categorical confidence labels are sensor-specific. Low, Nominal and High are shown for exploration, not as equivalent probabilities. Confidence-class cell-days can overlap when one cell-day has detections of different classes, so they must not be summed as unique activity.</div>', unsafe_allow_html=True)
# ---------------------------------------------------------------------
# Sensitivity Analysis
# ---------------------------------------------------------------------
elif page == "Sensitivity Analysis":

          section_header("05 / ROBUSTNESS TESTS", "Sensitivity & Robustness Lab", "Testing how analytical choices change measured sensor agreement.")

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

          section_header("06 / SCIENTIFIC FRAMEWORK", "Methodology & Responsible Interpretation", "The processing and comparison rules behind the dashboard.")

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

st.markdown(
    """<div class="fp-footer"><b>FIRE PARALLAX</b> · ROCHE DOMINION · NASA SPACE APPS CHALLENGE 2026<br>OBSERVE EARTH. COMPARE SENSORS. UNDERSTAND THE DIFFERENCE.<br>DATA: NASA FIRMS ACTIVE-FIRE PRODUCTS · INDEPENDENT PROJECT, NOT AN OFFICIAL NASA PRODUCT</div>""",
    unsafe_allow_html=True,
)
