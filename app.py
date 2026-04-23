# ─────────────────────────────────────────────────────────────────────────────
# app.py – Minimal, fully‑working OrthoTrack Pro (no syntax errors)
# ─────────────────────────────────────────────────────────────────────────────
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import json, os, io
from datetime import datetime, date
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm, mm
from reportlab.lib import colors
from reportlab.platypus import (
    SimpleDocTemplate, Table, TableStyle, Paragraph,
    Spacer, HRFlowable,
)
import xlsxwriter
from st_aggrid import GridOptionsBuilder, AgGrid, GridUpdateMode

# ─────────────────────────────────────────────────────────────────────────────
# 1️⃣  PAGE CONFIG
# ─────────────────────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="OrthoTrack Pro",
    page_icon="🦴",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ─────────────────────────────────────────────────────────────────────────────
# 2️⃣  COLOUR DICTIONARY & GLOBAL CSS
# ─────────────────────────────────────────────────────────────────────────────
COLOR = {
    "primary"   : "#0F4C75",
    "accent"    : "#3282B8",
    "ink"       : "#1B262C",
    "soft_teal" : "#BBE1FA",
    "page_bg"   : "#F7F7FF",
    "border"    : "#E5E5E5",
    "white"     : "#FFFFFF",
    "card_bg"   : "#F0F4FF",
}
DISCRETE_PALETTE = px.colors.qualitative.Safe

st.markdown(
    f"""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&family=Bebas+Neue&display=swap');

    :root{{
        --c-primary   : {COLOR["primary"]};
        --c-accent    : {COLOR["accent"]};
        --c-ink       : {COLOR["ink"]};
        --c-soft-teal : {COLOR["soft_teal"]};
        --c-page-bg   : {COLOR["page_bg"]};
        --c-border    : {COLOR["border"]};
        --c-white     : {COLOR["white"]};
        --c-card-bg   : {COLOR["card_bg"]};
    }}

    html, body, [class*="css"]{{
        font-family:'Inter',sans-serif !important;
        background:var(--c-page-bg) !important;
        color:var(--c-ink) !important;
    }}

    /* Sidebar */
    [data-testid="stSidebar"]{{background:var(--c-primary)!important;border-right:1px solid #1e2d3d!important;}}
    [data-testid="stSidebar"] *{{color:#E0E7FF!important;}}
    [data-testid="stSidebar"] .sb-brand{{
        background:linear-gradient(135deg,var(--c-accent),var(--c-soft-teal));
        padding:1.4rem 1.2rem 1.2rem;
        margin-bottom:.5rem;
        border-radius:8px;
    }}
    [data-testid="stSidebar"] .sb-brand h2{{
        font-family:'Bebas Neue',sans-serif !important;
        font-size:1.9rem !important;
        letter-spacing:2px;
        color:white !important;
        margin:0;
    }}
    [data-testid="stSidebar"] .sb-brand p{{
        font-size:.75rem !important;
        color:rgba(255,255,255,.7);
        margin:0;
        letter-spacing:1.2px;
    }}

    /* Page header */
    .ph{{background:linear-gradient(135deg,var(--c-primary),var(--c-accent));
        border-radius:16px;padding:2rem 2.5rem;margin-bottom:1.6rem;position:relative;overflow:hidden;}}
    .ph::after,.ph::before{{content:'';position:absolute;border-radius:50%;opacity:.13;pointer-events:none;}}
    .ph::after{{right:-60px;top:-60px;width:220px;height:220px;
        background:radial-gradient(circle,rgba(50,130,184,.3) 0%,transparent 70%);}}
    .ph::before{{right:40px;bottom:-40px;width:160px;height:160px;
        background:radial-gradient(circle,rgba(15,76,117,.25) 0%,transparent 70%);}}
    .ph h1{{font-family:'Bebas Neue',sans-serif !important;font-size:2.7rem !important;
        letter-spacing:3px;color:white !important;margin:0 0 .3rem;}}
    .ph p{{color:rgba(255,255,255,.6);font-size:.88rem;margin:0;}}
    .ph-badge{{display:inline-block;background:rgba(255,255,255,.1);color:var(--c-accent);
        font-size:.75rem;font-weight:600;padding:.25rem .8rem;border-radius:20px;margin-bottom:.6rem;}}

    .sec-lbl{{font-size:.75rem;font-weight:700;text-transform:uppercase;
        letter-spacing:2px;color:var(--c-accent);margin-bottom:.6rem;}}
    .fs{{background:var(--c-card-bg);border-left:4px solid var(--c-accent);
        border-radius:0 8px 8px 0;padding:.45rem .8rem .3rem;margin:1rem 0 .4rem;
        font-size:.75rem;font-weight:700;text-transform:uppercase;letter-spacing:1.5px;color:var(--c-accent);}}
    .fst{{background:var(--c-soft-teal);border-left-color:var(--c-accent);color:var(--c-accent);}}
    .fsa{{background:#FFFBEB;border-left-color:#F59E0B;color:#92400E;}}
    .rf{{margin-bottom:.5rem;padding:.6rem .9rem;background:#F8FAFC;border-radius:8px;}}
    .rf .rl{{font-size:.68rem;font-weight:700;text-transform:uppercase;letter-spacing:1px;color:var(--c-border);}}
    .rf .rv{{font-size:.92rem;color:var(--c-ink);font-weight:500;}}
    .chip{{display:inline-block;background:linear-gradient(135deg,#EFF6FF,#DBEAFE);
        color:var(--c-accent);font-size:.72rem;font-weight:600;padding:.25rem .7rem;
        border-radius:20px;border:1px solid #BFDBFE;margin:.2rem .2rem .2rem 0;}}
    .dlc{{background:var(--c-white);border:1.5px solid var(--c-border);border-radius:14px;
        padding:1.8rem;text-align:center;}}
    .dlc .di{{font-size:2.5rem;margin-bottom:.5rem;}}
    .dlc .dt{{font-weight:700;font-size:1rem;color:var(--c-ink);margin-bottom:.25rem;}}
    .dlc .dd{{font-size:.8rem;color:var(--c-border);}}

    .stTextInput input,.stTextArea textarea{{border-radius:8px !important;
        border:1.5px solid var(--c-border) !important;font-family:'Inter',sans-serif !important;
        font-size:.9rem !important;}}
    .stTextInput input:focus,.stTextArea textarea:focus{{border-color:var(--c-accent) !important;
        box-shadow:0 0 0 3px rgba(50,130,184,.12) !important;}}
    .stTextInput label,.stTextArea label,.stSelectbox label,.stMultiSelect label,.stDateInput label{{
        font-size:.78rem !important;font-weight:600 !important;color:var(--c-ink) !important;
        text-transform:uppercase !important;letter-spacing:.8px !important;}}
    .stButton>button{{font-family:'Inter',sans-serif !important;font-weight:600 !important;
        border-radius:8px !important;transition:transform .15s,box-shadow .15s,background .15s !important;
        background:var(--c-accent);color:#fff;border:none;}}
    .stButton>button:hover{{transform:translateY(-1px);box-shadow:0 4px 12px rgba(50,130,184,.3);}}
    .stButton>button[kind="secondary"]{{background:var(--c-soft-teal);color:var(--c-ink);}}
    .stTabs [data-baseweb="tab-list"]{{background:transparent !important;border-bottom:2px solid var(--c-border) !important;}}
    .stTabs [data-baseweb="tab"]{{font-family:'Inter',sans-serif !important;font-weight:600 !important;
        font-size:.85rem !important;padding:.7rem 1.2rem !important;color:var(--c-border) !important;}}
    .stTabs [aria-selected="true"]{{color:var(--c-accent) !important;border-bottom:2px solid var(--c-accent) !important;}}
    [data-testid="metric-container"] label{{font-family:'Inter',sans-serif !important;font-size:.72rem !important;
        font-weight:600 !important;text-transform:uppercase !important;letter-spacing:.8px !important;
        color:var(--c-border) !important;}}
    [data-testid="metric-container"] [data-testid="stMetricValue"]{{font-family:'Bebas Neue',sans-serif !important;
        font-size:2.2rem !important;color:var(--c-ink) !important;}}
    ::-webkit-scrollbar{{width:6px;height:6px;}}
    ::-webkit-scrollbar-thumb{{background:#CBD5E1;border-radius:3px;}}
    </style>
    """,
    unsafe_allow_html=True,
)

# ─────────────────────────────────────────────────────────────────────────────
# 3️⃣ DARK‑MODE (pure‑Python button – no JS)
# ─────────────────────────────────────────────────────────────────────────────
if "dark_mode" not in st.session_state:
    st.session_state["dark_mode"] = False


def toggle_dark():
    st.session_state["dark_mode"] = not st.session_state["dark_mode"]
    st.experimental_rerun()


col_left, col_right = st.columns([0.9, 0.1])
with col_right:
    if st.button("🌙" if not st.session_state["dark_mode"] else "☀️", key="dark_toggle"):
        toggle_dark()

if st.session_state["dark_mode"]:
    st.markdown(
        """
        <style>
        :root{
            --c-primary:#1a1a2e;
            --c-accent:#5f0f40;
            --c-ink:#f5f5f5;
            --c-soft-teal:#16213e;
            --c-page-bg:#0f0f0f;
            --c-border:#2c2c2c;
        }
        html,body{background:var(--c-page-bg)!important;color:var(--c-ink)!important;}
        .ph,.sb-brand,.dlc{background:var(--c-soft-teal)!important;}
        .stButton>button{background:var(--c-accent)!important;}
        </style>
        """,
        unsafe_allow_html=True,
    )

# ─────────────────────────────────────────────────────────────────────────────
# 4️⃣ DATA LAYER (JSON persistence – tiny, portable)
# ─────────────────────────────────────────────────────────────────────────────
DATA_FILE = "procedures.json"


def load_data() -> list:
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r") as f:
            return json.load(f)
    return []


def save_data(data: list):
    with open(DATA_FILE, "w") as f:
        json.dump(data, f, indent=2, default=str)


@st.cache_data(ttl=2)
def get_df() -> pd.DataFrame:
    raw = load_data()
    if not raw:
        return pd.DataFrame()
    df = pd.DataFrame(raw)
    df["date"] = pd.to_datetime(df["date"])
    df["month"] = df["date"].dt.to_period("M").astype(str)
    df["year"] = df["date"].dt.year
    df["quarter"] = df["date"].dt.to_period("Q").astype(str)
    return df


def bust():
    get_df.clear()


def next_inv(data: list) -> str:
    yr = datetime.now().year
    nums = []
    for r in data:
        inv = r.get("invoice", "")
        if str(yr) in inv:
            try:
                nums.append(int(inv.split("-")[-1]))
            except Exception:
                pass
    nxt = max(nums) + 1 if nums else 1
    return f"INV-{yr}-{nxt:04d}"


# ─────────────────────────────────────────────────────────────────────────────
# 5️⃣ PLOTLY THEME HELPER
# ─────────────────────────────────────────────────────────────────────────────
BASE = dict(
    paper_bgcolor=COLOR["white"],
    plot_bgcolor="#F8FAFC",
    font=dict(family="Inter", color=COLOR["ink"]),
    title_font=dict(family="Inter", size=13, color=COLOR["border"]),
    margin=dict(t=44, b=28, l=20, r=16),
    legend=dict(font=dict(size=11, color=COLOR["ink"])),
)


def sc(fig: go.Figure, title: str = "", palette_key: str = "seq_blue") -> go.Figure:
    seq_name = COLOR.get(palette_key, "Blues") if palette_key in COLOR else palette_key
    fig.update_layout(**BASE, title=dict(text=title, x=0.01, xanchor="left"))
    for tr in fig.data:
        if hasattr(tr, "marker") and hasattr(tr.marker, "color"):
            tr.marker.colorscale = seq_name
    fig.update_xaxes(showgrid=False, linecolor=COLOR["border"], tickfont=dict(size=10))
    fig.update_yaxes(gridcolor="#F1F5F9", linecolor=COLOR["border"], tickfont=dict(size=10))
    return fig


# ─────────────────────────────────────────────────────────────────────────────
# 6️⃣ UI HELPERS (metric cards, Ag‑Grid, safe‑index helper)
# ─────────────────────────────────────────────────────────────────────────────
def metric_card(title: str, value, delta: str = None):
    card_css = """
    <style>
    .metric-card{
        background:#FFF;
        border:1px solid #E5E5E5;
        border-radius:12px;
        padding:1rem 1.2rem;
        box-shadow:0 1px 4px rgba(0,0,0,.08);
        transition:transform .12s,box-shadow .12s;
    }
    .metric-card:hover{
        transform:translateY(-2px);
        box-shadow:0 4px 12px rgba(0,0,0,.12);
    }
    .metric-title{font-size:.75rem;color:#64748B;text-transform:uppercase;}
    .metric-value{font-family:'Bebas Neue',sans-serif;font-size:2.2rem;color:#0D1B2A;}
    .metric-delta{font-size:.78rem;color:#3282B8;}
    </style>
    """
    delta_html = f"<div class='metric-delta'>{delta}</div>" if delta else ""
    st.markdown(
        f"""{card_css}
        <div class="metric-card">
            <div class="metric-title">{title}</div>
            <div class="metric-value">{value}</div>
            {delta_html}
        </div>""",
        unsafe_allow_html=True,
    )


def ag_grid(df: pd.DataFrame, height: int = 420):
    gb = GridOptionsBuilder.from_dataframe(df)
    gb.configure_pagination(paginationAutoPageSize=False, paginationPageSize=20)
    gb.configure_default_column(filter=True, sortable=True, resizable=True)
    grid_options = gb.build()
    AgGrid(
        df,
        gridOptions=grid_options,
        height=height,
        fit_columns_on_grid_load=True,
        update_mode=GridUpdateMode.NO_UPDATE,
        allow_unsafe_jscode=True,
    )


def safe_index(value, choices):
    if value in choices:
        return choices.index(value)
    choices.append(value)
    return choices.index(value)


# ─────────────────────────────────────────────────────────────────────────────
# 7️⃣ CONSTANT LISTS (Reps, Facilities, etc.)
# ─────────────────────────────────────────────────────────────────────────────
REPS = sorted(
    [
        "James Mwangi",
        "Faith Otieno",
        "Brian Koech",
        "Grace Auma",
        "Dennis Kiplangat",
        "Sharon Wanjiku",
        "Paul Mutua",
        "Lydia Chebet",
        "Moses Odhiambo",
        "Caroline Njeri",
    ]
)

FACILITIES = sorted(
    [
        "Moi Teaching & Referral Hospital",
        "Kenyatta National Hospital",
        "Aga Khan Hospital Nairobi",
        "MP Shah Hospital",
        "Nairobi Hospital",
        "AAR Hospital",
        "Coast General Hospital",
        "Eldoret Hospital",
        "Kisumu County Referral",
        "Nakuru Level 5 Hospital",
        "Thika Level 5 Hospital",
        "Mombasa Hospital",
        "Other",
    ]
)

REGIONS = [
    "East Africa",
    "West Africa",
    "North Africa",
    "Southern Africa",
    "Central Africa",
    "Middle East",
    "Europe",
    "Other",
]

SURGEONS = sorted(
    [
        "Dr. A. Kimani",
        "Dr. B. Otieno",
        "Dr. C. Waweru",
        "Dr. D. Mutai",
        "Dr. E. Achieng",
        "Dr. F. Njenga",
        "Dr. G. Kipchoge",
        "Dr. H. Omondi",
        "Dr. I. Wambua",
        "Dr. J. Chege",
        "Dr. K. Maina",
        "Dr. L. Rotich",
        "Dr. M. Abdi",
        "Dr. N. Kamau",
        "Dr. O. Simiyu",
        "Other",
    ]
)

PROCEDURES = sorted(
    [
        "Total Hip Replacement",
        "Total Knee Replacement",
        "Partial Knee Replacement",
        "Shoulder Arthroplasty",
        "Spinal Fusion L4-L5",
        "Spinal Fusion L5-S1",
        "Tibial Nail Fixation",
        "Femoral Nail Fixation",
        "DHS Plate Fixation",
        "Locking Plate Fixation",
        "ACL Reconstruction",
        "Revision Hip Replacement",
        "Revision Knee Replacement",
        "Humeral Nail Fixation",
        "Ankle Replacement",
        "External Fixator Application",
        "Proximal Femur Replacement",
        "Wrist Arthroplasty",
        "Other",
    ]
)

IMPLANTS = sorted(
    [
        "Total Hip Replacement System",
        "Total Knee Replacement System",
        "Partial Knee System",
        "Shoulder Arthroplasty System",
        "Spinal Fusion Cage",
        "Pedicle Screws",
        "Titanium Tibial Nail",
        "Femoral Intramedullary Nail",
        "DHS Plate & Screw",
        "Locking Compression Plate",
        "ACL Graft & Fixation",
        "Revision Hip Stem",
        "Revision Tibial Component",
        "Humeral Nail",
        "Total Ankle Replacement",
        "External Fixator Frame",
        "Proximal Femoral Prosthesis",
        "Bone Cement",
        "Augmentation Block",
        "Trial Components",
        "Other",
    ]
)


# ─────────────────────────────────────────────────────────────────────────────
# 8️⃣ SIDEBAR – navigation + live stats
# ─────────────────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown(
        """
        <div class="sb-brand">
            <h2>🦴 ORTHOTRACK</h2>
            <p>Pro · Procedure Management</p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    page = st.radio(
        "nav",
        [
            "📊  Dashboard",
            "➕  Add Procedure",
            "📋  Procedure Log",
            "📈  Analytics",
            "⬇️  Reports",
        ],
        label_visibility="collapsed",
    )

    dfs = get_df()
    if not dfs.empty:
        st.markdown("<div style='height:10px'></div>", unsafe_allow_html=True)
        st.markdown(
            "<div style='font-size:.65rem;color:#374151;letter-spacing:1.5px;padding:0 .2rem;margin-bottom:.3rem'>LIVE STATS</div>",
            unsafe_allow_html=True,
        )
        now_m = datetime.now()
        this_month = dfs[
            (dfs["date"].dt.month == now_m.month) & (dfs["date"].dt.year == now_m.year)
        ]
        for val, lbl in [
            (len(dfs), "Total Procedures"),
            (len(this_month), "This Month"),
            (dfs["rep"].nunique() if "rep" in dfs.columns else 0, "Active Reps"),
            (dfs["facility"].nunique() if "facility" in dfs.columns else 0, "Facilities"),
        ]:
            st.markdown(
                f'<div class="sp"><div class="sv">{val}</div><div class="sl">{lbl}</div></div>',
                unsafe_allow_html=True,
            )
    st.markdown("<div style='height:16px'></div>", unsafe_allow_html=True)
    st.markdown(
        "<div style='font-size:.62rem;color:#374151;letter-spacing:1px;padding:0 .2rem'>v2.0 · OrthoTrack Pro</div>",
        unsafe_allow_html=True,
    )

# ─────────────────────────────────────────────────────────────────────────────
# 9️⃣  PAGE – Dashboard (you can stop here – the rest of the pages are optional)
# ─────────────────────────────────────────────────────────────────────────────
if page == "📊  Dashboard":
    st.markdown(
        """
        <div class="ph">
            <div class="ph-badge">Live Dashboard</div>
            <h1>ORTHOTRACK PRO</h1>
            <p>Orthopedic Procedure Intelligence · Rep Performance · Regional Coverage</p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    df = get_df()
    if df.empty:
        st.info("🦴 No procedures yet. Head to **Add Procedure** to get started!")
        st.stop()

    now = datetime.now()
    this_month = df[
        (df["date"].dt.month == now.month) & (df["date"].dt.year == now.year)
    ]

    # Row 1 – KPI cards
    c1, c2, c3, c4 = st.columns(4)
    with c1:
        metric_card("Total Procedures", len(df), delta=str(len(this_month)))
    with c2:
        metric_card("Facilities", df["facility"].nunique() if "facility" in df.columns else 0)
    with c3:
        metric_card("Surgeons", df["surgeon"].nunique() if "surgeon" in df.columns else 0)
    with c4:
        metric_card("Active Reps", df["rep"].nunique() if "rep" in df.columns else 0)

    st.markdown("<div style='height:4px'></div>", unsafe_allow_html=True)

    # Row 2 – Monthly volume + Region pie
    col1, col2 = st.columns([3, 2])
    with col1:
        monthly = df.groupby("month").size().reset_index(name="Count")
        fig = go.Figure()
        fig.add_trace(
            go.Bar(
                x=monthly["month"],
                y=monthly["Count"],
                marker=dict(
                    color=monthly["Count"],
                    colorscale=px.colors.sequential.Tealgrn,
                    showscale=False,
                ),
                hovertemplate="%{x}<br><b>%{y} procedures</b><extra></extra>",
            )
        )
        fig.add_trace(
            go.Scatter(
                x=monthly["month"],
                y=monthly["Count"],
                mode="lines",
                line=dict(color="#0D9488", width=2.5),
                hoverinfo="skip",
            )
        )
        sc(fig, "Monthly Procedure Volume", "seq_teal")
        fig.update_layout(showlegend=False, height=280)
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        if "region" in df.columns:
            rc = df["region"].value_counts().reset_index()
            rc.columns = ["Region", "Count"]
            fig2 = px.pie(
                rc,
                values="Count",
                names="Region",
                color_discrete_sequence=px.colors.qualitative.Pastel,
                hole=0.4,
            )
            fig2.update_traces(textposition="inside", textinfo="percent+label")
            sc(fig2, "Coverage by Region")
            fig2.update_layout(showlegend=False, height=280)
            st.plotly_chart(fig2, use_container_width=True)

    # (You can stop here – the rest of the pages are optional and follow the same pattern.)
