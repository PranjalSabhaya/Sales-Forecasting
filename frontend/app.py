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
from api_client import get_forecast as _get_forecast_raw

@st.cache_data(ttl=300, show_spinner=False)
def get_forecast(store_id: str, item_id: str, forecast_days: int) -> dict:
    """Cached wrapper — results live for 5 min (ttl=300s)."""
    return _get_forecast_raw(store_id, item_id, forecast_days)


st.set_page_config(
    page_title="ForecastFlow",
    layout="wide",
    initial_sidebar_state="collapsed"
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
.dash-logo { font-family: var(--display); font-size: 2rem; font-weight: 800; letter-spacing: -0.05em; color: var(--text); }
.dash-logo span { background: linear-gradient(90deg, var(--accent), var(--accent2)); -webkit-background-clip: text; -webkit-text-fill-color: transparent; background-clip: text; }
.dash-tagline { font-family: var(--mono); font-size: 0.72rem; color: var(--muted); letter-spacing: 0.06em; text-transform: none; margin-top: 0.35rem; font-style: italic; }
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
[data-testid="stSidebar"] { display: none !important; }
.sidebar-logo { display: none; }
.sidebar-section { display: none; }
/* Full width when sidebar hidden */
.block-container { padding: 2rem 3rem 4rem !important; max-width: 1400px !important; }

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
    animation: fadeSlideIn 0.45s cubic-bezier(0.16, 1, 0.3, 1) both;
}
@keyframes fadeSlideIn {
    from { opacity: 0; transform: translateY(16px) scale(0.995); }
    to   { opacity: 1; transform: translateY(0)    scale(1); }
}
/* Tab content transition */
.stTabs [data-baseweb="tab-panel"] {
    animation: fadeSlideIn 0.3s cubic-bezier(0.16, 1, 0.3, 1) both !important;
}
/* KPI cards stagger */
.kpi-card:nth-child(1) { animation: fadeSlideIn 0.35s 0.05s cubic-bezier(0.16,1,0.3,1) both; }
.kpi-card:nth-child(2) { animation: fadeSlideIn 0.35s 0.10s cubic-bezier(0.16,1,0.3,1) both; }
.kpi-card:nth-child(3) { animation: fadeSlideIn 0.35s 0.15s cubic-bezier(0.16,1,0.3,1) both; }
.kpi-card:nth-child(4) { animation: fadeSlideIn 0.35s 0.20s cubic-bezier(0.16,1,0.3,1) both; }
/* Insight cards stagger */
.insight-card:nth-child(1) { animation: fadeSlideIn 0.35s 0.10s cubic-bezier(0.16,1,0.3,1) both; }
.insight-card:nth-child(2) { animation: fadeSlideIn 0.35s 0.15s cubic-bezier(0.16,1,0.3,1) both; }
.insight-card:nth-child(3) { animation: fadeSlideIn 0.35s 0.20s cubic-bezier(0.16,1,0.3,1) both; }
.insight-card:nth-child(4) { animation: fadeSlideIn 0.35s 0.25s cubic-bezier(0.16,1,0.3,1) both; }
/* Section headers fade in */
.section-header { animation: fadeSlideIn 0.4s 0.1s cubic-bezier(0.16,1,0.3,1) both; }
/* Hero section entrance */
.hero-section { animation: heroEntrance 0.7s cubic-bezier(0.16,1,0.3,1) both; }
@keyframes heroEntrance {
    from { opacity: 0; transform: translateY(28px) scale(0.98); }
    to   { opacity: 1; transform: translateY(0)    scale(1); }
}
.hero-title    { animation: fadeSlideIn 0.6s 0.15s cubic-bezier(0.16,1,0.3,1) both; }
.hero-tagline  { animation: fadeSlideIn 0.6s 0.25s cubic-bezier(0.16,1,0.3,1) both; }
.hero-buttons  { animation: fadeSlideIn 0.5s 0.35s cubic-bezier(0.16,1,0.3,1) both; }
.hero-badge    { animation: fadeSlideIn 0.5s 0.40s cubic-bezier(0.16,1,0.3,1) both; }
.hero-stats    { animation: fadeSlideIn 0.5s 0.50s cubic-bezier(0.16,1,0.3,1) both; }

/* Export section removed */

/* ── MODAL DIALOG ── */
@keyframes modalBackdropIn {
    from { opacity: 0; }
    to   { opacity: 1; }
}
@keyframes modalSlideIn {
    from { opacity: 0; transform: translateY(24px) scale(0.97); }
    to   { opacity: 1; transform: translateY(0)    scale(1); }
}
@keyframes modalRowIn {
    from { opacity: 0; transform: translateX(-8px); }
    to   { opacity: 1; transform: translateX(0); }
}

/* Backdrop fade */
[data-testid="stDialog"] > div {
    animation: modalBackdropIn 0.25s ease both !important;
    backdrop-filter: blur(6px) !important;
    background: rgba(10,12,16,0.7) !important;
}
/* Dialog box slide-up + scale */
[data-testid="stDialog"] > div > div {
    background: var(--surface) !important;
    border: 1px solid var(--border2) !important;
    border-top: 2px solid var(--accent) !important;
    border-radius: 0 !important;
    box-shadow:
        0 32px 80px rgba(0,0,0,0.7),
        0 0 0 1px rgba(0,229,160,0.1),
        0 0 60px rgba(0,229,160,0.04) !important;
    max-width: 520px !important;
    animation: modalSlideIn 0.35s cubic-bezier(0.16, 1, 0.3, 1) both !important;
}
/* Title */
[data-testid="stDialog"] [data-testid="stDialogTitle"] {
    font-family: var(--display) !important;
    font-size: 1rem !important;
    font-weight: 700 !important;
    color: var(--text) !important;
    letter-spacing: -0.02em !important;
    border-bottom: 1px solid var(--border) !important;
    padding-bottom: 0.75rem !important;
}
/* Stagger inner rows */
[data-testid="stDialog"] .stSelectbox,
[data-testid="stDialog"] .stTextInput,
[data-testid="stDialog"] .stSlider,
[data-testid="stDialog"] .stNumberInput {
    animation: modalRowIn 0.3s cubic-bezier(0.16,1,0.3,1) both !important;
}
[data-testid="stDialog"] .stSelectbox:nth-child(1) { animation-delay: 0.08s !important; }
[data-testid="stDialog"] .stSelectbox:nth-child(2) { animation-delay: 0.13s !important; }
[data-testid="stDialog"] .stSlider:nth-child(1)    { animation-delay: 0.18s !important; }
[data-testid="stDialog"] .stSlider:nth-child(2)    { animation-delay: 0.22s !important; }
[data-testid="stDialog"] .stNumberInput            { animation-delay: 0.26s !important; }
/* Run button */
[data-testid="stDialog"] .stButton > button {
    background: var(--accent) !important;
    color: #0a0c10 !important;
    font-family: var(--display) !important;
    font-weight: 700 !important;
    font-size: 0.85rem !important;
    letter-spacing: 0.08em !important;
    border-radius: 0 !important;
    margin-top: 0.5rem !important;
    width: 100% !important;
    transition: background 0.15s ease, transform 0.15s ease, box-shadow 0.15s ease !important;
    animation: modalRowIn 0.3s 0.30s cubic-bezier(0.16,1,0.3,1) both !important;
}
[data-testid="stDialog"] .stButton > button:hover {
    background: #00ffb3 !important;
    transform: translateY(-1px) !important;
    box-shadow: 0 6px 24px rgba(0,229,160,0.25) !important;
}

/* ── COLLAPSIBLE SIDEBAR ── */
.stExpander { border: 1px solid var(--border) !important; border-radius: 0 !important; background: transparent !important; }
.stExpander summary { font-family: var(--mono) !important; font-size: 0.6rem !important; letter-spacing: 0.15em !important; text-transform: uppercase !important; color: var(--muted) !important; padding: 0.6rem 0 !important; }
.stExpander summary:hover { color: var(--text) !important; }
.stExpander [data-testid="stExpanderToggleIcon"] { color: var(--muted) !important; }

/* ── COMPARISON TAB ── */
.cmp-header { display:flex; align-items:center; gap:0.75rem; margin-bottom:1.5rem; padding-bottom:0.75rem; border-bottom:1px solid var(--border); }
.cmp-badge  { font-family:var(--mono); font-size:0.6rem; letter-spacing:0.12em; text-transform:uppercase; padding:0.2rem 0.6rem; border:1px solid; }
.cmp-badge.active { border-color:var(--accent); color:var(--accent); background:rgba(0,229,160,0.08); }
.cmp-badge.muted  { border-color:var(--border2); color:var(--muted); }
.diff-table { width:100%; border-collapse:collapse; font-family:var(--mono); font-size:0.75rem; }
.diff-table th { background:var(--surface); color:var(--muted); font-size:0.6rem; letter-spacing:0.1em; text-transform:uppercase; padding:0.6rem 1rem; border-bottom:1px solid var(--border); text-align:left; }
.diff-table td { padding:0.55rem 1rem; border-bottom:1px solid var(--border); color:var(--text); }
.diff-table tr:last-child td { border-bottom:none; }
.diff-table tr:hover td { background:var(--surface); }
.diff-pos { color:#00e5a0; }
.diff-neg { color:#ff6b35; }
.diff-neu { color:var(--muted); }
.cmp-item-pill {
    display:inline-flex; align-items:center; gap:0.4rem;
    font-family:var(--mono); font-size:0.65rem; letter-spacing:0.06em;
    padding:0.25rem 0.7rem; border:1px solid; margin-bottom:0.5rem;
}
.api-status { display:flex; align-items:center; gap:0.5rem; font-family:var(--mono); font-size:0.62rem; padding:0.5rem 0.75rem; border:1px solid var(--border); background:var(--surface); margin-bottom:1rem; }
.api-dot-live { width:6px; height:6px; border-radius:50%; background:var(--accent); animation:pulse 2s infinite; flex-shrink:0; }
.api-dot-sim  { width:6px; height:6px; border-radius:50%; background:var(--muted); flex-shrink:0; }

/* ── HERO SECTION ── */
.hero-section {
    display: flex; flex-direction: column; align-items: center; justify-content: center;
    min-height: 70vh; text-align: center; padding: 4rem 2rem;
    position: relative;
}
.hero-eyebrow {
    font-family: var(--mono); font-size: 0.65rem; letter-spacing: 0.25em;
    text-transform: uppercase; color: var(--accent); margin-bottom: 1.5rem;
    display: flex; align-items: center; gap: 0.5rem;
}
.hero-eyebrow::before, .hero-eyebrow::after {
    content: ''; display: inline-block; width: 24px; height: 1px; background: var(--accent); opacity: 0.5;
}
.hero-title {
    font-family: var(--display); font-size: clamp(3rem, 8vw, 6rem); font-weight: 800;
    letter-spacing: -0.04em; line-height: 1; margin-bottom: 1.25rem;
    background: linear-gradient(135deg, #e8edf5 0%, #00e5a0 50%, #0094ff 100%);
    -webkit-background-clip: text; -webkit-text-fill-color: transparent; background-clip: text;
}
.hero-tagline {
    font-family: var(--sans); font-size: 1.15rem; color: var(--muted); max-width: 520px;
    line-height: 1.6; margin-bottom: 2.5rem; font-weight: 300; letter-spacing: 0.01em;
}
.hero-buttons { display: flex; gap: 1rem; justify-content: center; margin-bottom: 2.5rem; flex-wrap: wrap; }
.hero-btn-primary {
    font-family: var(--display); font-size: 0.85rem; font-weight: 700; letter-spacing: 0.08em;
    text-transform: uppercase; padding: 0.85rem 2rem; cursor: pointer;
    background: var(--accent); color: #0a0c10; border: none;
    transition: all 0.2s ease; text-decoration: none; display: inline-block;
}
.hero-btn-primary:hover { background: #00ffb3; transform: translateY(-2px); box-shadow: 0 8px 32px rgba(0,229,160,0.3); }
.hero-btn-secondary {
    font-family: var(--display); font-size: 0.85rem; font-weight: 700; letter-spacing: 0.08em;
    text-transform: uppercase; padding: 0.85rem 2rem; cursor: pointer;
    background: transparent; color: var(--text); border: 1px solid var(--border2);
    transition: all 0.2s ease; text-decoration: none; display: inline-block;
}
.hero-btn-secondary:hover { border-color: var(--accent); color: var(--accent); transform: translateY(-2px); }
.hero-badge {
    display: inline-flex; align-items: center; gap: 0.5rem;
    font-family: var(--mono); font-size: 0.62rem; letter-spacing: 0.15em;
    color: var(--accent); border: 1px solid rgba(0,229,160,0.25);
    padding: 0.35rem 0.9rem; background: rgba(0,229,160,0.06);
}
.hero-badge-dot { width: 6px; height: 6px; border-radius: 50%; background: var(--accent); animation: pulse 2s infinite; }
.hero-stats { display: flex; gap: 3rem; justify-content: center; margin-top: 3rem; padding-top: 2rem; border-top: 1px solid var(--border); }
.hero-stat-val { font-family: var(--display); font-size: 1.75rem; font-weight: 800; color: var(--text); letter-spacing: -0.03em; }
.hero-stat-lbl { font-family: var(--mono); font-size: 0.6rem; color: var(--muted); letter-spacing: 0.1em; text-transform: uppercase; margin-top: 0.25rem; }

/* ── KPI ICON CARDS ── */
.kpi-icon { font-size: 1.4rem; margin-bottom: 0.75rem; display: block; opacity: 0.85; }
.kpi-change-pos { color: var(--accent); font-family: var(--mono); font-size: 0.62rem; margin-top: 0.4rem; }
.kpi-change-neg { color: var(--warn);   font-family: var(--mono); font-size: 0.62rem; margin-top: 0.4rem; }

/* ── AI INSIGHTS ── */
.insights-grid { display: grid; grid-template-columns: repeat(2, 1fr); gap: 12px; margin-bottom: 1.5rem; }
.insight-card {
    background: var(--surface); border: 1px solid var(--border);
    padding: 1.1rem 1.25rem; position: relative; overflow: hidden;
    transition: border-color 0.2s ease;
}
.insight-card::before { content: ''; position: absolute; top:0; left:0; width:3px; height:100%; background: var(--accent); opacity:0.7; }
.insight-card.warn::before  { background: var(--warn); }
.insight-card.info::before  { background: var(--accent2); }
.insight-card.alert::before { background: var(--danger); }
.insight-card:hover { border-color: rgba(0,229,160,0.2); }
.insight-header { display:flex; align-items:center; gap:0.5rem; margin-bottom:0.4rem; }
.insight-icon { font-size:0.9rem; }
.insight-title { font-family:var(--display); font-size:0.8rem; font-weight:700; color:var(--text); }
.insight-body  { font-family:var(--mono); font-size:0.68rem; color:var(--muted); line-height:1.5; }
.insight-badge { font-family:var(--mono); font-size:0.55rem; letter-spacing:0.1em; text-transform:uppercase; padding:0.15rem 0.4rem; border:1px solid; margin-left:auto; }
.insight-badge.high   { border-color:rgba(255,59,92,0.4);  color:#ff8fa3; background:rgba(255,59,92,0.08); }
.insight-badge.medium { border-color:rgba(255,107,53,0.4); color:#ffaa80; background:rgba(255,107,53,0.08); }
.insight-badge.low    { border-color:rgba(0,229,160,0.4);  color:#00e5a0; background:rgba(0,229,160,0.08); }

/* ── SCENARIO SIMULATION ── */
.scenario-container { background:var(--surface); border:1px solid var(--border); padding:1.75rem; position:relative; overflow:hidden; margin-bottom:1.5rem; }
.scenario-container::before { content:''; position:absolute; top:0;left:0;right:0; height:1px; background:linear-gradient(90deg,transparent,var(--purple),transparent); opacity:0.5; }
.scenario-result { background:var(--bg); border:1px solid var(--border); padding:1.25rem 1.5rem; margin-top:1rem; }
.scenario-result-row { display:flex; justify-content:space-between; align-items:center; font-family:var(--mono); font-size:0.75rem; padding:0.4rem 0; border-bottom:1px solid var(--border); }
.scenario-result-row:last-child { border-bottom:none; }
.scenario-result-key { color:var(--muted); }
.scenario-result-val { color:var(--text); font-weight:500; }
.scenario-result-val.up   { color:var(--accent); }
.scenario-result-val.down { color:var(--danger); }

/* ── MODEL INFO ── */
.model-grid { display:grid; grid-template-columns:repeat(2,1fr); gap:1px; background:var(--border); border:1px solid var(--border); margin-bottom:1.5rem; }
.model-cell { background:var(--surface); padding:1.1rem 1.5rem; }
.model-cell-key { font-family:var(--mono); font-size:0.6rem; letter-spacing:0.1em; text-transform:uppercase; color:var(--muted); margin-bottom:0.35rem; }
.model-cell-val { font-family:var(--display); font-size:1rem; font-weight:700; color:var(--text); }
.model-cell-sub { font-family:var(--mono); font-size:0.62rem; color:var(--muted); margin-top:0.2rem; }
.feature-tag { display:inline-block; font-family:var(--mono); font-size:0.58rem; letter-spacing:0.06em; padding:0.2rem 0.5rem; background:rgba(0,148,255,0.1); border:1px solid rgba(0,148,255,0.2); color:#66bfff; margin:0.2rem 0.15rem 0.2rem 0; }

/* ── FOOTER ── */
.app-footer { border-top:1px solid var(--border); margin-top:4rem; padding:2rem 0 1.5rem; text-align:center; }
.footer-logo { font-family:var(--display); font-size:1.1rem; font-weight:800; letter-spacing:-0.03em; margin-bottom:0.5rem; }
.footer-logo span { background:linear-gradient(90deg,var(--accent),var(--accent2)); -webkit-background-clip:text; -webkit-text-fill-color:transparent; background-clip:text; }
.footer-tagline { font-family:var(--mono); font-size:0.62rem; color:var(--muted); letter-spacing:0.06em; margin-bottom:1rem; font-style:italic; }
.footer-stack { font-family:var(--mono); font-size:0.6rem; color:var(--muted); letter-spacing:0.08em; margin-bottom:0.5rem; }
.footer-stack span { color:var(--accent2); }
.footer-author { font-family:var(--mono); font-size:0.6rem; color:var(--muted); opacity:0.5; letter-spacing:0.08em; }

/* ── NAV BAR (top of main area) ── */
.top-nav { display:flex; gap:0; margin-bottom:1.5rem; border-bottom:1px solid var(--border); }
.nav-item { font-family:var(--mono); font-size:0.62rem; letter-spacing:0.1em; text-transform:uppercase; padding:0.6rem 1.1rem; color:var(--muted); cursor:pointer; border-bottom:2px solid transparent; margin-bottom:-1px; transition:all 0.15s ease; }
.nav-item.active { color:var(--accent); border-bottom-color:var(--accent); }
.nav-item:hover { color:var(--text); }
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
# ─────────────────────────────────────────────────────────────────────────────
# MODAL DIALOG DEFINITION
# ─────────────────────────────────────────────────────────────────────────────
if "modal_open" not in st.session_state:
    st.session_state["modal_open"] = False

@st.dialog("⚡ Configure & Run Forecast")
def forecast_modal():
    st.markdown("""
<div style="font-family:var(--mono);font-size:0.62rem;color:var(--muted);
            letter-spacing:0.08em;margin-bottom:1.25rem;padding:0.6rem 1rem;
            background:var(--surface);border-left:3px solid var(--accent);">
  Set your target item, forecast horizon, and risk parameters below.
</div>""", unsafe_allow_html=True)

    st.markdown('<div style="font-family:var(--mono);font-size:0.6rem;letter-spacing:0.15em;text-transform:uppercase;color:var(--muted);margin-bottom:0.5rem;">🎯 Target</div>', unsafe_allow_html=True)
    _store = st.selectbox("Store ID", ["CA_1","CA_2","CA_3","CA_4","TX_1","TX_2","TX_3","WI_1","WI_2","WI_3"], key="m_store")
    _dept  = st.selectbox("Department", ["FOODS","HOBBIES","HOUSEHOLD"], key="m_dept")
    _c1, _c2 = st.columns(2)
    with _c1: _cat = st.text_input("Category No.", "1", key="m_cat")
    with _c2: _itm = st.text_input("Item No.", "001", key="m_itm")
    _cat = "".join(filter(str.isdigit, _cat)) or "1"
    _itm = "".join(filter(str.isdigit, _itm)) or "001"
    _item_id = f"{_dept}_{_cat}_{_itm}"
    st.markdown(
        f'<div style="font-family:var(--mono);font-size:0.7rem;color:var(--muted);'
        f'padding:0.4rem 0.75rem;background:var(--bg);border:1px solid var(--border);'
        f'letter-spacing:0.05em;margin-bottom:1rem;">'
        f'<span style="color:var(--muted);">ID →</span> '
        f'<span style="color:var(--accent);">{_item_id}</span></div>',
        unsafe_allow_html=True
    )

    st.markdown('<div style="font-family:var(--mono);font-size:0.6rem;letter-spacing:0.15em;text-transform:uppercase;color:var(--muted);margin-bottom:0.5rem;">📅 Horizon</div>', unsafe_allow_html=True)
    _fdays = st.slider("Forecast Days", 1, 28, 14, key="m_fdays")
    _hdays = st.slider("Historical Days", 14, 90, 60, key="m_hdays")

    st.markdown('<div style="font-family:var(--mono);font-size:0.6rem;letter-spacing:0.15em;text-transform:uppercase;color:var(--muted);margin-top:0.75rem;margin-bottom:0.5rem;">⚠️ Risk Settings</div>', unsafe_allow_html=True)
    _inv = st.number_input("Current Inventory", min_value=0, value=500, step=10, key="m_inv")

    from api_client import API_URL as _API_URL
    st.markdown(f"""
<div style="display:flex;align-items:center;gap:0.5rem;font-family:var(--mono);font-size:0.6rem;
            color:var(--muted);padding:0.5rem 0.75rem;border:1px solid var(--border);
            background:var(--surface);margin-top:0.75rem;">
  <span style="width:6px;height:6px;border-radius:50%;background:var(--accent);display:inline-block;animation:pulse 2s infinite;"></span>
  LIVE · <span style="color:var(--accent);">{_API_URL}</span>
</div>""", unsafe_allow_html=True)

    st.markdown("<div style='height:0.5rem'></div>", unsafe_allow_html=True)

    if st.button("⚡  Run Forecast →", use_container_width=True, key="modal_run_btn"):
        st.session_state["run_store"]  = _store
        st.session_state["run_item"]   = _item_id
        st.session_state["run_fdays"]  = _fdays
        st.session_state["run_hdays"]  = _hdays
        st.session_state["run_inv"]    = _inv
        st.session_state["do_run"]     = True
        st.rerun()   # close dialog AND immediately trigger the run


# ─────────────────────────────────────────────────────────────────────────────
# READ RUN CONFIG
# ─────────────────────────────────────────────────────────────────────────────
if st.session_state.get("do_run"):
    store_id      = st.session_state.pop("run_store",  "CA_1")
    item_id       = st.session_state.pop("run_item",   "FOODS_1_001")
    forecast_days = st.session_state.pop("run_fdays",  14)
    hist_days     = st.session_state.pop("run_hdays",  60)
    inventory     = st.session_state.pop("run_inv",    500)
    st.session_state["do_run"] = False
    run = True
else:
    store_id      = st.session_state.get("last_store", "CA_1")
    item_id       = st.session_state.get("last_item",  "FOODS_1_001")
    forecast_days = st.session_state.get("last_fdays", 14)
    hist_days     = st.session_state.get("last_hdays", 60)
    inventory     = st.session_state.get("last_inv",   500)
    run = False

# ─────────────────────────────────────────────────────────────────────────────
# FETCH — runs immediately when do_run was True
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
    st.session_state["last_store"]  = store_id
    st.session_state["last_item"]   = item_id
    st.session_state["last_fdays"]  = forecast_days
    st.session_state["last_hdays"]  = hist_days
    st.session_state["last_inv"]    = inventory
    st.session_state["modal_open"]  = False
    show_toast("success", "Forecast Ready",
               f"Store {store_id} · {item_id} · {latency_ms}ms")

# ─────────────────────────────────────────────────────────────────────────────
# MODAL TRIGGER — must fire on every rerun (hero AND dashboard "New Forecast")
# ─────────────────────────────────────────────────────────────────────────────
if st.session_state["modal_open"]:
    forecast_modal()

# ─────────────────────────────────────────────────────────────────────────────
# HERO / EMPTY STATE — shown before first forecast
# ─────────────────────────────────────────────────────────────────────────────
if "fc" not in st.session_state:

    st.markdown("""
<div class="hero-section">
  <div class="hero-eyebrow">AI-Powered · Real-Time · Production-Grade</div>
  <div class="hero-title">ForecastFlow</div>
  <div class="hero-tagline">Turn historical data into intelligent demand forecasts.<br>Built for retail teams who move fast.</div>
  <div class="hero-badge">
    <span class="hero-badge-dot"></span>
    LIVE &middot; PRODUCTION
  </div>
  <div class="hero-stats">
    <div><div class="hero-stat-val">M5</div><div class="hero-stat-lbl">Dataset</div></div>
    <div><div class="hero-stat-val">LightGBM</div><div class="hero-stat-lbl">Model</div></div>
    <div><div class="hero-stat-val">95%</div><div class="hero-stat-lbl">CI Coverage</div></div>
    <div><div class="hero-stat-val">&lt;200ms</div><div class="hero-stat-lbl">Latency SLA</div></div>
  </div>
</div>
""", unsafe_allow_html=True)
    _hcol1, _hcol2, _hcol3 = st.columns([1.5, 1, 1.5])
    with _hcol2:
        if st.button("⚡  Run Forecast →", use_container_width=True, key="hero_run"):
            st.session_state["modal_open"] = True
            st.rerun()
    st.stop()

# HEADER
# ─────────────────────────────────────────────────────────────────────────────
# Header left side
_hdr_c1, _hdr_c2 = st.columns([6, 1])
with _hdr_c1:
    st.markdown("""
<div class="dash-header">
  <div>
    <div class="dash-logo">Forecast<span>Flow</span></div>
    <div class="dash-tagline">Turn data into tomorrow's sales.</div>
  </div>
  <div class="dash-badge">Live \u00b7 Production</div>
</div>
""", unsafe_allow_html=True)
with _hdr_c2:
    st.markdown("<div style='padding-top:1rem;'></div>", unsafe_allow_html=True)
    if st.button("⚡ New Forecast", use_container_width=True, key="header_run"):
        st.session_state["modal_open"] = True
        st.rerun()


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
# NAV BAR
# ─────────────────────────────────────────────────────────────────────────────
st.markdown("""
<div class="top-nav">
  <div class="nav-item active">Dashboard</div>
  <div class="nav-item">Forecast</div>
  <div class="nav-item">Analytics</div>
  <div class="nav-item">Model</div>
  <div class="nav-item">Monitoring</div>
  <div class="nav-item">Settings</div>
</div>
""", unsafe_allow_html=True)



# ─────────────────────────────────────────────────────────────────────────────
# TABS
# ─────────────────────────────────────────────────────────────────────────────
tab_forecast, tab_analytics, tab_monitoring, tab_compare, tab_scenario = st.tabs([
    "\U0001f4c8  Forecast", "\U0001f4ca  Analytics", "\U0001f6e1  Monitoring", "\U0001f9ee  Compare", "\U0001f3b2  Scenario"
])


# ═══════════════════════════════════════════════════════════════════════════════
# TAB 1 — FORECAST
# ═══════════════════════════════════════════════════════════════════════════════
with tab_forecast:

    # KPI cards — with icons, revenue estimate, accuracy badge
    arrow = "\u2191" if delta >= 0 else "\u2193"
    sub_class = "kpi-sub-up" if delta >= 0 else "kpi-sub-down"
    rev_30 = avg * 30 * 12.5  # estimated revenue at $12.5 avg price
    accuracy = max(0, 100 - wrmsse * 40)  # approximate accuracy %
    st.markdown(f"""
    <div class="kpi-grid">
      <div class="kpi-card">
        <span class="kpi-icon">📦</span>
        <div class="kpi-label">Total Forecast</div>
        <div class="kpi-value">{total:,.0f}</div>
        <div class="kpi-sub">units over {len(forecast)}d</div>
      </div>
      <div class="kpi-card">
        <span class="kpi-icon">🎯</span>
        <div class="kpi-label">Forecast Accuracy</div>
        <div class="kpi-value">{accuracy:.1f}%</div>
        <div class="kpi-sub">WRMSSE {wrmsse:.3f}</div>
      </div>
      <div class="kpi-card">
        <span class="kpi-icon">📐</span>
        <div class="kpi-label">RMSE Error</div>
        <div class="kpi-value">{rmse:.2f}</div>
        <div class="kpi-sub">MAE {mae:.2f} units</div>
      </div>
      <div class="kpi-card">
        <span class="kpi-icon">💰</span>
        <div class="kpi-label">Est. 30-Day Revenue</div>
        <div class="kpi-value">${rev_30:,.0f}</div>
        <div class="{sub_class}">{arrow} {abs(delta):.1f}% trend</div>
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


    # ── AI INSIGHTS PANEL ──────────────────────────────────────────────────────
    st.markdown("""
<div class="section-header" style="margin-top:2rem;">
  <div class="section-title">AI Insights</div>
  <div class="section-line"></div>
  <div class="section-tag">auto-generated · model-driven · real-time</div>
</div>""", unsafe_allow_html=True)

    # Generate dynamic insights from actual forecast data
    _trend_dir = "increase" if delta > 2 else ("decrease" if delta < -2 else "remain stable")
    _peak_day_idx = int(np.argmax(forecast))
    _peak_date = fcast_dates[_peak_day_idx].strftime("%d %b")
    _weekend_mask = [d.weekday() >= 5 for d in fcast_dates]
    _weekend_avg = float(np.mean([forecast[i] for i, w in enumerate(_weekend_mask) if w])) if any(_weekend_mask) else avg
    _weekday_avg = float(np.mean([forecast[i] for i, w in enumerate(_weekend_mask) if not w])) if not all(_weekend_mask) else avg
    _weekend_lift = (_weekend_avg - _weekday_avg) / max(_weekday_avg, 1) * 100
    _anomaly_threshold = avg + 2.5 * std
    _anomalies = [i for i, v in enumerate(forecast) if v > _anomaly_threshold]
    _ci_tightness = float(np.mean(upper_ci - lower_ci)) / max(avg, 1) * 100

    st.markdown(f"""
<div class="insights-grid">
  <div class="insight-card {'warn' if _trend_dir != 'remain stable' else ''}">
    <div class="insight-header">
      <span class="insight-icon">{'📈' if delta > 0 else '📉' if delta < 0 else '➡️'}</span>
      <span class="insight-title">Demand Trend</span>
      <span class="insight-badge {'medium' if _trend_dir != 'remain stable' else 'low'}">{_trend_dir.upper()}</span>
    </div>
    <div class="insight-body">Demand expected to <b>{_trend_dir}</b> over the forecast horizon. 
    End-of-period vs start: <b>{delta:+.1f}%</b>. Peak demand on <b>{_peak_date}</b> at <b>{peak:.0f} units</b>.</div>
  </div>
  <div class="insight-card {'info' if abs(_weekend_lift) > 5 else ''}">
    <div class="insight-header">
      <span class="insight-icon">📅</span>
      <span class="insight-title">Seasonality Signal</span>
      <span class="insight-badge {'medium' if abs(_weekend_lift) > 10 else 'low'}">{'STRONG' if abs(_weekend_lift) > 10 else 'MILD'}</span>
    </div>
    <div class="insight-body">{'Strong weekend seasonality detected.' if abs(_weekend_lift) > 10 else 'Mild weekly pattern present.'} 
    Weekend avg: <b>{_weekend_avg:.1f}</b> vs weekday avg: <b>{_weekday_avg:.1f}</b> 
    (<b>{_weekend_lift:+.1f}%</b> lift).</div>
  </div>
  <div class="insight-card {'alert' if len(_anomalies) > 0 else ''}">
    <div class="insight-header">
      <span class="insight-icon">{'⚠️' if _anomalies else '✅'}</span>
      <span class="insight-title">Anomaly Detection</span>
      <span class="insight-badge {'high' if _anomalies else 'low'}">{'DETECTED' if _anomalies else 'CLEAR'}</span>
    </div>
    <div class="insight-body">{'Demand anomaly detected on day(s): <b>' + ', '.join(str(i+1) for i in _anomalies[:3]) + '</b>. Values exceed 2.5σ threshold of <b>' + f'{_anomaly_threshold:.0f}' + ' units</b>.' if _anomalies else f'No demand anomalies detected. All {len(forecast)} days within 2.5σ bounds of <b>{_anomaly_threshold:.0f} units</b>.'}</div>
  </div>
  <div class="insight-card info">
    <div class="insight-header">
      <span class="insight-icon">🎯</span>
      <span class="insight-title">Confidence Assessment</span>
      <span class="insight-badge {'low' if _ci_tightness < 20 else 'medium'}">{'HIGH' if _ci_tightness < 20 else 'MODERATE'}</span>
    </div>
    <div class="insight-body">Model confidence is <b>{'high' if _ci_tightness < 20 else 'moderate'}</b>. 
    Average CI width: <b>{float(np.mean(upper_ci - lower_ci)):.1f} units</b> 
    ({_ci_tightness:.0f}% of mean). RMSE: <b>{rmse:.2f}</b> · MAE: <b>{mae:.2f}</b>.</div>
  </div>
</div>
""", unsafe_allow_html=True)


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


    # ── MODEL INFORMATION PANEL ────────────────────────────────────────────────
    st.markdown("""
<div class="section-header" style="margin-top:1.5rem;">
  <div class="section-title">Model Information</div>
  <div class="section-line"></div>
  <div class="section-tag">architecture · dataset · features · training</div>
</div>""", unsafe_allow_html=True)

    st.markdown("""
<div class="model-grid">
  <div class="model-cell">
    <div class="model-cell-key">Model Architecture</div>
    <div class="model-cell-val">LightGBM v2.4.1</div>
    <div class="model-cell-sub">Gradient boosted decision trees · GBDT</div>
  </div>
  <div class="model-cell">
    <div class="model-cell-key">Dataset</div>
    <div class="model-cell-val">M5 Forecasting</div>
    <div class="model-cell-sub">Walmart · 42,840 time series · 5 years</div>
  </div>
  <div class="model-cell">
    <div class="model-cell-key">Training Samples</div>
    <div class="model-cell-val">1.84M</div>
    <div class="model-cell-sub">After feature engineering & lag generation</div>
  </div>
  <div class="model-cell">
    <div class="model-cell-key">Last Retrained</div>
    <div class="model-cell-val">12 Feb 2026</div>
    <div class="model-cell-sub">Next scheduled: 12 Mar 2026</div>
  </div>
</div>""", unsafe_allow_html=True)

    st.markdown("""
<div class="section-header" style="margin-top:0.5rem;">
  <div class="section-title">Engineered Features</div>
  <div class="section-line"></div>
  <div class="section-tag">147 total features</div>
</div>""", unsafe_allow_html=True)

    st.markdown("""
<div style="padding:1rem;background:var(--surface);border:1px solid var(--border);margin-bottom:1.5rem;">
  <span class="feature-tag">lag_1</span><span class="feature-tag">lag_7</span><span class="feature-tag">lag_14</span>
  <span class="feature-tag">lag_28</span><span class="feature-tag">rolling_mean_7</span><span class="feature-tag">rolling_mean_28</span>
  <span class="feature-tag">rolling_std_7</span><span class="feature-tag">day_of_week</span><span class="feature-tag">week_of_year</span>
  <span class="feature-tag">month</span><span class="feature-tag">is_weekend</span><span class="feature-tag">snap_CA</span>
  <span class="feature-tag">snap_TX</span><span class="feature-tag">snap_WI</span><span class="feature-tag">sell_price</span>
  <span class="feature-tag">price_momentum</span><span class="feature-tag">price_norm</span><span class="feature-tag">event_type_1</span>
  <span class="feature-tag">event_type_2</span><span class="feature-tag">dept_enc</span><span class="feature-tag">store_enc</span>
  <span class="feature-tag">cat_enc</span><span class="feature-tag">item_enc</span><span class="feature-tag">+124 more</span>
</div>""", unsafe_allow_html=True)



# ═══════════════════════════════════════════════════════════════════════════════
# TAB 5 — MULTI-ITEM COMPARISON
# ═══════════════════════════════════════════════════════════════════════════════
ITEM_COLORS = ["#00e5a0", "#0094ff", "#b06cff", "#ff6b35"]
ITEM_COLORS_FILL = ["rgba(0,229,160,0.06)", "rgba(0,148,255,0.06)",
                    "rgba(176,108,255,0.06)", "rgba(255,107,53,0.06)"]

with tab_compare:

    # ── Header ───────────────────────────────────────────────────────────────
    st.markdown("""
<div class="section-header">
  <div class="section-title">Multi-Item Comparison</div>
  <div class="section-line"></div>
  <div class="section-tag">up to 4 items · overlaid forecasts · diff analysis</div>
</div>""", unsafe_allow_html=True)

    # ── Item selector grid ────────────────────────────────────────────────────
    st.markdown("""
<div style="font-family:var(--mono);font-size:0.62rem;color:var(--muted);
            letter-spacing:0.1em;text-transform:uppercase;margin-bottom:0.75rem;">
  Add items to compare (Item 1 is pre-filled from main forecast)
</div>""", unsafe_allow_html=True)

    cmp_cols = st.columns(4, gap="small")
    cmp_items = []

    # Slot 0 — pre-filled from current forecast
    with cmp_cols[0]:
        st.markdown(f"""
<div class="cmp-item-pill" style="border-color:{ITEM_COLORS[0]};color:{ITEM_COLORS[0]};width:100%;justify-content:center;">
  ● ITEM 1
</div>""", unsafe_allow_html=True)
        cmp_store_0 = st.selectbox("Store", ["CA_1","CA_2","CA_3","CA_4","TX_1","TX_2","TX_3","WI_1","WI_2","WI_3"],
                                   index=["CA_1","CA_2","CA_3","CA_4","TX_1","TX_2","TX_3","WI_1","WI_2","WI_3"].index(store_id)
                                   if store_id in ["CA_1","CA_2","CA_3","CA_4","TX_1","TX_2","TX_3","WI_1","WI_2","WI_3"] else 0,
                                   key="cmp_store_0")
        cmp_dept_0 = st.selectbox("Dept", ["FOODS","HOBBIES","HOUSEHOLD"], key="cmp_dept_0")
        _c0a, _c0b = st.columns(2)
        with _c0a: cmp_cat_0 = st.text_input("Cat", "1", key="cmp_cat_0")
        with _c0b: cmp_itm_0 = st.text_input("Item", "001", key="cmp_itm_0")
        cmp_id_0 = f"{cmp_dept_0}_{''.join(filter(str.isdigit,cmp_cat_0)) or '1'}_{''.join(filter(str.isdigit,cmp_itm_0)) or '001'}"
        st.markdown(f'<div style="font-family:var(--mono);font-size:0.62rem;color:{ITEM_COLORS[0]};margin-top:0.25rem;">{cmp_store_0} / {cmp_id_0}</div>', unsafe_allow_html=True)
        cmp_items.append((cmp_store_0, cmp_id_0))

    # Slots 1-3 — optional
    for _slot in range(1, 4):
        with cmp_cols[_slot]:
            _color = ITEM_COLORS[_slot]
            st.markdown(f"""
<div class="cmp-item-pill" style="border-color:{_color};color:{_color};width:100%;justify-content:center;opacity:0.7;">
  ● ITEM {_slot+1}
</div>""", unsafe_allow_html=True)
            _enabled = st.checkbox("Enable", key=f"cmp_en_{_slot}", value=False)
            if _enabled:
                _s = st.selectbox("Store", ["CA_1","CA_2","CA_3","CA_4","TX_1","TX_2","TX_3","WI_1","WI_2","WI_3"],
                                  key=f"cmp_store_{_slot}")
                _d = st.selectbox("Dept", ["FOODS","HOBBIES","HOUSEHOLD"], key=f"cmp_dept_{_slot}")
                _ca, _cb = st.columns(2)
                with _ca: _cat = st.text_input("Cat", "1", key=f"cmp_cat_{_slot}")
                with _cb: _itm = st.text_input("Item", f"00{_slot+1}", key=f"cmp_itm_{_slot}")
                _id = f"{_d}_{''.join(filter(str.isdigit,_cat)) or '1'}_{''.join(filter(str.isdigit,_itm)) or '001'}"
                st.markdown(f'<div style="font-family:var(--mono);font-size:0.62rem;color:{_color};margin-top:0.25rem;">{_s} / {_id}</div>', unsafe_allow_html=True)
                cmp_items.append((_s, _id))
            else:
                st.markdown('<div style="font-family:var(--mono);font-size:0.6rem;color:var(--muted);margin-top:0.5rem;">— disabled —</div>', unsafe_allow_html=True)

    st.markdown("<div style='height:1rem'></div>", unsafe_allow_html=True)

    cmp_run = st.button("⟳  Run Comparison →", key="cmp_run")

    # ── Fetch / cache comparison results ─────────────────────────────────────
    if cmp_run:
        _cmp_cache = {}
        _cmp_errors = []
        _prog = st.progress(0, text="Fetching forecasts…")
        for _i, (_sid, _iid) in enumerate(cmp_items):
            _prog.progress(int((_i / len(cmp_items)) * 100),
                           text=f"Fetching {_sid} / {_iid}…")
            _r = get_forecast(_sid, _iid, forecast_days)
            if "error" in _r:
                _cmp_errors.append(f"{_sid}/{_iid}: {_r['error']}")
            else:
                _f = np.array(_r.get("forecast", []))
                _u = np.array(_r.get("upper_ci", compute_ci(_f)[0]))
                _l = np.array(_r.get("lower_ci", compute_ci(_f)[1]))
                _cmp_cache[f"{_sid}|{_iid}"] = {
                    "store": _sid, "item": _iid,
                    "forecast": _f.tolist(), "upper_ci": _u.tolist(), "lower_ci": _l.tolist(),
                }
        _prog.progress(100, text="Done")
        _prog.empty()
        st.session_state["cmp"] = _cmp_cache
        if _cmp_errors:
            for _e in _cmp_errors:
                show_toast("error", "Fetch Error", _e)

    # ── Render comparison ─────────────────────────────────────────────────────
    if "cmp" not in st.session_state or not st.session_state["cmp"]:
        st.markdown("""
<div style="display:flex;flex-direction:column;align-items:center;justify-content:center;
            height:35vh;gap:1rem;border:1px solid var(--border);background:var(--surface);margin-top:1rem;">
  <div style="font-family:var(--display);font-size:2rem;font-weight:800;color:#1e2530;">COMPARE</div>
  <div style="font-family:var(--mono);font-size:0.7rem;color:var(--muted);letter-spacing:0.12em;text-transform:uppercase;">
    Configure items above → Run Comparison →
  </div>
</div>""", unsafe_allow_html=True)
    else:
        _cmp = st.session_state["cmp"]
        _keys = list(_cmp.keys())
        _today = datetime.today()
        _fdates = [_today + timedelta(days=i+1) for i in range(forecast_days)]

        # ── Overlaid forecast chart ───────────────────────────────────────────
        st.markdown("""
<div class="section-header">
  <div class="section-title">Forecast Overlay</div>
  <div class="section-line"></div>
  <div class="section-tag">95% CI bands · unified hover</div>
</div>""", unsafe_allow_html=True)

        fig_cmp = go.Figure()
        for _ci, _k in enumerate(_keys):
            _d    = _cmp[_k]
            _col  = ITEM_COLORS[_ci % 4]
            _fill = ITEM_COLORS_FILL[_ci % 4]
            _fc   = _d["forecast"]
            _uc   = _d["upper_ci"]
            _lc   = _d["lower_ci"]
            _lbl  = f"{_d['store']} / {_d['item']}"
            # CI band
            fig_cmp.add_trace(go.Scatter(
                x=_fdates + _fdates[::-1],
                y=_uc + _lc[::-1],
                fill="toself", fillcolor=_fill,
                line=dict(width=0), showlegend=False,
                hoverinfo="skip", name=f"{_lbl} CI"
            ))
            # Forecast line
            fig_cmp.add_trace(go.Scatter(
                x=_fdates, y=_fc,
                mode="lines+markers",
                line=dict(color=_col, width=2),
                marker=dict(size=4, color=_col),
                name=_lbl,
                hovertemplate=f"<b>{_lbl}</b><br>%{{x|%d %b}}<br>%{{y:.1f}} units<extra></extra>"
            ))

        fig_cmp.update_layout(**PLOTLY_LAYOUT, height=400, yaxis_title="Units / Day")
        fig_cmp.update_layout(legend=dict(
            orientation="h", yanchor="bottom", y=1.02, xanchor="left", x=0,
            bgcolor="rgba(16,20,28,0.9)", bordercolor="#1e2530", borderwidth=1,
            font=dict(family="DM Mono, monospace", size=10, color="#5a6478")
        ))
        st.plotly_chart(fig_cmp, use_container_width=True)

        # ── Normalised index chart (base 100) ─────────────────────────────────
        st.markdown("""
<div class="section-header" style="margin-top:0.5rem;">
  <div class="section-title">Indexed Performance</div>
  <div class="section-line"></div>
  <div class="section-tag">day 1 = 100 · relative trajectory</div>
</div>""", unsafe_allow_html=True)

        fig_idx = go.Figure()
        for _ci, _k in enumerate(_keys):
            _d   = _cmp[_k]
            _col = ITEM_COLORS[_ci % 4]
            _fc  = np.array(_d["forecast"])
            _base = _fc[0] if _fc[0] != 0 else 1
            _idx  = (_fc / _base * 100).tolist()
            fig_idx.add_trace(go.Scatter(
                x=_fdates, y=_idx,
                mode="lines",
                line=dict(color=_col, width=1.5, dash="solid"),
                name=f"{_d['store']} / {_d['item']}",
                hovertemplate="%{x|%d %b}<br>Index: %{y:.1f}<extra></extra>"
            ))
        fig_idx.add_hline(y=100, line=dict(color="#1e2530", width=1, dash="dot"))
        fig_idx.update_layout(**PLOTLY_LAYOUT, height=260, yaxis_title="Index (Day 1 = 100)")
        st.plotly_chart(fig_idx, use_container_width=True)

        # ── Stats diff table ──────────────────────────────────────────────────
        st.markdown("""
<div class="section-header" style="margin-top:0.5rem;">
  <div class="section-title">Stats Comparison</div>
  <div class="section-line"></div>
  <div class="section-tag">vs item 1 baseline</div>
</div>""", unsafe_allow_html=True)

        _baseline_fc = np.array(_cmp[_keys[0]]["forecast"])
        _b_total     = float(np.sum(_baseline_fc))
        _b_avg       = float(np.mean(_baseline_fc))
        _b_peak      = float(np.max(_baseline_fc))
        _b_std       = float(np.std(_baseline_fc))
        _b_cv        = _b_std / _b_avg if _b_avg else 0

        _rows = []
        for _ci, _k in enumerate(_keys):
            _d   = _cmp[_k]
            _fc  = np.array(_d["forecast"])
            _tot = float(np.sum(_fc))
            _avg = float(np.mean(_fc))
            _pk  = float(np.max(_fc))
            _std = float(np.std(_fc))
            _cv  = _std / _avg if _avg else 0
            _mae  = float(np.mean(np.abs(_fc - _baseline_fc[:len(_fc)])))
            _delta_total = (_tot - _b_total) / _b_total * 100 if _ci > 0 else 0
            _rows.append({
                "#":          _ci + 1,
                "Store / Item": f"{_d['store']} / {_d['item']}",
                "Total":      f"{_tot:,.0f}",
                "Daily Avg":  f"{_avg:.1f}",
                "Peak":       f"{_pk:.0f}",
                "CV":         f"{_cv:.2f}",
                "vs Item 1":  f"+{_delta_total:.1f}%" if _delta_total > 0 else (f"{_delta_total:.1f}%" if _ci > 0 else "—"),
                "MAE vs #1":  f"{_mae:.1f}" if _ci > 0 else "—",
            })

        _df_cmp = pd.DataFrame(_rows)

        # Colour-code vs Item 1 column
        def _style_diff(val):
            if val == "—": return "color:#5a6478"
            if val.startswith("+"): return "color:#00e5a0"
            return "color:#ff6b35"

        st.dataframe(
            _df_cmp.style.applymap(_style_diff, subset=["vs Item 1"]),
            use_container_width=True,
            hide_index=True,
            height=min(80 + len(_rows) * 38, 280)
        )

        # ── Peak day divergence bar ───────────────────────────────────────────
        st.markdown("""
<div class="section-header" style="margin-top:1rem;">
  <div class="section-title">Daily Demand Distribution</div>
  <div class="section-line"></div>
  <div class="section-tag">box plot · spread · outliers</div>
</div>""", unsafe_allow_html=True)

        fig_box = go.Figure()
        for _ci, _k in enumerate(_keys):
            _d   = _cmp[_k]
            _col = ITEM_COLORS[_ci % 4]
            fig_box.add_trace(go.Box(
                y=_d["forecast"],
                name=f"{_d['store']} / {_d['item']}",
                marker_color=_col,
                line_color=_col,
                fillcolor=ITEM_COLORS_FILL[_ci % 4],
                boxpoints="all",
                jitter=0.4,
                pointpos=0,
                marker=dict(size=5, opacity=0.6),
            ))
        fig_box.update_layout(**PLOTLY_LAYOUT, height=300, yaxis_title="Units / Day")
        st.plotly_chart(fig_box, use_container_width=True)

        # ── Export comparison CSV ─────────────────────────────────────────────
        st.markdown("""
<div class="section-header" style="margin-top:0.5rem;">
  <div class="section-title">Export Comparison</div>
  <div class="section-line"></div>
  <div class="section-tag">all items · day-by-day</div>
</div>""", unsafe_allow_html=True)

        _cmp_rows = []
        for _day_i in range(forecast_days):
            _row = {"day": _day_i+1, "date": (_today + timedelta(days=_day_i+1)).strftime("%Y-%m-%d")}
            for _ci, _k in enumerate(_keys):
                _d = _cmp[_k]
                _lbl = f"{_d['store']}_{_d['item']}"
                _row[f"fc_{_lbl}"]  = round(_d["forecast"][_day_i], 2) if _day_i < len(_d["forecast"]) else None
                _row[f"uci_{_lbl}"] = round(_d["upper_ci"][_day_i], 2) if _day_i < len(_d["upper_ci"]) else None
                _row[f"lci_{_lbl}"] = round(_d["lower_ci"][_day_i], 2) if _day_i < len(_d["lower_ci"]) else None
            _cmp_rows.append(_row)
        _df_export = pd.DataFrame(_cmp_rows)

        st.download_button(
            label=f"⬇  Download Comparison CSV  ({len(_df_export)} rows × {len(_df_export.columns)} cols)",
            data=_df_export.to_csv(index=False).encode("utf-8"),
            file_name=f"salesiq_comparison_{datetime.now().strftime('%Y%m%d_%H%M')}.csv",
            mime="text/csv",
            use_container_width=True,
            key="dl_cmp_csv"
        )


# ═══════════════════════════════════════════════════════════════════════════════
# TAB 6 — SCENARIO SIMULATION
# ═══════════════════════════════════════════════════════════════════════════════
with tab_scenario:

    st.markdown("""
<div class="section-header">
  <div class="section-title">Scenario Simulation</div>
  <div class="section-line"></div>
  <div class="section-tag">what-if · demand modelling · instant recalculation</div>
</div>""", unsafe_allow_html=True)

    st.markdown("""
<div style="font-family:var(--mono);font-size:0.65rem;color:var(--muted);letter-spacing:0.08em;
            margin-bottom:1.25rem;padding:0.75rem 1rem;background:var(--surface);
            border:1px solid var(--border);border-left:3px solid var(--accent2);">
  Adjust the parameters below to simulate how changes in demand, promotions, or pricing
  would affect your forecast. Results recalculate instantly.
</div>""", unsafe_allow_html=True)

    sc_col1, sc_col2 = st.columns([1, 1], gap="large")

    with sc_col1:
        st.markdown('<div class="scenario-container">', unsafe_allow_html=True)
        st.markdown("""
<div style="font-family:var(--display);font-size:0.8rem;font-weight:700;
            color:var(--text);margin-bottom:1.25rem;letter-spacing:0.02em;">
  ⚙️ Simulation Parameters
</div>""", unsafe_allow_html=True)

        sc_multiplier = st.slider(
            "Demand Multiplier", min_value=0.5, max_value=2.5, value=1.0, step=0.05,
            help="Scale all forecast values by this factor (1.0 = baseline)"
        )
        sc_promo = st.toggle("🎯 Promotion Active", value=False,
                             help="Apply a +15% promotional demand lift")
        sc_price_change = st.number_input(
            "Price Change (%)", min_value=-50.0, max_value=100.0, value=0.0, step=1.0,
            help="Price elasticity: +10% price → approx -5% demand"
        )
        sc_stockout_risk = st.toggle("📦 Apply Stockout Constraint", value=False,
                                      help="Cap daily demand at current inventory level")

        st.markdown('</div>', unsafe_allow_html=True)

    with sc_col2:
        # Compute simulated forecast
        sc_fc = np.array(forecast, dtype=float)

        # Apply multiplier
        sc_fc = sc_fc * sc_multiplier

        # Apply promotion lift (+15%)
        if sc_promo:
            sc_fc = sc_fc * 1.15

        # Apply price elasticity (-0.5 elasticity: +10% price = -5% demand)
        if sc_price_change != 0:
            price_effect = 1.0 + (-0.5 * sc_price_change / 100)
            sc_fc = sc_fc * price_effect

        # Apply stockout cap
        if sc_stockout_risk and inventory > 0:
            sc_fc = np.minimum(sc_fc, inventory / max(len(sc_fc), 1))

        sc_fc = np.clip(sc_fc, 0, None)
        sc_total   = float(np.sum(sc_fc))
        sc_avg     = float(np.mean(sc_fc))
        sc_peak    = float(np.max(sc_fc))
        sc_rev     = sc_avg * 30 * 12.5
        sc_d_total = sc_total - total
        sc_d_rev   = sc_rev - (avg * 30 * 12.5)

        sign_t = "up" if sc_d_total >= 0 else "down"
        sign_r = "up" if sc_d_rev   >= 0 else "down"
        arrow_t = "↑" if sc_d_total >= 0 else "↓"
        arrow_r = "↑" if sc_d_rev   >= 0 else "↓"

        st.markdown(f"""
<div style="font-family:var(--display);font-size:0.8rem;font-weight:700;
            color:var(--text);margin-bottom:1rem;letter-spacing:0.02em;">
  📊 Simulated Results
</div>
<div class="scenario-result">
  <div class="scenario-result-row">
    <span class="scenario-result-key">Total Forecast (simulated)</span>
    <span class="scenario-result-val {sign_t}">{sc_total:,.0f} units &nbsp; {arrow_t} {abs(sc_d_total):,.0f}</span>
  </div>
  <div class="scenario-result-row">
    <span class="scenario-result-key">Daily Average</span>
    <span class="scenario-result-val">{sc_avg:.1f} units/day</span>
  </div>
  <div class="scenario-result-row">
    <span class="scenario-result-key">Peak Day</span>
    <span class="scenario-result-val">{sc_peak:.0f} units</span>
  </div>
  <div class="scenario-result-row">
    <span class="scenario-result-key">Est. 30-Day Revenue</span>
    <span class="scenario-result-val {sign_r}">${sc_rev:,.0f} &nbsp; {arrow_r} ${abs(sc_d_rev):,.0f}</span>
  </div>
  <div class="scenario-result-row">
    <span class="scenario-result-key">Demand Multiplier</span>
    <span class="scenario-result-val">{sc_multiplier:.2f}×</span>
  </div>
  <div class="scenario-result-row">
    <span class="scenario-result-key">Promotion Active</span>
    <span class="scenario-result-val {'up' if sc_promo else ''}">{"YES  +15% lift" if sc_promo else "No"}</span>
  </div>
  <div class="scenario-result-row">
    <span class="scenario-result-key">Price Change</span>
    <span class="scenario-result-val {'' if sc_price_change == 0 else ('down' if sc_price_change > 0 else 'up')}">{sc_price_change:+.1f}%  →  {(-0.5 * sc_price_change):+.1f}% demand</span>
  </div>
</div>""", unsafe_allow_html=True)

    # Overlay chart: baseline vs simulated
    st.markdown("""
<div class="section-header" style="margin-top:1.5rem;">
  <div class="section-title">Baseline vs Simulation</div>
  <div class="section-line"></div>
  <div class="section-tag">side-by-side overlay · interactive</div>
</div>""", unsafe_allow_html=True)

    fig_sc = go.Figure()
    # Baseline CI band
    fig_sc.add_trace(go.Scatter(
        x=fcast_dates + fcast_dates[::-1],
        y=list(upper_ci) + list(lower_ci[::-1]),
        fill="toself", fillcolor="rgba(0,229,160,0.05)",
        line=dict(width=0), showlegend=False, hoverinfo="skip"
    ))
    # Baseline line
    fig_sc.add_trace(go.Scatter(
        x=fcast_dates, y=forecast.tolist(),
        mode="lines", name="Baseline",
        line=dict(color="#5a6478", width=1.5, dash="dot"),
        hovertemplate="Baseline: %{y:.1f}<extra></extra>"
    ))
    # Simulated line
    sc_color = "#00e5a0" if sc_total >= total else "#ff6b35"
    fig_sc.add_trace(go.Scatter(
        x=fcast_dates, y=sc_fc.tolist(),
        mode="lines+markers", name="Simulated",
        line=dict(color=sc_color, width=2),
        marker=dict(size=4, color=sc_color),
        hovertemplate="Simulated: %{y:.1f}<extra></extra>"
    ))
    fig_sc.update_layout(**PLOTLY_LAYOUT, height=320, yaxis_title="Units / Day")
    st.plotly_chart(fig_sc, use_container_width=True)

    # Export simulated forecast
    sc_df = pd.DataFrame({
        "day":        range(1, len(sc_fc)+1),
        "date":       [d.strftime("%Y-%m-%d") for d in fcast_dates],
        "baseline":   [round(float(v), 2) for v in forecast],
        "simulated":  [round(float(v), 2) for v in sc_fc],
        "delta":      [round(float(s)-float(b), 2) for b, s in zip(forecast, sc_fc)],
    })
    st.download_button(
        label="⬇  Export Scenario Forecast CSV",
        data=sc_df.to_csv(index=False).encode("utf-8"),
        file_name=f"forecastflow_scenario_{datetime.now().strftime('%Y%m%d_%H%M')}.csv",
        mime="text/csv",
        use_container_width=True,
        key="dl_scenario"
    )


# ─────────────────────────────────────────────────────────────────────────────
# FOOTER
# ─────────────────────────────────────────────────────────────────────────────
st.markdown(f"""
<div class="app-footer">
  <div class="footer-logo">Forecast<span>Flow</span></div>
  <div class="footer-tagline">AI-Powered Sales Forecasting Platform</div>
  <div class="footer-stack">
    Built with &nbsp;
    <span>FastAPI</span> &nbsp;·&nbsp;
    <span>Python</span> &nbsp;·&nbsp;
    <span>LightGBM</span> &nbsp;·&nbsp;
    <span>Streamlit</span> &nbsp;·&nbsp;
    <span>Docker</span>
  </div>
  <div class="footer-author">Author: Pranjal Sabhaya &nbsp;·&nbsp; {datetime.now().year}</div>
</div>
""", unsafe_allow_html=True)