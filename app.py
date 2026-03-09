"""
DHL Same Day — Mahoney Express Shipment Dashboard
Streamlit web app — reads shipments.json from the same repo.
"""
import json
from pathlib import Path
import streamlit as st
import pandas as pd

# ── page config ───────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="DHL Mahoney — Shipments",
    page_icon="✈️",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ── load data ─────────────────────────────────────────────────────────────────
DATA_FILE = Path(__file__).parent / "shipments.json"

@st.cache_data(ttl=60)
def load_data():
    if not DATA_FILE.exists():
        return []
    with open(DATA_FILE, encoding="utf-8") as f:
        return json.load(f)

data = load_data()
df = pd.DataFrame(data) if data else pd.DataFrame()

# ── custom CSS ────────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=IBM+Plex+Mono:wght@400;600&family=IBM+Plex+Sans:wght@300;400;600;700&display=swap');

html, body, [class*="css"] { font-family: 'IBM Plex Sans', sans-serif; }

.block-container { padding-top: 1.5rem !important; max-width: 100% !important; }

/* header */
.dhl-header {
    background: linear-gradient(135deg, #0a1628 0%, #1F4E79 100%);
    border-left: 5px solid #FFCC00;
    border-radius: 6px;
    padding: 18px 24px;
    margin-bottom: 20px;
    display: flex;
    align-items: center;
    gap: 16px;
}
.dhl-badge {
    background: #FFCC00;
    color: #0a1628;
    font-family: 'IBM Plex Mono', monospace;
    font-weight: 700;
    font-size: 14px;
    padding: 5px 12px;
    border-radius: 3px;
    letter-spacing: 2px;
}
.dhl-title { color: white; font-size: 20px; font-weight: 600; margin: 0; }
.dhl-sub   { color: #8892a4; font-size: 12px; font-family: 'IBM Plex Mono', monospace; }

/* metric cards */
.metric-row { display: flex; gap: 12px; margin-bottom: 20px; flex-wrap: wrap; }
.metric-card {
    background: #0f1f3d;
    border: 1px solid #1e3a5f;
    border-radius: 6px;
    padding: 14px 20px;
    min-width: 120px;
    flex: 1;
}
.metric-card .val {
    font-family: 'IBM Plex Mono', monospace;
    font-size: 26px;
    font-weight: 700;
    color: #FFCC00;
}
.metric-card .lbl { font-size: 10px; color: #8892a4; letter-spacing: 1px; text-transform: uppercase; }
.metric-import  .val { color: #60a5fa; }
.metric-export  .val { color: #fb923c; }
.metric-domestic .val { color: #4ade80; }

/* direction badges */
.badge-Import   { background:#1e3a8a; color:#93c5fd; padding:2px 8px; border-radius:3px; font-size:11px; font-weight:600; }
.badge-Export   { background:#78350f; color:#fcd34d; padding:2px 8px; border-radius:3px; font-size:11px; font-weight:600; }
.badge-Domestic { background:#14532d; color:#86efac; padding:2px 8px; border-radius:3px; font-size:11px; font-weight:600; }

/* detail card */
.detail-card {
    background: #0f1f3d;
    border: 1px solid #1e3a5f;
    border-radius: 8px;
    padding: 20px;
    margin-top: 16px;
}
.detail-section-title {
    font-family: 'IBM Plex Mono', monospace;
    font-size: 10px;
    letter-spacing: 1.5px;
    color: #8892a4;
    text-transform: uppercase;
    border-bottom: 1px solid #1e3a5f;
    padding-bottom: 6px;
    margin: 16px 0 10px;
}
.detail-row { display: flex; gap: 12px; margin-bottom: 6px; font-size: 13px; }
.detail-label { color: #8892a4; font-family: 'IBM Plex Mono', monospace; font-size: 10px; width: 160px; flex-shrink: 0; padding-top: 2px; }
.detail-value { color: #e8eaf0; }

/* search input override */
div[data-testid="stTextInput"] input {
    background: #0f1f3d !important;
    border: 1.5px solid #1e3a5f !important;
    color: #e8eaf0 !important;
    font-family: 'IBM Plex Sans', sans-serif !important;
    font-size: 15px !important;
}
div[data-testid="stTextInput"] input:focus {
    border-color: #FFCC00 !important;
    box-shadow: none !important;
}

/* dataframe */
.stDataFrame { border: 1px solid #1e3a5f; border-radius: 6px; }
</style>
""", unsafe_allow_html=True)

# ── header ────────────────────────────────────────────────────────────────────
total = len(df)
n_import   = len(df[df["Direction"] == "Import"])   if total else 0
n_export   = len(df[df["Direction"] == "Export"])   if total else 0
n_domestic = len(df[df["Direction"] == "Domestic"]) if total else 0

st.markdown(f"""
<div class="dhl-header">
  <div class="dhl-badge">DHL</div>
  <div>
    <div class="dhl-title">Mahoney Express — Shipment Dashboard</div>
    <div class="dhl-sub">{total} SHIPMENTS LOADED</div>
  </div>
</div>
<div class="metric-row">
  <div class="metric-card"><div class="val">{total}</div><div class="lbl">Total Jobs</div></div>
  <div class="metric-card metric-import"><div class="val">{n_import}</div><div class="lbl">Import</div></div>
  <div class="metric-card metric-export"><div class="val">{n_export}</div><div class="lbl">Export</div></div>
  <div class="metric-card metric-domestic"><div class="val">{n_domestic}</div><div class="lbl">Domestic</div></div>
</div>
""", unsafe_allow_html=True)

if df.empty:
    st.warning("No shipment data found. Run `process_dhl_pdfs.py` to populate the database.")
    st.stop()

# ── search & filters ──────────────────────────────────────────────────────────
col_search, col_dir, col_sort = st.columns([3, 1.2, 1.2])

with col_search:
    query = st.text_input("", placeholder="🔍  Search jobs, shippers, consignees, goods, flight #, customs…", label_visibility="collapsed")

with col_dir:
    direction = st.selectbox("Direction", ["All", "Import", "Export", "Domestic"], label_visibility="collapsed")

with col_sort:
    sort_by = st.selectbox("Sort by", ["Date Issued", "JOB/HAWB", "Shipper Company", "Consignee Company", "Direction"], label_visibility="collapsed")

# ── apply filters ─────────────────────────────────────────────────────────────
filtered = df.copy()

if direction != "All":
    filtered = filtered[filtered["Direction"] == direction]

if query:
    q = query.lower()
    mask = filtered.apply(lambda row: row.astype(str).str.lower().str.contains(q).any(), axis=1)
    filtered = filtered[mask]

if sort_by in filtered.columns:
    filtered = filtered.sort_values(sort_by, ascending=False)

st.caption(f"Showing **{len(filtered)}** of **{total}** shipments")

# ── results table ─────────────────────────────────────────────────────────────
DISPLAY_COLS = [
    "JOB/HAWB", "Date Issued", "Direction",
    "Shipper Company", "Consignee Company",
    "Goods Description", "Flight #", "MAWB",
    "Weight", "Delivery Date/Time",
]
display_cols = [c for c in DISPLAY_COLS if c in filtered.columns]
display_df = filtered[display_cols].copy()

# Truncate long fields for table view
for col in ["Goods Description", "Shipper Company", "Consignee Company"]:
    if col in display_df.columns:
        display_df[col] = display_df[col].apply(lambda x: (str(x)[:45] + "…") if len(str(x)) > 45 else str(x))

# Show table — user clicks row number to view details
event = st.dataframe(
    display_df.reset_index(drop=True),
    use_container_width=True,
    height=min(400, 60 + len(display_df) * 35),
    on_select="rerun",
    selection_mode="single-row",
)

# ── detail panel ──────────────────────────────────────────────────────────────
selected_rows = event.selection.get("rows", []) if event and hasattr(event, "selection") else []

if selected_rows:
    idx = filtered.reset_index(drop=True).index[selected_rows[0]]
    row = filtered.reset_index(drop=True).iloc[selected_rows[0]]

    SECTIONS = [
        ("Job Information",    ["JOB/HAWB", "Date Issued", "Vehicle", "Special Instructions", "Direction"]),
        ("Shipper",            ["Shipper Company", "Shipper Address", "Shipper City/ZIP", "Shipper Country"]),
        ("Consignee",          ["Consignee Company", "Consignee Address", "Consignee City/ZIP", "Consignee Country", "Delivery Contact"]),
        ("References & Goods", ["Reference", "Goods Description", "Pkg Qty", "Pkg Type", "Weight", "Dimensions"]),
        ("Flight",             ["Airline", "Flight #", "MAWB", "Dep Time", "Dep Airport", "Arr Time", "Arr Airport"]),
        ("Pickup & Delivery",  ["Pickup Location", "Pickup Start Time", "Customs Entry #", "Firm Code", "Delivery Date/Time", "Segment End Time"]),
    ]

    rows_html = ""
    for sec_title, fields in SECTIONS:
        rows_html += f'<div class="detail-section-title">{sec_title}</div>'
        for field in fields:
            val = str(row.get(field, "")) if field in row.index else ""
            if val and val not in ("nan", "None", ""):
                rows_html += f'<div class="detail-row"><span class="detail-label">{field}</span><span class="detail-value">{val}</span></div>'

    dir_val = str(row.get("Direction", ""))
    st.markdown(f"""
    <div class="detail-card">
      <div style="display:flex; align-items:center; gap:12px; margin-bottom:4px">
        <span style="font-family:'IBM Plex Mono',monospace; font-size:20px; font-weight:700; color:#FFCC00">{row.get("JOB/HAWB","")}</span>
        <span class="badge-{dir_val}">{dir_val.upper()}</span>
      </div>
      <div style="color:#8892a4; font-size:12px; font-family:'IBM Plex Mono',monospace; margin-bottom:4px">{row.get("Source File","")}</div>
      {rows_html}
    </div>
    """, unsafe_allow_html=True)

# ── footer ────────────────────────────────────────────────────────────────────
st.markdown("---")
st.caption("DHL Same Day · Mahoney Express Inc · 1531 Ashland Ave · ORD IL 60305")
