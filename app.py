import re
from pathlib import Path

import pandas as pd
import plotly.express as px
import streamlit as st
from runtime_diagnostics import render_display_dataframe

st.set_page_config(page_title="PBOS ΓÇö Business Planning Operating System", page_icon="≡ƒôè", layout="wide")

BASE = Path(__file__).parent

def parse_num(x):
    if pd.isna(x):
        return None
    if isinstance(x, (int, float)):
        return float(x)
    s = str(x).strip()
    if s == "" or s.lower() in {"nan", "none"}:
        return None
    is_pct = "%" in s
    s = s.replace("Γé╣", "").replace(",", "").replace("%", "").strip()
    s = re.sub(r"[^0-9.\-]", "", s)
    if s in {"", "-", "."}:
        return None
    try:
        val = float(s)
        return val / 100 if is_pct else val
    except Exception:
        return None

def normalize_hc(v):
    if v is None or pd.isna(v):
        return None
    v = float(v)
    if v > 10000:
        return v / 1000
    return v

def money(v):
    if v is None or pd.isna(v):
        return "ΓÇö"
    v = float(v)
    sign = "-" if v < 0 else ""
    v = abs(v)
    if v >= 10_000_000:
        return f"{sign}Γé╣{v/10_000_000:.2f} Cr"
    if v >= 100_000:
        return f"{sign}Γé╣{v/100_000:.2f} L"
    return f"{sign}Γé╣{v:,.0f}"

def fmt(v, unit=""):
    if v is None or pd.isna(v):
        return "ΓÇö"
    unit = str(unit)
    if unit == "Γé╣":
        return money(v)
    if unit == "%":
        return f"{float(v)*100:.1f}%" if abs(float(v)) < 2 else f"{float(v):.1f}%"
    if unit == "HC":
        return f"{normalize_hc(v):,.0f} HC"
    if unit == "MT/month":
        return f"{float(v):,.0f} MT/month"
    if "Bird" in unit:
        return f"{float(v):,.0f} Birds/day"
    if unit == "Days":
        return f"{float(v):,.0f} Days"
    if unit == "kg":
        return f"{float(v):,.0f} kg"
    return f"{float(v):,.2f}"

def kpi_value(df, kpi_name, col="Current Value"):
    key = str(kpi_name).strip()
    if key:
        hit = df[df["KPI ID"].astype(str).str.strip().str.lower() == key.lower()]
        if not hit.empty:
            return parse_num(hit.iloc[0].get(col))
    hit = df[df["KPI"].astype(str).str.lower() == key.lower()]
    if hit.empty:
        return None
    return parse_num(hit.iloc[0].get(col))

def driver_value(drivers, driver_id, col="Scenario"):
    hit = drivers[drivers["Driver ID"].astype(str) == driver_id]
    if hit.empty:
        return None
    return parse_num(hit.iloc[0].get(col))

@st.cache_data
def load_dependency_registry():
    path = BASE / "dependency_registry.csv"
    if not path.exists():
        return pd.DataFrame(columns=["driver_id", "driver_name", "affected_kpi_id", "affected_kpi_name", "relationship_type", "impact_strength", "condition", "business_reason"])
    try:
        return pd.read_csv(path)
    except Exception:
        return pd.DataFrame(columns=["driver_id", "driver_name", "affected_kpi_id", "affected_kpi_name", "relationship_type", "impact_strength", "condition", "business_reason"])

@st.cache_data
def load_data():
    dash = pd.read_csv(BASE / "dashboard_data.csv")
    drivers = pd.read_csv(BASE / "strategy_drivers.csv")
    for col in ["Current Value", "Scenario Value", "Delta", "Delta %", "FY2027", "FY2028", "FY2029", "FY2030", "FY2031"]:
        if col in dash.columns:
            dash[col + " Num"] = dash[col].apply(parse_num)
    drivers["Current Num"] = drivers["Current"].apply(parse_num)
    drivers["Scenario Num"] = drivers["Scenario"].apply(parse_num)
    return dash, drivers

dash, drivers = load_data()

st.markdown("""
<style>
.main {background:#f7f9fc;}
.block-container {padding-top:1.2rem;}
.hero {background:#0B1F33;color:white;padding:20px 26px;border-radius:14px;margin-bottom:18px;}
.hero h1 {margin:0;font-size:26px;line-height:1.2;}
.hero p {margin:4px 0 0 0;color:#c9d6e4;font-size:0.92rem;}
.hero-meta {display:flex;flex-wrap:wrap;gap:8px;margin-top:8px;}
.hero-chip {display:inline-block;border:1px solid rgba(201,214,228,.45);border-radius:999px;padding:2px 8px;font-size:11px;color:#d6e3ef;}
.hero-badge {display:inline-block;border-radius:999px;padding:2px 8px;font-size:11px;font-weight:700;background:#dbeafe;color:#0f2340;}
.demo-note {border:1px solid #d9e4f0;background:#f4f8fc;color:#3f566e;border-radius:10px;padding:7px 10px;margin-bottom:14px;font-size:0.8rem;}
.top-controls .stButton > button {width:100%;border-radius:10px;border:1px solid #c8d2e0;background:#ffffff;color:#163453;font-size:0.82rem;padding:0.4rem 0.65rem;}
.card {background:white;border:1px solid #e5e7eb;border-radius:14px;padding:14px 16px;box-shadow:0 2px 8px rgba(15,23,42,.06);min-height:190px;height:190px;display:flex;flex-direction:column;justify-content:flex-start;gap:4px;overflow:hidden;}
.card-title {font-size:13px;color:#64748b;margin-bottom:2px;white-space:nowrap;overflow:hidden;text-overflow:ellipsis;font-weight:700;}
.card-value {font-size:25px;font-weight:800;color:#0f172a;line-height:1.15;white-space:nowrap;}
.card-sub {font-size:12px;color:#64748b;margin-top:4px;display:flex;flex-direction:column;gap:3px;}
.card-delta {font-size:14px;font-weight:800;}
.card-badge {display:inline-block;width:fit-content;padding:2px 8px;border-radius:999px;font-size:11px;font-weight:700;letter-spacing:0.02em;}
.insight {background:#fff;border-left:5px solid #1f4e78;padding:14px 16px;border-radius:10px;margin-bottom:10px;}
</style>
""", unsafe_allow_html=True)

def show_about_pbos():
        if hasattr(st, "dialog"):
                @st.dialog("About PBOS")
                def _about_dialog():
                        st.markdown("### PBOS ΓÇö Business Planning Operating System")
                        st.write("Version 1.0 MVP")
                        st.write("Created by:")
                        st.write("Sumit Kumar Mukherjee")
                        st.write("Role:")
                        st.write("Founder & Product Architect")
                        st.write("Purpose:")
                        st.write("PBOS is a scenario-based business planning platform for poultry and food manufacturing operations. It connects revenue planning with channel ownership, plant capacity, raw-material requirement, logistics, manpower and financial impact.")
                        st.write("Current status:")
                        st.write("Public planning prototype. Scenario values are planning assumptions and are not live ERP or confirmed operational data.")
                        st.write("Technology:")
                        st.markdown("- Python\n- Streamlit\n- Pandas\n- Plotly\n- GitHub\n- Streamlit Community Cloud")
                        st.write("Repository:")
                        st.write("https://github.com/fundusumit/PBOS")

                _about_dialog()


hero_left, hero_right = st.columns([0.84, 0.16])
with hero_left:
        st.markdown("""
        <div class="hero">
            <h1>PBOS ΓÇö Business Planning Operating System</h1>
            <p>Scenario-based planning for revenue, channels, plant capacity, procurement, logistics, manpower and profitability.</p>
            <div class="hero-meta">
                <span class="hero-chip">Version 1.0 MVP</span>
                <span class="hero-chip">Created by Sumit Kumar Mukherjee</span>
                <span class="hero-chip">Founder & Product Architect</span>
                <span class="hero-badge">Public Planning Prototype</span>
            </div>
        </div>
        """, unsafe_allow_html=True)
with hero_right:
        st.markdown("<div class='top-controls'>", unsafe_allow_html=True)
        if st.button("About PBOS", key="about_pbos_app"):
                show_about_pbos()
        st.markdown("</div>", unsafe_allow_html=True)

st.markdown("<div class='demo-note'><b>Demo note:</b> This public version uses planning assumptions and scenario inputs. It does not contain confidential company data or live ERP transactions.</div>", unsafe_allow_html=True)

with st.sidebar:
    st.header("Scenario Drivers")
    rev_default = driver_value(drivers, "REV_TARGET") or kpi_value(dash, "Revenue") or 75_000_000
    asp_default = driver_value(drivers, "ASP_KG") or 240
    bird_default = driver_value(drivers, "BIRD_RATE") or 120
    yield_default = driver_value(drivers, "YIELD") or 0.73
    cap_default = driver_value(drivers, "CAPACITY_MT") or 75
    mkt_default = driver_value(drivers, "MKT_PCT") or 0.06
    wc_days_default = driver_value(drivers, "INV_DAYS") or 35

    revenue_target = st.number_input("Revenue Target (Γé╣)", value=float(rev_default), step=5_000_000.0, format="%.0f")
    bird_rate = st.number_input("Live Bird Rate (Γé╣/kg)", value=float(bird_default), step=1.0)
    yield_pct = st.slider("Planning Yield %", min_value=0.50, max_value=0.90, value=float(yield_default), step=0.01, format="%.2f")
    plant_capacity = st.number_input("Plant Capacity (MT/month)", value=float(cap_default), step=5.0)
    marketing_pct = st.slider("Marketing % of Revenue", min_value=0.00, max_value=0.15, value=float(mkt_default), step=0.005, format="%.3f")
    inventory_days = st.number_input("Inventory Days", value=float(wc_days_default), step=1.0)
    run = st.button("Run Scenario", type="primary", width="stretch")

rev_cur = kpi_value(dash, "EXE001") or kpi_value(dash, "Revenue") or kpi_value(dash, "Annual Revenue") or 60_000_000
eb_cur = kpi_value(dash, "EXE003") or kpi_value(dash, "EBITDA") or 5_224_000
pat_cur = kpi_value(dash, "EXE004") or kpi_value(dash, "PAT") or 1_443_000
gc_cur = kpi_value(dash, "EXE002") or kpi_value(dash, "Gross Contribution") or 16_324_000
wc_cur = kpi_value(dash, "EXE007") or kpi_value(dash, "Working Capital Requirement") or kpi_value(dash, "Total Funding Requirement") or 829_306_914
birds_cur = kpi_value(dash, "EXE009") or kpi_value(dash, "Birds / Day") or 356
capex_cur = kpi_value(dash, "EXE012") or kpi_value(dash, "Total CAPEX") or 30_450_000
opex_cur = kpi_value(dash, "EXE013") or kpi_value(dash, "Total OPEX") or 20_400_000
emp_cur = normalize_hc(kpi_value(dash, "EXE011") or kpi_value(dash, "Total Employees") or 923)
capacity_cur = kpi_value(dash, "EXE010") or kpi_value(dash, "Plant Capacity MT / Month") or 50
bird_rate_cur = driver_value(drivers, "BIRD_RATE", "Current") or 115
yield_cur = driver_value(drivers, "YIELD", "Current") or 0.72

ratio = revenue_target / rev_cur if rev_cur else 1
bird_cost_pressure = bird_rate / bird_rate_cur if bird_rate_cur else 1
yield_benefit = yield_cur / yield_pct if yield_pct else 1

rev_scn = revenue_target
birds_scn = birds_cur * ratio * yield_benefit
capacity_need = (rev_scn / asp_default) / 1000 / 12 if asp_default else 0
capacity_util = capacity_need / plant_capacity if plant_capacity else 0
wc_scn = wc_cur * ratio * (inventory_days / 35)
gc_margin = gc_cur / rev_cur if rev_cur else 0.27
gc_scn = rev_scn * gc_margin * (1 + max(0, yield_pct-yield_cur))
opex_scn = opex_cur * (ratio ** 0.85) + (rev_scn * max(0, marketing_pct - 0.05))
ebitda_scn = gc_scn - opex_scn - (rev_scn * 0.02 * (bird_cost_pressure - 1))
pat_ratio = pat_cur / eb_cur if eb_cur else 0.28
pat_scn = max(0, ebitda_scn * pat_ratio)
capex_scn = capex_cur + (11_500_000 if capacity_util > 0.90 else 0)
emp_scn = normalize_hc(emp_cur * ratio * (1 - 0.12))

metrics = [
    ("≡ƒÆ░ Revenue", rev_cur, rev_scn, "Γé╣"),
    ("≡ƒôê Gross Contribution", gc_cur, gc_scn, "Γé╣"),
    ("≡ƒÅª EBITDA", eb_cur, ebitda_scn, "Γé╣"),
    ("Γ£à PAT", pat_cur, pat_scn, "Γé╣"),
    ("≡ƒÆ╡ Working Capital Requirement", wc_cur, wc_scn, "Γé╣"),
    ("≡ƒÉö Bird Requirement", birds_cur, birds_scn, "Birds/day"),
    ("≡ƒÅ¡ Available Plant Capacity", capacity_cur, plant_capacity, "MT/month"),
    ("≡ƒÅù∩╕Å CAPEX", capex_cur, capex_scn, "Γé╣"),
    ("ΓÜÖ∩╕Å OPEX", opex_cur, opex_scn, "Γé╣"),
    ("≡ƒæÑ Automation-adjusted HC", emp_cur, emp_scn, "HC"),
]

dependency_registry = load_dependency_registry()
changed_driver_ids = []
changed_driver_values = []
for driver_id, scenario_value in [("REV_TARGET", revenue_target), ("BIRD_RATE", bird_rate), ("YIELD", yield_pct), ("CAPACITY_MT", plant_capacity), ("MKT_PCT", marketing_pct), ("INV_DAYS", inventory_days)]:
    current_value = driver_value(drivers, driver_id, "Current")
    if current_value is None or scenario_value is None:
        continue
    if abs(float(scenario_value) - float(current_value)) > 1e-9:
        changed_driver_ids.append(driver_id)
        changed_driver_values.append((driver_id, current_value, scenario_value))

if not dependency_registry.empty and changed_driver_values:
    st.markdown("---")
    st.subheader("Business Dependency Intelligence")
    rows = []
    for driver_id, current_value, scenario_value in changed_driver_values:
        relevant = dependency_registry[dependency_registry["driver_id"].astype(str) == driver_id]
        for _, row in relevant.iterrows():
            rows.append({
                "Changed Driver": row.get("driver_name", driver_id),
                "Current": current_value,
                "Scenario": scenario_value,
                "Affected KPIs": row.get("affected_kpi_name", ""),
                "Relationship Type": row.get("relationship_type", ""),
                "Business Reason": row.get("business_reason", ""),
            })
    if rows:
        render_display_dataframe(st, "business_dependency_intelligence", pd.DataFrame(rows), width="stretch", hide_index=True)

st.subheader("Executive KPIs")
cols = st.columns(5)
for i, (name, cur, scn, unit) in enumerate(metrics):
    delta = scn - cur
    delta_pct = None if cur in (None, 0) else ((scn - cur) / cur) * 100
    if "Working Capital" in name:
        status = "Needs Funding"
        status_color = "#dc2626" if delta > 0 else "#16a34a"
    elif "Bird" in name:
        status = "Procurement Increase"
        status_color = "#f59e0b" if delta > 0 else "#16a34a"
    elif "Capacity" in name:
        status = "Expansion Ready"
        status_color = "#16a34a" if delta > 0 else "#f59e0b"
    elif "CAPEX" in name:
        status = "Capacity Investment"
        status_color = "#f59e0b" if delta > 0 else "#16a34a"
    elif "OPEX" in name:
        status = "Cost Pressure"
        status_color = "#dc2626" if delta > 0 else "#16a34a"
    elif "Automation-adjusted HC" in name:
        status = "Efficiency Gain"
        status_color = "#16a34a" if delta < 0 else "#f59e0b"
    else:
        status = "Growing" if delta > 0 else "Softening"
        status_color = "#16a34a" if delta > 0 else "#f59e0b"
    arrow = "Γû▓" if (delta_pct or 0) >= 0 else "Γû╝"
    delta_text = "ΓÇö" if delta_pct is None else f"{arrow}{abs(delta_pct):.0f}%"
    with cols[i % 5]:
        st.markdown(f"""
        <div class="card">
          <div class="card-title">{name}</div>
          <div class="card-value">{fmt(scn, unit)}</div>
          <div class="card-sub">
            <div><b>Current:</b> {fmt(cur, unit)}</div>
            <div class="card-delta" style="color:{'#16a34a' if delta >= 0 else '#dc2626'};">{delta_text}</div>
            <div class="card-badge" style="background:{status_color}20;color:{status_color};">{status}</div>
          </div>
        </div>
        """, unsafe_allow_html=True)

st.markdown("---")
left, right = st.columns([1.15, 0.85])

with left:
    st.subheader("Business Impact: Current vs Scenario")
    comp = pd.DataFrame(metrics, columns=["KPI", "Current", "Scenario", "Unit"])
    comp["KPI"] = comp["KPI"].str.replace("≡ƒÆ░ ","").str.replace("≡ƒôê ","").str.replace("≡ƒÅª ","").str.replace("Γ£à ","").str.replace("≡ƒÆ╡ ","").str.replace("≡ƒÉö ","").str.replace("≡ƒÅ¡ ","").str.replace("≡ƒÅù∩╕Å ","").str.replace("ΓÜÖ∩╕Å ","").str.replace("≡ƒæÑ ","")
    comp_long = comp.melt(id_vars=["KPI", "Unit"], value_vars=["Current", "Scenario"], var_name="Plan", value_name="Value")
    fig = px.bar(
        comp_long[comp_long["KPI"].isin(["Revenue", "EBITDA", "PAT", "Working Capital", "CAPEX", "OPEX"])],
        x="KPI", y="Value", color="Plan", barmode="group", height=410
    )
    fig.update_layout(margin=dict(l=10, r=10, t=30, b=10), legend_title_text="")
    st.plotly_chart(fig, width="stretch")

with right:
    st.subheader("Five-Year Revenue Roadmap")
    fy_row = dash[dash["KPI ID"].astype(str).eq("FY001")]
    if not fy_row.empty:
        values = [parse_num(fy_row.iloc[0].get(y)) for y in ["FY2027", "FY2028", "FY2029", "FY2030", "FY2031"]]
    else:
        values = [60_000_000, 75_000_000, 95_000_000, 120_000_000, 150_000_000]
    road = pd.DataFrame({"Year": ["FY2027", "FY2028", "FY2029", "FY2030", "FY2031"], "Revenue": values})
    fig2 = px.line(road, x="Year", y="Revenue", markers=True, height=410)
    fig2.update_layout(margin=dict(l=10, r=10, t=30, b=10))
    st.plotly_chart(fig2, width="stretch")

st.markdown("---")
col_a, col_b = st.columns([0.58, 0.42])

with col_a:
    st.subheader("CEO KPI Table")
    table = pd.DataFrame({
        "KPI": [m[0] for m in metrics],
        "Current": [fmt(m[1], m[3]) for m in metrics],
        "Scenario": [fmt(m[2], m[3]) for m in metrics],
        "Delta": [fmt(m[2]-m[1], m[3]) for m in metrics],
        "Signal": ["Expansion Risk" if m[0].endswith("CAPEX") and capacity_util>0.90 else ("Improves" if m[2] >= m[1] else "Weakens") for m in metrics]
    })
    render_display_dataframe(st, "ceo_kpi_table", table, width="stretch", hide_index=True)

with col_b:
    st.subheader("PBOS AI Advisor")
    wc_delta = wc_scn - wc_cur
    rev_delta = rev_scn - rev_cur
    ebitda_delta = ebitda_scn - eb_cur
    cap_msg = "Expansion CAPEX is triggered because utilization crosses 90%." if capacity_util > 0.90 else "No immediate expansion CAPEX is triggered."
    st.markdown(f"""
    <div class="insight"><b>Revenue impact:</b> Revenue moves by {money(rev_delta)} to {money(rev_scn)}.</div>
    <div class="insight"><b>Operations impact:</b> Bird requirement moves to {fmt(birds_scn, 'Birds/day')}. Capacity utilization is {capacity_util*100:.1f}%.</div>
    <div class="insight"><b>Cash impact:</b> Working capital changes by {money(wc_delta)}.</div>
    <div class="insight"><b>Profitability impact:</b> EBITDA changes by {money(ebitda_delta)}.</div>
    <div class="insight"><b>Recommendation:</b> {cap_msg} Keep procurement and working capital under weekly review.</div>
    """, unsafe_allow_html=True)

st.markdown("---")
with st.expander("Raw Dashboard Data", expanded=False):
    render_display_dataframe(st, "raw_dashboard_data", dash, max_rows=300, width="stretch")
with st.expander("Strategy Drivers", expanded=False):
    render_display_dataframe(st, "strategy_drivers", drivers, max_rows=300, width="stretch")
