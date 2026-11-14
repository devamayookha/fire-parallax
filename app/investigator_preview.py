import streamlit as st

from disagreement import render_disagreement_investigator

st.set_page_config(
    page_title="Fire Parallax | Disagreement Investigator",
    page_icon="F",
    layout="wide"
)

render_disagreement_investigator()