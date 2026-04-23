# ─────────────────────────────────────────────────────────────────────────────
# app.py – OrthoTrack Pro  (working version)
# ─────────────────────────────────────────────────────────────────────────────
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import json, os, io
from datetime import datetime, date

# ── GLOBAL CSS (fonts, colours, dark‑mode button) ────────────────────────────
st.markdown(
    """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&family=Bebas+Neue&display=swap');

    :root{
        --c-primary   : #0F4C75;
        --c-accent    : #3282B8;
        --c-ink       : #1B262C;
        --c-soft-teal : #BBE1FA;
        --c-page-bg   : #F7F7FF;
        --c-border    : #E5E5E5;
        --c-white     : #FFFFFF;
        --c-card-bg   : #F0F4FF;
    }

    html, body, [class*="css"]{
        font-family:'Inter',sans-serif !important;
        background:var(--c-page-bg) !important;
        color:var(--c-ink) !important;
    }

    /* ── Sidebar ── */
    [data-testid="stSidebar"]{
        background:var(--c-primary) !important;
        border-right:1px solid #1e2d3d !important;
    }
    [data-testid="stSidebar"] *{color:#E0E7FF !important;}
    [data-testid="stSidebar"] .sb-brand{
        background:linear-gradient(135deg,var(--c-accent),var(--c-soft-teal));
        padding:1.4rem 1.2rem 1.2rem;
        margin-bottom:.5rem;
        border-radius:8px;
    }
    [data-testid="stSidebar"] .sb-brand h2{
        font-family:'Bebas Neue',sans-serif !important;
        font-size:1.9rem !important;
        letter-spacing:2px;
        color:white !important;
        margin:0;
    }
    [data-testid="stSidebar"] .sb-brand p{
        font-size:.75rem !important;
        color:rgba(255,255,255,.7);
        margin:0;
        letter-spacing:1.2px;
    }

    /* ── Page Header ── */
    .ph{
        background:linear-gradient(135deg,var(--c-primary),var(--c-accent));
        border-radius:16px;
        padding:2rem 2.5rem;
        margin-bottom:1.6rem;
        position:relative; overflow:hidden;
    }
    .ph::after,.ph::before{
        content:'';position:absolute;border-radius:50%;
        opacity:.13;pointer-events:none;
    }
    .ph::after{
        right:-60px;top:-60px;width:220px;height:220px;
        background:radial-gradient(circle,rgba(50,130,184,.3) 0%,transparent 70%);
    }
    .ph::before{
        right:40px;bottom:-40px;width:160px;height:160px;
        background:radial-gradient(circle,rgba(15,76,117,.25) 0%,transparent 70%);
    }
    .ph h1{
        font-family:'Bebas Neue',sans-serif !important;
        font-size:2.7rem !important;
        letter-spacing:3px;
        color:white !important;
        margin:0 0 .3rem;
    }
    .ph p{
        color:rgba(255,255,255,.6);
        font-size:.88rem;
        margin:0;
    }
    .ph-badge{
        display:inline-block;
        background:rgba(255,255,255,.1);
        color:var(--c-accent);
        font-size:.75rem;
        font-weight:600;
        padding:.25rem .8rem;
        border-radius:20px;
        margin-bottom:.6rem;
    }

    .sec-lbl{
        font-size:.75rem;font-weight:700;text-transform:uppercase;
        letter-spacing:2px;color:var(--c-accent);margin-bottom:.6rem;
    }

    .fs{
        background:var(--c-card-bg);
        border-left:4px solid var(--c-accent);
        border-radius:0 8px 8px 0;
        padding:.45rem .8rem .3rem;
        margin:1rem 0 .4rem;
        font-size:.75rem;font-weight:700;
        text-transform:uppercase;
        letter-spacing:1.5px;
        color:var(--c-accent);
    }
    .fst{background:var(--c-soft-teal);border-left-color:var(--c-accent);color:var(--c-accent);}
    .fsa{background:#FFFBEB;border-left-color:#F59E0B;color:#92400E;}

    .rf{margin-bottom:.5rem;padding:.6rem .9rem;background:#F8FAFC;border-radius:8px;}
    .rf .rl{font-size:.68rem;font-weight:700;text-transform:uppercase;letter-spacing:1px;color:var(--c-border);}
    .rf .rv{font-size:.92rem;color:var(--c-ink);font-weight:500;}

    .chip{
        display:inline-block;
        background:linear-gradient(135deg,#EFF6FF,#DBEAFE);
        color:var(--c-accent);
        font-size:.72rem;font-weight:600;
        padding:.25rem .7rem;
        border-radius:20px;border:1px solid #BFDBFE;
        margin:.2rem .2rem .2rem 0;
    }

    .dlc{
        background:var(--c-white);
        border:1.5px solid var(--c-border);
        border-radius:14px;
        padding:1.8rem;
        text-align:center;
    }
    .dlc .di{font-size:2.5rem;margin-bottom:.5rem;}
    .dlc .dt{font-weight:700;font-size:1rem;color:var(--c-ink);margin-bottom:.25rem;}
    .dlc .dd{font-size:.8rem;color:var(--c-border);}

    .stTextInput input,.stTextArea textarea{
        border-radius:8px !important;
        border:1.5px solid var(--c-border) !important;
        font-family:'Inter',sans-serif !important;
        font-size:.9rem !important;
    }
    .stTextInput input:focus,.stTextArea textarea:focus{
        border-color:var(--c-accent) !important;
        box-shadow:0 0 0 3px rgba(50,130,184,.12) !important;
    }
    .stTextInput label,.stTextArea label,.stSelectbox label,.stMultiSelect label,.stDateInput label{
        font-size:.78rem !important;
        font-weight:600 !important;
        color:var(--c-ink) !important;
        text-transform:uppercase !important;
        letter-spacing:.8px !important;
    }

    .stButton>button{
        font-family:'Inter',sans-serif !important;
        font-weight:600 !important;
        border-radius:8px !important;
        transition:transform .15s,box-shadow .15s,background .15s !important;
        background:var(--c-accent);
        color:#fff;
        border:none;
    }
    .stButton>button:hover{
        transform:translateY(-1px);
        box-shadow:0 4px 12px rgba(50,130,184,.3);
    }
    .stButton>button[kind="secondary"]{
        background:var(--c-soft-teal);
        color:var(--c-ink);
    }

    .stTabs [data-baseweb="tab-list"]{
        background:transparent !important;
        border-bottom:2px solid var(--c-border) !important;
    }
    .stTabs [data-baseweb="tab"]{
        font-family:'Inter',sans-serif !important;
        font-weight:600 !important;
        font-size:.85rem !important;
        padding:.7rem 1.2rem !important;
        color:var(--c-border) !important;
    }
    .stTabs [aria-selected="true"]{
        color:var(--c-accent) !important;
        border-bottom:2px solid var(--c-accent) !important;
    }

    [data-testid="metric-container"] label{
        font-family:'Inter',sans-serif !important;
        font-size:.72rem !important;
        font-weight:600 !important;
        text-transform:uppercase !important;
        letter-spacing:.8px !important;
        color:var(--c-border) !important;
    }
    [data-testid="metric-container"] [data-testid="stMetricValue"]{
        font-family:'Bebas Neue',sans-serif !important;
        font-size:2.2rem !important;
        color:var(--c-ink) !important;
    }

    ::-webkit-scrollbar{width:6px;height:6px;}
    ::-webkit-scrollbar-thumb{background:#CBD5E1;border-radius:3px;}
    </style>
    """,
    unsafe_allow_html=True,
)
# ─────────────────────────────────────────────────────────────────────────────
