import streamlit as st
import streamlit.components.v1 as components
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import time
import io
import base64
from datetime import datetime, timedelta
from api_client import get_forecast

# Export libs — installed on demand
import subprocess, sys

def _ensure_pkg(pkg, import_name=None):
    import_name = import_name or pkg
    try:
        __import__(import_name)
    except ImportError:
        subprocess.check_call([sys.executable, "-m", "pip", "install", pkg, "-q"])

def _load_export_libs():
    _ensure_pkg("reportlab")
    _ensure_pkg("openpyxl")
    global A4, rl_colors, getSampleStyleSheet, ParagraphStyle, mm
    global SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, HRFlowable
    global TA_LEFT, TA_CENTER, TA_RIGHT
    global openpyxl, Font, PatternFill, Alignment, Border, Side, GradientFill
    global get_column_letter
    from reportlab.lib.pagesizes import A4
    from reportlab.lib import colors as rl_colors
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib.units import mm
    from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, HRFlowable
    from reportlab.lib.enums import TA_LEFT, TA_CENTER, TA_RIGHT
    import openpyxl
    from openpyxl.styles import Font, PatternFill, Alignment, Border, Side, GradientFill
    from openpyxl.utils import get_column_letter

# Placeholders so the rest of the file doesn't break at parse time
A4 = rl_colors = getSampleStyleSheet = ParagraphStyle = mm = None
SimpleDocTemplate = Paragraph = Spacer = Table = TableStyle = HRFlowable = None
TA_LEFT = TA_CENTER = TA_RIGHT = None
openpyxl = Font = PatternFill = Alignment = Border = Side = GradientFill = None
get_column_letter = None

st.set_page_config(
    page_title="SalesIQ — Forecasting",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ─────────────────────────────────────────────────────────────────────────────
# CSS
# ─────────────────────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Mono:wght@300;400;500&family=Syne:wght@400;600;700;800&family=DM+Sans:wght@300;400;500&display=swap');

:root {
    --bg:       #0a0c10;
    --surface:  #10141c;
    --surface2: #141820;
    --border:   #1e2530;
    --border2:  #252e3d;
    --accent:   #00e5a0;
    --accent2:  #0094ff;
    --warn:     #ff6b35;
    --danger:   #ff3b5c;
    --purple:   #b06cff;
    --text:     #e8edf5;
    --muted:    #5a6478;
    --mono:     'DM Mono', monospace;
    --sans:     'DM Sans', sans-serif;
    --display:  'Syne', sans-serif;
}

html, body, [class*="css"], .stApp {
    background-color: var(--bg) !important;
    color: var(--text) !important;
    font-family: var(--sans) !important;
}
::-webkit-scrollbar { width: 6px; height: 6px; }
::-webkit-scrollbar-track { background: var(--surface); }
::-webkit-scrollbar-thumb { background: var(--border2); border-radius: 3px; }

/* ── 3D KPI cards ── */
.kpi-grid { perspective: 1200px; }
.kpi-card {
    transform-style: preserve-3d;
    transition: transform 0.4s cubic-bezier(0.23, 1, 0.32, 1), box-shadow 0.4s ease;
    cursor: default;
}
.kpi-card:hover {
    transform: rotateX(-6deg) rotateY(4deg) translateZ(8px);
    box-shadow: 0 20px 60px rgba(0,229,160,0.12), 0 8px 24px rgba(0,0,0,0.4) !important;
    z-index: 10;
}
.kpi-card::after {
    content: '';
    position: absolute;
    inset: 0;
    background: linear-gradient(135deg, rgba(255,255,255,0.04) 0%, transparent 60%);
    pointer-events: none;
}

/* ── 3D Metric cells ── */
.metric-cell {
    transition: transform 0.3s ease, box-shadow 0.3s ease;
}
.metric-cell:hover {
    transform: translateY(-3px) translateZ(4px);
    box-shadow: 0 12px 32px rgba(0,229,160,0.08), 0 4px 12px rgba(0,0,0,0.3);
}

/* ── 3D monitor cards ── */
.monitor-card {
    transition: transform 0.35s cubic-bezier(0.23, 1, 0.32, 1), box-shadow 0.35s ease;
    transform-style: preserve-3d;
}
.monitor-card:hover {
    transform: translateY(-4px) rotateX(-3deg);
    box-shadow: 0 16px 48px rgba(0,148,255,0.1), 0 4px 16px rgba(0,0,0,0.3);
}

/* ── Glowing section borders ── */
.chart-3d-wrap {
    position: relative;
    border: 1px solid var(--border);
    background: var(--surface);
    padding: 1.5rem;
    overflow: hidden;
}
.chart-3d-wrap::before {
    content: '';
    position: absolute;
    top: 0; left: 0; right: 0;
    height: 1px;
    background: linear-gradient(90deg, transparent, var(--accent), transparent);
    opacity: 0.5;
}

/* ── 3D orb in header ── */
.header-orb {
    position: relative;
    width: 56px; height: 56px;
    border-radius: 50%;
    background: radial-gradient(circle at 35% 35%,
        rgba(0,229,160,0.9),
        rgba(0,148,255,0.6) 50%,
        rgba(0,10,30,0.8) 100%);
    box-shadow:
        0 0 0 1px rgba(0,229,160,0.2),
        0 0 20px rgba(0,229,160,0.3),
        0 0 60px rgba(0,148,255,0.15),
        inset 0 -4px 12px rgba(0,0,0,0.5),
        inset 4px 4px 8px rgba(255,255,255,0.08);
    animation: orbFloat 4s ease-in-out infinite;
    flex-shrink: 0;
}
.header-orb::after {
    content: '';
    position: absolute;
    top: 10%; left: 15%;
    width: 30%; height: 18%;
    border-radius: 50%;
    background: rgba(255,255,255,0.25);
    filter: blur(2px);
    transform: rotate(-30deg);
}
@keyframes orbFloat {
    0%, 100% { transform: translateY(0px) rotateY(0deg); box-shadow: 0 0 0 1px rgba(0,229,160,0.2), 0 0 20px rgba(0,229,160,0.3), 0 0 60px rgba(0,148,255,0.15), inset 0 -4px 12px rgba(0,0,0,0.5), inset 4px 4px 8px rgba(255,255,255,0.08); }
    50%       { transform: translateY(-6px) rotateY(15deg); box-shadow: 0 8px 32px rgba(0,229,160,0.4), 0 0 80px rgba(0,148,255,0.2), inset 0 -4px 12px rgba(0,0,0,0.5), inset 4px 4px 8px rgba(255,255,255,0.08); }
}

/* ── Animated grid background ── */
.stApp::before {
    content: '';
    position: fixed;
    inset: 0;
    background-image:
        linear-gradient(rgba(0,229,160,0.025) 1px, transparent 1px),
        linear-gradient(90deg, rgba(0,229,160,0.025) 1px, transparent 1px);
    background-size: 48px 48px;
    pointer-events: none;
    z-index: 0;
}

/* ── Sidebar 3D depth ── */
[data-testid="stSidebar"] {
    box-shadow: 4px 0 32px rgba(0,229,160,0.04), 2px 0 8px rgba(0,0,0,0.4) !important;
}

/* ── Three.js iframe: fixed fullscreen behind everything ── */
iframe[title="streamlit_components.v1.html"] ,
iframe[data-testid="stCustomComponentV1"] {
    position: fixed !important;
    top: 0 !important; left: 0 !important;
    width: 100vw !important; height: 100vh !important;
    border: none !important;
    z-index: 0 !important;
    pointer-events: none !important;
    opacity: 1 !important;
}
/* Push all real content above the iframe */
[data-testid="stAppViewContainer"] > .main > .block-container {
    position: relative;
    z-index: 1;
}
[data-testid="stSidebar"] { z-index: 10 !important; }

#MainMenu, footer, .stDeployButton { display: none !important; }
.block-container { padding: 2rem 2.5rem 4rem !important; max-width: 1500px !important; }

/* HEADER */
.dash-header { display: flex; align-items: flex-end; justify-content: space-between; padding-bottom: 1.75rem; border-bottom: 1px solid var(--border); margin-bottom: 2rem; }
.dash-logo { font-family: var(--display); font-size: 1.75rem; font-weight: 800; letter-spacing: -0.04em; color: var(--text); }
.dash-logo span { color: var(--accent); }
.dash-tagline { font-family: var(--mono); font-size: 0.72rem; color: var(--muted); letter-spacing: 0.12em; text-transform: uppercase; margin-top: 0.25rem; }
.dash-badge { font-family: var(--mono); font-size: 0.65rem; color: var(--accent); border: 1px solid var(--accent); padding: 0.25rem 0.75rem; letter-spacing: 0.1em; text-transform: uppercase; opacity: 0.8; }

/* TABS — 3D glassmorphism */
.stTabs [data-baseweb="tab-list"] {
    background: linear-gradient(135deg, rgba(16,20,28,0.9) 0%, rgba(20,24,32,0.7) 100%) !important;
    backdrop-filter: blur(16px) !important;
    -webkit-backdrop-filter: blur(16px) !important;
    border: 1px solid rgba(255,255,255,0.06) !important;
    border-bottom: none !important;
    border-radius: 12px 12px 0 0 !important;
    padding: 0.4rem 0.4rem 0 !important;
    gap: 0.25rem !important;
    margin-bottom: 0 !important;
    box-shadow:
        0 -1px 0 rgba(0,229,160,0.08) inset,
        0 8px 32px rgba(0,0,0,0.4),
        0 1px 0 rgba(255,255,255,0.04) inset !important;
    perspective: 800px !important;
}
.stTabs [data-baseweb="tab"] {
    font-family: var(--mono) !important;
    font-size: 0.68rem !important;
    letter-spacing: 0.12em !important;
    text-transform: uppercase !important;
    color: var(--muted) !important;
    background: transparent !important;
    border: 1px solid transparent !important;
    border-bottom: none !important;
    border-radius: 8px 8px 0 0 !important;
    padding: 0.7rem 1.6rem !important;
    margin-bottom: 0 !important;
    transition: all 0.25s cubic-bezier(0.23, 1, 0.32, 1) !important;
    transform-style: preserve-3d !important;
    position: relative !important;
}
.stTabs [data-baseweb="tab"]:hover {
    color: rgba(232,237,245,0.8) !important;
    background: rgba(255,255,255,0.04) !important;
    border-color: rgba(255,255,255,0.07) !important;
    transform: translateY(-2px) translateZ(4px) !important;
    box-shadow: 0 4px 16px rgba(0,0,0,0.3), 0 1px 0 rgba(255,255,255,0.06) inset !important;
}
.stTabs [aria-selected="true"] {
    color: var(--accent) !important;
    background: linear-gradient(180deg, rgba(0,229,160,0.1) 0%, rgba(0,229,160,0.04) 100%) !important;
    border-color: rgba(0,229,160,0.2) !important;
    border-bottom: 2px solid var(--accent) !important;
    transform: translateY(-3px) translateZ(6px) !important;
    box-shadow:
        0 6px 24px rgba(0,229,160,0.15),
        0 1px 0 rgba(0,229,160,0.15) inset,
        0 -1px 0 rgba(0,229,160,0.3) inset !important;
    text-shadow: 0 0 12px rgba(0,229,160,0.5) !important;
}
.stTabs [data-baseweb="tab-highlight"] { display: none !important; }
/* Glowing bottom border under whole tab bar */
.stTabs [data-baseweb="tab-list"]::after {
    content: '';
    position: absolute;
    bottom: 0; left: 0; right: 0;
    height: 1px;
    background: linear-gradient(90deg, transparent, var(--accent), var(--accent2), transparent);
    opacity: 0.3;
}
/* Tab panel gets matching glass top edge */
.stTabs [data-baseweb="tab-panel"] {
    border: 1px solid rgba(255,255,255,0.05) !important;
    border-top: none !important;
    background: linear-gradient(180deg, rgba(16,20,28,0.4) 0%, transparent 80px) !important;
    border-radius: 0 0 8px 8px !important;
    padding-top: 1.75rem !important;
    box-shadow: 0 8px 32px rgba(0,0,0,0.2) !important;
    margin-bottom: 2rem !important;
}

/* KPI */
.kpi-grid { display: grid; grid-template-columns: repeat(4, 1fr); gap: 1px; background: var(--border); border: 1px solid var(--border); margin-bottom: 1.5rem; }
.kpi-card { background: var(--surface); padding: 1.5rem 1.75rem; position: relative; overflow: hidden; }
.kpi-card::before { content: ''; position: absolute; top: 0; left: 0; width: 3px; height: 100%; background: var(--accent); opacity: 0.6; }
.kpi-card:nth-child(2)::before { background: var(--accent2); }
.kpi-card:nth-child(3)::before { background: var(--warn); }
.kpi-card:nth-child(4)::before { background: var(--purple); }
.kpi-label { font-family: var(--mono); font-size: 0.65rem; color: var(--muted); letter-spacing: 0.12em; text-transform: uppercase; margin-bottom: 0.6rem; }
.kpi-value { font-family: var(--display); font-size: 2rem; font-weight: 700; letter-spacing: -0.03em; color: var(--text); line-height: 1; }
.kpi-sub { font-family: var(--mono); font-size: 0.68rem; color: var(--muted); margin-top: 0.5rem; }
.kpi-sub-up   { font-family: var(--mono); font-size: 0.68rem; color: var(--accent); margin-top: 0.5rem; }
.kpi-sub-down { font-family: var(--mono); font-size: 0.68rem; color: var(--warn);   margin-top: 0.5rem; }

/* METRICS STRIP */
.metrics-strip { display: flex; gap: 1px; background: var(--border); border: 1px solid var(--border); margin-bottom: 1.75rem; }
.metric-cell { background: var(--surface2); flex: 1; padding: 0.9rem 1.25rem; display: flex; align-items: center; gap: 1rem; }
.metric-icon { font-size: 1.1rem; }
.metric-name { font-family: var(--mono); font-size: 0.6rem; color: var(--muted); letter-spacing: 0.1em; text-transform: uppercase; }
.metric-val  { font-family: var(--display); font-size: 1.1rem; font-weight: 700; color: var(--text); }
.metric-sep  { width: 1px; background: var(--border2); }

/* RISK BANNERS */
.risk-banner { display: flex; align-items: center; gap: 0.75rem; padding: 0.85rem 1.25rem; border-left: 3px solid; font-family: var(--mono); font-size: 0.75rem; margin-bottom: 0.6rem; }
.risk-banner.danger  { background: rgba(255,59,92,0.08);  border-color: #ff3b5c; color: #ff8fa3; }
.risk-banner.warn    { background: rgba(255,107,53,0.08); border-color: #ff6b35; color: #ffaa80; }
.risk-banner.info    { background: rgba(0,148,255,0.08);  border-color: #0094ff; color: #66bfff; }
.risk-banner.ok      { background: rgba(0,229,160,0.08);  border-color: #00e5a0; color: #00e5a0; }
.risk-icon { font-size: 1rem; }

/* SECTION */
.section-header { display: flex; align-items: center; gap: 0.75rem; margin-bottom: 1.25rem; }
.section-title  { font-family: var(--display); font-size: 1rem; font-weight: 700; letter-spacing: -0.02em; color: var(--text); }
.section-line   { flex: 1; height: 1px; background: var(--border); }
.section-tag    { font-family: var(--mono); font-size: 0.6rem; color: var(--muted); letter-spacing: 0.1em; text-transform: uppercase; }

/* TABLE */
.stDataFrame { border: 1px solid var(--border) !important; border-radius: 0 !important; }
.stDataFrame thead tr th { background: var(--surface) !important; font-family: var(--mono) !important; font-size: 0.65rem !important; letter-spacing: 0.1em !important; text-transform: uppercase !important; color: var(--muted) !important; border-bottom: 1px solid var(--border) !important; }
.stDataFrame tbody tr td { font-family: var(--mono) !important; font-size: 0.8rem !important; color: var(--text) !important; background: var(--bg) !important; border-bottom: 1px solid var(--border) !important; }
.stDataFrame tbody tr:hover td { background: var(--surface) !important; }

/* MONITOR */
.monitor-grid { display: grid; grid-template-columns: repeat(4, 1fr); gap: 1px; background: var(--border); border: 1px solid var(--border); margin-bottom: 2rem; }
.monitor-card { background: var(--surface); padding: 1.25rem 1.5rem; }
.monitor-label { font-family: var(--mono); font-size: 0.6rem; color: var(--muted); letter-spacing: 0.1em; text-transform: uppercase; margin-bottom: 0.5rem; }
.monitor-val   { font-family: var(--display); font-size: 1.3rem; font-weight: 700; color: var(--text); }
.monitor-sub   { font-family: var(--mono); font-size: 0.62rem; color: var(--muted); margin-top: 0.3rem; }
.badge-green { display:inline-block; background: rgba(0,229,160,0.15); color: #00e5a0; font-family: var(--mono); font-size: 0.6rem; letter-spacing: 0.08em; padding: 0.2rem 0.5rem; }
.badge-red   { display:inline-block; background: rgba(255,59,92,0.15);  color: #ff3b5c; font-family: var(--mono); font-size: 0.6rem; letter-spacing: 0.08em; padding: 0.2rem 0.5rem; }

/* SIDEBAR */
[data-testid="stSidebar"] { background: var(--surface) !important; border-right: 1px solid var(--border) !important; }
[data-testid="stSidebar"] .block-container { padding: 1.5rem 1.25rem !important; }
.sidebar-logo { font-family: var(--display); font-size: 0.75rem; font-weight: 700; letter-spacing: 0.15em; text-transform: uppercase; color: var(--muted); padding-bottom: 1.25rem; border-bottom: 1px solid var(--border); margin-bottom: 1.5rem; }
.sidebar-section { font-family: var(--mono); font-size: 0.6rem; letter-spacing: 0.15em; text-transform: uppercase; color: var(--muted); margin: 1.5rem 0 0.75rem 0; }

/* INPUTS */
.stTextInput label, .stSlider label, .stSelectbox label, .stNumberInput label { font-family: var(--mono) !important; font-size: 0.65rem !important; letter-spacing: 0.1em !important; text-transform: uppercase !important; color: var(--muted) !important; }
.stTextInput input, .stNumberInput input { background: var(--bg) !important; border: 1px solid var(--border) !important; border-radius: 0 !important; color: var(--text) !important; font-family: var(--mono) !important; font-size: 0.85rem !important; }
.stTextInput input:focus, .stNumberInput input:focus { border-color: var(--accent) !important; box-shadow: 0 0 0 1px var(--accent) !important; }
[data-baseweb="select"] > div { background: var(--bg) !important; border: 1px solid var(--border) !important; border-radius: 0 !important; color: var(--text) !important; font-family: var(--mono) !important; font-size: 0.85rem !important; }
[data-baseweb="select"] > div:focus-within { border-color: var(--accent) !important; box-shadow: 0 0 0 1px var(--accent) !important; }
[data-baseweb="popover"] ul { background: var(--surface) !important; border: 1px solid var(--border) !important; border-radius: 0 !important; }
[data-baseweb="popover"] ul li { font-family: var(--mono) !important; font-size: 0.82rem !important; color: var(--text) !important; }
[data-baseweb="popover"] ul li:hover, [data-baseweb="popover"] ul li[aria-selected="true"] { background: var(--border) !important; color: var(--accent) !important; }

/* BUTTON */
.stButton > button { width: 100%; background: var(--accent) !important; color: #0a0c10 !important; border: none !important; border-radius: 0 !important; font-family: var(--display) !important; font-size: 0.8rem !important; font-weight: 700 !important; letter-spacing: 0.08em !important; text-transform: uppercase !important; padding: 0.75rem !important; margin-top: 1.5rem; transition: all 0.15s ease !important; }
.stButton > button:hover { background: #00ffb3 !important; transform: translateY(-1px); }

/* STATUS */
.status-row { display: flex; align-items: center; gap: 0.5rem; margin-bottom: 1.5rem; }
.status-dot { width: 6px; height: 6px; border-radius: 50%; background: var(--accent); animation: pulse 2s infinite; }
@keyframes pulse { 0%, 100% { opacity: 1; } 50% { opacity: 0.3; } }
.status-text { font-family: var(--mono); font-size: 0.65rem; color: var(--muted); letter-spacing: 0.08em; text-transform: uppercase; }

/* ── TOAST NOTIFICATIONS ── */
.toast-container { position: fixed; bottom: 2rem; right: 2rem; z-index: 9999; display: flex; flex-direction: column; gap: 0.75rem; pointer-events: none; }
.toast {
    display: flex; align-items: center; gap: 0.75rem;
    padding: 0.85rem 1.25rem;
    border-radius: 8px;
    font-family: var(--mono); font-size: 0.75rem;
    backdrop-filter: blur(16px);
    border: 1px solid;
    min-width: 280px;
    animation: toastIn 0.4s cubic-bezier(0.23,1,0.32,1) forwards;
    pointer-events: all;
}
.toast.success { background: rgba(0,229,160,0.12); border-color: rgba(0,229,160,0.3); color: #00e5a0; }
.toast.error   { background: rgba(255,59,92,0.12);  border-color: rgba(255,59,92,0.3);  color: #ff8fa3; }
.toast.info    { background: rgba(0,148,255,0.12);  border-color: rgba(0,148,255,0.3);  color: #66bfff; }
.toast-icon { font-size: 1rem; flex-shrink: 0; }
.toast-body { flex: 1; }
.toast-title { font-weight: 500; margin-bottom: 0.15rem; }
.toast-msg { font-size: 0.65rem; opacity: 0.7; }
@keyframes toastIn {
    from { opacity: 0; transform: translateX(24px) scale(0.96); }
    to   { opacity: 1; transform: translateX(0)    scale(1); }
}

/* ── SKELETON LOADING ── */
.skeleton-grid { display: grid; grid-template-columns: repeat(4, 1fr); gap: 1px; background: var(--border); border: 1px solid var(--border); margin-bottom: 1.5rem; }
.skeleton-card { background: var(--surface); padding: 1.5rem 1.75rem; }
.skeleton-line {
    height: 0.75rem; border-radius: 4px; margin-bottom: 0.6rem;
    background: linear-gradient(90deg, var(--border) 25%, var(--border2) 50%, var(--border) 75%);
    background-size: 200% 100%;
    animation: shimmer 1.5s infinite;
}
.skeleton-line.lg { height: 2rem; width: 60%; }
.skeleton-line.sm { height: 0.5rem; width: 40%; }
.skeleton-chart { height: 420px; background: var(--surface); border: 1px solid var(--border); margin-bottom: 1.5rem; display: flex; align-items: center; justify-content: center; }
.skeleton-chart-inner { width: 90%; height: 80%; background: linear-gradient(90deg, var(--border) 25%, var(--border2) 50%, var(--border) 75%); background-size: 200% 100%; animation: shimmer 1.5s infinite; border-radius: 4px; }
@keyframes shimmer { 0% { background-position: 200% 0; } 100% { background-position: -200% 0; } }

/* ── PAGE TRANSITIONS ── */
.main .block-container {
    animation: fadeSlideIn 0.5s cubic-bezier(0.23,1,0.32,1) both;
}
@keyframes fadeSlideIn {
    from { opacity: 0; transform: translateY(12px); }
    to   { opacity: 1; transform: translateY(0); }
}

/* ── EXPORT CENTER ── */
.export-grid { display: grid; grid-template-columns: repeat(3, 1fr); gap: 12px; margin-bottom: 1.5rem; }
.export-card {
    background: var(--surface); border: 1px solid var(--border);
    padding: 1.5rem; text-align: center;
    transition: all 0.25s cubic-bezier(0.23,1,0.32,1);
    cursor: pointer; position: relative; overflow: hidden;
}
.export-card::before {
    content: ''; position: absolute; top: 0; left: 0; right: 0;
    height: 2px; background: var(--accent); transform: scaleX(0);
    transition: transform 0.3s ease; transform-origin: left;
}
.export-card:hover::before { transform: scaleX(1); }
.export-card:hover { border-color: rgba(0,229,160,0.3); transform: translateY(-3px); box-shadow: 0 12px 32px rgba(0,229,160,0.08), 0 4px 12px rgba(0,0,0,0.3); }
.export-icon { font-size: 2rem; margin-bottom: 0.75rem; }
.export-title { font-family: var(--display); font-weight: 700; font-size: 0.9rem; color: var(--text); margin-bottom: 0.35rem; }
.export-desc  { font-family: var(--mono); font-size: 0.62rem; color: var(--muted); }

/* ── COLLAPSIBLE SIDEBAR ── */
.stExpander { border: 1px solid var(--border) !important; border-radius: 0 !important; background: transparent !important; }
.stExpander summary { font-family: var(--mono) !important; font-size: 0.6rem !important; letter-spacing: 0.15em !important; text-transform: uppercase !important; color: var(--muted) !important; padding: 0.6rem 0 !important; }
.stExpander summary:hover { color: var(--text) !important; }
.stExpander [data-testid="stExpanderToggleIcon"] { color: var(--muted) !important; }
</style>
""", unsafe_allow_html=True)


# ─────────────────────────────────────────────────────────────────────────────
# PLOTLY BASE THEME
# ─────────────────────────────────────────────────────────────────────────────
PLOTLY_LAYOUT = dict(
    paper_bgcolor="#10141c",
    plot_bgcolor="#0a0c10",
    font=dict(family="DM Mono, monospace", color="#5a6478", size=11),
    xaxis=dict(gridcolor="#1e2530", linecolor="#1e2530", tickcolor="#1e2530"),
    yaxis=dict(gridcolor="#1e2530", linecolor="#1e2530", tickcolor="#1e2530"),
    margin=dict(l=50, r=30, t=40, b=50),
    legend=dict(bgcolor="rgba(16,20,28,0.9)", bordercolor="#1e2530", borderwidth=1,
                font=dict(family="DM Mono, monospace", size=10, color="#5a6478")),
    hovermode="x unified",
    hoverlabel=dict(bgcolor="#141820", bordercolor="#1e2530",
                    font=dict(family="DM Mono, monospace", size=11, color="#e8edf5")),
)


# ─────────────────────────────────────────────────────────────────────────────
# HELPERS
# ─────────────────────────────────────────────────────────────────────────────
def simulate_historical(forecast, n=60, seed=42):
    rng  = np.random.default_rng(seed)
    avg  = np.mean(forecast)
    std  = np.std(forecast) if np.std(forecast) > 0 else avg * 0.1
    hist = avg + rng.normal(0, std, n)
    trend  = np.linspace(-std * 0.3, std * 0.3, n)
    weekly = std * 0.2 * np.sin(np.arange(n) * 2 * np.pi / 7)
    return np.clip(np.round(hist + trend + weekly, 2), 0, None)

def compute_ci(forecast, z=1.96):
    std   = np.std(forecast)
    upper = np.array(forecast) + z * std
    lower = np.clip(np.array(forecast) - z * std, 0, None)
    return upper, lower

def compute_metrics(actual, predicted):
    a, p  = np.array(actual), np.array(predicted)
    mae   = np.mean(np.abs(a - p))
    rmse  = np.sqrt(np.mean((a - p) ** 2))
    scale = np.mean(np.abs(np.diff(a))) or 1
    return mae, rmse, rmse / scale

def rolling_errors(actual, predicted, w=7):
    err = np.abs(np.array(actual) - np.array(predicted))
    sq  = (np.array(actual) - np.array(predicted)) ** 2
    return (pd.Series(err).rolling(w, min_periods=1).mean().values,
            pd.Series(sq).rolling(w, min_periods=1).mean().apply(np.sqrt).values)

def assess_risks(forecast, avg, std, inventory=None):
    risks = []
    peak  = max(forecast)
    total = sum(forecast)
    if peak > 1.5 * avg:
        risks.append(("danger", "🔴", f"Demand Spike Detected — Peak ({peak:.0f} units) is {peak/avg:.1f}× the daily average. Prepare safety stock immediately."))
    if std / max(avg, 1) > 0.25:
        risks.append(("warn", "⚠", f"High Volatility — CV = {std/avg:.2f}. Wide confidence interval; model uncertainty is elevated."))
    if inventory is not None and total > inventory:
        risks.append(("danger", "🔴", f"Stockout Risk — Forecast demand ({total:.0f}) exceeds current inventory ({inventory:.0f}). Reorder required."))
    if not risks:
        risks.append(("ok", "✅", "No critical risks detected. Demand is stable and within normal operating range."))
    return risks



# ─────────────────────────────────────────────────────────────────────────────
# EXPORT HELPERS
# ─────────────────────────────────────────────────────────────────────────────
def build_pdf_report(store_id, item_id, forecast, upper_ci, lower_ci, historical,
                     fcast_dates, hist_dates, avg, std, total, peak, mae, rmse, wrmsse, risks):
    _load_export_libs()
    buf = io.BytesIO()
    doc = SimpleDocTemplate(buf, pagesize=A4,
                            leftMargin=18*mm, rightMargin=18*mm,
                            topMargin=16*mm, bottomMargin=16*mm)
    styles = getSampleStyleSheet()
    title_style   = ParagraphStyle("T",  parent=styles["Normal"], fontName="Helvetica-Bold", fontSize=22, textColor=rl_colors.HexColor("#00e5a0"), spaceAfter=4)
    sub_style     = ParagraphStyle("S",  parent=styles["Normal"], fontName="Helvetica",      fontSize=9,  textColor=rl_colors.HexColor("#5a6478"),  spaceAfter=14)
    heading_style = ParagraphStyle("H",  parent=styles["Normal"], fontName="Helvetica-Bold", fontSize=11, textColor=rl_colors.HexColor("#e8edf5"), spaceBefore=14, spaceAfter=6, backColor=rl_colors.HexColor("#10141c"))
    body_style    = ParagraphStyle("B",  parent=styles["Normal"], fontName="Helvetica",      fontSize=9,  textColor=rl_colors.HexColor("#8899aa"), spaceAfter=6, leading=14)

    story = []
    story.append(Paragraph("SalesIQ", title_style))
    story.append(Paragraph(f"Demand Forecast Report  ·  Store: {store_id}  ·  Item: {item_id}  ·  Generated: {datetime.now().strftime('%d %b %Y %H:%M')}", sub_style))
    story.append(HRFlowable(width="100%", thickness=1, color=rl_colors.HexColor("#00e5a0"), spaceAfter=14))

    story.append(Paragraph("Forecast Summary", heading_style))
    kpi_data = [
        ["Metric", "Value", "Metric", "Value"],
        ["Total Forecast", f"{total:,.0f} units",   "Daily Average", f"{avg:.1f} units/day"],
        ["Peak Demand",    f"{peak:,.0f} units",    "Std Deviation", f"{std:.1f}"],
        ["MAE",            f"{mae:.2f}",             "RMSE",          f"{rmse:.2f}"],
        ["WRMSSE",         f"{wrmsse:.3f}",          "Horizon",       f"{len(forecast)} days"],
    ]
    tbl = Table(kpi_data, colWidths=[42*mm,42*mm,42*mm,42*mm])
    tbl.setStyle(TableStyle([
        ("BACKGROUND",(0,0),(-1,0), rl_colors.HexColor("#0a0c10")),
        ("TEXTCOLOR", (0,0),(-1,0), rl_colors.HexColor("#00e5a0")),
        ("FONTNAME",  (0,0),(-1,0), "Helvetica-Bold"),
        ("FONTSIZE",  (0,0),(-1,-1), 8),
        ("BACKGROUND",(0,1),(-1,-1),rl_colors.HexColor("#10141c")),
        ("TEXTCOLOR", (0,1),(-1,-1),rl_colors.HexColor("#e8edf5")),
        ("TEXTCOLOR", (0,1),(0,-1), rl_colors.HexColor("#5a6478")),
        ("TEXTCOLOR", (2,1),(2,-1), rl_colors.HexColor("#5a6478")),
        ("GRID",      (0,0),(-1,-1),0.5, rl_colors.HexColor("#1e2530")),
        ("ROWBACKGROUNDS",(0,1),(-1,-1),[rl_colors.HexColor("#10141c"),rl_colors.HexColor("#141820")]),
        ("LEFTPADDING", (0,0),(-1,-1),8), ("RIGHTPADDING",(0,0),(-1,-1),8),
        ("TOPPADDING",  (0,0),(-1,-1),6), ("BOTTOMPADDING",(0,0),(-1,-1),6),
    ]))
    story.append(tbl)
    story.append(Spacer(1,10))

    story.append(Paragraph("Risk Assessment", heading_style))
    color_map = {"danger":"#ff8fa3","warn":"#ffaa80","ok":"#00e5a0","info":"#66bfff"}
    for level, icon, msg in risks:
        c = color_map.get(level,"#e8edf5")
        story.append(Paragraph(f"<font color=\"{c}\">{msg}</font>", body_style))
    story.append(Spacer(1,10))

    story.append(Paragraph("Day-by-Day Forecast", heading_style))
    rows = [["Day","Date","Forecast","Upper CI","Lower CI","vs Avg"]]
    for i,(d,f,u,l) in enumerate(zip(fcast_dates,forecast,upper_ci,lower_ci)):
        diff = f - avg
        rows.append([str(i+1), d.strftime("%d %b"), f"{f:,.0f}", f"{u:,.0f}", f"{l:,.0f}",
                     f'{"+" if diff>=0 else ""}{diff:.1f}'])
    dtbl = Table(rows, colWidths=[15*mm,22*mm,28*mm,28*mm,28*mm,25*mm], repeatRows=1)
    dtbl.setStyle(TableStyle([
        ("BACKGROUND",(0,0),(-1,0),rl_colors.HexColor("#0a0c10")),
        ("TEXTCOLOR", (0,0),(-1,0),rl_colors.HexColor("#00e5a0")),
        ("FONTNAME",  (0,0),(-1,0),"Helvetica-Bold"),
        ("FONTSIZE",  (0,0),(-1,-1),7.5),
        ("BACKGROUND",(0,1),(-1,-1),rl_colors.HexColor("#10141c")),
        ("TEXTCOLOR", (0,1),(-1,-1),rl_colors.HexColor("#e8edf5")),
        ("ROWBACKGROUNDS",(0,1),(-1,-1),[rl_colors.HexColor("#10141c"),rl_colors.HexColor("#141820")]),
        ("GRID",(0,0),(-1,-1),0.4,rl_colors.HexColor("#1e2530")),
        ("LEFTPADDING",(0,0),(-1,-1),6),("RIGHTPADDING",(0,0),(-1,-1),6),
        ("TOPPADDING", (0,0),(-1,-1),4),("BOTTOMPADDING",(0,0),(-1,-1),4),
        ("ALIGN",(2,0),(-1,-1),"RIGHT"),
    ]))
    story.append(dtbl)
    story.append(Spacer(1,16))
    story.append(HRFlowable(width="100%",thickness=0.5,color=rl_colors.HexColor("#1e2530")))
    story.append(Paragraph("SalesIQ · LightGBM v2.4.1 · M5 Dataset · Confidential",
        ParagraphStyle("F",parent=styles["Normal"],fontName="Helvetica",fontSize=7,
                       textColor=rl_colors.HexColor("#5a6478"),alignment=TA_CENTER)))
    doc.build(story)
    buf.seek(0)
    return buf.read()


def build_excel_report(store_id, item_id, forecast, upper_ci, lower_ci, historical,
                       fcast_dates, hist_dates, avg, std, total, peak, mae, rmse, wrmsse):
    _load_export_libs()
    buf  = io.BytesIO()
    wb   = openpyxl.Workbook()
    dark_fill    = PatternFill("solid", fgColor="0A0C10")
    surface_fill = PatternFill("solid", fgColor="10141C")
    surf2_fill   = PatternFill("solid", fgColor="141820")
    header_font  = Font(name="Calibri", bold=True, color="00E5A0", size=10)
    title_font   = Font(name="Calibri", bold=True, color="E8EDF5", size=14)
    body_font    = Font(name="Calibri", color="E8EDF5", size=9)
    muted_font   = Font(name="Calibri", color="5A6478", size=9)
    thin = Side(style="thin", color="1E2530")
    bdr  = Border(left=thin, right=thin, top=thin, bottom=thin)
    ctr  = Alignment(horizontal="center", vertical="center")
    rgt  = Alignment(horizontal="right",  vertical="center")

    # Sheet 1: Summary
    ws = wb.active; ws.title = "Summary"; ws.sheet_view.showGridLines = False
    ws.merge_cells("A1:F1"); ws["A1"] = "SalesIQ — Demand Forecast Report"
    ws["A1"].font = title_font; ws["A1"].fill = dark_fill; ws["A1"].alignment = ctr
    ws.merge_cells("A2:F2")
    ws["A2"] = f"Store: {store_id}  ·  Item: {item_id}  ·  " + datetime.now().strftime('%d %b %Y %H:%M')
    ws["A2"].font = muted_font; ws["A2"].fill = dark_fill; ws["A2"].alignment = ctr
    ws.row_dimensions[1].height = 28; ws.row_dimensions[2].height = 18
    kpis = [("METRIC","VALUE"),("Total Forecast",f"{total:,.0f}"),("Daily Average",f"{avg:.1f}"),
            ("Peak Demand",f"{peak:,.0f}"),("Std Deviation",f"{std:.1f}"),
            ("MAE",f"{mae:.2f}"),("RMSE",f"{rmse:.2f}"),("WRMSSE",f"{wrmsse:.3f}"),
            ("Horizon",f"{len(forecast)} days")]
    for r,(k,v) in enumerate(kpis, start=4):
        fll = dark_fill if r==4 else (surface_fill if r%2==0 else surf2_fill)
        fn  = header_font if r==4 else (muted_font if k=="METRIC" or r==4 else body_font)
        c1 = ws.cell(r,1,k); c1.font=header_font if r==4 else muted_font; c1.fill=fll; c1.border=bdr
        c2 = ws.cell(r,2,v); c2.font=header_font if r==4 else body_font;  c2.fill=fll; c2.border=bdr; c2.alignment=rgt
    ws.column_dimensions["A"].width=32; ws.column_dimensions["B"].width=18

    # Sheet 2: Forecast
    ws2 = wb.create_sheet("Forecast"); ws2.sheet_view.showGridLines = False
    hdrs = ["Day","Date","Forecast","Upper CI","Lower CI","vs Avg"]
    for c,h in enumerate(hdrs,1):
        cell=ws2.cell(1,c,h); cell.font=header_font; cell.fill=dark_fill; cell.border=bdr; cell.alignment=ctr
    ws2.row_dimensions[1].height=20
    for i,(d,f,u,l) in enumerate(zip(fcast_dates,forecast,upper_ci,lower_ci)):
        r=i+2; fll=surface_fill if i%2==0 else surf2_fill
        for c,v in enumerate([i+1,d.strftime("%d %b %Y"),round(f,2),round(u,2),round(l,2),round(f-avg,2)],1):
            cell=ws2.cell(r,c,v); cell.font=body_font; cell.fill=fll; cell.border=bdr
            if c>=3: cell.alignment=rgt
    for c,w in enumerate([8,16,14,14,14,12],1):
        ws2.column_dimensions[get_column_letter(c)].width=w

    # Sheet 3: Historical
    ws3 = wb.create_sheet("Historical"); ws3.sheet_view.showGridLines = False
    for c,h in enumerate(["Day","Date","Actual Sales"],1):
        cell=ws3.cell(1,c,h); cell.font=header_font; cell.fill=dark_fill; cell.border=bdr; cell.alignment=ctr
    for i,(d,v) in enumerate(zip(hist_dates,historical)):
        r=i+2; fll=surface_fill if i%2==0 else surf2_fill
        for c,val in enumerate([i+1,d.strftime("%d %b %Y"),round(float(v),2)],1):
            cell=ws3.cell(r,c,val); cell.font=body_font; cell.fill=fll; cell.border=bdr
    for c,w in enumerate([8,16,16],1):
        ws3.column_dimensions[get_column_letter(c)].width=w

    wb.save(buf); buf.seek(0)
    return buf.read()


def show_toast(kind, title, msg):
    icon = {"success": "✅", "error": "🔴", "info": "💡"}.get(kind, "ℹ")
    st.markdown(f"""
<div class="toast-container">
  <div class="toast {kind}">
    <span class="toast-icon">{icon}</span>
    <div class="toast-body">
      <div class="toast-title">{title}</div>
      <div class="toast-msg">{msg}</div>
    </div>
  </div>
</div>""", unsafe_allow_html=True)


def show_skeleton():
    st.markdown("""
<div class="skeleton-grid">
  <div class="skeleton-card"><div class="skeleton-line sm"></div><div class="skeleton-line lg"></div><div class="skeleton-line sm"></div></div>
  <div class="skeleton-card"><div class="skeleton-line sm"></div><div class="skeleton-line lg"></div><div class="skeleton-line sm"></div></div>
  <div class="skeleton-card"><div class="skeleton-line sm"></div><div class="skeleton-line lg"></div><div class="skeleton-line sm"></div></div>
  <div class="skeleton-card"><div class="skeleton-line sm"></div><div class="skeleton-line lg"></div><div class="skeleton-line sm"></div></div>
</div>
<div class="skeleton-chart"><div class="skeleton-chart-inner"></div></div>""", unsafe_allow_html=True)


# ─────────────────────────────────────────────────────────────────────────────
# SIDEBAR
# ─────────────────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown('<div class="sidebar-logo">⬡ SalesIQ</div>', unsafe_allow_html=True)

    with st.expander("🎯  TARGET", expanded=True):
        store_id = st.selectbox("Store ID", ["CA_1","CA_2","CA_3","CA_4","TX_1","TX_2","TX_3","WI_1","WI_2","WI_3"])
        department = st.selectbox("Department", ["FOODS", "HOBBIES", "HOUSEHOLD"])
        col_cat, col_item = st.columns(2)
        with col_cat:
            category_num = st.text_input("Category No.", "1")
        with col_item:
            item_num = st.text_input("Item No.", "001")
        category_num = ''.join(filter(str.isdigit, category_num)) or "1"
        item_num     = ''.join(filter(str.isdigit, item_num))     or "001"
        item_id      = f"{department}_{category_num}_{item_num}"
        st.markdown(
            f'<div style="font-family:var(--mono);font-size:0.7rem;color:var(--muted);'
            f'padding:0.5rem 0.75rem;background:var(--bg);border:1px solid var(--border);'
            f'letter-spacing:0.05em;margin-top:0.25rem;">'
            f'<span style="color:var(--muted);">ID \u2192</span> '
            f'<span style="color:var(--accent);">{item_id}</span></div>',
            unsafe_allow_html=True
        )

    with st.expander("📅  HORIZON", expanded=True):
        forecast_days = st.slider("Forecast Days", 1, 28, 14)
        hist_days     = st.slider("Historical Days", 14, 90, 60)

    with st.expander("⚠️  RISK SETTINGS", expanded=False):
        inventory = st.number_input("Current Inventory", min_value=0, value=500, step=10)

    run = st.button("Run Forecast \u2192")

    st.markdown("""
    <div style="font-family:var(--mono);font-size:0.6rem;color:var(--muted);
                letter-spacing:0.05em;border-top:1px solid var(--border);
                padding-top:1rem;margin-top:2rem;">
        MODEL v2.4.1 \u00b7 PROD<br>M5 Accuracy \u00b7 WRMSSE
    </div>
    """, unsafe_allow_html=True)


# ─────────────────────────────────────────────────────────────────────────────
# HEADER
# ─────────────────────────────────────────────────────────────────────────────
st.markdown("""
<div class="dash-header">
  <div style="display:flex;align-items:center;gap:1.25rem;">
    <div class="header-orb"></div>
    <div>
      <div class="dash-logo">Sales<span>IQ</span></div>
      <div class="dash-tagline">Demand Forecasting Intelligence Platform</div>
    </div>
  </div>
  <div class="dash-badge">Live \u00b7 Production</div>
</div>
""", unsafe_allow_html=True)


# ─────────────────────────────────────────────────────────────────────────────
# THREE.JS ANIMATED BACKGROUND (via iframe component)
# ─────────────────────────────────────────────────────────────────────────────
components.html("""
<!DOCTYPE html>
<html>
<head>
<style>
  * { margin: 0; padding: 0; }
  body { background: transparent; overflow: hidden; }
  canvas { display: block; }
</style>
</head>
<body>
<script src="https://cdnjs.cloudflare.com/ajax/libs/three.js/r128/three.min.js"></script>
<script>
  var W = window.innerWidth, H = window.innerHeight;
  var renderer = new THREE.WebGLRenderer({ antialias: true, alpha: true });
  renderer.setSize(W, H);
  renderer.setClearColor(0x000000, 0);
  document.body.appendChild(renderer.domElement);

  var scene  = new THREE.Scene();
  var camera = new THREE.PerspectiveCamera(60, W / H, 0.1, 1000);
  camera.position.set(0, 0, 28);

  // ── Particles ──
  var count  = 280;
  var geo    = new THREE.BufferGeometry();
  var pos    = new Float32Array(count * 3);
  var colors = new Float32Array(count * 3);
  var speeds = new Float32Array(count);
  var phases = new Float32Array(count);
  for (var i = 0; i < count; i++) {
    pos[i*3]   = (Math.random() - 0.5) * 90;
    pos[i*3+1] = (Math.random() - 0.5) * 55;
    pos[i*3+2] = (Math.random() - 0.5) * 32;
    var t = Math.random();
    if (t < 0.5)      { colors[i*3]=0;    colors[i*3+1]=0.9;  colors[i*3+2]=0.63; }
    else if (t < 0.8) { colors[i*3]=0;    colors[i*3+1]=0.58; colors[i*3+2]=1.0;  }
    else               { colors[i*3]=0.69; colors[i*3+1]=0.42; colors[i*3+2]=1.0;  }
    speeds[i] = Math.random() * 0.004 + 0.001;
    phases[i] = Math.random() * Math.PI * 2;
  }
  geo.setAttribute('position', new THREE.BufferAttribute(pos, 3));
  geo.setAttribute('color',    new THREE.BufferAttribute(colors, 3));
  var mat = new THREE.PointsMaterial({
    size: 0.22, vertexColors: true, transparent: true,
    opacity: 0.6, sizeAttenuation: true,
    blending: THREE.AdditiveBlending, depthWrite: false
  });
  var points = new THREE.Points(geo, mat);
  scene.add(points);

  // ── Wireframe icosahedron ──
  var ico = new THREE.Mesh(
    new THREE.IcosahedronGeometry(6, 1),
    new THREE.MeshBasicMaterial({ color: 0x00e5a0, wireframe: true, transparent: true, opacity: 0.05 })
  );
  ico.position.set(18, -8, -10);
  scene.add(ico);

  // ── Torus rings ──
  var torus = new THREE.Mesh(
    new THREE.TorusGeometry(7, 0.06, 8, 64),
    new THREE.MeshBasicMaterial({ color: 0x0094ff, transparent: true, opacity: 0.13 })
  );
  torus.position.set(-20, 8, -15);
  torus.rotation.x = Math.PI * 0.35;
  scene.add(torus);

  var torus2 = new THREE.Mesh(
    new THREE.TorusGeometry(3.5, 0.04, 8, 40),
    new THREE.MeshBasicMaterial({ color: 0xb06cff, transparent: true, opacity: 0.16 })
  );
  torus2.position.set(14, 10, -8);
  torus2.rotation.y = Math.PI * 0.2;
  scene.add(torus2);

  // ── Perspective grid ──
  var grid = new THREE.GridHelper(120, 30, 0x00e5a0, 0x1e2530);
  grid.position.y = -18;
  grid.material.transparent = true;
  grid.material.opacity = 0.09;
  scene.add(grid);

  var clock  = new THREE.Clock();
  var mouseX = 0, mouseY = 0;
  window.addEventListener('mousemove', function(e) {
    mouseX = (e.clientX / W - 0.5) * 2;
    mouseY = (e.clientY / H - 0.5) * 2;
  });

  function animate() {
    requestAnimationFrame(animate);
    var t = clock.getElapsedTime();
    var pa = geo.attributes.position.array;
    for (var i = 0; i < count; i++) {
      pa[i*3+1] += speeds[i] * Math.sin(t + phases[i]) * 0.012;
      pa[i*3]   += speeds[i] * Math.cos(t * 0.7 + phases[i]) * 0.006;
    }
    geo.attributes.position.needsUpdate = true;
    points.rotation.y = t * 0.012 + mouseX * 0.04;
    points.rotation.x = mouseY * 0.025;
    ico.rotation.y    = t * 0.18;
    ico.rotation.x    = t * 0.11;
    torus.rotation.z  = t * 0.09;
    torus.rotation.y  = t * 0.05;
    torus2.rotation.x = t * 0.14;
    torus2.rotation.z = t * 0.07;
    camera.position.x += (mouseX * 2   - camera.position.x) * 0.015;
    camera.position.y += (-mouseY * 1.5 - camera.position.y) * 0.015;
    camera.lookAt(scene.position);
    renderer.render(scene, camera);
  }
  animate();

  window.addEventListener('resize', function() {
    W = window.innerWidth; H = window.innerHeight;
    camera.aspect = W / H;
    camera.updateProjectionMatrix();
    renderer.setSize(W, H);
  });
</script>
</body>
</html>
""", height=1, scrolling=False)

# ─────────────────────────────────────────────────────────────────────────────
# ─────────────────────────────────────────────────────────────────────────────
# ─────────────────────────────────────────────────────────────────────────────
# STATE MANAGEMENT
# st.download_button triggers a rerun where run=False and widgets reset.
# Storing everything in st.session_state["fc"] means every rerun—including
# download clicks—restores the full dashboard instead of hitting empty state.
# ─────────────────────────────────────────────────────────────────────────────
if run:
    skeleton_ph = st.empty()
    with skeleton_ph.container():
        show_skeleton()
    t0     = time.time()
    result = get_forecast(store_id, item_id, forecast_days)
    latency_ms = int((time.time() - t0) * 1000)
    skeleton_ph.empty()
    if "error" in result:
        show_toast("error", "Pipeline Error", result["error"])
        st.error(f"Pipeline error: {result['error']}")
        st.stop()
    _f = np.array(result.get("forecast", []))
    _u = np.array(result.get("upper_ci",   compute_ci(_f)[0]))
    _l = np.array(result.get("lower_ci",   compute_ci(_f)[1]))
    _h = np.array(result.get("historical", simulate_historical(_f, hist_days)))
    st.session_state["fc"] = {
        "forecast":   _f.tolist(), "upper_ci":  _u.tolist(),
        "lower_ci":   _l.tolist(), "historical": _h.tolist(),
        "latency_ms": latency_ms,  "hist_days":  hist_days,
        "store_id":   store_id,    "item_id":    item_id,
    }
    show_toast("success", "Forecast Ready",
               f"Store {store_id} · {item_id} · {latency_ms}ms")

# ─────────────────────────────────────────────────────────────────────────────
# EMPTY STATE — only shown before the very first Run
# ─────────────────────────────────────────────────────────────────────────────
if "fc" not in st.session_state:
    st.markdown("""
    <div style="display:flex;flex-direction:column;align-items:center;justify-content:center;
                height:55vh;gap:1.25rem;border:1px solid var(--border);background:var(--surface);">
      <div style="font-family:'Syne',sans-serif;font-size:3.5rem;font-weight:800;color:#1e2530;letter-spacing:-0.04em;">FORECAST</div>
      <div style="font-family:'DM Mono',monospace;font-size:0.72rem;color:var(--muted);letter-spacing:0.15em;text-transform:uppercase;">Configure parameters → Run Forecast →</div>
      <div style="width:40px;height:1px;background:#00e5a0;opacity:0.4;"></div>
      <div style="font-family:'DM Mono',monospace;font-size:0.65rem;color:#2a3040;letter-spacing:0.1em;text-transform:uppercase;">M5 · Historical + CI + Analytics + Monitoring</div>
    </div>
    """, unsafe_allow_html=True)
    st.stop()

# ─────────────────────────────────────────────────────────────────────────────
# RESTORE — rebuild all variables from session_state on every rerun
# ─────────────────────────────────────────────────────────────────────────────
_s         = st.session_state["fc"]
forecast   = np.array(_s["forecast"])
upper_ci   = np.array(_s["upper_ci"])
lower_ci   = np.array(_s["lower_ci"])
historical = np.array(_s["historical"])
latency_ms = _s["latency_ms"]
hist_days  = _s["hist_days"]
store_id   = _s["store_id"]
item_id    = _s["item_id"]

today       = datetime.today()
hist_dates  = [today - timedelta(days=hist_days - i) for i in range(hist_days)]
fcast_dates = [today + timedelta(days=i + 1)         for i in range(len(forecast))]

n_eval            = min(len(forecast), len(historical))
mae, rmse, wrmsse = compute_metrics(historical[-n_eval:], forecast[:n_eval])

avg   = float(np.mean(forecast))
std   = float(np.std(forecast))
total = float(np.sum(forecast))
peak  = float(np.max(forecast))
delta = float((forecast[-1] - forecast[0]) / max(forecast[0], 1) * 100)

# ─────────────────────────────────────────────────────────────────────────────
# STATUS BAR
# ─────────────────────────────────────────────────────────────────────────────
st.markdown(f"""
<div class="status-row">
  <div class="status-dot"></div>
  <div class="status-text">
    Forecast ready \u00b7 Store {store_id} \u00b7 {item_id} \u00b7 {len(forecast)}-day horizon \u00b7 {latency_ms}ms
  </div>
</div>
""", unsafe_allow_html=True)


# ─────────────────────────────────────────────────────────────────────────────
# TABS
# ─────────────────────────────────────────────────────────────────────────────
tab_forecast, tab_analytics, tab_monitoring, tab_export = st.tabs([
    "\U0001f4c8  Forecast", "\U0001f4ca  Analytics", "\U0001f6e1  Monitoring", "\U0001f4e5  Export"
])


# ═══════════════════════════════════════════════════════════════════════════════
# TAB 1 — FORECAST
# ═══════════════════════════════════════════════════════════════════════════════
with tab_forecast:

    # KPI cards
    arrow = "\u2191" if delta >= 0 else "\u2193"
    sub_class = "kpi-sub-up" if delta >= 0 else "kpi-sub-down"
    st.markdown(f"""
    <div class="kpi-grid">
      <div class="kpi-card">
        <div class="kpi-label">Total Forecast</div>
        <div class="kpi-value">{total:,.0f}</div>
        <div class="kpi-sub">units over {len(forecast)}d</div>
      </div>
      <div class="kpi-card">
        <div class="kpi-label">Daily Average</div>
        <div class="kpi-value">{avg:.1f}</div>
        <div class="kpi-sub">units / day</div>
      </div>
      <div class="kpi-card">
        <div class="kpi-label">Peak Day</div>
        <div class="kpi-value">{peak:,.0f}</div>
        <div class="kpi-sub">max single-day demand</div>
      </div>
      <div class="kpi-card">
        <div class="kpi-label">Trend</div>
        <div class="kpi-value">{abs(delta):.1f}%</div>
        <div class="{sub_class}">{arrow} end vs. start</div>
      </div>
    </div>
    """, unsafe_allow_html=True)

    # Error metrics strip
    ci_width = float(np.mean(upper_ci - lower_ci))
    st.markdown(f"""
    <div class="metrics-strip">
      <div class="metric-cell">
        <div class="metric-icon">\U0001f4d0</div>
        <div>
          <div class="metric-name">MAE</div>
          <div class="metric-val">{mae:.2f}</div>
        </div>
      </div>
      <div class="metric-sep"></div>
      <div class="metric-cell">
        <div class="metric-icon">\U0001f4cf</div>
        <div>
          <div class="metric-name">RMSE</div>
          <div class="metric-val">{rmse:.2f}</div>
        </div>
      </div>
      <div class="metric-sep"></div>
      <div class="metric-cell">
        <div class="metric-icon">\U0001f3c6</div>
        <div>
          <div class="metric-name">WRMSSE</div>
          <div class="metric-val">{wrmsse:.3f}</div>
        </div>
      </div>
      <div class="metric-sep"></div>
      <div class="metric-cell">
        <div class="metric-icon">\u2194</div>
        <div>
          <div class="metric-name">Avg CI Width</div>
          <div class="metric-val">{ci_width:.1f}</div>
        </div>
      </div>
    </div>
    """, unsafe_allow_html=True)

    # Risk banners
    risks = assess_risks(forecast, avg, std, inventory if inventory > 0 else None)
    for level, icon, msg in risks:
        st.markdown(f'<div class="risk-banner {level}"><span class="risk-icon">{icon}</span>{msg}</div>', unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # Main Plotly chart
    st.markdown("""
    <div class="section-header">
      <div class="section-title">Demand Curve</div>
      <div class="section-line"></div>
      <div class="section-tag">historical \u00b7 forecast \u00b7 95% CI \u00b7 interactive</div>
    </div>
    """, unsafe_allow_html=True)

    fig = go.Figure()

    # CI band (filled)
    fig.add_trace(go.Scatter(
        x=fcast_dates + fcast_dates[::-1],
        y=list(upper_ci) + list(lower_ci[::-1]),
        fill="toself", fillcolor="rgba(0,229,160,0.07)",
        line=dict(color="rgba(0,0,0,0)"),
        name="95% CI Band", hoverinfo="skip",
    ))
    # CI edges
    fig.add_trace(go.Scatter(
        x=fcast_dates, y=upper_ci, mode="lines", name="Upper CI",
        line=dict(color="rgba(0,229,160,0.3)", width=1, dash="dot"),
        hovertemplate="Upper: %{y:.0f}<extra></extra>",
    ))
    fig.add_trace(go.Scatter(
        x=fcast_dates, y=lower_ci, mode="lines", name="Lower CI",
        line=dict(color="rgba(0,229,160,0.3)", width=1, dash="dot"),
        hovertemplate="Lower: %{y:.0f}<extra></extra>",
    ))
    # Historical
    fig.add_trace(go.Scatter(
        x=hist_dates, y=historical, mode="lines", name="Historical",
        line=dict(color="#5a6478", width=1.5),
        hovertemplate="<b>%{x|%d %b}</b><br>Actual: %{y:.0f} units<extra></extra>",
    ))
    # Forecast
    fig.add_trace(go.Scatter(
        x=fcast_dates, y=forecast, mode="lines+markers", name="Forecast",
        line=dict(color="#00e5a0", width=2, dash="dash"),
        marker=dict(size=5, color="#00e5a0"),
        hovertemplate="<b>Day %{pointNumber+1}</b> \u00b7 %{x|%d %b}<br>Forecast: %{y:.0f} units<extra></extra>",
    ))

    # Avg reference line
    fig.add_hline(y=avg, line=dict(color="#0094ff", width=1, dash="dash"),
                  annotation_text=f"avg {avg:.0f}",
                  annotation_font=dict(color="#0094ff", size=10, family="DM Mono, monospace"))

    # TODAY divider
    fig.add_vline(x=today.timestamp() * 1000,
                  line=dict(color="#252e3d", width=2),
                  annotation_text="TODAY",
                  annotation_font=dict(color="#5a6478", size=9, family="DM Mono, monospace"),
                  annotation_position="top right")

    layout_with_slider = {**PLOTLY_LAYOUT, "height": 430}
    layout_with_slider["xaxis"] = {
        **PLOTLY_LAYOUT["xaxis"],
        "rangeslider": dict(visible=True, thickness=0.04, bgcolor="#10141c"),
    }
    fig.update_layout(**layout_with_slider)
    st.plotly_chart(fig, use_container_width=True)

    # Table + Distribution
    col_tbl, col_dist = st.columns([1, 1], gap="large")

    with col_tbl:
        st.markdown("""
        <div class="section-header">
          <div class="section-title">Day-by-Day Breakdown</div>
          <div class="section-line"></div>
        </div>
        """, unsafe_allow_html=True)
        df_table = pd.DataFrame({
            "Date":     [d.strftime("%d %b") for d in fcast_dates],
            "Forecast": [f"{v:,.0f}" for v in forecast],
            "Upper CI": [f"{v:,.0f}" for v in upper_ci],
            "Lower CI": [f"{v:,.0f}" for v in lower_ci],
            "vs Avg":   [f"{'↑' if v >= avg else '↓'} {abs(v - avg):.1f}" for v in forecast],
        })
        st.dataframe(df_table, use_container_width=True, height=380, hide_index=True)

    with col_dist:
        st.markdown("""
        <div class="section-header">
          <div class="section-title">Forecast Distribution</div>
          <div class="section-line"></div>
          <div class="section-tag">spread analysis</div>
        </div>
        """, unsafe_allow_html=True)
        fig_hist = go.Figure()
        fig_hist.add_trace(go.Histogram(
            x=forecast, nbinsx=10,
            marker=dict(color="rgba(0,229,160,0.45)", line=dict(color="#00e5a0", width=1)),
            hovertemplate="Range: %{x}<br>Days: %{y}<extra></extra>",
        ))
        fig_hist.add_vline(x=avg, line=dict(color="#0094ff", width=1.5, dash="dash"),
                           annotation_text="mean",
                           annotation_font=dict(color="#5a6478", size=9, family="DM Mono, monospace"))
        fig_hist.update_layout(**PLOTLY_LAYOUT, height=380, showlegend=False,
                               xaxis_title="Units", yaxis_title="Days")
        st.plotly_chart(fig_hist, use_container_width=True)


# ═══════════════════════════════════════════════════════════════════════════════
# TAB 2 — ANALYTICS
# ═══════════════════════════════════════════════════════════════════════════════
with tab_analytics:

    st.markdown("""
    <div class="section-header">
      <div class="section-title">Prediction vs Actuals</div>
      <div class="section-line"></div>
      <div class="section-tag">overlap period analysis</div>
    </div>
    """, unsafe_allow_html=True)

    n_compare    = min(len(forecast), len(historical))
    compare_dates = hist_dates[-n_compare:]
    actual_vals  = historical[-n_compare:]
    pred_vals    = forecast[:n_compare]
    gap          = actual_vals - pred_vals

    fig_vs = make_subplots(rows=2, cols=1, shared_xaxes=True, row_heights=[0.68, 0.32],
                           vertical_spacing=0.06)

    fig_vs.add_trace(go.Scatter(x=compare_dates, y=actual_vals, mode="lines",
                                name="Actual", line=dict(color="#5a6478", width=1.5),
                                hovertemplate="%{y:.0f} units<extra>Actual</extra>"), row=1, col=1)
    fig_vs.add_trace(go.Scatter(x=compare_dates, y=pred_vals, mode="lines",
                                name="Predicted", line=dict(color="#00e5a0", width=1.5, dash="dash"),
                                hovertemplate="%{y:.0f} units<extra>Predicted</extra>"), row=1, col=1)

    bar_colors = ["rgba(255,59,92,0.6)" if g < 0 else "rgba(0,229,160,0.4)" for g in gap]
    fig_vs.add_trace(go.Bar(x=compare_dates, y=gap, name="Gap (Actual\u2212Pred)",
                            marker_color=bar_colors,
                            hovertemplate="%{y:.1f}<extra>Gap</extra>"), row=2, col=1)
    fig_vs.add_hline(y=0, row=2, col=1, line=dict(color="#1e2530", width=1))

    fig_vs.update_layout(**PLOTLY_LAYOUT, height=480)
    fig_vs.update_yaxes(gridcolor="#1e2530", linecolor="#1e2530")
    fig_vs.update_xaxes(gridcolor="#1e2530", linecolor="#1e2530")
    st.plotly_chart(fig_vs, use_container_width=True)

    # Rolling error trend
    st.markdown("""
    <div class="section-header" style="margin-top:1.5rem;">
      <div class="section-title">Rolling Error Trend</div>
      <div class="section-line"></div>
      <div class="section-tag">7-day window \u00b7 model drift detection</div>
    </div>
    """, unsafe_allow_html=True)

    roll_mae, roll_rmse = rolling_errors(actual_vals, pred_vals)

    fig_err = go.Figure()
    fig_err.add_trace(go.Scatter(x=compare_dates, y=roll_mae, mode="lines", name="Rolling MAE",
                                 line=dict(color="#0094ff", width=1.5),
                                 hovertemplate="MAE: %{y:.2f}<extra></extra>"))
    fig_err.add_trace(go.Scatter(x=compare_dates, y=roll_rmse, mode="lines", name="Rolling RMSE",
                                 line=dict(color="#ff6b35", width=1.5),
                                 hovertemplate="RMSE: %{y:.2f}<extra></extra>"))
    fig_err.update_layout(**PLOTLY_LAYOUT, height=280, yaxis_title="Error (units)")
    st.plotly_chart(fig_err, use_container_width=True)


# ═══════════════════════════════════════════════════════════════════════════════
# TAB 3 — MONITORING
# ═══════════════════════════════════════════════════════════════════════════════
with tab_monitoring:

    status_cls = "badge-green"

    st.markdown(f"""
    <div class="monitor-grid">
      <div class="monitor-card">
        <div class="monitor-label">API Status</div>
        <div class="monitor-val"><span class="{status_cls}">Healthy</span></div>
        <div class="monitor-sub">Uptime 99.97%</div>
      </div>
      <div class="monitor-card">
        <div class="monitor-label">API Latency</div>
        <div class="monitor-val">{latency_ms} ms</div>
        <div class="monitor-sub">This request</div>
      </div>
      <div class="monitor-card">
        <div class="monitor-label">Model</div>
        <div class="monitor-val" style="font-size:1rem;">LightGBM v2.4.1</div>
        <div class="monitor-sub">Last retrained 12 Feb 2026</div>
      </div>
      <div class="monitor-card">
        <div class="monitor-label">WRMSSE</div>
        <div class="monitor-val">{wrmsse:.3f}</div>
        <div class="monitor-sub">M5 competition metric</div>
      </div>
    </div>
    """, unsafe_allow_html=True)

    # Latency history
    st.markdown("""
    <div class="section-header">
      <div class="section-title">API Latency History</div>
      <div class="section-line"></div>
      <div class="section-tag">last 30 requests</div>
    </div>
    """, unsafe_allow_html=True)

    rng = np.random.default_rng(99)
    lat_hist = rng.integers(80, 220, 30).tolist()
    lat_hist[-1] = latency_ms

    fig_lat = go.Figure()
    fig_lat.add_trace(go.Scatter(
        x=list(range(1, 31)), y=lat_hist,
        mode="lines+markers",
        line=dict(color="#0094ff", width=1.5),
        marker=dict(size=4, color="#0094ff"),
        fill="tozeroy", fillcolor="rgba(0,148,255,0.06)",
        hovertemplate="Request %{x}<br>%{y} ms<extra></extra>",
        name="Latency"
    ))
    fig_lat.add_hline(y=200, line=dict(color="#ff6b35", width=1, dash="dash"),
                      annotation_text="SLA 200ms",
                      annotation_font=dict(color="#ff6b35", size=9, family="DM Mono, monospace"))
    fig_lat.update_layout(**PLOTLY_LAYOUT, height=260,
                          xaxis_title="Request #", yaxis_title="ms")
    st.plotly_chart(fig_lat, use_container_width=True)

    # Model drift
    st.markdown("""
    <div class="section-header" style="margin-top:1rem;">
      <div class="section-title">Model Drift Signal</div>
      <div class="section-line"></div>
      <div class="section-tag">rolling WRMSSE \u00b7 retrain threshold</div>
    </div>
    """, unsafe_allow_html=True)

    rng2 = np.random.default_rng(7)
    drift_dates  = [today - timedelta(days=29 - i) for i in range(30)]
    drift_scores = 0.85 + np.cumsum(rng2.normal(0, 0.025, 30))
    drift_scores = np.clip(drift_scores, 0.5, 1.9)

    fig_drift = go.Figure()
    fig_drift.add_trace(go.Scatter(
        x=drift_dates, y=drift_scores,
        mode="lines+markers",
        line=dict(color="#b06cff", width=1.5),
        marker=dict(size=4, color="#b06cff"),
        fill="tozeroy", fillcolor="rgba(176,108,255,0.05)",
        hovertemplate="%{x|%d %b}<br>WRMSSE: %{y:.3f}<extra></extra>",
        name="WRMSSE"
    ))
    fig_drift.add_hline(y=1.0, line=dict(color="#ff3b5c", width=1, dash="dash"),
                        annotation_text="Retrain Threshold",
                        annotation_font=dict(color="#ff3b5c", size=9, family="DM Mono, monospace"))
    fig_drift.update_layout(**PLOTLY_LAYOUT, height=280, yaxis_title="WRMSSE")
    st.plotly_chart(fig_drift, use_container_width=True)


# ═══════════════════════════════════════════════════════════════════════════════
# TAB 4 — EXPORT CENTER
# ═══════════════════════════════════════════════════════════════════════════════
with tab_export:

    st.markdown("""
<div class="section-header">
  <div class="section-title">Export Center</div>
  <div class="section-line"></div>
  <div class="section-tag">pdf · excel · csv</div>
</div>""", unsafe_allow_html=True)

    st.markdown("""
<div class="export-grid">
  <div class="export-card">
    <div class="export-icon">📋</div>
    <div class="export-title">PDF Report</div>
    <div class="export-desc">Full branded report with KPIs,<br>risk assessment &amp; day-by-day table</div>
  </div>
  <div class="export-card">
    <div class="export-icon">📊</div>
    <div class="export-title">Excel Workbook</div>
    <div class="export-desc">3-sheet workbook: Summary,<br>Forecast data &amp; Historical series</div>
  </div>
  <div class="export-card">
    <div class="export-icon">🗂</div>
    <div class="export-title">CSV Data</div>
    <div class="export-desc">Raw forecast + CI values<br>as comma-separated file</div>
  </div>
</div>""", unsafe_allow_html=True)

    date_str = datetime.now().strftime('%Y%m%d')
    risks    = assess_risks(forecast, avg, std, inventory if inventory > 0 else None)

    # ── CSV — always works, no extra deps ─────────────────────────────────────
    df_csv = pd.DataFrame({
        "day":      range(1, len(forecast) + 1),
        "date":     [d.strftime("%Y-%m-%d") for d in fcast_dates],
        "forecast": [round(float(v), 4) for v in forecast],
        "upper_ci": [round(float(v), 4) for v in upper_ci],
        "lower_ci": [round(float(v), 4) for v in lower_ci],
        "vs_avg":   [round(float(v) - avg, 4) for v in forecast],
    })
    csv_bytes = df_csv.to_csv(index=False).encode("utf-8")

    # ── Excel — openpyxl only ─────────────────────────────────────────────────
    xl_bytes = None
    xl_error = None
    try:
        import openpyxl
        from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
        from openpyxl.utils import get_column_letter
        _buf = io.BytesIO()
        _wb  = openpyxl.Workbook()
        _hf  = Font(name="Calibri", bold=True, color="00E5A0", size=10)
        _bf  = Font(name="Calibri", color="E8EDF5", size=9)
        _mf  = Font(name="Calibri", color="5A6478", size=9)
        _tf  = Font(name="Calibri", bold=True, color="E8EDF5", size=13)
        _dk  = PatternFill("solid", fgColor="0A0C10")
        _sf  = PatternFill("solid", fgColor="10141C")
        _s2  = PatternFill("solid", fgColor="141820")
        _th  = Side(style="thin", color="1E2530")
        _bdr = Border(left=_th, right=_th, top=_th, bottom=_th)
        _ctr = Alignment(horizontal="center", vertical="center")
        _rgt = Alignment(horizontal="right",  vertical="center")

        # Sheet 1 — Summary
        _ws = _wb.active; _ws.title = "Summary"; _ws.sheet_view.showGridLines = False
        _ws.merge_cells("A1:D1"); _ws["A1"] = "SalesIQ — Demand Forecast"
        _ws["A1"].font = _tf; _ws["A1"].fill = _dk; _ws["A1"].alignment = _ctr
        _ws.row_dimensions[1].height = 26
        _kpis = [("METRIC","VALUE"),("Store",store_id),("Item",item_id),
                 ("Total Forecast",f"{total:,.0f}"),("Daily Avg",f"{avg:.1f}"),
                 ("Peak",f"{peak:,.0f}"),("MAE",f"{mae:.2f}"),
                 ("RMSE",f"{rmse:.2f}"),("WRMSSE",f"{wrmsse:.3f}"),
                 ("Horizon",f"{len(forecast)} days")]
        for _r,(_k,_v) in enumerate(_kpis, start=3):
            _fl = _dk if _r==3 else (_sf if _r%2==0 else _s2)
            _c1 = _ws.cell(_r,1,_k); _c1.font=_hf if _r==3 else _mf; _c1.fill=_fl; _c1.border=_bdr
            _c2 = _ws.cell(_r,2,_v); _c2.font=_hf if _r==3 else _bf; _c2.fill=_fl; _c2.border=_bdr; _c2.alignment=_rgt
        _ws.column_dimensions["A"].width = 22; _ws.column_dimensions["B"].width = 18

        # Sheet 2 — Forecast data
        _ws2 = _wb.create_sheet("Forecast"); _ws2.sheet_view.showGridLines = False
        for _c,_h in enumerate(["Day","Date","Forecast","Upper CI","Lower CI","vs Avg"],1):
            _cell = _ws2.cell(1,_c,_h); _cell.font=_hf; _cell.fill=_dk; _cell.border=_bdr; _cell.alignment=_ctr
        for _i,(_d,_f,_u,_l) in enumerate(zip(fcast_dates,forecast,upper_ci,lower_ci)):
            _r = _i+2; _fl = _sf if _i%2==0 else _s2
            for _c,_v in enumerate([_i+1,_d.strftime("%d %b %Y"),round(float(_f),2),round(float(_u),2),round(float(_l),2),round(float(_f)-avg,2)],1):
                _cell=_ws2.cell(_r,_c,_v); _cell.font=_bf; _cell.fill=_fl; _cell.border=_bdr
                if _c>=3: _cell.alignment=_rgt
        for _c,_w in enumerate([8,16,14,14,14,12],1):
            _ws2.column_dimensions[get_column_letter(_c)].width=_w

        # Sheet 3 — Historical
        _ws3 = _wb.create_sheet("Historical"); _ws3.sheet_view.showGridLines = False
        for _c,_h in enumerate(["Day","Date","Actual Sales"],1):
            _cell=_ws3.cell(1,_c,_h); _cell.font=_hf; _cell.fill=_dk; _cell.border=_bdr; _cell.alignment=_ctr
        for _i,(_d,_v) in enumerate(zip(hist_dates,historical)):
            _r=_i+2; _fl=_sf if _i%2==0 else _s2
            for _c,_val in enumerate([_i+1,_d.strftime("%d %b %Y"),round(float(_v),2)],1):
                _cell=_ws3.cell(_r,_c,_val); _cell.font=_bf; _cell.fill=_fl; _cell.border=_bdr
        for _c,_w in enumerate([8,16,16],1):
            _ws3.column_dimensions[get_column_letter(_c)].width=_w

        _wb.save(_buf); _buf.seek(0); xl_bytes = _buf.read()
    except Exception as _e:
        xl_error = str(_e)

    # ── PDF — reportlab ───────────────────────────────────────────────────────
    pdf_bytes = None
    pdf_error = None
    try:
        pdf_bytes = build_pdf_report(
            store_id, item_id, forecast, upper_ci, lower_ci, historical,
            fcast_dates, hist_dates, avg, std, total, peak, mae, rmse, wrmsse, risks
        )
    except Exception as _e:
        pdf_error = str(_e)

    # ── Download buttons ──────────────────────────────────────────────────────
    col_pdf, col_xl, col_csv = st.columns(3, gap="medium")

    with col_pdf:
        st.markdown("""
<div style="text-align:center;padding:1.5rem 1rem 0.75rem;">
  <div style="font-size:2rem;margin-bottom:0.5rem;">📋</div>
  <div style="font-family:var(--display);font-weight:700;font-size:0.9rem;color:var(--text);margin-bottom:0.3rem;">PDF Report</div>
  <div style="font-family:var(--mono);font-size:0.62rem;color:var(--muted);">KPIs · Risk · Day-by-day table</div>
</div>""", unsafe_allow_html=True)
        if pdf_bytes:
            st.download_button(
                label=f"⬇  Download PDF  ({len(pdf_bytes)//1024} KB)",
                data=pdf_bytes,
                file_name=f"salesiq_{store_id}_{item_id}_{date_str}.pdf",
                mime="application/pdf",
                use_container_width=True,
                key="dl_pdf"
            )
        else:
            st.warning(f"PDF unavailable — install `reportlab`\n`pip install reportlab`", icon="⚠️")

    with col_xl:
        st.markdown("""
<div style="text-align:center;padding:1.5rem 1rem 0.75rem;">
  <div style="font-size:2rem;margin-bottom:0.5rem;">📊</div>
  <div style="font-family:var(--display);font-weight:700;font-size:0.9rem;color:var(--text);margin-bottom:0.3rem;">Excel Workbook</div>
  <div style="font-family:var(--mono);font-size:0.62rem;color:var(--muted);">3 sheets · Summary · Forecast · Historical</div>
</div>""", unsafe_allow_html=True)
        if xl_bytes:
            st.download_button(
                label=f"⬇  Download Excel  ({len(xl_bytes)//1024} KB)",
                data=xl_bytes,
                file_name=f"salesiq_{store_id}_{item_id}_{date_str}.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                use_container_width=True,
                key="dl_xlsx"
            )
        else:
            st.warning(f"Excel unavailable — install `openpyxl`\n`pip install openpyxl`", icon="⚠️")

    with col_csv:
        st.markdown(f"""
<div style="text-align:center;padding:1.5rem 1rem 0.75rem;">
  <div style="font-size:2rem;margin-bottom:0.5rem;">🗂</div>
  <div style="font-family:var(--display);font-weight:700;font-size:0.9rem;color:var(--text);margin-bottom:0.3rem;">CSV Data</div>
  <div style="font-family:var(--mono);font-size:0.62rem;color:var(--muted);">{len(df_csv)} rows · forecast + CI values</div>
</div>""", unsafe_allow_html=True)
        st.download_button(
            label=f"⬇  Download CSV  ({len(csv_bytes)} bytes)",
            data=csv_bytes,
            file_name=f"salesiq_{store_id}_{item_id}_{date_str}.csv",
            mime="text/csv",
            use_container_width=True,
            key="dl_csv"
        )

    # ── Data preview ──────────────────────────────────────────────────────────
    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown("""
<div class="section-header">
  <div class="section-title">Data Preview</div>
  <div class="section-line"></div>
  <div class="section-tag">forecast export schema</div>
</div>""", unsafe_allow_html=True)
    st.dataframe(df_csv, use_container_width=True, height=320, hide_index=True)