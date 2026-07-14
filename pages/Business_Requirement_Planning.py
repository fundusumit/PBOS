import math
import os
import sys
from datetime import date
from html import escape
import pandas as pd
import streamlit as st

sys.path.append(os.path.dirname(os.path.dirname(__file__)))
from calculation_engine import align_manpower_sales, build_channel_sales_output, build_contract_pricing_output, build_distributor_output, build_explainability, build_financial_chain, build_logistics_output, build_order_capacity_intelligence, build_plant_planning
from runtime_diagnostics import get_runtime_environment, log_dataframe_shape, log_runtime_event, log_section_end, log_section_start, render_display_dataframe, render_display_editor

st.set_page_config(page_title="PBOS — Business Planning Operating System", page_icon="📊", layout="wide")
log_runtime_event("page_start", **get_runtime_environment())

st.markdown("""
<style>
.pbos-page-header {
    background: linear-gradient(135deg, #0f2340 0%, #162c4d 100%);
    border-radius: 18px;
    padding: 14px 18px;
    margin-bottom: 10px;
    box-shadow: 0 8px 24px rgba(15, 35, 64, 0.16);
}
.pbos-page-title {
    font-size: 1.45rem;
    font-weight: 700;
    color: #ffffff;
    margin: 0 0 4px 0;
    line-height: 1.2;
    word-break: normal;
    overflow-wrap: anywhere;
}
.pbos-page-subtitle {
    font-size: 0.88rem;
    color: #c8d2e0;
    margin: 0 0 8px 0;
    line-height: 1.4;
}
.pbos-page-meta {
    display: flex;
    flex-wrap: wrap;
    gap: 8px;
    margin-top: 2px;
    align-items: center;
}
.pbos-meta-chip {
    display: inline-block;
    border: 1px solid rgba(200, 210, 224, 0.45);
    border-radius: 999px;
    padding: 2px 9px;
    color: #d7e3ef;
    font-size: 0.74rem;
    line-height: 1.3;
}
.pbos-status-chip {
    display: inline-block;
    border-radius: 999px;
    padding: 2px 9px;
    color: #0f2340;
    background: #dbeafe;
    font-size: 0.72rem;
    font-weight: 700;
    line-height: 1.3;
    margin-left: 4px;
}
.pbos-page-creator {
    margin-left: auto;
    color: #9fb4ca;
    font-size: 0.72rem;
    text-align: right;
}
.pbos-page-section-heading {
    margin: 2px 0 12px;
    padding: 0 4px;
}
.pbos-page-section-heading h2 {
    margin: 0;
    font-size: 1.25rem;
    color: #13304a;
    line-height: 1.2;
}
.pbos-page-section-heading p {
    margin: 3px 0 0;
    font-size: 0.86rem;
    color: #5f6f7f;
}
.pbos-top-controls {
    display: flex;
    justify-content: flex-end;
    align-items: flex-start;
    padding-top: 8px;
}
.pbos-top-controls .stButton > button {
    width: auto;
    min-width: 120px;
    border-radius: 10px;
    border: 1px solid #c8d2e0;
    background: #ffffff;
    color: #163453;
    font-size: 0.82rem;
    padding: 0.42rem 0.65rem;
}
.pbos-demo-note {
    border: 1px solid #d9e4f0;
    background: #f4f8fc;
    color: #3f566e;
    border-radius: 10px;
    padding: 7px 10px;
    margin-bottom: 14px;
    font-size: 0.8rem;
}
.pbos-section-card {
    background: #ffffff;
    border: 1px solid #e6ebf2;
    border-radius: 16px;
    padding: 16px 16px 14px;
    box-shadow: 0 6px 18px rgba(15, 35, 64, 0.06);
    margin-bottom: 16px;
}
.pbos-section-title {
    font-size: 1.04rem;
    font-weight: 700;
    color: #12324d;
    margin-bottom: 3px;
}
.pbos-section-subtitle {
    font-size: 0.84rem;
    color: #5f6f7f;
    margin-bottom: 10px;
}
.pbos-kpi-card {
    position: relative;
    background: #ffffff;
    border: 1px solid #dbe3ee;
    border-radius: 14px;
    padding: 14px;
    min-height: 120px;
    height: auto;
    box-shadow: 0 4px 14px rgba(15, 23, 42, 0.06);
    display: flex;
    flex-direction: column;
    justify-content: flex-start;
    gap: 6px;
    overflow: visible;
    box-sizing: border-box;
}
.pbos-kpi-accent {
    position: absolute;
    top: 0;
    left: 0;
    right: 0;
    height: 4px;
}
.pbos-kpi-head {
    display: flex;
    align-items: center;
    gap: 8px;
}
.pbos-kpi-icon {
    width: 28px;
    height: 28px;
    display: inline-flex;
    align-items: center;
    justify-content: center;
    border-radius: 999px;
    background: #eaf2ff;
    color: #1d4ed8;
    font-size: 0.95rem;
}
.pbos-kpi-title {
    font-size: 12px;
    font-weight: 700;
    color: #475569;
    text-transform: uppercase;
    letter-spacing: 0.03em;
    white-space: normal;
}
.pbos-kpi-value {
    font-size: 22px;
    font-weight: 800;
    line-height: 1.15;
    color: #0f172a;
    white-space: normal;
    overflow-wrap: anywhere;
}
.pbos-kpi-subtitle {
    font-size: 12px;
    color: #64748b;
    white-space: normal;
}
.pbos-value-negative {
    color: #c2410c;
}
.pbos-status-badge {
    display: inline-block;
    width: fit-content;
    padding: 3px 8px;
    border-radius: 999px;
    font-size: 0.74rem;
    font-weight: 600;
    margin-top: auto;
}
.pbos-status-positive {
    background: #e7f7ec;
    color: #1c7b3f;
}
.pbos-status-warn {
    background: #fff4e5;
    color: #a16207;
}
.pbos-status-alert {
    background: #fde8e8;
    color: #b91c1c;
}
.pbos-status-neutral {
    background: #e8eef6;
    color: #3f5267;
}
.pbos-info-banner {
    background: #eef6ff;
    border: 1px solid #dbeafe;
    color: #1d4ed8;
    border-radius: 10px;
    padding: 8px 10px;
    font-size: 0.84rem;
    margin-top: 8px;
}
.pbos-kpi-card .stButton > button {
    width: 100%;
    border-radius: 10px;
    border: 1px solid #dbe5ee;
    background: #ffffff;
    color: #23415c;
    font-size: 0.8rem;
    padding: 6px 10px;
}
.pbos-kpi-card .stButton > button:hover {
    border-color: #a6c1e4;
    background: #f6faff;
}
.pbos-sidebar-caption {
    font-size: 0.79rem;
    color: #5b6e82;
    margin: -2px 0 8px 0;
}
.pbos-sidebar-note {
    font-size: 0.76rem;
    color: #5f7388;
    margin: 4px 0 8px;
}
.pbos-staffing-wrap {
    border: 1px solid #dbe3ee;
    border-radius: 12px;
    overflow-x: auto;
    overflow-y: hidden;
    margin-top: 8px;
}
.pbos-staffing-wrap table {
    width: 100%;
    min-width: 980px;
    border-collapse: collapse;
    table-layout: fixed;
    font-size: 0.78rem;
}
.pbos-staffing-wrap th {
    background: #f4f8fc;
    color: #334155;
    font-weight: 700;
    padding: 8px;
    text-align: left;
    border-bottom: 1px solid #e2e8f0;
}
.pbos-staffing-wrap td {
    padding: 8px;
    border-top: 1px solid #eef2f7;
    vertical-align: top;
    white-space: normal;
    word-break: break-word;
    overflow-wrap: anywhere;
}
.pbos-ceo-summary {
    border: 1px solid #d7e1ec;
    border-radius: 12px;
    padding: 12px;
    background: #fbfdff;
}
.pbos-ceo-row {
    font-size: 0.88rem;
    color: #2c4055;
    margin-bottom: 6px;
}
.pbos-footer {
    border-top: 1px solid #e4ebf4;
    margin-top: 8px;
    padding-top: 10px;
    color: #5b6e82;
    font-size: 0.78rem;
    line-height: 1.5;
}
.pbos-footer a {
    color: #2d5b88;
    text-decoration: none;
}
.pbos-formula-table-wrap {
    width: 100%;
    overflow: visible;
}
.pbos-formula-table {
    width: 100%;
    border-collapse: collapse;
    table-layout: fixed;
    font-size: 0.8rem;
    border: 1px solid #e6ebf2;
    border-radius: 10px;
    overflow: hidden;
}
.pbos-formula-table th,
.pbos-formula-table td {
    border-bottom: 1px solid #eef2f7;
    padding: 8px 10px;
    text-align: left;
    vertical-align: top;
    white-space: normal;
    word-break: break-word;
    overflow-wrap: anywhere;
    height: auto;
    line-height: 1.35;
}
.pbos-formula-table th {
    background: #f8fafc;
    color: #334155;
    font-weight: 600;
}
.pbos-formula-table tbody tr:last-child td {
    border-bottom: none;
}
.pbos-formula-table .pbos-formula-empty {
    color: #94a3b8;
}
.pbos-formula-block {
    white-space: normal;
    word-break: break-word;
    overflow-wrap: anywhere;
    line-height: 1.45;
}
@media (max-width: 900px) {
    .pbos-page-header {
        padding: 12px 14px;
    }
    .pbos-page-title {
        font-size: 1.2rem;
    }
    .pbos-kpi-card {
        min-height: auto;
    }
    .pbos-page-creator {
        margin-left: 0;
        width: 100%;
        text-align: left;
    }
}
@media (max-width: 768px) {
    .block-container {
        padding-left: 0.9rem;
        padding-right: 0.9rem;
        padding-bottom: 5rem;
    }
    .pbos-page-header {
        padding: 1rem 1rem 0.9rem 1rem;
        margin-bottom: 0.6rem;
    }
    .pbos-page-title {
        font-size: 1.55rem;
        line-height: 1.2;
        word-break: normal;
        overflow-wrap: anywhere;
    }
    .pbos-page-subtitle {
        font-size: 0.9rem;
        line-height: 1.4;
    }
    .pbos-page-meta {
        gap: 0.4rem;
    }
    .pbos-meta-chip,
    .pbos-status-chip {
        font-size: 0.68rem;
        padding: 2px 7px;
        max-width: 100%;
    }
    .pbos-page-creator {
        margin-top: 0.15rem;
        font-size: 0.72rem;
    }
    .pbos-top-controls {
        justify-content: flex-start;
        padding-top: 0.15rem;
        margin-top: 0.6rem;
    }
    .pbos-top-controls .stButton > button {
        width: auto;
        min-width: 112px;
        padding: 0.38rem 0.62rem;
    }
    .pbos-demo-note {
        padding: 0.8rem 0.9rem;
        font-size: 0.9rem;
        line-height: 1.45;
    }
    .pbos-page-section-heading {
        margin-top: 0;
        margin-bottom: 10px;
    }
    .pbos-page-section-heading h2 {
        font-size: 1.8rem;
        line-height: 1.2;
    }
    .pbos-page-section-heading p {
        font-size: 0.9rem;
        line-height: 1.4;
    }
    [data-testid="stSidebar"] [data-testid="stExpander"] summary {
        font-size: 0.86rem;
        line-height: 1.25;
        min-height: 44px;
        padding-top: 0.35rem;
        padding-bottom: 0.35rem;
        white-space: normal;
    }
    [data-testid="stSidebar"] [data-testid="stVerticalBlock"] {
        gap: 0.45rem;
    }
    [data-testid="stSidebar"] [data-baseweb="input"],
    [data-testid="stSidebar"] [data-baseweb="select"],
    [data-testid="stSidebar"] .stSlider,
    [data-testid="stSidebar"] .stButton {
        width: 100%;
    }
    [data-testid="stHorizontalBlock"] {
        gap: 0.55rem;
    }
    [data-testid="stHorizontalBlock"] > [data-testid="column"] {
        min-width: calc(50% - 0.3rem);
        flex: 1 1 calc(50% - 0.3rem);
    }
    .pbos-kpi-card {
        padding: 12px;
    }
    .pbos-kpi-title {
        font-size: 0.78rem;
        line-height: 1.25;
    }
    .pbos-kpi-value {
        font-size: 1.35rem;
        line-height: 1.2;
    }
    .pbos-kpi-subtitle {
        font-size: 0.82rem;
    }
    .pbos-status-badge {
        font-size: 0.7rem;
        padding: 2px 7px;
    }
    .pbos-staffing-wrap {
        overflow-x: auto;
    }
    .pbos-staffing-wrap table {
        font-size: 0.74rem;
        min-width: 900px;
    }
}
@media (max-width: 600px) {
    [data-testid="stHorizontalBlock"] > [data-testid="column"] {
        min-width: 100%;
        flex: 1 1 100%;
    }
    .pbos-formula-table {
        font-size: 0.76rem;
    }
}
</style>
""", unsafe_allow_html=True)

def show_about_pbos():
    if hasattr(st, "dialog"):
        @st.dialog("About PBOS")
        def _about_dialog():
            st.markdown("### PBOS — Business Planning Operating System")
            st.write("Version 1.0 MVP")
            st.write("Created by Sumit Kumar Mukherjee")
            st.write("PBOS is a scenario-based planning platform connecting revenue, channel allocation, plant capacity, procurement, logistics, manpower and profitability.")
            st.write("Current status:")
            st.write("Public planning prototype using assumptions and scenario inputs. It is not connected to live ERP data.")

        _about_dialog()
    else:
        with st.expander("About PBOS", expanded=False):
            st.markdown("### PBOS — Business Planning Operating System")
            st.write("Version 1.0 MVP")
            st.write("Created by: Sumit Kumar Mukherjee")


def render_staffing_bands_table(staffing_df):
    columns = [
        "Function",
        "Current Workload",
        "Unit",
        "Staffing Band",
        "Lower Threshold",
        "Upper Threshold",
        "Current HC",
        "Recommended HC",
        "Threshold Status",
        "Business Reason",
    ]
    widths = {
        "Function": "10%",
        "Current Workload": "8%",
        "Unit": "7%",
        "Staffing Band": "11%",
        "Lower Threshold": "8%",
        "Upper Threshold": "8%",
        "Current HC": "7%",
        "Recommended HC": "8%",
        "Threshold Status": "11%",
        "Business Reason": "22%",
    }
    header_html = "".join(f"<th>{escape(col)}</th>" for col in columns)
    colgroup_html = "".join(f"<col style='width:{widths[col]};'>" for col in columns)
    row_html = []
    for _, row in staffing_df.iterrows():
        cell_html = "".join(f"<td>{escape(str(row.get(col, '')))}</td>" for col in columns)
        row_html.append(f"<tr>{cell_html}</tr>")

    st.markdown(
        f"""
        <div class='pbos-staffing-wrap'>
          <table>
            <colgroup>{colgroup_html}</colgroup>
            <thead><tr>{header_html}</tr></thead>
            <tbody>{''.join(row_html)}</tbody>
          </table>
        </div>
        """,
        unsafe_allow_html=True,
    )


hero_left, hero_right = st.columns([0.84, 0.16])
with hero_left:
    st.markdown("""
    <div class="pbos-page-header">
      <div class="pbos-page-title">PBOS — Business Planning Operating System</div>
      <div class="pbos-page-subtitle">Scenario-based planning for revenue, channels, plant capacity, procurement, logistics, manpower and profitability.</div>
      <div class="pbos-page-meta">
        <span class="pbos-meta-chip">Version 1.0 MVP</span>
        <span class="pbos-status-chip">Public Planning Prototype</span>
                <span class="pbos-page-creator">Created by Sumit Kumar Mukherjee</span>
      </div>
    </div>
    """, unsafe_allow_html=True)
with hero_right:
    st.markdown("<div class='pbos-top-controls'>", unsafe_allow_html=True)
    if st.button("About PBOS", key="about_pbos_top"):
        show_about_pbos()
    st.markdown("</div>", unsafe_allow_html=True)

st.markdown("<div class='pbos-demo-note'><b>Demo note:</b> This public version uses planning assumptions and scenario inputs. It does not contain confidential company data or live ERP transactions.</div>", unsafe_allow_html=True)
st.markdown(
        """
        <div class='pbos-page-section-heading'>
            <h2>Business Strategic Planning</h2>
            <p>Scenario-based strategic planning for revenue, product portfolios, channels, plant capacity, procurement, logistics, manpower and profitability.</p>
        </div>
        """,
        unsafe_allow_html=True,
)


def fmt_currency(value):
    if value is None:
        return "—"
    sign = "-" if value < 0 else ""
    abs_value = abs(value)
    if abs_value < 10_000_000:
        return f"{sign}₹{abs_value/100_000:.0f} L"
    return f"{sign}₹{abs_value/10_000_000:.2f} Cr"


def fmt_volume(value):
    return f"{value:,.1f} MT/day"


def fmt_birds(value, period="day"):
    suffix = "birds/day" if period == "day" else "birds/month"
    return f"{value:,.0f} {suffix}"


def fmt_rate_per_kg(value):
    sign = "-" if value < 0 else ""
    return f"{sign}₹{abs(value):,.0f}/kg"


def fmt_currency_plain(value, decimals=0):
    sign = "-" if value < 0 else ""
    return f"{sign}₹{abs(value):,.{decimals}f}"


FORMULA_METADATA = {
    "effective_yield": {
        "label": "Effective Finished-Goods Yield",
        "formula": "Planning Yield × (1 − Processing Loss %)",
        "expanded_formula": "Dressed Yield × (1 − Processing Loss %)",
        "assumptions": "Planning yield converts live weight to dressed output. Processing loss reduces dressed output to saleable finished goods. Mortality is not applied in this yield step.",
        "business_meaning": "Saleable yield used to translate live input into finished goods.",
        "related_kpis": "Live Weight Required/month, Birds/day, Raw Material Cost/kg, Live Bird Procurement Spend/month",
    },
    "birds_per_day": {
        "label": "Birds / Day",
        "formula": "Finished Goods kg/month ÷ Effective Finished-Goods Yield → Live Weight Required/month → Net Birds Required/month → Gross Birds Required/month → Birds/day",
        "expanded_formula": "Finished Goods kg/month ÷ Effective Finished-Goods Yield = Live Weight Required/month; Live Weight Required/month ÷ Average Bird Weight = Net Birds Required/month; Adjust for Mortality = Gross Birds Required/month; Gross Birds Required/month ÷ Working Days/month = Birds/day",
        "assumptions": "Finished goods volume is monthly. Average bird weight is the current planning input. Mortality is applied after conversion to gross birds. Working days are the current planning days.",
        "business_meaning": "Daily bird intake required to support the monthly finished-goods plan.",
        "related_kpis": "Effective Finished-Goods Yield, Live Weight Required/month, Live Bird Procurement Spend/month, Traders Required, Farms Required",
    },
    "live_bird_procurement_spend": {
        "label": "Live Bird Procurement Spend",
        "formula": "Live Weight Required × Live Bird Rate",
        "expanded_formula": "Live Weight Required/month × Live Bird Rate/kg = Live Bird Procurement Spend/month",
        "assumptions": "Live Bird Rate is the final all-inclusive procurement or lifting rate. Live weight requirement already reflects yield and mortality logic.",
        "business_meaning": "Monthly upstream bird sourcing cash requirement.",
        "related_kpis": "Birds/day, Raw Material Cost/kg, Traders Required, Farms Required",
    },
    "raw_material_cost_per_kg": {
        "label": "Raw Material Cost / kg",
        "formula": "Live Bird Procurement Spend ÷ Finished Goods kg",
        "expanded_formula": "Live Bird Rate × Live Weight Required ÷ Finished Goods kg",
        "assumptions": "Live Bird Procurement Spend already reflects the gross bird requirement, so mortality is not counted again here.",
        "business_meaning": "Live-bird input cost required to produce one kg of finished goods.",
        "related_kpis": "Live Bird Procurement Spend, Birds/day, Effective Finished-Goods Yield, Gross Contribution",
    },
    "packaging_spend": {
        "label": "Packaging Spend",
        "formula": "Finished Goods kg/month × Packaging Cost/kg",
        "expanded_formula": "Finished Goods kg/month × Packaging Cost/kg = Packaging Spend/month",
        "assumptions": "Packaging cost is a per-kg direct variable cost. It changes profitability but does not change birds/day.",
        "business_meaning": "Packaging cash requirement for the current finished-goods plan.",
        "related_kpis": "Gross Contribution, EBITDA, PAT, Delivered Cost/kg",
    },
    "processing_spend": {
        "label": "Processing Spend",
        "formula": "Finished Goods kg/month × Processing Cost/kg",
        "expanded_formula": "Finished Goods kg/month × Processing Cost/kg = Processing Spend/month",
        "assumptions": "Processing cost is a per-kg direct variable cost from the current governed waterfall.",
        "business_meaning": "Processing cash requirement for the current finished-goods plan.",
        "related_kpis": "Gross Contribution, EBITDA, PAT, Total Direct Variable Spend",
    },
    "transport_spend": {
        "label": "Transport Spend",
        "formula": "Finished Goods kg/month × Transport Cost/kg",
        "expanded_formula": "Finished Goods kg/month × Transport Cost/kg = Transport Spend/month",
        "assumptions": "Transport cost is a per-kg direct variable cost. It affects delivered cost, gross contribution, EBITDA and PAT, but not procurement quantity.",
        "business_meaning": "Finished-goods delivery cost for the current channel plan.",
        "related_kpis": "Delivered Cost/kg, Gross Contribution, EBITDA, PAT",
    },
    "total_direct_variable_spend": {
        "label": "Total Direct Variable Spend",
        "formula": "Live Bird Spend + Processing Spend + Packaging Spend + Transport Spend + Other Direct Variable Costs",
        "expanded_formula": "Live Bird Procurement Spend + Processing Spend + Packaging Spend + Transport Spend + Other Direct Variable Spend = Total Direct Variable Spend",
        "assumptions": "Only governed direct-variable components from the engine are included. No balancing plug is used.",
        "business_meaning": "Total monthly direct variable cost supporting the current production and sales plan.",
        "related_kpis": "Gross Contribution, EBITDA, PAT",
    },
    "ex_factory_cost_per_kg": {
        "label": "Ex-factory Cost / kg",
        "formula": "Raw Material Cost/kg + Processing Cost/kg + Packaging Cost/kg + Factory Overhead/kg",
        "expanded_formula": "Raw Material Cost/kg + Processing Cost/kg + Packaging Cost/kg + Factory Overhead/kg = Ex-factory Cost/kg",
        "assumptions": "Uses the canonical engine waterfall components only. Fixed opex stays below contribution.",
        "business_meaning": "Cost to produce one kg before outbound transport.",
        "related_kpis": "Raw Material Cost/kg, Delivered Cost/kg, Recommended Delivered Price/kg",
    },
    "delivered_cost_per_kg": {
        "label": "Delivered Cost / kg",
        "formula": "Ex-factory Cost/kg + Transport Cost/kg",
        "expanded_formula": "Ex-factory Cost/kg + Transport Cost/kg = Delivered Cost/kg",
        "assumptions": "Delivered cost adds outbound transport to the ex-factory stack.",
        "business_meaning": "Total cost to deliver one kg to the market or customer.",
        "related_kpis": "Ex-factory Cost/kg, Recommended Delivered Price/kg, Gross Contribution",
    },
    "recommended_delivered_price_per_kg": {
        "label": "Recommended Delivered Price / kg",
        "formula": "Delivered Cost/kg ÷ (1 − Target Margin %)",
        "expanded_formula": "Delivered Cost/kg ÷ (1 − Target Margin %) = Recommended Delivered Price/kg",
        "assumptions": "Margin convention is used, not markup. Target margin comes from the current cost-registry or assumption input.",
        "business_meaning": "Margin-based selling price needed to achieve the target delivered margin.",
        "related_kpis": "Delivered Cost/kg, Gross Contribution, EBITDA, PAT",
    },
    "gross_contribution": {
        "label": "Gross Contribution",
        "formula": "Revenue − Total Direct Variable Spend",
        "expanded_formula": "Revenue − Live Bird Procurement Spend − Processing Spend − Packaging Spend − Transport Spend",
        "assumptions": "Direct variable spend includes live bird procurement, processing, packaging and transport. Fixed OPEX is below contribution.",
        "business_meaning": "Direct contribution before operating expenses.",
        "related_kpis": "Live Bird Procurement Spend, Packaging Spend, Transport Spend, EBITDA, PAT",
    },
    "ebitda": {
        "label": "EBITDA",
        "formula": "Displayed Gross Contribution − Marketing Spend − Warehouse OPEX",
        "expanded_formula": "Engine EBITDA − GT Distributor Margin Value",
        "assumptions": "The page-level corporate summary applies a GT distributor margin deduction on top of the engine output before displaying EBITDA.",
        "business_meaning": "Operating profit after marketing and warehouse overhead, as shown in the page-level financial summary.",
        "related_kpis": "Gross Contribution, Marketing Spend, Warehouse OPEX, PAT",
    },
    "pat": {
        "label": "PAT",
        "formula": "Displayed EBITDA × 75%",
        "expanded_formula": "(Engine EBITDA − GT Distributor Margin Value) × 75%",
        "assumptions": "Tax factor is the current simplified page model. The page-level corporate summary applies the GT distributor margin deduction before PAT.",
        "business_meaning": "Net profit shown by the current simplified PBOS corporate model.",
        "related_kpis": "EBITDA, Gross Contribution, GT Distributor Margin Value",
    },
    "traders_required": {
        "label": "Traders Required",
        "formula": "ceil(Birds Required/month ÷ Capacity per Trader)",
        "expanded_formula": "ceil(Birds Required/month ÷ Average Trader Capacity) = Traders Required",
        "assumptions": "Capacity input is treated on the same monthly bird-capacity basis as Birds Required in the current engine. Traders aggregate supply from farms in the upstream sourcing model.",
        "business_meaning": "Upstream live-bird sourcing partner count required to support the current plan.",
        "related_kpis": "Birds/day, Live Bird Procurement Spend, Farms Required, Primary Trips/day, Primary Vehicles Required",
    },
    "farms_required": {
        "label": "Farms Required",
        "formula": "ceil(Birds Required/month ÷ Capacity per Farm)",
        "expanded_formula": "ceil(Birds Required/month ÷ Average Farm Capacity) = Farms Required",
        "assumptions": "Growing cycle is not separately modelled in the current engine. Farm capacity is treated on the same monthly bird-capacity basis as Birds Required. Mortality remains part of the upstream sourcing logic.",
        "business_meaning": "Upstream live-bird farm supply base required to support the current plan.",
        "related_kpis": "Birds/day, Live Bird Procurement Spend, Traders Required, Primary Trips/day, Primary Vehicles Required",
    },
    "primary_trips_day": {
        "label": "Primary Trips / Day",
        "formula": "Live Bird Weight/day ÷ Vehicle Capacity",
        "expanded_formula": "ceil(Live Bird Weight/day ÷ Vehicle Capacity) = Primary Trips/day",
        "assumptions": "Primary logistics uses live-bird weight per day and the current primary vehicle capacity assumption.",
        "business_meaning": "Daily trip requirement to move live birds from the sourcing network to the plant.",
        "related_kpis": "Primary Vehicles Required, Live Bird Procurement Spend, Traders Required, Farms Required",
    },
    "primary_vehicles_required": {
        "label": "Primary Vehicles Required",
        "formula": "ceil(Primary Trips/day ÷ Trips per Vehicle/day)",
        "expanded_formula": "ceil(Primary Trips/day ÷ Trips per Vehicle/day) = Primary Vehicles Required",
        "assumptions": "Vehicle count is based on the current trips-per-vehicle planning assumption.",
        "business_meaning": "Vehicle count required to support the live-bird sourcing plan.",
        "related_kpis": "Primary Trips/day, Live Bird Procurement Spend, Traders Required, Farms Required",
    },
}


def build_formula_rows(section_key, current_value, unit, status, worked_calculation, extra_rows=None, planning_status="Capacity Modelled", actual_status="Not Connected", formula_expression=None, assumptions=None, business_meaning=None, related_kpis=None):
    meta = FORMULA_METADATA[section_key]
    rows = [
        {"Item": "KPI Name", "Value": meta["label"]},
        {"Item": "Current Value", "Value": current_value},
        {"Item": "Unit", "Value": unit},
        {"Item": "Status", "Value": status},
        {"Item": "Formula", "Value": meta["formula"]},
        {"Item": "Formula Expression", "Value": formula_expression or meta["expanded_formula"]},
        {"Item": "Worked Calculation", "Value": worked_calculation},
        {"Item": "Assumptions", "Value": assumptions or meta["assumptions"]},
        {"Item": "Business Meaning", "Value": business_meaning or meta["business_meaning"]},
        {"Item": "Related KPIs", "Value": related_kpis or meta["related_kpis"]},
        {"Item": "Planning Status", "Value": planning_status},
        {"Item": "Actual Network Status", "Value": actual_status},
    ]
    if extra_rows:
        rows.extend(extra_rows)
    return rows


def _format_formula_text(item, value):
        text = "" if value is None else str(value)
        escaped = escape(text)
        if item == "Related KPIs":
                parts = [escape(part.strip()) for part in text.split(",") if part.strip()]
                return "<br>".join(parts)
        if item in {"Formula", "Formula Expression", "Worked Calculation"}:
                formatted = escaped.replace(" = ", "<br>=<br>")
                formatted = formatted.replace(" + ", "<br>+<br>")
                formatted = formatted.replace(" − ", "<br>−<br>")
                formatted = formatted.replace(" × ", "<br>×<br>")
                formatted = formatted.replace(" ÷ ", "<br>÷<br>")
                formatted = formatted.replace(" → ", "<br>→<br>")
                formatted = formatted.replace("\n", "<br>")
                return formatted
        return escaped.replace("\n", "<br>")


def render_wrapped_formula_table(table_key, rows):
        detail_items = {
                "Formula",
                "Formula Expression",
                "Worked Calculation",
                "Assumptions",
                "Business Meaning",
                "Related KPIs",
        }
        body_html = []
        for row in rows:
                item = str(row.get("Item", ""))
                raw_value = row.get("Value", "")
                formatted_value = _format_formula_text(item, raw_value)
                metric_cell = escape(item)
                if item in detail_items:
                        value_cell = "<span class='pbos-formula-empty'>—</span>"
                        description_cell = f"<div class='pbos-formula-block'>{formatted_value}</div>"
                else:
                        value_cell = f"<div class='pbos-formula-block'>{formatted_value}</div>"
                        description_cell = "<span class='pbos-formula-empty'>—</span>"
                body_html.append(
                        f"<tr><td>{metric_cell}</td><td>{value_cell}</td><td>{description_cell}</td></tr>"
                )

        st.markdown(
                f"""
                <div class='pbos-formula-table-wrap' id='{escape(table_key)}'>
                    <table class='pbos-formula-table'>
                        <colgroup>
                            <col style='width:25%;'>
                            <col style='width:20%;'>
                            <col style='width:55%;'>
                        </colgroup>
                        <thead>
                            <tr>
                                <th>Metric</th>
                                <th>Value</th>
                                <th>Description</th>
                            </tr>
                        </thead>
                        <tbody>
                            {''.join(body_html)}
                        </tbody>
                    </table>
                </div>
                """,
                unsafe_allow_html=True,
        )


def render_formula_section(section_key, rows):
    st.markdown(f"**{FORMULA_METADATA[section_key]['label']}**")
    render_wrapped_formula_table(f"formula_{section_key}", rows)


def validate_required_keys(output, required_keys, context):
    missing = [key for key in required_keys if key not in output]
    if missing:
        st.error(f"{context} output contract is missing: {', '.join(missing)}")
        st.stop()


def show_employees_popup():
    st.info("Use the Manpower Planning KPI cards for role responsibilities, risk impact, and CEO recommendations.")


def utilization_status(utilization_pct):
    if utilization_pct < 70:
        return "Green"
    if utilization_pct <= 85:
        return "Healthy"
    return "Expansion Planning"


def format_configuration(lines: int, shifts: int) -> str:
    line_word = "line" if lines == 1 else "lines"
    shift_word = "shift" if shifts == 1 else "shifts"
    return f"{lines} {line_word} × {shifts} {shift_word}"


def _recommended_action_subtitle(output):
    action = str(output.get("recommended_action", "Continue Current Configuration"))
    decision_reason = str(output.get("decision_reason", ""))
    if decision_reason:
        return decision_reason
    return action


def render_plant_capacity_governance_dialog():
    required_output = float(plant_capacity_output.get("required_capacity_mt_day", plant_capacity_output.get("finished_goods_mt_day", 0.0)) or 0.0)
    base_capacity = float(plant_capacity_output.get("plant_base_capacity_mt_day", plant_capacity_output.get("capacity_per_line_mt_day", 0.0)) or 0.0)
    installed_lines = int(round(float(plant_capacity_output.get("current_installed_lines", plant_capacity_output.get("installed_lines", plant_capacity_output.get("production_lines_required", 1))) or 1)))
    active_shifts = int(round(float(plant_capacity_output.get("current_active_shifts", plant_capacity_output.get("active_shifts", plant_capacity_output.get("shifts_required", 1))) or 1)))
    current_configuration_label = str(plant_capacity_output.get("current_configuration_label", f"{installed_lines:,.0f} {'line' if installed_lines == 1 else 'lines'} × {active_shifts:,.0f} {'shift' if active_shifts == 1 else 'shifts'}"))
    installed_capacity = float(plant_capacity_output.get("current_installed_capacity_mt_day", plant_capacity_output.get("installed_capacity_mt_day", 0.0)) or 0.0)
    max_shifts = int(round(float(plant_capacity_output.get("maximum_shifts_per_line", plant_capacity_output.get("max_shifts", 3)) or 3)))
    max_lines = int(round(float(plant_capacity_output.get("maximum_lines_in_current_plant", installed_lines) or installed_lines)))
    max_site_capacity = float(plant_capacity_output.get("maximum_current_plant_capacity_mt_day", 0.0) or 0.0)
    capacity_shortfall = float(plant_capacity_output.get("current_capacity_shortfall_mt_day", plant_capacity_output.get("capacity_shortfall_mt_day", 0.0)) or 0.0)
    capacity_headroom = float(plant_capacity_output.get("capacity_headroom_mt_day", 0.0) or 0.0)
    current_load_ratio = float(plant_capacity_output.get("current_load_ratio_pct", plant_capacity_output.get("plant_utilization_pct", 0.0)) or 0.0)
    projected_utilization = float(plant_capacity_output.get("projected_utilization_pct", 0.0) or 0.0)
    projected_future_utilization = float(plant_capacity_output.get("projected_future_utilization_pct", 0.0) or 0.0)
    capacity_recommendation_mode = str(plant_capacity_output.get("capacity_recommendation_mode", "")).strip()
    recommended_lines = int(round(float(plant_capacity_output.get("recommended_lines", 1) or 1)))
    recommended_shifts = int(round(float(plant_capacity_output.get("recommended_shifts", 1) or 1)))
    recommended_capacity = float(plant_capacity_output.get("recommended_capacity_mt_day", 0.0) or 0.0)
    recommended_configuration_label = str(plant_capacity_output.get("recommended_configuration_label", "")).strip()
    maximum_site_lines = int(round(float(plant_capacity_output.get("maximum_site_lines", max_lines) or max_lines)))
    maximum_site_shifts = int(round(float(plant_capacity_output.get("maximum_site_shifts", max_shifts) or max_shifts)))
    maximum_site_configuration_label = str(plant_capacity_output.get("maximum_site_configuration_label", "")).strip()
    if not maximum_site_configuration_label:
        maximum_site_configuration_label = format_configuration(maximum_site_lines, maximum_site_shifts)
    if not recommended_configuration_label and capacity_recommendation_mode == "CURRENT_SITE_OPTIMIZATION":
        recommended_configuration_label = format_configuration(recommended_lines, recommended_shifts)
    remaining_shift_capacity = float(plant_capacity_output.get("remaining_shift_capacity_mt_day", 0.0) or 0.0)
    remaining_line_capacity = float(plant_capacity_output.get("remaining_line_capacity_mt_day", 0.0) or 0.0)
    remaining_site_capacity = float(plant_capacity_output.get("remaining_current_site_capacity_mt_day", 0.0) or 0.0)
    site_headroom_after_demand = float(plant_capacity_output.get("remaining_site_headroom_after_demand_mt_day", 0.0) or 0.0)
    additional_capacity_required = float(plant_capacity_output.get("additional_capacity_required_mt_day", plant_capacity_output.get("current_site_capacity_deficit_mt_day", 0.0)) or 0.0)
    site_expandable = str(plant_capacity_output.get("existing_plant_expandable", "No"))
    recommended_action = str(plant_capacity_output.get("recommended_action", "Continue Current Configuration"))
    new_plant_required = str(plant_capacity_output.get("new_plant_required", "No"))
    recommended_new_plant_capacity = float(plant_capacity_output.get("recommended_new_plant_capacity_mt_day", 0.0) or 0.0)
    total_future_capacity = float(plant_capacity_output.get("total_future_capacity_mt_day", 0.0) or 0.0)
    cold_storage_required = float(plant_capacity_output.get("cold_storage_required_mt", 0.0) or 0.0)
    decision_reason = str(plant_capacity_output.get("decision_reason", ""))
    supporting_actions = plant_capacity_output.get("supporting_actions", []) or []

    st.write("This view explains the current plant configuration, capacity shortfall or headroom, available expansion options, and the next governed capacity action.")

    if capacity_recommendation_mode not in {"CURRENT_SITE_OPTIMIZATION", "NEW_PLANT_EXPANSION"}:
        log_runtime_event(
            "plant_capacity_mode_missing",
            recommended_action=recommended_action,
            required_output_mt_day=f"{required_output:.4f}",
            maximum_current_site_capacity_mt_day=f"{max_site_capacity:.4f}",
        )
        st.warning("Configuration Review Required")

    st.markdown("**A. Current State**")
    requirement_rows = pd.DataFrame([
        {"Metric": "Current Installed Lines", "Value": f"{installed_lines:,.0f}"},
        {"Metric": "Current Active Shifts", "Value": f"{active_shifts:,.0f}"},
        {"Metric": "Current Configuration", "Value": current_configuration_label},
        {"Metric": "Required Output", "Value": f"{required_output:,.1f} MT/day"},
        {"Metric": "Current Installed Capacity", "Value": f"{installed_capacity:,.1f} MT/day"},
        {"Metric": "Current Installed Capacity Shortfall", "Value": f"{capacity_shortfall:,.1f} MT/day" if capacity_shortfall > 0 else "0.0 MT/day"},
        {"Metric": "Current Capacity Headroom", "Value": f"{capacity_headroom:,.1f} MT/day" if capacity_headroom > 0 else "0.0 MT/day"},
        {"Metric": "Current Load Ratio", "Value": f"{current_load_ratio:,.1f}%"},
    ])
    render_display_dataframe(st, "plant_capacity_current_requirement", requirement_rows, hide_index=True, width="stretch")

    st.markdown("**B. Current-Site Potential**")
    config_rows = pd.DataFrame([
        {"Metric": "Base Capacity per Line per Shift", "Value": f"{base_capacity:,.1f} MT/day"},
        {"Metric": "Maximum Lines in Current Plant", "Value": f"{max_lines:,.0f}"},
        {"Metric": "Maximum Shifts per Line", "Value": f"{max_shifts:,.0f}"},
        {"Metric": "Maximum-Site Configuration", "Value": maximum_site_configuration_label},
        {"Metric": "Maximum Current-Site Capacity", "Value": f"{max_site_capacity:,.1f} MT/day"},
        {"Metric": "Current-Site Capacity Deficit", "Value": f"{additional_capacity_required:,.1f} MT/day" if additional_capacity_required > 0 else "0.0 MT/day"},
        {"Metric": "Current-Site Capacity Headroom", "Value": f"{site_headroom_after_demand:,.1f} MT/day" if site_headroom_after_demand > 0 else "0.0 MT/day"},
    ])
    render_display_dataframe(st, "plant_capacity_current_configuration", config_rows, hide_index=True, width="stretch")

    st.markdown("**C. Recommendation Mode**")
    st.write("Current-Site Optimization" if capacity_recommendation_mode == "CURRENT_SITE_OPTIMIZATION" else "New-Plant Expansion" if capacity_recommendation_mode == "NEW_PLANT_EXPANSION" else "Configuration Review Required")

    st.markdown("**D. Recommended Action**")
    if capacity_recommendation_mode == "CURRENT_SITE_OPTIMIZATION":
        st.write(f"Recommended Lines: {recommended_lines:,.0f}")
        st.write(f"Recommended Shifts: {recommended_shifts:,.0f}")
        st.write(f"Recommended Configuration: {recommended_configuration_label if recommended_configuration_label else 'Configuration Review Required'}")
        st.write(f"Recommended Capacity: {recommended_capacity:,.1f} MT/day")
        st.write(f"Projected Utilization: {projected_utilization:,.1f}%")
    else:
        st.write(f"Maximum Current-Site Configuration: {maximum_site_configuration_label}")
        st.write(f"Maximum Current-Site Capacity: {max_site_capacity:,.1f} MT/day")
        st.write(f"Additional Capacity Required: {additional_capacity_required:,.1f} MT/day")
        st.write(f"Recommended New-Plant Capacity: {recommended_new_plant_capacity:,.1f} MT/day")
        st.write(f"Total Future Capacity: {total_future_capacity:,.1f} MT/day")
        st.write(f"Projected Future Utilization: {projected_future_utilization:,.1f}%")
    st.write(recommended_action)
    if supporting_actions:
        st.write("Supporting step(s): " + ", ".join([str(x) for x in supporting_actions]))
    if decision_reason:
        st.write(decision_reason)

    st.markdown("**E. New Plant Decision**")
    st.write(f"New Plant Required: {'Yes' if new_plant_required == 'Yes' else 'No'}")
    st.write(f"Reason: {decision_reason if decision_reason else _recommended_action_subtitle(plant_capacity_output)}")
    if new_plant_required == "Yes":
        st.write(f"Additional Capacity Required: {additional_capacity_required:,.1f} MT/day")
        st.write(f"Recommended New Plant Capacity: {recommended_new_plant_capacity:,.1f} MT/day")

    st.markdown("**Expansion Headroom Reference**")
    headroom_rows = pd.DataFrame([
        {"Metric": "Remaining Shift Capacity", "Value": f"{remaining_shift_capacity:,.1f} MT/day"},
        {"Metric": "Remaining Line Capacity", "Value": f"{remaining_line_capacity:,.1f} MT/day"},
        {"Metric": "Remaining Current-Site Capacity", "Value": f"{remaining_site_capacity:,.1f} MT/day"},
        {"Metric": "Maximum Site Headroom After Meeting Demand", "Value": f"{site_headroom_after_demand:,.1f} MT/day"},
        {"Metric": "Site Expandable", "Value": site_expandable},
        {"Metric": "Cold Storage Required", "Value": f"{cold_storage_required:,.1f} MT"},
    ])
    render_display_dataframe(st, "plant_capacity_expansion_headroom", headroom_rows, hide_index=True, width="stretch")

    st.markdown("**Formula Section**")
    st.write("Current Installed Capacity = Base Capacity per Line per Shift x Installed Lines x Active Shifts")
    st.write(f"Worked: {base_capacity:,.1f} x {installed_lines:,.0f} x {active_shifts:,.0f} = {installed_capacity:,.1f} MT/day")
    st.write("Current Installed Capacity Shortfall = Required Output - Current Installed Capacity")
    st.write(f"Worked: {required_output:,.1f} - {installed_capacity:,.1f} = {capacity_shortfall:,.1f} MT/day shortfall")
    st.write("Maximum Current-Site Capacity = Base Capacity per Line per Shift x Maximum Lines x Maximum Shifts per Line")
    st.write(f"Worked: {base_capacity:,.1f} x {max_lines:,.0f} x {max_shifts:,.0f} = {max_site_capacity:,.1f} MT/day")
    st.write("Current-Site Capacity Deficit = Required Output - Maximum Current-Site Capacity")
    st.write(f"Worked: {required_output:,.1f} - {max_site_capacity:,.1f} = {additional_capacity_required:,.1f} MT/day")
    if capacity_recommendation_mode == "CURRENT_SITE_OPTIMIZATION":
        st.write("Projected Utilization = Required Output / Recommended Capacity x 100")
        st.write(f"Worked: {required_output:,.1f} / {recommended_capacity:,.1f} x 100 = {projected_utilization:,.1f}%")
    else:
        st.write("Total Future Capacity = Maximum Current-Site Capacity + Recommended New-Plant Capacity")
        st.write(f"Worked: {max_site_capacity:,.1f} + {recommended_new_plant_capacity:,.1f} = {total_future_capacity:,.1f} MT/day")
        st.write("Projected Future Utilization = Required Output / Total Future Capacity x 100")
        st.write(f"Worked: {required_output:,.1f} / {total_future_capacity:,.1f} x 100 = {projected_future_utilization:,.1f}%")


def show_plant_capacity_governance_dialog():
    if hasattr(st, "dialog"):
        @st.dialog("Plant Capacity Governance")
        def _plant_dialog():
            render_plant_capacity_governance_dialog()

        _plant_dialog()
    else:
        with st.expander("Plant Capacity Governance", expanded=True):
            render_plant_capacity_governance_dialog()


KPI_ICONS = {
    "corporate_revenue": "💰",
    "corporate_birds_day": "🐔",
    "corporate_capacity": "🏭",
    "corporate_manpower": "👥",
    "total_commercial_revenue": "💼",
    "sales_manager": "🧑‍💼",
    "general_trade": "🏪",
    "modern_trade": "🏬",
    "quick_commerce": "⚡",
    "ecommerce": "🛒",
    "exports": "🌍",
    "horeca": "🍽️",
    "institutional_government": "🏛️",
    "selected_market": "📍",
    "revenue_allocation": "💰",
    "assigned_plant": "🏭",
    "market_status": "🧭",
    "frozen_raw_business": "❄️",
    "rte_business": "📦",
    "shared_distribution_network": "🔗",
    "finished_goods_day": "📦",
    "installed_capacity_day": "🏭",
    "production_lines": "⚙️",
    "shift_requirement": "🕒",
    "plant_utilization": "📈",
    "cold_storage": "❄️",
    "expansion_required": "🚧",
    "live_bird_rate": "🐔",
    "yield": "⚖️",
    "birds_day": "🐔",
    "live_weight_day": "⚖️",
    "procurement_spend": "💳",
    "traders_required": "🤝",
    "farms_required": "🌾",
    "primary_vehicles": "🚛",
    "primary_trips": "🔄",
    "primary_cost": "💸",
    "secondary_vehicles": "🚚",
    "secondary_trips": "🔁",
    "secondary_cost": "💸",
    "cold_chain_required": "❄️",
    "production_hc": "👷",
    "warehouse_hc": "📦",
    "sales_hc": "🧑‍💼",
    "marketing_hc": "📣",
    "finance_hc": "🧾",
    "hr_hc": "👥",
    "admin_hc": "🗂️",
    "qa_hc": "✅",
    "procurement_hc": "🤝",
    "total_employees": "👥",
    "revenue": "💰",
    "gross_contribution": "📊",
    "ebitda": "📈",
    "pat": "🏁",
    "planned_demand": "🎯",
    "scenario_orders": "🧾",
    "achievement": "📊",
    "capacity_gap": "⚠️",
    "capacity_status": "🚦",
    "scenario_mode": "🧭",
    "order_source": "🧾",
    "available_inventory": "📦",
    "available_plant_capacity": "🏭",
    "scenario_plant_utilization": "📈",
    "market_distance": "📍",
}

PLANT_ICON_KEYS = {
    "Required Output": "finished_goods_day",
    "Current Plant Configuration": "production_lines",
    "Recommended Plant Configuration": "production_lines",
    "Maximum Current-Site Configuration": "production_lines",
    "Current Installed Capacity": "installed_capacity_day",
    "Maximum Current-Site Capacity": "corporate_capacity",
    "Plant Utilization": "plant_utilization",
    "Recommended Capacity Action": "expansion_required",
    "New Plant Required": "expansion_required",
    "Cold Storage Required": "cold_storage",
}

MANPOWER_ICON_KEYS = {
    "Production": "production_hc",
    "Warehouse + Cold Room": "warehouse_hc",
    "Sales": "sales_hc",
    "Marketing": "marketing_hc",
    "Finance": "finance_hc",
    "HR": "hr_hc",
    "Admin": "admin_hc",
    "QA / Food Safety": "qa_hc",
    "Procurement": "procurement_hc",
    "Total Employees": "total_employees",
}

LOGISTICS_ICON_KEYS = {
    "Primary Vehicles Required": "primary_vehicles",
    "Primary Trips / Day": "primary_trips",
    "Primary Cost / Month": "primary_cost",
    "Secondary Vehicles Required": "secondary_vehicles",
    "Secondary Trips / Day": "secondary_trips",
    "Secondary Cost / Month": "secondary_cost",
    "Cold Chain Required": "cold_chain_required",
    "Average Primary Distance": "market_distance",
    "Market Distance": "market_distance",
}

DISTRIBUTION_ICON_KEYS = {
    "Fresh Chilled Business": "frozen_raw_business",
    "Frozen Raw Business": "frozen_raw_business",
    "Ready To Eat Business": "rte_business",
    "Further Value Added Business": "shared_distribution_network",
}


def render_kpi_card(title, value, subtitle=None, status=None, status_type=None, button_label=None, key=None, button_action=None, icon_key=None, value_class=None):
    icon = KPI_ICONS.get(icon_key, "📌")
    accent_map = {
        "corporate_revenue": "#3b82f6",
        "revenue": "#3b82f6",
        "gross_contribution": "#22c55e",
        "ebitda": "#8b5cf6",
        "pat": "#f59e0b",
        "production_hc": "#14b8a6",
        "total_employees": "#14b8a6",
        "plant_utilization": "#22c55e",
        "capacity_gap": "#f59e0b",
        "scenario_orders": "#3b82f6",
    }
    accent_color = accent_map.get(icon_key, "#3b82f6")
    badge_html = ""
    if status:
        badge_class = f"pbos-status-badge {status_type or 'pbos-status-neutral'}"
        badge_html = f"<div class='{badge_class}'>{status}</div>"
    subtitle_html = f"<div class='pbos-kpi-subtitle'>{subtitle}</div>" if subtitle else ""
    value_class_name = f" pbos-value-negative" if value_class == "negative" else ""
    card_html = (
        f"<div class='pbos-kpi-card'>"
        f"<div class='pbos-kpi-accent' style='background:{accent_color};'></div>"
        f"<div class='pbos-kpi-head'><div class='pbos-kpi-icon'>{icon}</div><div class='pbos-kpi-title'>{title}</div></div>"
        f"<div class='pbos-kpi-value{value_class_name}'>{value}</div>"
        f"{subtitle_html}"
        f"{badge_html}"
        f"</div>"
    )
    st.markdown(card_html, unsafe_allow_html=True)
    if button_label and key:
        if st.button(button_label, key=key):
            if button_action:
                button_action()


def plant_kpi_card(label, value, key, subtitle=None, status=None, status_type=None):
    render_kpi_card(label, value, subtitle=subtitle, status=status, status_type=status_type, icon_key=PLANT_ICON_KEYS.get(label))


def render_manpower_drilldown(kpi_name):
    role_key = {
        "Production": "production",
        "Warehouse + Cold Room": "warehouse",
        "Sales": "sales",
        "Marketing": "marketing",
        "Finance": "finance",
        "HR": "hr",
        "Admin": "admin",
        "QA / Food Safety": "qa_food_safety",
        "Procurement": "procurement",
        "Total Employees": "total_employees",
    }[kpi_name]
    headcount = manpower_output[role_key]
    finished_goods_day = manpower_output["finished_goods_mt_day"]
    lines = manpower_output["production_lines"]
    stage_name = manpower_output["business_stage"]
    model_name = manpower_output["operating_model"]
    role_splits = manpower_output.get("role_splits", {})

    st.markdown("**What This Team Does**")
    if kpi_name == "Production":
        st.write("Runs processing, packing, cleaning, sanitation, and shift control for daily finished goods output.")
    elif kpi_name == "Warehouse + Cold Room":
        st.write("Handles inbound finished goods, cold room inventory discipline, FEFO rotation, and dispatch loading.")
    elif kpi_name == "Sales":
        st.write("Builds channel coverage through GT reps, account managers, HoReCa coverage, institutional/export support, and sales coordination.")
    elif kpi_name == "Marketing":
        st.write("Owns brand activation, POSM, digital campaigns, trade promotions, and product launch support.")
    elif kpi_name == "Finance":
        st.write("Controls collections, vendor payments, GST, MIS, banking, and financial discipline.")
    elif kpi_name == "HR":
        st.write("Covers plant hiring, attendance, payroll, compliance, recruitment, and contractor coordination.")
    elif kpi_name == "Admin":
        st.write("Coordinates security, housekeeping, utilities, vendor support, AMC follow-up, and office support.")
    elif kpi_name == "QA / Food Safety":
        st.write("Protects hygiene, HACCP discipline, process checks, complaint handling, and audit readiness.")
    elif kpi_name == "Procurement":
        st.write("Coordinates live bird traders, daily lifting plans, price negotiation, and supplier follow-up.")
    else:
        st.write("Shows the total operating team required to support production, cold chain handling, commercial execution, controls, QA, and procurement.")

    st.markdown("**Why This Headcount Is Needed**")
    st.write(f"{headcount:,.0f} employees are planned for {kpi_name} to support {finished_goods_day:,.1f} MT/day, {lines:,.0f} production line(s), the {model_name} operating model, and the {stage_name} stage.")

    st.markdown("**Role Split**")
    split_rows = role_splits.get(role_key, [])
    if split_rows:
        render_display_dataframe(st, f"manpower_role_split_{role_key}", pd.DataFrame(split_rows), hide_index=True, width="stretch")
    else:
        render_display_dataframe(st, f"manpower_role_split_{role_key}", pd.DataFrame([
            {"role": "Total operating team", "responsibility": "Combined headcount across all functions.", "headcount": headcount}
        ]), hide_index=True, width="stretch")

    st.markdown("**What Happens If Reduced**")
    if kpi_name == "Production":
        st.write("Lower production staffing reduces throughput, increases overtime risk, and weakens cleaning and sanitation discipline.")
    elif kpi_name == "Warehouse + Cold Room":
        st.write("Lower warehouse staffing creates loading delays, cold room mismatch risk, FEFO/inventory errors, and dispatch SLA risk.")
    elif kpi_name == "Sales":
        st.write("Lower sales staffing reduces market coverage, slows GT expansion, lowers outlet visits, and puts revenue at risk.")
    elif kpi_name == "Marketing":
        st.write("Lower marketing staffing weakens launch support, trade promotion execution, and in-market brand visibility.")
    elif kpi_name == "Finance":
        st.write("Lower finance staffing slows collections, vendor payments, compliance, MIS, and banking follow-up.")
    elif kpi_name == "HR":
        st.write("Lower HR staffing weakens hiring speed, attendance control, payroll coordination, and compliance tracking.")
    elif kpi_name == "Admin":
        st.write("Lower admin staffing increases site upkeep, vendor, utilities, and office support risk.")
    elif kpi_name == "QA / Food Safety":
        st.write("Lower QA staffing increases hygiene, food safety, audit, and customer complaint risk.")
    elif kpi_name == "Procurement":
        st.write("Lower procurement staffing weakens trader coordination, daily lifting planning, price tracking, and supplier follow-up.")
    else:
        st.write("Reducing total headcount without changing the operating plan creates execution risk across service, quality, and revenue coverage.")

    st.markdown("**CEO Recommendation**")
    if kpi_name == "Total Employees":
        st.write("Treat total employees as an execution capacity decision. Reduce only after lowering revenue ambition, simplifying channels, or improving productivity.")
    else:
        st.write(f"Keep {kpi_name} at the planned level unless the revenue target, channel coverage, or plant operating plan is reduced.")

    st.markdown("**Planning Assumptions**")
    st.write(f"Finished goods/day: {finished_goods_day:,.1f} MT. Production lines: {lines:,.0f}. Operating model: {model_name}. Business stage: {stage_name}.")


def show_manpower_drilldown(kpi_name):
    if hasattr(st, "dialog"):
        @st.dialog(kpi_name)
        def _manpower_dialog():
            render_manpower_drilldown(kpi_name)

        _manpower_dialog()
    else:
        with st.expander(kpi_name, expanded=True):
            render_manpower_drilldown(kpi_name)


def manpower_kpi_card(label, value, key, subtitle=None, status=None, status_type=None):
    render_kpi_card(label, f"{value:,.0f}", subtitle=subtitle, status=status, status_type=status_type, button_label="View details", key=key, button_action=lambda: show_manpower_drilldown(label), icon_key=MANPOWER_ICON_KEYS.get(label))


def render_logistics_drilldown(kpi_name):
    primary = logistics_output["primary"]
    secondary = logistics_output["secondary"]
    if kpi_name.startswith("Primary"):
        st.write("What:")
        st.write("Vehicles carrying live birds from sourcing points, traders, or farms to the production plant.")
        st.write("Why:")
        st.write("Required to ensure uninterrupted daily bird lifting for plant production.")
        st.write("How calculated:")
        st.write("Daily live bird weight is matched against vehicle capacity and planned trips per vehicle.")
        render_display_dataframe(st, "logistics_primary_detail", pd.DataFrame([
            {"Item": "Plant", "Value": selected_plant_name},
            {"Item": "Birds/day", "Value": f"{primary['birds_per_day']:,.0f}"},
            {"Item": "Average bird weight", "Value": f"{primary['average_bird_weight']:,.2f} kg"},
            {"Item": "Live weight/day", "Value": f"{primary['live_weight_kg_day']:,.0f} kg"},
            {"Item": "Vehicle capacity", "Value": f"{primary['vehicle_capacity_kg']:,.0f} kg"},
            {"Item": "Trips/day", "Value": f"{primary['trips_day']:,.0f}"},
            {"Item": "Vehicles required", "Value": f"{primary['vehicles_required']:,.0f}"},
            {"Item": "Monthly cost", "Value": fmt_currency(primary["cost_month"])},
        ]), hide_index=True, width="stretch")
        st.write("Business interpretation:")
        st.write(f"The {selected_plant_name} requires {primary['vehicles_required']:,.0f} primary vehicle(s) to lift the planned live-bird volume without interrupting production.")
        render_formula_section("primary_trips_day", build_formula_rows(
            "primary_trips_day",
            current_value=f"{primary['trips_day']:,.0f} trips/day",
            unit="trips/day",
            status="Reconciled",
            worked_calculation=f"{primary['live_weight_kg_day']:,.0f} kg/day ÷ {primary['vehicle_capacity_kg']:,.0f} kg = {primary['trips_day']:,.0f} trips/day",
            related_kpis="Primary Vehicles Required, Live Bird Procurement Spend, Traders Required, Farms Required",
        ))
        render_formula_section("primary_vehicles_required", build_formula_rows(
            "primary_vehicles_required",
            current_value=f"{primary['vehicles_required']:,.0f} vehicles",
            unit="vehicles",
            status="Reconciled",
            worked_calculation=f"ceil({primary['trips_day']:,.0f} trips/day ÷ {primary_trips_per_vehicle_per_day:,.0f} trips/vehicle/day) = {primary['vehicles_required']:,.0f} vehicles",
            related_kpis="Primary Trips/day, Live Bird Procurement Spend, Traders Required, Farms Required",
            extra_rows=[
                {"Item": "Primary Cost / Month", "Value": fmt_currency(primary["cost_month"])},
                {"Item": "Primary Cost Formula", "Value": f"{primary['trips_day']:,.0f} trips/day × ({primary['average_distance_km']:,.0f} km × ₹{primary_cost_per_km:,.0f} + ₹{primary_fixed_cost_per_trip:,.0f}) × {working_days:,.0f} working days"},
            ],
        ))
        return

    if kpi_name.startswith("Secondary") or kpi_name == "Cold Chain Required":
        st.write("What:")
        st.write("Vehicles carrying finished goods from the plant to the selected market, distributor, DC, or customer.")
        st.write("Why:")
        st.write("Required to maintain daily delivery and cold-chain continuity.")
        render_display_dataframe(st, "logistics_secondary_detail", pd.DataFrame([
            {"Item": "Selected market", "Value": selected_market_name},
            {"Item": "Finished goods/day", "Value": f"{secondary['finished_goods_mt_day']:,.1f} MT"},
            {"Item": "Market distance", "Value": f"{secondary['market_distance_km']:,.0f} km"},
            {"Item": "Vehicle capacity", "Value": f"{secondary['vehicle_capacity_mt']:,.1f} MT"},
            {"Item": "Trips/day", "Value": f"{secondary['trips_day']:,.0f}"},
            {"Item": "Vehicles required", "Value": f"{secondary['vehicles_required']:,.0f}"},
            {"Item": "Cold-chain requirement", "Value": secondary["cold_chain_required"]},
            {"Item": "Monthly cost", "Value": fmt_currency(secondary["cost_month"])},
        ]), hide_index=True, width="stretch")
        st.write("Business interpretation:")
        st.write(f"{selected_market_name} requires {secondary['vehicles_required']:,.0f} secondary vehicle(s) to support daily finished-goods delivery from {selected_plant_name}.")
        return

    st.write("Total Logistics Cost / Month")
    st.write("This combines plant-level primary logistics and selected-market secondary logistics without mixing vehicle requirements.")
    st.write(f"Primary cost: {fmt_currency(primary['cost_month'])}")
    st.write(f"Secondary cost: {fmt_currency(secondary['cost_month'])}")
    st.write(f"Total logistics cost: {fmt_currency(logistics_output['total_logistics_cost_month'])}")


def show_logistics_drilldown(kpi_name):
    if hasattr(st, "dialog"):
        @st.dialog(kpi_name)
        def _logistics_dialog():
            render_logistics_drilldown(kpi_name)

        _logistics_dialog()
    else:
        with st.expander(kpi_name, expanded=True):
            render_logistics_drilldown(kpi_name)


def logistics_kpi_card(label, value, key, subtitle=None, status=None, status_type=None):
    render_kpi_card(label, value, subtitle=subtitle, status=status, status_type=status_type, button_label="View details", key=key, button_action=lambda: show_logistics_drilldown(label), icon_key=LOGISTICS_ICON_KEYS.get(label))


def render_order_capacity_drilldown():
    if not order_capacity_intelligence.get("scenario_active"):
        st.write("No order scenario has been activated. Select an order scenario to test channel demand, releasable inventory and plant capacity.")
    else:
        st.write("Scenario orders are user-entered planning assumptions and are not confirmed ERP purchase orders.")

    st.write(order_capacity_intelligence["business_impact"])
    st.write(order_capacity_intelligence.get("scenario_variance_explanation", order_capacity_intelligence.get("demand_variance_explanation", "Scenario demand is aligned with the channel-mix planning baseline.")))
    st.write(order_capacity_intelligence.get("observation_status", "Scenario persistence is simulated and not yet connected to historical daily order history."))
    st.write("Consolidated demand summary")
    render_display_dataframe(st, "order_capacity_summary", pd.DataFrame([
        {"Metric": "Planned Demand", "Value": f"{order_capacity_intelligence.get('planned_demand_mt_day', 0.0):,.2f} MT/day"},
        {"Metric": "Scenario Demand", "Value": f"{order_capacity_intelligence.get('scenario_order_demand_mt_day', 0.0):,.2f} MT/day"},
        {"Metric": "Net Variance", "Value": f"{order_capacity_intelligence.get('demand_variance_mt_day', 0.0):+,.2f} MT/day"},
        {"Metric": "Overall Achievement", "Value": f"{order_capacity_intelligence.get('overall_achievement_pct', 0.0):,.1f}%"},
    ]), hide_index=True, width="stretch")
    st.write("Channel-wise planned vs scenario orders")
    channel_rows = []
    for channel, data in order_capacity_intelligence.get("channel_results", order_capacity_intelligence["channel_planned_vs_actual"]).items():
        channel_rows.append({
            "Channel": channel,
            "Planned MT/day": f"{data.get('planned_demand_mt_day', data.get('planned_volume_mt_day', data['planned_volume_kg'] / 1000.0)):,.2f}",
            "Scenario MT/day": f"{data.get('scenario_demand_mt_day', data.get('scenario_order_mt_day', data.get('actual_order_kg', data.get('actual_order_volume_kg', 0.0)) / 1000.0)):,.2f}",
            "Variance MT/day": f"{data.get('variance_mt_day', (data.get('actual_order_kg', data.get('actual_order_volume_kg', 0.0)) - data.get('planned_volume_kg', 0.0)) / 1000.0):+,.2f}",
            "Achievement %": f"{data['achievement_pct']:,.1f}%",
            "Status": data.get("status", ""),
            "Commercial Comment": data.get("commercial_comment", ""),
        })
    render_display_dataframe(st, "order_capacity_channel_contribution", pd.DataFrame(channel_rows), hide_index=True, width="stretch")

    st.write("Recommendation area")
    recommendation_rows = []
    for label, key in [
        ("Capacity Recommendation", "capacity_recommendations"),
        ("Marketing / Sales Recommendation", "marketing_recommendations"),
        ("Procurement Recommendation", "procurement_recommendations"),
        ("Logistics Recommendation", "logistics_recommendations"),
        ("Manpower Recommendation", "manpower_recommendations"),
    ]:
        recommendation_rows.append({
            "Area": label,
            "Recommendation": " ".join(order_capacity_intelligence.get(key, [])),
        })
    render_display_dataframe(st, "order_capacity_recommendations", pd.DataFrame(recommendation_rows), hide_index=True, width="stretch")

    st.write("Inventory impact")
    inventory = order_capacity_intelligence["inventory_impact"]
    render_display_dataframe(st, "order_capacity_inventory_impact", pd.DataFrame([
        {"Item": "Inventory build risk", "Value": f"{inventory['inventory_build_risk_kg']:,.0f} kg"},
        {"Item": "Days of inventory", "Value": f"{inventory['days_of_inventory']:,.1f}"},
        {"Item": "Fresh expiry risk", "Value": inventory["fresh_expiry_risk"]},
        {"Item": "Frozen storage impact", "Value": f"{inventory['frozen_storage_impact']:,.1f} MT"},
        {"Item": "Stockout risk", "Value": inventory["stockout_risk"]},
    ]), hide_index=True, width="stretch")

    st.write("Line utilization and recommendation hierarchy")
    st.write(f"Line utilization: {order_capacity_intelligence['scenario_line_utilization_pct']:,.1f}%")
    for action in order_capacity_intelligence["recommended_actions"]:
        st.write(f"- {action}")


def show_order_capacity_drilldown():
    if hasattr(st, "dialog"):
        @st.dialog("Order & Capacity Intelligence")
        def _order_capacity_dialog():
            render_order_capacity_drilldown()

        _order_capacity_dialog()
    else:
        with st.expander("Order & Capacity Intelligence", expanded=True):
            render_order_capacity_drilldown()


def render_distributor_channel_drilldown(kpi_name):
    distribution_map = {
        "Fresh Chilled Business": ("Fresh Chilled", "FRESH", "fresh_chilled_revenue", "fresh_distributors", "fresh_revenue_capacity_per_distributor", "fresh_network_capacity", "fresh_utilization_pct", "fresh_capacity_status"),
        "Frozen Raw Business": ("Frozen Raw", "FROZEN", "frozen_raw_revenue", "frozen_raw_distributors", "frozen_revenue_capacity_per_distributor", "frozen_network_capacity", "frozen_utilization_pct", "frozen_capacity_status"),
        "Ready To Eat Business": ("Ready To Eat", "RTE", "rte_revenue", "rte_distributors", "rte_revenue_capacity_per_distributor", "rte_network_capacity", "rte_utilization_pct", "rte_capacity_status"),
        "Further Value Added Business": ("Further Value Added", "FVA", "fva_revenue", "fva_distributors", "fva_revenue_capacity_per_distributor", "fva_network_capacity", "fva_utilization_pct", "fva_capacity_status"),
    }
    if kpi_name in distribution_map:
        if len(distribution_map[kpi_name]) == 8:
            name, product_key, revenue_key, count_key, partner_capacity_key, network_capacity_key, utilization_key, status_key = distribution_map[kpi_name]
            product_mix_pct = float(product_mix.get(product_key, 0.0) or 0.0)
        else:
            name, revenue_key, count_key, partner_capacity_key, network_capacity_key, utilization_key, status_key = distribution_map[kpi_name]
            product_mix_pct = 0.0
        st.write("What this network owns")
        if kpi_name == "Fresh Chilled Business":
            st.write("Fresh Chilled business is governed by GT retail coverage, account coverage, cold-chiller capacity and same-day distribution readiness.")
        else:
            st.write(f"{name} distribution partners carry the planned business revenue with enough capacity for service frequency, cold-chain discipline, and account follow-up.")
        partner_label = "GT Retail Coverage" if kpi_name == "Fresh Chilled Business" else "Distribution partners"
        render_display_dataframe(st, f"distribution_{name.lower().replace(' ', '_')}", pd.DataFrame([
            {"Item": "Product Business", "Value": name},
            {"Item": "Product Mix %", "Value": f"{product_mix_pct:,.1f}%"},
            {"Item": "Corporate Revenue Target", "Value": fmt_currency(corporate_revenue_rupees)},
            {"Item": "Allocated Revenue", "Value": fmt_currency(distributor_output[revenue_key])},
            {"Item": "Revenue responsibility", "Value": fmt_currency(distributor_output[revenue_key])},
            {"Item": partner_label, "Value": "Not Connected" if kpi_name == "Fresh Chilled Business" else f"{distributor_output[count_key]:,.0f}"},
            {"Item": "Monthly capacity per partner", "Value": fmt_currency(distributor_output[partner_capacity_key])},
            {"Item": "Monthly network capacity", "Value": fmt_currency(distributor_output[network_capacity_key])},
            {"Item": "Capacity utilization", "Value": f"{distributor_output[utilization_key]:,.1f}%"},
            {"Item": "Capacity signal", "Value": distributor_output[status_key]},
            {"Item": "HORECA Accounts", "Value": "Not Connected" if kpi_name == "Fresh Chilled Business" else "Not Connected"},
            {"Item": "Institutional Accounts", "Value": "Not Connected" if kpi_name == "Fresh Chilled Business" else "Not Connected"},
            {"Item": "Active Market Coverage", "Value": "Not Connected" if kpi_name == "Fresh Chilled Business" else "Not Connected"},
            {"Item": "Actual Partner Count status", "Value": "Not Connected"},
        ]), hide_index=True, width="stretch")
        st.write("What happens if partners are reduced")
        st.write("The same revenue has to move through fewer partners, which increases service-frequency pressure, cold-chain execution risk, and account follow-up delays.")
        st.write("CEO recommendation")
        if distributor_output[status_key] == "Additional Partner Required":
            st.write("Add a distribution partner before committing the revenue plan.")
        elif distributor_output[status_key] == "Near Capacity":
            st.write("Monitor this network closely; it is close to the practical operating limit.")
        else:
            st.write("Current partner capacity can support the planned business.")
        return

    if kpi_name == "GT Sales Executives":
        gt = channel_sales_output["general_trade"]
        active_distributors = gt.get("active_distributors")
        st.write("What this team owns")
        st.write("General Trade sales executives required to manage distributor-led outlet coverage and beat execution.")
        render_display_dataframe(st, "gt_sales_executives_detail", pd.DataFrame([
            {"Item": "GT revenue", "Value": fmt_currency(gt["revenue"])},
            {"Item": "GT planned revenue", "Value": fmt_currency(gt["revenue"])} ,
            {"Item": "Pricing basis", "Value": gt.get("gt_pricing_basis", "Distributor selling value")},
            {"Item": "Distributor margin %", "Value": f"{gt.get('gt_distributor_margin_pct', 0.0):,.1f}%"},
            {"Item": "Distributor margin value", "Value": fmt_currency(gt.get("gt_distributor_margin_value", 0.0))},
            {"Item": "Company net realization", "Value": fmt_currency(gt.get("gt_company_net_realization", gt["revenue"]))},
            {"Item": "Company net realization / kg", "Value": f"{fmt_currency_plain(gt.get('gt_company_net_realization_per_kg', 0.0), 2)}/kg"},
            {"Item": "GT volume", "Value": f"{gt.get('gt_volume_kg', 0.0):,.0f} kg/month"},
            {"Item": "GT variable cost", "Value": fmt_currency(gt.get("gt_variable_cost", 0.0))},
            {"Item": "GT gross contribution", "Value": fmt_currency(gt.get("gt_gross_contribution", 0.0))},
            {"Item": "Required distributors", "Value": f"{gt['required_distributors']:,.0f}"},
            {"Item": "Actual active distributors", "Value": "Not Connected" if active_distributors is None else f"{active_distributors:,.0f}"},
            {"Item": "Distributor gap", "Value": "Not Available" if gt["coverage_gap_distributors"] is None else f"{gt['coverage_gap_distributors']:,.0f}"},
            {"Item": "Target outlets", "Value": f"{gt['target_outlets']:,.0f}"},
            {"Item": "Outlets per distributor", "Value": f"{gt['outlets_per_distributor']:,.0f}"},
            {"Item": "Coverage status", "Value": gt["coverage_status"]},
            {"Item": "Revenue handled per salesperson", "Value": fmt_currency(gt["revenue_per_sales_executive"])},
            {"Item": "Outlets handled per salesperson", "Value": f"{gt['outlets_per_sales_executive']:,.0f}"},
            {"Item": "Sales executives required", "Value": f"{gt['sales_executives']:,.0f}"},
            {"Item": "Beats", "Value": f"{gt['beats']:,.0f}"},
            {"Item": "Daily calls required", "Value": f"{gt['calls_day']:,.0f}"},
            {"Item": "Supported revenue", "Value": fmt_currency(gt["supported_revenue"])},
            {"Item": "Revenue at risk", "Value": fmt_currency(gt["revenue_at_risk"])},
        ]), hide_index=True, width="stretch")
        st.write("Pricing convention: GT planned revenue is treated as distributor selling value, so company realization is shown net of GT distributor margin for economics and contribution tracking.")
        if active_distributors is None:
            st.write("Actual distributor count is not connected. PBOS is showing the planning requirement.")
        st.write("CEO recommendation:")
        st.write("Keep GT field coverage aligned with distributor load, outlet expansion, and daily call discipline.")
        return

    if kpi_name == "MT KAM":
        data = channel_sales_output["modern_trade"]
        st.write("What this role owns")
        st.write("Modern Trade KAM owns chain negotiation, annual trading terms, listing, promotions, claims, fill rate, store execution, and category reviews.")
        render_display_dataframe(st, "mt_kam_detail", pd.DataFrame([
            {"Item": "MT revenue", "Value": fmt_currency(data["revenue"])},
            {"Item": "Accounts", "Value": f"{data['accounts']:,.0f}"},
            {"Item": "KAM required", "Value": f"{data['kam']:,.0f}"},
        ]), hide_index=True, width="stretch")
        st.write("What happens if headcount is reduced")
        st.write("Chain negotiation slows, listing execution weakens, claims and promotion closure get delayed, and revenue visibility reduces.")
        st.write("CEO recommendation:")
        st.write("Keep separate MT ownership when MT revenue exists; it protects trading terms and store execution.")
        return

    if kpi_name == "QCom KAM":
        data = channel_sales_output["quick_commerce"]
        st.write("What this role owns")
        st.write("Quick Commerce KAM owns platform relationships, buying accounts, regional buying teams, assortment, replenishment, platform promotions, visibility, SLA adherence, and near-real-time demand planning.")
        render_display_dataframe(st, "qcom_kam_detail", pd.DataFrame([
            {"Item": "Active Platforms", "Value": f"{data['active_platforms']:,.0f}"},
            {"Item": "Buying Accounts", "Value": f"{data['buying_accounts']:,.0f}"},
            {"Item": "Buying Regions", "Value": f"{data['buying_regions']:,.0f}"},
            {"Item": "Dark Stores Served", "Value": f"{data['dark_stores_served']:,.0f}"},
            {"Item": "Monthly Volume kg", "Value": f"{data['monthly_volume_kg']:,.0f}"},
            {"Item": "Revenue", "Value": fmt_currency(data["revenue"])},
            {"Item": "Required KAM", "Value": f"{data['required_kam']:,.0f}"},
            {"Item": "Average Revenue per Platform", "Value": fmt_currency(data["average_revenue_per_platform"])},
            {"Item": "Average Volume per Platform", "Value": f"{data['average_volume_per_platform']:,.0f} kg"},
        ]), hide_index=True, width="stretch")
        st.write("What happens if headcount is reduced")
        st.write("Platform relationship ownership, buying-region follow-up, replenishment speed, stock-out control, and promotion execution weaken.")
        st.write("CEO recommendation:")
        st.write("Keep QCom separate from MT when QCom revenue exists; the operating rhythm is different and faster.")
        return

    if kpi_name == "HoReCa Revenue":
        data = channel_sales_output["horeca"]
        st.write("HoReCa Commercial Planning")
        st.write("HoReCa covers hotels, restaurants, caterers, and cloud kitchens.")
        st.write("Planned revenue is allocated from the selected market target using the HoReCa channel mix. The system-recommended contract rate determines the monthly volume required to achieve that target.")
        render_display_dataframe(st, "horeca_revenue_detail", pd.DataFrame([
            {"Item": "Live Bird Rate", "Value": f"{fmt_currency_plain(data['live_bird_rate'], 2)}/kg"},
            {"Item": "Average Live Bird Weight", "Value": f"{data['average_live_bird_weight_kg']:,.2f} kg"},
            {"Item": "Dressed Output", "Value": f"{data['dressed_output_kg']:,.2f} kg"},
            {"Item": "Dressed Yield", "Value": f"{data['dressed_yield_pct'] * 100:,.1f}%"},
            {"Item": "Raw Material Cost/kg", "Value": f"{fmt_currency_plain(data['raw_material_cost_per_kg'], 2)}/kg"},
            {"Item": "Processing Cost/kg", "Value": f"{fmt_currency_plain(data['processing_cost_per_kg'], 2)}/kg"},
            {"Item": "Packaging Cost/kg", "Value": f"{fmt_currency_plain(data['packaging_cost_per_kg'], 2)}/kg"},
            {"Item": "Cold Chain and Logistics/kg", "Value": f"{fmt_currency_plain(data['cold_chain_logistics_cost_per_kg'], 2)}/kg"},
            {"Item": "Factory Overhead/kg", "Value": f"{fmt_currency_plain(data['factory_overhead_per_kg'], 2)}/kg"},
            {"Item": "Total Cost/kg", "Value": f"{fmt_currency_plain(data['total_cost_per_kg'], 2)}/kg"},
            {"Item": "Target Gross Margin", "Value": f"{data['target_margin_pct']:,.1f}%"},
            {"Item": "Recommended Selling Price/kg", "Value": f"{fmt_currency_plain(data['recommended_selling_price_per_kg'], 0)}/kg"},
            {"Item": "Final Contract Rate/kg", "Value": f"{fmt_currency_plain(data['contract_rate_per_kg'], 0)}/kg"},
            {"Item": "Price Difference", "Value": fmt_currency_plain(data['contract_rate_per_kg'] - data['recommended_selling_price_per_kg'], 0)},
            {"Item": "Actual Margin %", "Value": f"{data['actual_margin_pct']:,.1f}%"},
            {"Item": "Pricing Status", "Value": data["pricing_status"]},
            {"Item": "Required Volume kg/month", "Value": f"{data['required_volume_kg_month']:,.0f}"},
            {"Item": "Planned Revenue", "Value": fmt_currency(data["planned_revenue"])},
            {"Item": "Mix Allocation", "Value": fmt_currency(channel_sales_output.get("horeca_mix_allocation", data.get("mix_allocation_revenue", 0.0)))},
            {"Item": "Planning Revenue", "Value": fmt_currency(data["planned_revenue"])},
            {"Item": "Difference", "Value": fmt_currency(data["revenue"] - channel_sales_output.get("horeca_mix_allocation", data.get("mix_allocation_revenue", 0.0)))},
            {"Item": "Active Accounts", "Value": f"{data['accounts']:,.0f}"},
            {"Item": "Required HoReCa HC", "Value": f"{data['sales_executives']:,.0f}"},
            {"Item": "Credit Days", "Value": f"{data['credit_days']:,.0f}"},
        ]), hide_index=True, width="stretch")
        st.write("Contract-rate override will be enabled later through governed commercial approval.")
        if data["revenue_mode"] != "PLANNING" and abs(data["reconciliation_variance"]) > 0:
            st.warning(f"Contract revenue differs from channel mix allocation by {fmt_currency(data['reconciliation_variance'])}.")
        st.write("Required HoReCa HC reflects the number of people needed to manage active hotel, restaurant, caterer, and cloud-kitchen contracts, collections, service levels, and account development.")
        if data["sales_executives"] == 1:
            st.write("One HoReCa executive is sufficient at the current contract volume and account load.")
        st.write("CEO recommendation:")
        st.write("Use contract mode when volume is backed by negotiated accounts; use mix allocation only for scenario planning.")
        return

    if kpi_name == "Institutional / Government Revenue":
        data = channel_sales_output["institutional_government"]
        st.write("Institutional / Government Commercial Planning")
        st.write("Institutional / Government covers hospitals, railways, military, defence canteens, government departments, tenders, and rate contracts.")
        st.write("Planned revenue is allocated from the selected market target using the Institutional/Government mix. The recommended contract rate determines the awarded volume and number of 2 kg packs required.")
        render_display_dataframe(st, "institutional_government_revenue_detail", pd.DataFrame([
            {"Item": "Product", "Value": data["product"]},
            {"Item": "Pack Size", "Value": f"{data['pack_size_kg']:,.0f} kg"},
            {"Item": "Pack Type", "Value": data["pack_type"]},
            {"Item": "MRP", "Value": data["mrp"]},
            {"Item": "Live Bird Rate", "Value": f"{fmt_currency_plain(data['live_bird_rate'], 2)}/kg"},
            {"Item": "Dressed Yield", "Value": f"{data['dressed_yield_pct'] * 100:,.1f}%"},
            {"Item": "Raw Material Cost/kg", "Value": f"{fmt_currency_plain(data['raw_material_cost_per_kg'], 2)}/kg"},
            {"Item": "Processing Cost/kg", "Value": f"{fmt_currency_plain(data['processing_cost_per_kg'], 2)}/kg"},
            {"Item": "Packaging Cost/kg", "Value": f"{fmt_currency_plain(data['packaging_cost_per_kg'], 2)}/kg"},
            {"Item": "Cold Chain and Logistics/kg", "Value": f"{fmt_currency_plain(data['cold_chain_logistics_cost_per_kg'], 2)}/kg"},
            {"Item": "Factory Overhead/kg", "Value": f"{fmt_currency_plain(data['factory_overhead_per_kg'], 2)}/kg"},
            {"Item": "Total Cost/kg", "Value": f"{fmt_currency_plain(data['total_cost_per_kg'], 2)}/kg"},
            {"Item": "Target Gross Margin", "Value": f"{data['target_margin_pct']:,.1f}%"},
            {"Item": "Recommended Selling Price/kg", "Value": f"{fmt_currency_plain(data['recommended_selling_price_per_kg'], 0)}/kg"},
            {"Item": "Final Contract Rate/kg", "Value": f"{fmt_currency_plain(data['contract_rate_per_kg'], 0)}/kg"},
            {"Item": "Contract Value per 2 kg Pack", "Value": fmt_currency_plain(data['contract_value_per_pack'], 0)},
            {"Item": "Actual Margin %", "Value": f"{data['actual_margin_pct']:,.1f}%"},
            {"Item": "Pricing Status", "Value": data["pricing_status"]},
            {"Item": "Required Volume kg/month", "Value": f"{data['required_volume_kg_month']:,.0f}"},
            {"Item": "Required 2 kg Packs/month", "Value": f"{data['required_packs_month']:,.0f}"},
            {"Item": "Planned Revenue", "Value": fmt_currency(data["planned_revenue"])},
            {"Item": "Mix Allocation", "Value": fmt_currency(channel_sales_output.get("institutional_mix_allocation", data.get("mix_allocation_revenue", 0.0)))},
            {"Item": "Planning Revenue", "Value": fmt_currency(data["planned_revenue"])},
            {"Item": "Difference", "Value": fmt_currency(data["revenue"] - channel_sales_output.get("institutional_mix_allocation", data.get("mix_allocation_revenue", 0.0)))},
            {"Item": "Active Tenders / Contracts", "Value": f"{data['active_tenders_contracts']:,.0f}"},
            {"Item": "Required Institutional / Government HC", "Value": f"{data['required_hc']:,.0f}"},
            {"Item": "Tender / Contract Name", "Value": data["contract_name"]},
            {"Item": "Contract Start Date", "Value": data["contract_start_date"]},
            {"Item": "Contract End Date", "Value": data["contract_end_date"]},
        ]), hide_index=True, width="stretch")
        if data["revenue_mode"] != "PLANNING" and abs(data["reconciliation_variance"]) > 0:
            st.warning(f"Contract revenue differs from channel mix allocation by {fmt_currency(data['reconciliation_variance'])}.")
        st.write("Required HC reflects tender tracking, bid submission, rate-contract management, compliance documents, order coordination, payment follow-up, and account servicing.")
        if data["required_hc"] == 1:
            st.write("One manager is sufficient for the current tender and contract workload.")
        st.write("CEO recommendation:")
        st.write("Keep this as a tender-backed model; Curry Cut 2 kg institutional packs remain locked for governance.")
        return

    if kpi_name == "HoReCa Sales HC":
        data = channel_sales_output["horeca"]
        st.write("What this team owns")
        st.write("HoReCa sales owns hotels, restaurants, caterers, cloud kitchens, sampling, pricing closure, repeat orders, and payment follow-up.")
        render_display_dataframe(st, "horeca_sales_hc_detail", pd.DataFrame([
            {"Item": "HoReCa Planned Revenue", "Value": fmt_currency(data["planned_revenue"])},
            {"Item": "Active accounts", "Value": f"{data['accounts']:,.0f}"},
            {"Item": "Required HoReCa HC", "Value": f"{data['sales_executives']:,.0f}"},
            {"Item": "Revenue handled per HoReCa executive", "Value": fmt_currency(data["revenue_per_sales_executive"])},
            {"Item": "Contract Rate ₹/kg", "Value": f"{fmt_currency_plain(data['contract_rate_per_kg'], 2)}/kg"},
            {"Item": "Required Volume kg/month", "Value": f"{data['required_volume_kg_month']:,.0f}"},
            {"Item": "Credit Days", "Value": f"{data['credit_days']:,.0f}"},
        ]), hide_index=True, width="stretch")
        st.write("Required HoReCa HC reflects the number of people needed to manage active hotel, restaurant, caterer, and cloud-kitchen contracts, collections, service levels, and account development.")
        if data["sales_executives"] == 1:
            st.write("One HoReCa executive is sufficient at the current contract volume and account load.")
        st.write("CEO recommendation:")
        st.write("Keep direct ownership where HoReCa revenue exists because acquisition and repeat order building need focused follow-up.")
        return

    if kpi_name == "Institutional / Government Manager":
        data = channel_sales_output["institutional_government"]
        st.write("What this role owns")
        st.write("Institutional / Government ownership covers hospitals, railways, military, defence canteens, tenders, rate contracts, documentation, and payment follow-up.")
        render_display_dataframe(st, "institutional_government_manager_detail", pd.DataFrame([
            {"Item": "Institutional / Government Planned Revenue", "Value": fmt_currency(data["planned_revenue"])},
            {"Item": "Active Tenders / Contracts", "Value": f"{data['active_tenders_contracts']:,.0f}"},
            {"Item": "Required Institutional / Government HC", "Value": f"{data['required_hc']:,.0f}"},
            {"Item": "Product", "Value": data["product"]},
            {"Item": "Pack Size", "Value": f"{data['pack_size_kg']:,.0f} kg"},
            {"Item": "Contract Rate ₹/kg", "Value": f"{fmt_currency_plain(data['contract_rate_per_kg'], 2)}/kg"},
            {"Item": "Required Volume kg/month", "Value": f"{data['required_volume_kg_month']:,.0f}"},
            {"Item": "Required 2 kg Packs/month", "Value": f"{data['required_packs_month']:,.0f}"},
            {"Item": "Tender / Contract Name", "Value": data["contract_name"]},
            {"Item": "Contract Start Date", "Value": data["contract_start_date"]},
            {"Item": "Contract End Date", "Value": data["contract_end_date"]},
        ]), hide_index=True, width="stretch")
        st.write("Required HC reflects tender tracking, bid submission, rate-contract management, compliance documents, order coordination, payment follow-up, and account servicing.")
        if data["account_managers"] == 1:
            st.write("One manager is sufficient for the current tender and contract workload.")
        st.write("CEO recommendation:")
        st.write("Keep dedicated ownership where institutional revenue exists because tenders and rate contracts need disciplined follow-through.")
        return

    if kpi_name == "Sales Manager":
        st.write("Sales organisation hierarchy")
        st.write("Sales Manager / Head of Sales sits above all commercial verticals and is not treated as a peer salesperson.")
        st.write(f"Revenue Accountability: {fmt_currency(channel_sales_output.get('selected_market_revenue', selected_market_revenue))}")
        st.write(f"Headcount: {channel_sales_output['sales_manager']:,.0f}")
        st.write(f"Total commercial manpower: {channel_sales_output['total_commercial_hc']:,.0f}")
        st.write(f"Markets supported: {channel_sales_output.get('total_markets_supported', 1):,.0f}")
        st.write(f"Active accounts supported: {channel_sales_output.get('total_active_accounts_supported', 0):,.0f}")
        st.write("CEO recommendation:")
        st.write("Protect the separated ownership structure so each channel has clear accountability and the Sales Manager can govern the full revenue plan.")
        return

    if kpi_name == "Sales Coordinator / MIS":
        st.write("What this role owns")
        st.write("Sales Coordinator / MIS supports all commercial divisions operationally through order coordination, reporting, and admin discipline.")
        render_display_dataframe(st, "sales_coordinator_mis_detail", pd.DataFrame([
            {"Item": "Total commercial revenue supported", "Value": fmt_currency(channel_sales_output.get("total_commercial_revenue", 0.0))},
            {"Item": "Total markets supported", "Value": f"{channel_sales_output.get('total_markets_supported', 0):,.0f}"},
            {"Item": "Total active accounts supported", "Value": f"{channel_sales_output.get('total_active_accounts_supported', 0):,.0f}"},
            {"Item": "Reporting / order-coordination workload", "Value": "Shared across GT, MT, QCom, HoReCa, and Institutional / Government"},
            {"Item": "Required HC", "Value": f"{channel_sales_output.get('sales_coordinator_mis', 0):,.0f}"},
        ]), hide_index=True, width="stretch")
        st.write("Why this role is required")
        st.write("It supports reporting, order lines, coordination, and governance across the commercial organization.")
        return

    if kpi_name == "Total Commercial HC":
        reconciliation_status = "Reconciled" if channel_sales_output.get("commercial_hc_reconciled", False) else "Not Reconciled"
        render_display_dataframe(st, "total_commercial_hc_detail", pd.DataFrame([
            {"Item": "Head of Sales", "Value": f"{int(channel_sales_output.get('head_sales_hc', channel_sales_output.get('sales_manager', 0)) or 0):,.0f}"},
            {"Item": "General Trade", "Value": f"{int(channel_sales_output.get('general_trade_hc', channel_sales_output.get('gt_sales_executives', 0)) or 0):,.0f}"},
            {"Item": "Modern Trade", "Value": f"{int(channel_sales_output.get('modern_trade_hc', channel_sales_output.get('mt_kam', 0)) or 0):,.0f}"},
            {"Item": "Quick Commerce", "Value": f"{int(channel_sales_output.get('quick_commerce_hc', channel_sales_output.get('qcom_kam', 0)) or 0):,.0f}"},
            {"Item": "E-commerce", "Value": f"{int(channel_sales_output.get('e_commerce_hc', channel_sales_output.get('ecommerce_kam', 0)) or 0):,.0f}"},
            {"Item": "HoReCa", "Value": f"{int(channel_sales_output.get('horeca_hc', channel_sales_output.get('horeca_sales_hc', 0)) or 0):,.0f}"},
            {"Item": "Institutional / Government", "Value": f"{int(channel_sales_output.get('institutional_hc', channel_sales_output.get('institution_government_manager', 0)) or 0):,.0f}"},
            {"Item": "Exports", "Value": f"{int(channel_sales_output.get('export_hc', channel_sales_output.get('exports_manager', 0)) or 0):,.0f}"},
            {"Item": "Total Commercial HC", "Value": f"{int(channel_sales_output.get('commercial_hc_sum', channel_sales_output.get('total_commercial_hc', 0)) or 0):,.0f}"},
            {"Item": "Reconciliation Status", "Value": reconciliation_status},
        ]), hide_index=True, width="stretch")
        if not channel_sales_output.get("commercial_hc_reconciled", False):
            st.warning(
                f"Commercial HC variance detected: reported {int(channel_sales_output.get('commercial_hc_reported', 0) or 0):,.0f} vs component sum {int(channel_sales_output.get('commercial_hc_sum', 0) or 0):,.0f} (variance {int(channel_sales_output.get('commercial_hc_variance', 0) or 0):+,.0f})."
            )
        st.write(f"Total commercial revenue: {fmt_currency(channel_sales_output.get('total_commercial_revenue', 0.0))}")
        st.write(f"Markets supported: {channel_sales_output.get('total_markets_supported', 1):,.0f}")
        st.write(f"Active accounts supported: {channel_sales_output.get('total_active_accounts_supported', 0):,.0f}")
        return

    st.write(f"Total commercial headcount: {channel_sales_output['total_commercial_hc']:,.0f}")


def show_distributor_channel_drilldown(kpi_name):
    dialog_title = {
        "HoReCa Revenue": "HoReCa Commercial Planning",
        "Institutional / Government Revenue": "Institutional / Government Commercial Planning",
    }.get(kpi_name, kpi_name)
    if hasattr(st, "dialog"):
        @st.dialog(dialog_title)
        def _distributor_channel_dialog():
            render_distributor_channel_drilldown(kpi_name)

        _distributor_channel_dialog()
    else:
        with st.expander(dialog_title, expanded=True):
            render_distributor_channel_drilldown(kpi_name)


def distributor_channel_kpi_card(label, value, key, subtitle=None, status=None, status_type=None):
    render_kpi_card(label, value, subtitle=subtitle, status=status, status_type=status_type, button_label="View details", key=key, button_action=lambda: show_distributor_channel_drilldown(label), icon_key=DISTRIBUTION_ICON_KEYS.get(label, "capacity_status"))


def distribution_business_card(label, revenue, partners, network_capacity, utilization_pct, status, key):
    if label == "Fresh Chilled Business":
        subtitle = f"GT Retail Coverage: Not Connected | HORECA Accounts: Not Connected | Institutional Accounts: Not Connected | Cold Chiller Capacity: {fmt_currency(network_capacity)} | Same-day Distribution: {utilization_pct:,.1f}% | Active Market Coverage: Not Connected"
    else:
        subtitle = f"Distribution Partners: {partners:,.0f} | Monthly Network Capacity: {fmt_currency(network_capacity)} | Utilization: {utilization_pct:,.1f}% | Active distributor actual count: Not Connected"
    render_kpi_card(label, fmt_currency(revenue), subtitle=subtitle, status=status, status_type="pbos-status-neutral", button_label="View details", key=key, button_action=lambda: show_distributor_channel_drilldown(label), icon_key=DISTRIBUTION_ICON_KEYS.get(label))


def as_int(v):
    try:
        return int(round(float(v)))
    except Exception:
        return 0


def as_float(v):
    try:
        return float(v)
    except Exception:
        return 0.0


def _normalize_key(value):
    return str(value).strip().upper().replace(" ", "_").replace("/", "_").replace("-", "_")


def _resolve(raw_values, keys, default=None):
    for key in keys:
        if key in raw_values:
            return raw_values[key]
    return default


def load_assumptions(path):
    if not os.path.exists(path):
        return {}

    df = pd.read_csv(path)
    raw_values = {}
    for _, row in df.iterrows():
        assumption_id = str(row.get("assumption_id", "")).strip()
        parameter = str(row.get("parameter", "")).strip()
        value = row.get("value", 0)
        if assumption_id:
            raw_values[_normalize_key(assumption_id)] = value
        if parameter:
            raw_values[_normalize_key(parameter)] = value

    return {
        "AVG_BIRDS_PER_FARM": as_int(_resolve(raw_values, ["AVG_BIRDS_PER_FARM", "AVERAGE_BIRDS_PER_FARM"], 50000)),
        "AVG_BIRDS_PER_TRADER": as_int(_resolve(raw_values, ["AVG_BIRDS_PER_TRADER", "AVERAGE_BIRDS_PER_TRADER"], 20000)),
        "AVG_BIRDS_PER_TRUCK": as_int(_resolve(raw_values, ["AVG_BIRDS_PER_TRUCK"], 9000)),
        "PRODUCTION_LINE_CAPACITY": as_float(_resolve(raw_values, ["PRODUCTION_LINE_CAPACITY", "PROD_LINE_CAPACITY"], 250.0)),
        "LIVE_BIRD_RATE": as_float(_resolve(raw_values, ["LIVE_BIRD_RATE", "BIRD_RATE"], 180.0)),
        "YIELD_PCT": as_float(_resolve(raw_values, ["YIELD_PCT"], 72.0)),
        "PROCESSING_LOSS_PCT": as_float(_resolve(raw_values, ["PROCESSING_LOSS_PCT"], 3.0)),
        "MORTALITY_PCT": as_float(_resolve(raw_values, ["MORTALITY_PCT"], 2.0)),
        "PACKAGING_COST_PER_KG": as_float(_resolve(raw_values, ["PACKAGING_COST_PER_KG", "PACKAGING_COST"], 18.0)),
        "TRANSPORT_COST_PER_KG": as_float(_resolve(raw_values, ["TRANSPORT_COST_PER_KG", "TRANSPORT_COST"], 12.0)),
        "WORKING_CAPITAL_PCT": as_float(_resolve(raw_values, ["WORKING_CAPITAL_PCT", "WC_PCT"], 0.22)),
        "EBITDA_MARGIN_PCT": as_float(_resolve(raw_values, ["EBITDA_MARGIN_PCT", "EBITDA_MARGIN"], 0.18)),
        "PAT_MARGIN_PCT": as_float(_resolve(raw_values, ["PAT_MARGIN_PCT", "PAT_MARGIN"], 0.10)),
        "CAPEX_PER_LINE": as_float(_resolve(raw_values, ["CAPEX_PER_LINE", "CAPEX_PER_PROD_LINE"], 50000000.0)),
        "ASP_KG": as_float(_resolve(raw_values, ["ASP_KG", "ASP"], 240.0)),
        "AVG_BIRD_WEIGHT": as_float(_resolve(raw_values, ["AVG_BIRD_WEIGHT"], 1.8)),
        "WORKING_DAYS": as_int(_resolve(raw_values, ["WORKING_DAYS"], 25)),
        "PLANT_CAPACITY_PER_LINE_MT_DAY": as_float(_resolve(raw_values, ["PLANT_CAPACITY_PER_LINE_MT_DAY"], 10.0)),
        "WORKING_HOURS_PER_SHIFT": as_float(_resolve(raw_values, ["WORKING_HOURS_PER_SHIFT"], 8.0)),
        "MAX_SHIFTS": as_int(_resolve(raw_values, ["MAX_SHIFTS", "MAXIMUM_SHIFTS"], 3)),
        "COLD_STORAGE_BUFFER_DAYS": as_float(_resolve(raw_values, ["COLD_STORAGE_BUFFER_DAYS"], 3.0)),
        "UTILIZATION_THRESHOLD_PCT": as_float(_resolve(raw_values, ["UTILIZATION_THRESHOLD_PCT", "UTILIZATION_THRESHOLD"], 85.0)),
    }


def get_assumption(assumptions, lookup_keys, default=None):
    for key in lookup_keys:
        if key in assumptions:
            return assumptions[key]
    return default


def load_logic_registry(path):
    if not os.path.exists(path):
        return pd.DataFrame(columns=["logic_id", "business_area", "description", "formula", "assumption_keys", "used_by"])
    return pd.read_csv(path)


def load_market_registry(path):
    if not os.path.exists(path):
        return pd.DataFrame(columns=[
            "market_id", "country", "state", "city", "distance_km", "growth_stage",
            "preferred_transport", "warehouse_required", "distribution_center_required",
            "break_even_revenue", "revenue_allocation_cr", "remarks"
        ])

    df = pd.read_csv(path)
    for col in [
        "market_id", "country", "state", "city", "distance_km", "growth_stage",
        "preferred_transport", "warehouse_required", "distribution_center_required",
        "break_even_revenue", "revenue_allocation_cr", "remarks", "assigned_plant_id"
    ]:
        if col not in df.columns:
            df[col] = None

    df["city"] = df["city"].fillna("N/A")
    df["state"] = df["state"].fillna("N/A")
    df["distance_km"] = pd.to_numeric(df["distance_km"], errors="coerce").fillna(0.0)
    df["break_even_revenue"] = pd.to_numeric(df["break_even_revenue"], errors="coerce").fillna(0.0)
    df["revenue_allocation_cr"] = pd.to_numeric(df["revenue_allocation_cr"], errors="coerce").fillna(0.0)
    df["growth_stage"] = df["growth_stage"].fillna("Scale-up")
    df["preferred_transport"] = df["preferred_transport"].fillna("Road")
    df["warehouse_required"] = df["warehouse_required"].fillna("No")
    df["distribution_center_required"] = df["distribution_center_required"].fillna("No")
    df["remarks"] = df["remarks"].fillna("")
    df["assigned_plant_id"] = df["assigned_plant_id"].fillna("PLANT_KOL")
    return df


def load_plant_registry(path):
    columns = [
        "plant_id", "plant_name", "city", "state", "status", "production_mode",
        "installed_capacity_mt_day", "line_capacity_mt_day", "installed_lines", "active_shifts",
        "maximum_lines_in_current_plant", "maximum_shifts_per_line", "maximum_shifts",
        "existing_plant_expandable",
        "cold_storage_capacity_mt", "served_markets", "is_default"
    ]
    if not os.path.exists(path):
        return pd.DataFrame([{
            "plant_id": "PLANT_KOL",
            "plant_name": "Kolkata Plant",
            "city": "Kolkata",
            "state": "West Bengal",
            "status": "Active",
            "production_mode": "Semi Automatic",
            "installed_capacity_mt_day": 10.0,
            "line_capacity_mt_day": 10.0,
            "installed_lines": 1,
            "active_shifts": 1,
            "maximum_lines_in_current_plant": 2,
            "maximum_shifts_per_line": 3,
            "maximum_shifts": 3,
            "existing_plant_expandable": "Yes",
            "cold_storage_capacity_mt": 30.0,
            "served_markets": "Kolkata|Guwahati|Patna|Bhubaneswar",
            "is_default": "Yes",
        }], columns=columns)

    df = pd.read_csv(path)
    for col in columns:
        if col not in df.columns:
            df[col] = None
    df["plant_id"] = df["plant_id"].fillna("PLANT_KOL")
    df["plant_name"] = df["plant_name"].fillna(df["plant_id"])
    df["status"] = df["status"].fillna("Active")
    df["production_mode"] = df["production_mode"].fillna("Semi Automatic")
    df["installed_capacity_mt_day"] = pd.to_numeric(df["installed_capacity_mt_day"], errors="coerce").fillna(10.0)
    df["line_capacity_mt_day"] = pd.to_numeric(df["line_capacity_mt_day"], errors="coerce").fillna(10.0)
    df["installed_lines"] = pd.to_numeric(df["installed_lines"], errors="coerce").fillna(1).astype(int)
    df["active_shifts"] = pd.to_numeric(df["active_shifts"], errors="coerce").fillna(1).astype(int)
    df["maximum_lines_in_current_plant"] = pd.to_numeric(df["maximum_lines_in_current_plant"], errors="coerce").fillna(df["installed_lines"].clip(lower=1) + 1).astype(int)
    if "maximum_shifts_per_line" in df.columns:
        max_shift_series = pd.to_numeric(df["maximum_shifts_per_line"], errors="coerce")
    else:
        max_shift_series = pd.Series([None] * len(df))
    fallback_max_shifts = pd.to_numeric(df["maximum_shifts"], errors="coerce") if "maximum_shifts" in df.columns else pd.Series([3] * len(df))
    df["maximum_shifts_per_line"] = max_shift_series.fillna(fallback_max_shifts).fillna(3).astype(int)
    df["maximum_shifts"] = df["maximum_shifts_per_line"]
    df["existing_plant_expandable"] = df["existing_plant_expandable"].fillna("Yes")
    df["maximum_shifts"] = pd.to_numeric(df["maximum_shifts"], errors="coerce").fillna(3).astype(int)
    df["cold_storage_capacity_mt"] = pd.to_numeric(df["cold_storage_capacity_mt"], errors="coerce").fillna(30.0)
    df["is_default"] = df["is_default"].fillna("No")
    return df


def stage_profile(stage):
    profiles = {
        "Startup": {
            "employees_per_line": 60,
            "line_capacity_mt_month": 0.7,
            "capex_per_line": 30_000_000,
            "working_capital_pct": 0.28,
            "warehouse_count": 1,
            "automation": "Manual",
            "automation_note": "Higher manpower and manual handling are required at launch.",
        },
        "Scale-up": {
            "employees_per_line": 45,
            "line_capacity_mt_month": 1.1,
            "capex_per_line": 50_000_000,
            "working_capital_pct": 0.24,
            "warehouse_count": 2,
            "automation": "Semi Automatic",
            "automation_note": "Semi-automatic operations support early scale-up discipline.",
        },
        "Regional": {
            "employees_per_line": 38,
            "line_capacity_mt_month": 1.4,
            "capex_per_line": 65_000_000,
            "working_capital_pct": 0.22,
            "warehouse_count": 2,
            "automation": "Semi Automatic",
            "automation_note": "Regional expansion requires moderate automation and stronger logistics.",
        },
        "Multi-state": {
            "employees_per_line": 35,
            "line_capacity_mt_month": 1.8,
            "capex_per_line": 75_000_000,
            "working_capital_pct": 0.20,
            "warehouse_count": 3,
            "automation": "Fully Automatic",
            "automation_note": "Multi-state expansion benefits from automation and regional warehousing.",
        },
        "National": {
            "employees_per_line": 30,
            "line_capacity_mt_month": 2.2,
            "capex_per_line": 90_000_000,
            "working_capital_pct": 0.18,
            "warehouse_count": 4,
            "automation": "Fully Automatic",
            "automation_note": "National scale requires high automation and multi-node warehousing.",
        },
    }
    return profiles.get(stage, profiles["Startup"])


base_dir = os.path.dirname(__file__)
assumptions_path = os.path.join(base_dir, "..", "business_assumptions.csv")
market_registry_path = os.path.join(base_dir, "..", "market_registry.csv")
plant_registry_path = os.path.join(base_dir, "..", "plant_registry.csv")
formula_registry_path = os.path.join(base_dir, "..", "formula_registry.csv")
dependency_registry_path = os.path.join(base_dir, "..", "dependency_registry.csv")
logic_registry_path = os.path.join(base_dir, "..", "logic_registry.csv")
product_registry_path = os.path.join(base_dir, "..", "product_registry.csv")
channel_registry_path = os.path.join(base_dir, "..", "channel_registry.csv")
pricing_registry_path = os.path.join(base_dir, "..", "pricing_registry.csv")
cost_registry_path = os.path.join(base_dir, "..", "cost_registry.csv")
order_registry_path = os.path.join(base_dir, "..", "order_registry.csv")

assumptions = load_assumptions(assumptions_path)
market_registry = load_market_registry(market_registry_path)
plant_registry = load_plant_registry(plant_registry_path)
formula_registry = pd.read_csv(formula_registry_path) if os.path.exists(formula_registry_path) else pd.DataFrame()
dependency_registry = pd.read_csv(dependency_registry_path) if os.path.exists(dependency_registry_path) else pd.DataFrame()
logic_registry = load_logic_registry(logic_registry_path)
product_registry = pd.read_csv(product_registry_path) if os.path.exists(product_registry_path) else pd.DataFrame()
channel_registry = pd.read_csv(channel_registry_path) if os.path.exists(channel_registry_path) else pd.DataFrame()
pricing_registry = pd.read_csv(pricing_registry_path) if os.path.exists(pricing_registry_path) else pd.DataFrame()
cost_registry = pd.read_csv(cost_registry_path) if os.path.exists(cost_registry_path) else pd.DataFrame()
order_registry = pd.read_csv(order_registry_path) if os.path.exists(order_registry_path) else pd.DataFrame(columns=[
    "order_id", "order_date", "market_id", "channel", "customer_id", "sku_id",
    "product_group", "ordered_quantity_kg", "required_delivery_date",
    "assigned_plant_id", "order_status"
])

formula_lookup = {str(row.get("kpi_name", "")).strip(): row for _, row in formula_registry.iterrows()} if not formula_registry.empty else {}
dependency_lookup = dependency_registry if not dependency_registry.empty else pd.DataFrame(columns=["affected_kpi_name", "driver_name", "business_reason"])
logic_lookup = {str(row.get("business_area", "")).strip(): row for _, row in logic_registry.iterrows()} if not logic_registry.empty else {}

with st.sidebar:
    log_section_start("sidebar_construction")
    st.markdown("### PBOS Planning Controls")
    st.markdown("<div class='pbos-sidebar-caption'>Adjust assumptions to test business scenarios.</div>", unsafe_allow_html=True)
    with st.expander("A. Business Planning Inputs", expanded=True):
        corporate_revenue_cr = st.number_input("Corporate Revenue Target (₹ Cr / month)", min_value=float(0.0), value=float(6.0), step=float(1.0))
        business_stage = st.selectbox("Business Stage", ["Startup", "Scale-up", "Regional", "Multi-state", "National"], index=0)
        operating_model = st.selectbox("Operating Model", ["Asset Light", "Partial Integration", "Fully Integrated"], index=0)

    product_mix = {}
    with st.expander("B. Product Mix", expanded=False):
        for _, row in product_registry.iterrows():
            product_id = str(row.get("product_id", "")).strip()
            product_name = str(row.get("product_name", product_id))
            default_mix = as_float(row.get("default_mix_percent", 0.0))
            product_mix[product_id] = st.slider(f"{product_name} %", 0, 100, int(default_mix), key=f"product_{product_id}")

    channel_mix = {}
    with st.expander("C. Channel Mix", expanded=False):
        st.markdown("<div class='pbos-sidebar-note'>Allocate the planned revenue target across active channels.</div>", unsafe_allow_html=True)
        for _, row in channel_registry.iterrows():
            channel_id = str(row.get("channel_id", "")).strip()
            channel_name = str(row.get("channel_name", channel_id))
            default_mix = as_float(row.get("default_mix_percent", 0.0))
            channel_mix[channel_id] = st.slider(f"{channel_name} %", 0, 100, int(default_mix), key=f"channel_{channel_id}")

    with st.expander("D. Procurement Drivers", expanded=False):
        st.subheader("Procurement Drivers")
        live_bird_rate = st.number_input("Live Bird Rate (₹/kg)", min_value=float(0.0), max_value=float(500.0), value=get_assumption(assumptions, ["LIVE_BIRD_RATE"], as_float(180.0)), step=float(5.0))
        yield_pct = st.number_input("Yield %", min_value=float(0.0), max_value=float(100.0), value=get_assumption(assumptions, ["YIELD_PCT"], as_float(72.0)), step=float(1.0))
        mortality_pct = st.number_input("Mortality %", min_value=float(0.0), max_value=float(100.0), value=get_assumption(assumptions, ["MORTALITY_PCT"], as_float(4.0)), step=float(0.5))
        processing_loss_pct = st.number_input("Processing Loss %", min_value=float(0.0), max_value=float(100.0), value=get_assumption(assumptions, ["PROCESSING_LOSS_PCT"], as_float(3.0)), step=float(0.5))
        gt_distributor_margin_pct = st.number_input("GT Distributor Margin %", min_value=float(0.0), max_value=float(100.0), value=get_assumption(assumptions, ["TRADER_MARGIN_PCT", "GT_DISTRIBUTOR_MARGIN_PCT"], as_float(6.0)), step=float(0.5), key="trader_margin_pct")
        st.caption("Applies only to General Trade distributor economics. It does not alter live-bird procurement cost.")
        packaging_cost = st.number_input("Packaging Cost (₹/kg)", min_value=float(0.0), max_value=float(250.0), value=get_assumption(assumptions, ["PACKAGING_COST_PER_KG"], as_float(18.0)), step=float(1.0))
        transport_cost = st.number_input("Transport Cost (₹/kg)", min_value=float(0.0), max_value=float(250.0), value=get_assumption(assumptions, ["TRANSPORT_COST_PER_KG"], as_float(12.0)), step=float(1.0))

    procurement_drivers = {
        "live_bird_rate_per_kg": live_bird_rate,
        "yield_pct": yield_pct,
        "mortality_pct": mortality_pct,
        "processing_loss_pct": processing_loss_pct,
        "gt_distributor_margin_pct": gt_distributor_margin_pct,
        "packaging_cost_per_kg": packaging_cost,
        "transport_cost_per_kg": transport_cost,
    }

    with st.expander("E. Plant & Manufacturing Assumptions", expanded=False):
        st.subheader("Operational Assumptions")
        asp_per_kg = st.number_input("Average Selling Price / kg", min_value=float(0.0), max_value=float(1000.0), value=get_assumption(assumptions, ["ASP_KG"], as_float(240.0)), step=float(10.0))
        avg_bird_weight = st.number_input("Average Bird Weight (kg)", min_value=float(0.1), max_value=float(5.0), value=get_assumption(assumptions, ["AVG_BIRD_WEIGHT"], as_float(1.8)), step=float(0.1))
        working_days = st.number_input("Working Days", min_value=int(1), max_value=int(365), value=get_assumption(assumptions, ["WORKING_DAYS"], as_int(25)), step=int(1))
        avg_farm_capacity = st.number_input("Average Farm Capacity (Birds)", min_value=int(1), max_value=int(1000000), value=get_assumption(assumptions, ["AVG_BIRDS_PER_FARM"], as_int(50000)), step=int(1000))
        avg_trader_capacity = st.number_input("Average Trader Capacity (Birds)", min_value=int(1), max_value=int(1000000), value=get_assumption(assumptions, ["AVG_BIRDS_PER_TRADER"], as_int(20000)), step=int(1000))

        st.subheader("Plant & Manufacturing Assumptions")
        plant_capacity_per_line_mt_day = st.number_input("Plant Capacity / Line / Day (MT)", min_value=float(0.1), max_value=float(500.0), value=get_assumption(assumptions, ["PLANT_CAPACITY_PER_LINE_MT_DAY"], as_float(10.0)), step=float(0.5))
        working_hours_per_shift = st.number_input("Working Hours / Shift", min_value=float(1.0), max_value=float(24.0), value=get_assumption(assumptions, ["WORKING_HOURS_PER_SHIFT"], as_float(8.0)), step=float(1.0))
        max_shifts = st.number_input("Maximum Shifts", min_value=int(1), max_value=int(4), value=get_assumption(assumptions, ["MAX_SHIFTS"], as_int(3)), step=int(1))
        cold_storage_buffer_days = st.number_input("Cold Storage Buffer Days", min_value=float(0.0), max_value=float(30.0), value=get_assumption(assumptions, ["COLD_STORAGE_BUFFER_DAYS"], as_float(3.0)), step=float(0.5))
        utilization_threshold_pct = st.number_input("Utilization Threshold %", min_value=float(1.0), max_value=float(100.0), value=get_assumption(assumptions, ["UTILIZATION_THRESHOLD_PCT"], as_float(85.0)), step=float(1.0))

    with st.expander("F. Logistics Assumptions", expanded=False):
        st.subheader("Logistics Assumptions")
        primary_vehicle_capacity_kg = st.number_input("Primary Vehicle Capacity (kg)", min_value=float(1.0), max_value=float(50000.0), value=float(4000.0), step=float(500.0))
        primary_trips_per_vehicle_per_day = st.number_input("Primary Trips per Vehicle per Day", min_value=int(1), max_value=int(10), value=int(2), step=int(1))
        average_primary_distance_km = st.number_input("Average Primary Distance (km)", min_value=float(0.0), max_value=float(2000.0), value=float(100.0), step=float(10.0))
        primary_cost_per_km = st.number_input("Primary Cost per km", min_value=float(0.0), max_value=float(500.0), value=float(28.0), step=float(1.0))
        primary_fixed_cost_per_trip = st.number_input("Primary Fixed Cost per trip", min_value=float(0.0), max_value=float(50000.0), value=float(1500.0), step=float(500.0))
        secondary_vehicle_capacity_mt = st.number_input("Secondary Vehicle Capacity (MT)", min_value=float(0.1), max_value=float(50.0), value=float(2.0), step=float(0.5))
        secondary_trips_per_vehicle_per_day = st.number_input("Secondary Trips per Vehicle per Day", min_value=int(1), max_value=int(10), value=int(2), step=int(1))
        secondary_cost_per_km = st.number_input("Secondary Cost per km", min_value=float(0.0), max_value=float(500.0), value=float(32.0), step=float(1.0))
        secondary_fixed_cost_per_trip = st.number_input("Secondary Fixed Cost per trip", min_value=float(0.0), max_value=float(50000.0), value=float(2000.0), step=float(500.0))
        cold_chain_cost_multiplier = st.number_input("Cold Chain Cost Multiplier", min_value=float(1.0), max_value=float(5.0), value=float(1.20), step=float(0.05))

    with st.expander("Contract and Tender Inputs", expanded=False):
        st.subheader("Distributor and Channel Sales Assumptions")
        fresh_distributor_enabled = st.checkbox("Enable Fresh Distributor", value=False)
        shared_frozen_rte_distributor = st.checkbox("Shared Frozen + RTE Distributor", value=True)
        fresh_revenue_per_distributor = st.number_input("Fresh revenue handled per distributor / month", min_value=float(1.0), max_value=float(100_000_000.0), value=float(4_000_000.0), step=float(500_000.0))
        frozen_revenue_per_distributor = st.number_input("Frozen revenue handled per distributor / month", min_value=float(1.0), max_value=float(100_000_000.0), value=float(6_000_000.0), step=float(500_000.0))
        rte_revenue_per_distributor = st.number_input("RTE revenue handled per distributor / month", min_value=float(1.0), max_value=float(100_000_000.0), value=float(7_500_000.0), step=float(500_000.0))
        gt_revenue_per_sales_executive = st.number_input("GT revenue per sales executive / month", min_value=float(1.0), max_value=float(100_000_000.0), value=float(3_000_000.0), step=float(500_000.0))
        gt_outlets_per_sales_executive = st.number_input("GT outlets per sales executive", min_value=int(1), max_value=int(1000), value=int(50), step=int(5))
        gt_sales_executives_per_asm = st.number_input("GT sales executives per ASM", min_value=int(1), max_value=int(50), value=int(6), step=int(1))
        mt_revenue_per_kam = st.number_input("MT revenue per KAM / month", min_value=float(1.0), max_value=float(100_000_000.0), value=float(7_500_000.0), step=float(500_000.0))
        quick_commerce_revenue_per_kam = st.number_input("Quick Commerce revenue per KAM / month", min_value=float(1.0), max_value=float(100_000_000.0), value=float(10_000_000.0), step=float(500_000.0))
        horeca_revenue_per_sales_executive = st.number_input("HoReCa revenue per sales executive / month", min_value=float(1.0), max_value=float(100_000_000.0), value=float(4_000_000.0), step=float(500_000.0))
        institution_revenue_per_account_manager = st.number_input("Institution revenue per account manager / month", min_value=float(1.0), max_value=float(100_000_000.0), value=float(7_500_000.0), step=float(500_000.0))
        calls_per_sales_executive_day = st.number_input("Calls per sales executive / day", min_value=int(1), max_value=int(100), value=int(12), step=int(1))

        st.subheader("HoReCa Contract Revenue")
        horeca_revenue_mode = st.selectbox("HoReCa Revenue Mode", ["CONTRACT", "MIX_ALLOCATION"], index=0)
        dynamic_contract_pricing = build_contract_pricing_output(live_bird_rate=live_bird_rate, procurement_drivers=procurement_drivers, operating_model=operating_model)
        recommended_contract_rate_per_kg = float(dynamic_contract_pricing["contract_rate_per_kg"])
        horeca_contract_rate_per_kg = st.number_input("HoReCa Contract Rate (₹/kg)", min_value=float(0.01), max_value=float(1000.0), value=recommended_contract_rate_per_kg, step=float(1.0), disabled=True)
        horeca_contract_volume_kg_month = st.number_input("HoReCa Contract Volume (kg/month)", min_value=float(0.0), max_value=float(1_000_000.0), value=float(5_000.0), step=float(500.0))
        horeca_active_accounts = st.number_input("HoReCa Active Accounts", min_value=int(0), max_value=int(10000), value=int(10), step=int(1))
        horeca_credit_days = st.number_input("HoReCa Credit Days", min_value=int(0), max_value=int(180), value=int(30), step=int(1))

        st.subheader("Institutional / Government Contract")
        institutional_revenue_mode = st.selectbox("Institutional / Government Revenue Mode", ["CONTRACT", "MIX_ALLOCATION"], index=0)
        institutional_contract_rate_per_kg = st.number_input("Institutional Contract Rate (₹/kg)", min_value=float(0.01), max_value=float(1000.0), value=recommended_contract_rate_per_kg, step=float(1.0), disabled=True)
        institutional_awarded_volume_kg_month = st.number_input("Institutional Awarded Volume (kg/month)", min_value=float(0.0), max_value=float(1_000_000.0), value=float(5_000.0), step=float(500.0))
        institutional_contract_name = st.text_input("Contract / Tender Name", value="Institutional Curry Cut Contract")
        institutional_contract_start_date = st.date_input("Contract Start Date", value=date.today())
        institutional_contract_end_date = st.date_input("Contract End Date", value=date.today())
    log_section_end("sidebar_construction")

fresh_pct = product_mix.get("FRESH", 0)
frozen_pct = product_mix.get("FROZEN", 0)
rte_pct = product_mix.get("RTE", 0)
fva_pct = product_mix.get("FVA", 0)
general_trade_pct = channel_mix.get("GT", 0)
modern_trade_pct = channel_mix.get("MT", 0)
quick_commerce_pct = channel_mix.get("QC", 0)
ecommerce_pct = channel_mix.get("ECOM", 0)
horeca_pct = channel_mix.get("HORECA", 0)
institution_pct = channel_mix.get("INST", 0)
export_pct = channel_mix.get("EXP", 0)
product_total = sum(product_mix.values())
channel_total = sum(channel_mix.values())

with st.expander("Add or Edit Market", expanded=False):
    market_registry = load_market_registry(market_registry_path)
    if market_registry.empty:
        market_registry = pd.DataFrame(columns=[
            "market_id", "country", "state", "city", "distance_km", "growth_stage",
            "preferred_transport", "warehouse_required", "distribution_center_required",
            "break_even_revenue", "revenue_allocation_cr", "assigned_plant_id", "remarks"
        ])

    if "revenue_allocation_cr" not in market_registry.columns:
        market_registry["revenue_allocation_cr"] = 0.0
    if "assigned_plant_id" not in market_registry.columns:
        market_registry["assigned_plant_id"] = "PLANT_KOL"
    market_registry["assigned_plant_id"] = market_registry["assigned_plant_id"].fillna("PLANT_KOL")

    if market_registry["revenue_allocation_cr"].isna().all() or float(market_registry["revenue_allocation_cr"].sum()) == 0.0:
        if not market_registry.empty:
            market_registry["revenue_allocation_cr"] = 0.0
            if "Kolkata" in market_registry["city"].astype(str).tolist():
                market_registry.loc[market_registry["city"].astype(str) == "Kolkata", "revenue_allocation_cr"] = corporate_revenue_cr
            elif len(market_registry) > 0:
                market_registry.iloc[0, market_registry.columns.get_loc("revenue_allocation_cr")] = corporate_revenue_cr
        else:
            market_registry["revenue_allocation_cr"] = 0.0

    visible_markets = market_registry[[
        "city", "state", "distance_km", "growth_stage", "preferred_transport",
        "warehouse_required", "distribution_center_required", "break_even_revenue",
        "revenue_allocation_cr", "assigned_plant_id", "remarks"
    ]].copy()
    visible_markets = visible_markets.reset_index(drop=True)
    log_dataframe_shape("market_editor", visible_markets)
    editable_markets = render_display_editor(
        st,
        "market_editor",
        visible_markets,
        num_rows="dynamic",
        hide_index=True,
        width="stretch",
        column_config={
            "revenue_allocation_cr": st.column_config.NumberColumn("Revenue Allocation (₹ Cr)", min_value=0.0, step=0.5),
            "distance_km": st.column_config.NumberColumn("Distance (km)", min_value=0.0, step=50.0),
            "assigned_plant_id": st.column_config.SelectboxColumn("Assigned Plant", options=plant_registry["plant_id"].astype(str).tolist()),
            "break_even_revenue": st.column_config.NumberColumn("Break-even Revenue (₹)", min_value=0.0, step=10_000_000.0),
        },
    )
    market_registry[[
        "city", "state", "distance_km", "growth_stage", "preferred_transport",
        "warehouse_required", "distribution_center_required", "break_even_revenue",
        "revenue_allocation_cr", "assigned_plant_id", "remarks"
    ]] = editable_markets
    market_registry["city"] = market_registry["city"].fillna("N/A")
    market_registry["state"] = market_registry["state"].fillna("N/A")
    market_registry["distance_km"] = pd.to_numeric(market_registry["distance_km"], errors="coerce").fillna(0.0)
    market_registry["break_even_revenue"] = pd.to_numeric(market_registry["break_even_revenue"], errors="coerce").fillna(0.0)
    market_registry["revenue_allocation_cr"] = pd.to_numeric(market_registry["revenue_allocation_cr"], errors="coerce").fillna(0.0)
    market_registry["assigned_plant_id"] = market_registry["assigned_plant_id"].fillna("PLANT_KOL")

    with st.form("add_market_form"):
        st.write("Add New Market")
        new_city = st.text_input("City", key="new_market_city")
        new_state = st.text_input("State", key="new_market_state")
        new_distance = st.number_input("Distance (km)", min_value=int(0), value=int(0), step=int(50), key="new_market_distance")
        new_revenue_cr = st.number_input("Revenue Allocation (₹ Cr)", min_value=float(0.0), value=float(1.0), step=float(0.5), key="new_market_revenue")
        submitted = st.form_submit_button("Save Market")
        if submitted and new_city:
            market_registry = pd.concat([
                market_registry,
                pd.DataFrame([{
                    "market_id": f"MKT{len(market_registry)+1:03d}",
                    "country": "India",
                    "state": new_state or "N/A",
                    "city": new_city,
                    "distance_km": new_distance,
                    "growth_stage": business_stage,
                    "preferred_transport": "Road",
                    "warehouse_required": "No",
                    "distribution_center_required": "No",
                    "break_even_revenue": new_revenue_cr * 10_000_000 * 1.15,
                    "revenue_allocation_cr": new_revenue_cr,
                    "assigned_plant_id": "PLANT_KOL",
                    "remarks": "User-added market"
                }])
            ], ignore_index=True)
            market_registry.to_csv(market_registry_path, index=False)
            st.success(f"Saved {new_city} to the market registry.")

issues = []
if abs(product_total - 100) > 0.01:
    issues.append("Product Mix must equal 100%.")
if abs(channel_total - 100) > 0.01:
    issues.append("Channel Mix must equal 100%.")
if live_bird_rate < 0:
    issues.append("Live Bird Rate must be greater than or equal to 0.")
if yield_pct <= 0 or yield_pct > 100:
    issues.append("Yield % must be greater than 0 and less than or equal to 100.")
if mortality_pct < 0 or mortality_pct >= 100:
    issues.append("Mortality % must be greater than or equal to 0 and less than 100.")
if processing_loss_pct < 0 or processing_loss_pct >= 100:
    issues.append("Processing Loss % must be greater than or equal to 0 and less than 100.")
if gt_distributor_margin_pct < 0:
    issues.append("GT Distributor Margin % must be greater than or equal to 0.")
if packaging_cost < 0:
    issues.append("Packaging Cost must be greater than or equal to 0.")
if transport_cost < 0:
    issues.append("Transport Cost must be greater than or equal to 0.")
if market_registry.empty:
    issues.append("Add at least one market before planning.")
else:
    if len(market_registry) == 1:
        market_registry.loc[market_registry.index[0], "revenue_allocation_cr"] = corporate_revenue_cr
    allocation_total_cr = float(market_registry["revenue_allocation_cr"].sum())
    if market_registry["revenue_allocation_cr"].notna().any() and float(market_registry["revenue_allocation_cr"].count()) > 0:
        if abs(allocation_total_cr - corporate_revenue_cr) > 0.01:
            issues.append("Revenue Allocation must equal Corporate Revenue.")

if issues:
    st.error("Validation failed: " + " ".join(issues))
    st.stop()

stage = stage_profile(business_stage)
corporate_revenue_rupees = corporate_revenue_cr * 10_000_000
allocation_total_rupees = float(market_registry["revenue_allocation_cr"].sum()) * 10_000_000
active_plants = plant_registry[plant_registry["status"].astype(str).str.lower() == "active"].copy()
if active_plants.empty:
    active_plants = plant_registry.copy()
default_plant_id = "PLANT_KOL"
default_matches = active_plants[active_plants["is_default"].astype(str).str.lower() == "yes"]
if not default_matches.empty:
    default_plant_id = str(default_matches.iloc[0].get("plant_id", "PLANT_KOL"))

plant_results = {}
for _, plant in active_plants.iterrows():
    plant_id = str(plant.get("plant_id", "")).strip()
    assigned_markets = market_registry[market_registry["assigned_plant_id"].astype(str) == plant_id]
    plant_results[plant_id] = build_plant_planning(
        plant=plant,
        assigned_markets=assigned_markets,
        product_mix=product_mix,
        channel_mix=channel_mix,
        product_registry=product_registry,
        channel_registry=channel_registry,
        pricing_registry=pricing_registry,
        cost_registry=cost_registry,
        avg_bird_weight=avg_bird_weight,
        working_days=working_days,
        stage_profile=stage,
        live_bird_rate=live_bird_rate,
        yield_pct=yield_pct,
        procurement_drivers=procurement_drivers,
        mortality_pct=mortality_pct,
        processing_loss_pct=processing_loss_pct,
        gt_distributor_margin_pct=gt_distributor_margin_pct,
        packaging_cost_per_kg=packaging_cost,
        transport_cost_per_kg=transport_cost,
        operating_model=operating_model,
        business_stage=business_stage,
        plant_capacity_per_line_mt_day=plant_capacity_per_line_mt_day,
        working_hours_per_shift=working_hours_per_shift,
        max_shifts=max_shifts,
        cold_storage_buffer_days=cold_storage_buffer_days,
        utilization_threshold_pct=utilization_threshold_pct,
    )

plant_options = active_plants["plant_name"].astype(str).tolist()
plant_id_by_name = {str(row.get("plant_name")): str(row.get("plant_id")) for _, row in active_plants.iterrows()}
default_plant_index = 0
for idx, plant_name in enumerate(plant_options):
    if plant_id_by_name.get(plant_name) == default_plant_id:
        default_plant_index = idx
        break
selected_plant_name = st.selectbox("Select Plant", plant_options, index=default_plant_index)
selected_plant_id = plant_id_by_name[selected_plant_name]
selected_plant_result = plant_results[selected_plant_id]
selected_plant_row = active_plants[active_plants["plant_id"].astype(str) == selected_plant_id]
if selected_plant_row.empty:
    selected_plant_row = active_plants.iloc[[0]]
selected_plant_markets = market_registry[market_registry["assigned_plant_id"].astype(str) == selected_plant_id]
if selected_plant_markets.empty:
    selected_plant_markets = market_registry
market_options = [str(city) for city in selected_plant_markets["city"].fillna("N/A")]
selected_market_name = st.selectbox("Select Market for Market-specific Planning", market_options, index=0)
selected_market = selected_plant_markets[selected_plant_markets["city"].astype(str) == selected_market_name].iloc[0]
selected_market_city = str(selected_market.get("city", selected_market_name) or selected_market_name)
selected_plant_city = str(selected_plant_row.iloc[0].get("city", selected_plant_name) or selected_plant_name)
market_revenue_rupees = float(selected_market.get("revenue_allocation_cr", 0.0)) * 10_000_000
selected_market_revenue = market_revenue_rupees
market_distance_km = float(selected_market.get("distance_km", 0.0) or 0.0)
market_growth_stage = selected_market.get("growth_stage", business_stage) or business_stage

log_section_start("calculation_call")
revenue_rupees = market_revenue_rupees
market_results = build_financial_chain(
    product_mix=product_mix,
    channel_mix=channel_mix,
    product_registry=product_registry,
    channel_registry=channel_registry,
    pricing_registry=pricing_registry,
    cost_registry=cost_registry,
    revenue_rupees=revenue_rupees,
    avg_bird_weight=avg_bird_weight,
    working_days=working_days,
    stage_profile=stage,
    market_distance_km=market_distance_km,
    live_bird_rate=live_bird_rate,
    yield_pct=yield_pct,
    procurement_drivers=procurement_drivers,
    mortality_pct=mortality_pct,
    processing_loss_pct=processing_loss_pct,
    gt_distributor_margin_pct=gt_distributor_margin_pct,
    packaging_cost_per_kg=packaging_cost,
    transport_cost_per_kg=transport_cost,
    plant_capacity_per_line_mt_day=plant_capacity_per_line_mt_day,
    working_hours_per_shift=working_hours_per_shift,
    max_shifts=max_shifts,
    cold_storage_buffer_days=cold_storage_buffer_days,
    utilization_threshold_pct=utilization_threshold_pct,
    operating_model=operating_model,
    business_stage=business_stage,
)
results = market_results
log_section_end("calculation_call")
corporate_plant_revenue = sum(result.get("assigned_market_revenue", 0.0) for result in plant_results.values())
corporate_birds_day = sum(result.get("birds_per_day", 0.0) for result in plant_results.values())
corporate_capacity_mt_day = sum(result.get("plant_capacity_output", {}).get("installed_capacity_mt_day", 0.0) for result in plant_results.values())
raw_material_output = results["raw_material_output"]
plant_raw_material_output = selected_plant_result["raw_material_output"]
plant_capacity_output = selected_plant_result["plant_capacity_output"]
manpower_output = selected_plant_result["manpower_output"]
logistics_output = build_logistics_output(
    plant_raw_material_output=plant_raw_material_output,
    market_raw_material_output=raw_material_output,
    product_mix=product_mix,
    market_distance_km=market_distance_km,
    avg_bird_weight=avg_bird_weight,
    working_days=working_days,
    primary_vehicle_capacity_kg=primary_vehicle_capacity_kg,
    primary_trips_per_vehicle_per_day=primary_trips_per_vehicle_per_day,
    average_primary_distance_km=average_primary_distance_km,
    primary_cost_per_km=primary_cost_per_km,
    primary_fixed_cost_per_trip=primary_fixed_cost_per_trip,
    secondary_vehicle_capacity_mt=secondary_vehicle_capacity_mt,
    secondary_trips_per_vehicle_per_day=secondary_trips_per_vehicle_per_day,
    secondary_cost_per_km=secondary_cost_per_km,
    secondary_fixed_cost_per_trip=secondary_fixed_cost_per_trip,
    cold_chain_cost_multiplier=cold_chain_cost_multiplier,
    plant_id=selected_plant_id,
)
distributor_output = build_distributor_output(
    market_revenue=corporate_revenue_rupees,
    product_mix=product_mix,
    fresh_revenue_per_distributor=fresh_revenue_per_distributor,
    frozen_revenue_per_distributor=frozen_revenue_per_distributor,
    rte_revenue_per_distributor=rte_revenue_per_distributor,
    fresh_distributor_enabled=fresh_distributor_enabled,
    shared_frozen_rte_distributor=shared_frozen_rte_distributor,
)
distributor_output = dict(distributor_output or {})
fresh_share = float(product_mix.get("FRESH", 0.0) or 0.0) / 100.0
frozen_share = float(product_mix.get("FROZEN", 0.0) or 0.0) / 100.0
rte_share = float(product_mix.get("RTE", 0.0) or 0.0) / 100.0
fva_share = float(product_mix.get("FVA", 0.0) or 0.0) / 100.0
def _util_pct(revenue_value, capacity_value):
    return (revenue_value / capacity_value * 100.0) if capacity_value > 0 else 0.0
def _capacity_status(utilization_pct):
    return "Additional Partner Required" if utilization_pct > 100 else "Near Capacity" if utilization_pct > 85 else "Healthy"
distributor_output.setdefault("fresh_chilled_revenue", corporate_revenue_rupees * fresh_share)
distributor_output.setdefault("fresh_revenue", distributor_output["fresh_chilled_revenue"])
distributor_output.setdefault("fresh_distributors", max(0, math.ceil(distributor_output["fresh_chilled_revenue"] / max(1.0, fresh_revenue_per_distributor))))
distributor_output.setdefault("fresh_revenue_capacity_per_distributor", float(fresh_revenue_per_distributor))
distributor_output.setdefault("fresh_network_capacity", distributor_output["fresh_distributors"] * distributor_output["fresh_revenue_capacity_per_distributor"])
distributor_output.setdefault("fresh_utilization_pct", _util_pct(distributor_output["fresh_chilled_revenue"], distributor_output["fresh_network_capacity"]))
distributor_output.setdefault("fresh_capacity_status", _capacity_status(distributor_output["fresh_utilization_pct"]))
distributor_output.setdefault("frozen_raw_revenue", corporate_revenue_rupees * frozen_share)
distributor_output.setdefault("rte_revenue", corporate_revenue_rupees * rte_share)
distributor_output.setdefault("fva_revenue", corporate_revenue_rupees * fva_share)
distributor_output.setdefault("fva_distributors", max(0, math.ceil(distributor_output["fva_revenue"] / max(1.0, rte_revenue_per_distributor))))
distributor_output.setdefault("fva_revenue_capacity_per_distributor", float(rte_revenue_per_distributor))
distributor_output.setdefault("fva_network_capacity", distributor_output["fva_distributors"] * distributor_output["fva_revenue_capacity_per_distributor"])
distributor_output.setdefault("fva_utilization_pct", _util_pct(distributor_output["fva_revenue"], distributor_output["fva_network_capacity"]))
distributor_output.setdefault("fva_capacity_status", _capacity_status(distributor_output["fva_utilization_pct"]))
distributor_output.setdefault("total_product_revenue", distributor_output["fresh_chilled_revenue"] + distributor_output["frozen_raw_revenue"] + distributor_output["rte_revenue"] + distributor_output["fva_revenue"])
distributor_output.setdefault("product_revenue_variance", distributor_output["total_product_revenue"] - corporate_revenue_rupees)
distributor_output.setdefault("product_revenue_reconciled", abs(distributor_output["product_revenue_variance"]) <= 0.01)
distributor_output.setdefault("shared_frozen_rte_revenue_served", distributor_output["frozen_raw_revenue"] + distributor_output["rte_revenue"])
distributor_output.setdefault("shared_network_is_consolidated_view", True)
channel_sales_output = build_channel_sales_output(
    market_revenue=market_revenue_rupees,
    channel_mix=channel_mix,
    working_days=working_days,
    gt_revenue_per_sales_executive=gt_revenue_per_sales_executive,
    gt_outlets_per_sales_executive=gt_outlets_per_sales_executive,
    gt_sales_executives_per_asm=gt_sales_executives_per_asm,
    mt_revenue_per_kam=mt_revenue_per_kam,
    quick_commerce_revenue_per_kam=quick_commerce_revenue_per_kam,
    horeca_revenue_per_sales_executive=horeca_revenue_per_sales_executive,
    institution_revenue_per_account_manager=institution_revenue_per_account_manager,
    calls_per_sales_executive_day=calls_per_sales_executive_day,
    distributor_output=distributor_output,
    business_stage=business_stage,
    procurement_drivers=procurement_drivers,
    operating_model=operating_model,
    live_bird_rate=live_bird_rate,
    horeca_revenue_mode=horeca_revenue_mode,
    horeca_contract_rate_per_kg=horeca_contract_rate_per_kg,
    horeca_contract_volume_kg_month=horeca_contract_volume_kg_month,
    horeca_active_accounts=horeca_active_accounts,
    horeca_credit_days=horeca_credit_days,
    institutional_revenue_mode=institutional_revenue_mode,
    institutional_contract_rate_per_kg=institutional_contract_rate_per_kg,
    institutional_awarded_volume_kg_month=institutional_awarded_volume_kg_month,
    institutional_contract_name=institutional_contract_name,
    institutional_contract_start_date=str(institutional_contract_start_date),
    institutional_contract_end_date=str(institutional_contract_end_date),
    revenue_mode="PLANNING",
)
channel_sales_output = dict(channel_sales_output)
channel_sales_output.setdefault("selected_market_revenue", selected_market_revenue)
channel_sales_output.setdefault("contract_revenue_total", float(channel_sales_output.get("horeca", {}).get("revenue", 0.0) or 0.0) + float(channel_sales_output.get("institution", {}).get("revenue", 0.0) or 0.0))
channel_sales_output.setdefault("residual_revenue", max(0.0, selected_market_revenue - float(channel_sales_output.get("contract_revenue_total", 0.0) or 0.0)))
channel_sales_output.setdefault("gt_revenue", float(channel_sales_output.get("general_trade", {}).get("revenue", 0.0) or 0.0))
channel_sales_output.setdefault("mt_revenue", float(channel_sales_output.get("modern_trade", {}).get("revenue", 0.0) or 0.0))
channel_sales_output.setdefault("qcom_revenue", float(channel_sales_output.get("quick_commerce", {}).get("revenue", 0.0) or 0.0))
channel_sales_output.setdefault("ecommerce_revenue", float(channel_sales_output.get("ecommerce", {}).get("revenue", 0.0) or 0.0))
channel_sales_output.setdefault("exports_revenue", float(channel_sales_output.get("exports", {}).get("revenue", 0.0) or 0.0))
channel_sales_output.setdefault("horeca_revenue", float(channel_sales_output.get("horeca", {}).get("revenue", 0.0) or 0.0))
channel_sales_output.setdefault("institutional_government_revenue", float(channel_sales_output.get("institution", {}).get("revenue", 0.0) or 0.0))
channel_sales_output.setdefault(
    "total_commercial_revenue",
    float(channel_sales_output.get("gt_revenue", 0.0) or 0.0)
    + float(channel_sales_output.get("mt_revenue", 0.0) or 0.0)
    + float(channel_sales_output.get("qcom_revenue", 0.0) or 0.0)
    + float(channel_sales_output.get("ecommerce_revenue", 0.0) or 0.0)
    + float(channel_sales_output.get("exports_revenue", 0.0) or 0.0)
    + float(channel_sales_output.get("horeca_revenue", 0.0) or 0.0)
    + float(channel_sales_output.get("institutional_government_revenue", 0.0) or 0.0),
)
channel_sales_output.setdefault("reconciliation_gap", selected_market_revenue - float(channel_sales_output.get("total_commercial_revenue", 0.0) or 0.0))
selected_plant_market_count = len(selected_plant_markets)
total_active_accounts_supported = (
    int(channel_sales_output["general_trade"].get("outlets", 0) or 0)
    + int(channel_sales_output["modern_trade"].get("accounts", 0) or 0)
    + int(channel_sales_output["quick_commerce"].get("dark_stores", 0) or 0)
    + int(channel_sales_output["horeca"].get("accounts", 0) or 0)
    + int(channel_sales_output["institution"].get("accounts", 0) or 0)
)
total_commercial_revenue = float(channel_sales_output.get("total_commercial_revenue", selected_market_revenue) or selected_market_revenue)
selected_market_revenue_output = float(channel_sales_output.get("selected_market_revenue", selected_market_revenue) or selected_market_revenue)
commercial_reconciliation_gap = float(channel_sales_output.get("reconciliation_gap", selected_market_revenue_output - total_commercial_revenue) or 0.0)
if abs(total_commercial_revenue - selected_market_revenue_output) > 1.0:
    st.warning("Total Commercial Revenue is not reconciled to Selected Market Revenue. Review contract commitments and residual channel allocation.")
sales_coordinator_required = bool(
    total_commercial_revenue > 100_000_000.0
    or total_active_accounts_supported >= 50
    or selected_plant_market_count > 1
)
sales_coordinator_hc = 1 if sales_coordinator_required else 0
channel_sales_output["sales_coordinator_mis"] = sales_coordinator_hc
channel_sales_output["sales_coordinator"] = sales_coordinator_hc
channel_sales_output["head_sales_hc"] = int(channel_sales_output.get("sales_manager", 0) or 0)
channel_sales_output["general_trade_hc"] = int(channel_sales_output.get("gt_sales_executives", 0) or 0)
channel_sales_output["modern_trade_hc"] = int(channel_sales_output.get("mt_kam", 0) or 0)
channel_sales_output["quick_commerce_hc"] = int(channel_sales_output.get("qcom_kam", 0) or 0)
channel_sales_output["e_commerce_hc"] = int(channel_sales_output.get("ecommerce_kam", 0) or 0)
channel_sales_output["horeca_hc"] = int(channel_sales_output.get("horeca_sales_hc", 0) or 0)
channel_sales_output["institutional_hc"] = int(channel_sales_output.get("institution_government_manager", 0) or 0)
channel_sales_output["export_hc"] = int(channel_sales_output.get("exports_manager", 0) or 0)
commercial_hc_sum = (
    channel_sales_output["head_sales_hc"]
    + channel_sales_output["general_trade_hc"]
    + channel_sales_output["modern_trade_hc"]
    + channel_sales_output["quick_commerce_hc"]
    + channel_sales_output["e_commerce_hc"]
    + channel_sales_output["horeca_hc"]
    + channel_sales_output["institutional_hc"]
    + channel_sales_output["export_hc"]
)
commercial_hc_reported = int(channel_sales_output.get("total_commercial_hc", commercial_hc_sum) or commercial_hc_sum)
commercial_hc_variance = commercial_hc_reported - commercial_hc_sum
commercial_hc_reconciled = commercial_hc_variance == 0
channel_sales_output["commercial_hc_sum"] = commercial_hc_sum
channel_sales_output["commercial_hc_reported"] = commercial_hc_reported
channel_sales_output["commercial_hc_variance"] = commercial_hc_variance
channel_sales_output["commercial_hc_reconciled"] = commercial_hc_reconciled
channel_sales_output["total_commercial_hc"] = commercial_hc_sum
channel_sales_output["total_sales_hc"] = commercial_hc_sum
channel_sales_output["total_commercial_revenue"] = total_commercial_revenue
channel_sales_output["reconciliation_gap"] = commercial_reconciliation_gap
channel_sales_output["selected_market_revenue"] = selected_market_revenue_output
channel_sales_output["total_markets_supported"] = selected_plant_market_count
channel_sales_output["total_active_accounts_supported"] = total_active_accounts_supported
channel_sales_output["sales_coordinator_required"] = sales_coordinator_required
validate_required_keys(channel_sales_output, [
    "selected_market_revenue",
    "total_commercial_revenue",
    "general_trade",
    "horeca",
    "institutional_government",
], "Channel Sales")
validate_required_keys(channel_sales_output["general_trade"], [
    "required_distributors",
    "active_distributors",
    "target_outlets",
    "outlets_per_distributor",
    "coverage_gap_distributors",
    "coverage_status",
    "sales_executives",
    "revenue_per_sales_executive",
    "beats",
    "calls_per_day",
    "supported_revenue",
    "revenue_at_risk",
], "General Trade")
validate_required_keys(channel_sales_output["horeca"], [
    "planned_revenue",
    "revenue",
    "live_bird_rate",
    "average_live_bird_weight_kg",
    "dressed_output_kg",
    "dressed_yield_pct",
    "raw_material_cost_per_kg",
    "processing_cost_per_kg",
    "packaging_cost_per_kg",
    "cold_chain_logistics_cost_per_kg",
    "factory_overhead_per_kg",
    "total_cost_per_kg",
    "target_margin_pct",
    "recommended_selling_price_per_kg",
    "contract_rate_per_kg",
    "required_volume_kg_month",
    "active_accounts",
    "required_hc",
    "credit_days",
], "HoReCa")
validate_required_keys(channel_sales_output["institutional_government"], [
    "planned_revenue",
    "revenue",
    "product",
    "pack_size_kg",
    "pack_type",
    "mrp",
    "live_bird_rate",
    "dressed_yield_pct",
    "raw_material_cost_per_kg",
    "processing_cost_per_kg",
    "packaging_cost_per_kg",
    "cold_chain_logistics_cost_per_kg",
    "factory_overhead_per_kg",
    "total_cost_per_kg",
    "target_margin_pct",
    "recommended_selling_price_per_kg",
    "contract_rate_per_kg",
    "contract_value_per_pack",
    "required_volume_kg_month",
    "required_packs_month",
    "active_tenders_contracts",
    "required_hc",
    "contract_name",
    "contract_start_date",
    "contract_end_date",
], "Institutional / Government")
planned_channel_volume_kg = {}
channel_volume_output = results.get("channel_product_volume_output", {}).get("channels", {})
for channel_label, revenue_key in {
    "GT": "general_trade",
    "MT": "modern_trade",
    "QCom": "quick_commerce",
    "E-commerce": "ecommerce",
    "HoReCa": "horeca",
    "Institutional / Government": "institution",
    "Exports": "exports",
}.items():
    planned_channel_volume_kg[channel_label] = float(channel_volume_output.get(revenue_key, {}).get("total_kg_month", 0.0) or 0.0)

gt_planned_revenue = float(channel_sales_output.get("general_trade", {}).get("revenue", 0.0) or 0.0)
gt_volume_kg = planned_channel_volume_kg.get("GT", 0.0)
gt_pricing_basis = "Distributor selling value"
gt_distributor_margin_value = gt_planned_revenue * (gt_distributor_margin_pct / 100.0)
gt_company_net_realization = max(0.0, gt_planned_revenue - gt_distributor_margin_value)
gt_company_net_realization_per_kg = gt_company_net_realization / max(1.0, gt_volume_kg)
total_variable_cost_per_kg = results.get("total_direct_variable_spend_month", 0.0) / max(1.0, results.get("finished_goods_kg", 1.0))
gt_variable_cost = gt_volume_kg * total_variable_cost_per_kg
gt_gross_contribution = gt_company_net_realization - gt_variable_cost
cost_waterfall = results.get("cost_waterfall", {})

channel_sales_output["general_trade"].update({
    "gt_distributor_margin_pct": gt_distributor_margin_pct,
    "gt_distributor_margin_value": gt_distributor_margin_value,
    "gt_pricing_basis": gt_pricing_basis,
    "gt_company_net_realization": gt_company_net_realization,
    "gt_company_net_realization_per_kg": gt_company_net_realization_per_kg,
    "gt_volume_kg": gt_volume_kg,
    "gt_variable_cost": gt_variable_cost,
    "gt_gross_contribution": gt_gross_contribution,
})

with st.sidebar.expander("G. Order Scenario Testing", expanded=False):
    order_scenario_mode = st.selectbox("Order Scenario Mode", ["No Scenario", "Channel Achievement %", "Manual Order Volume"], index=0)
    channel_achievement_pct = {}
    manual_order_volume_kg = {}
    releasable_cold_inventory_mt = 0.0
    if order_scenario_mode == "Channel Achievement %":
        for channel_label in planned_channel_volume_kg:
            channel_achievement_pct[channel_label] = st.number_input(f"{channel_label} Achievement %", min_value=float(0.0), max_value=float(200.0), value=float(100.0), step=float(5.0), key=f"order_achievement_{channel_label}")
        releasable_cold_inventory_mt = st.number_input("Releasable Cold Inventory (MT)", min_value=float(0.0), value=float(0.0), step=float(0.5), key="order_releasable_cold_inventory_mt_pct")
    elif order_scenario_mode == "Manual Order Volume":
        for channel_label, planned_volume in planned_channel_volume_kg.items():
            planned_volume_day = planned_volume / max(1, working_days)
            manual_order_volume_kg[channel_label] = st.number_input(f"{channel_label} Scenario Orders kg/day", min_value=float(0.0), value=float(planned_volume_day), step=float(100.0), key=f"manual_order_{channel_label}")
        releasable_cold_inventory_mt = st.number_input("Releasable Cold Inventory (MT)", min_value=float(0.0), value=float(0.0), step=float(0.5), key="order_releasable_cold_inventory_mt_manual")

order_capacity_intelligence = build_order_capacity_intelligence(
    raw_material_output=raw_material_output,
    plant_capacity_output=plant_capacity_output,
    channel_sales_output=channel_sales_output,
    order_registry=order_registry,
    plant_id=selected_plant_id,
    operating_mode="PLANNING",
    available_finished_goods_inventory_kg=0.0,
    committed_production_kg=0.0,
    persistence_days=1,
    average_bird_weight_kg=avg_bird_weight,
    scenario_mode=order_scenario_mode,
    channel_achievement_pct=channel_achievement_pct,
    manual_order_volume_kg=manual_order_volume_kg,
    releasable_cold_inventory_mt=releasable_cold_inventory_mt,
    current_marketing_spend=results.get("marketing_cost", 0.0),
    gross_contribution_pct=(results.get("gross_contribution", 0.0) / revenue_rupees if revenue_rupees else 0.0),
)
manpower_output = align_manpower_sales(manpower_output, channel_sales_output)
corporate_manpower = manpower_output["total_employees"]
manpower_role_keys = [
    "production",
    "warehouse",
    "sales",
    "marketing",
    "finance",
    "hr",
    "admin",
    "qa_food_safety",
    "procurement",
]
manpower_role_total = sum(int(manpower_output.get(key, 0) or 0) for key in manpower_role_keys)
if manpower_role_total != manpower_output["total_employees"]:
    st.warning("Corporate Manpower total was out of sync with the displayed manpower roles. Using final consolidated manpower total as source of truth.")
if corporate_manpower != manpower_output["total_employees"]:
    st.warning("Corporate Manpower differed from the final Manpower Planning total. Using final consolidated manpower total as source of truth.")
    corporate_manpower = manpower_output["total_employees"]
net_yield = results.get("weighted_yield", 0.0)
finished_goods_kg = results.get("finished_goods_kg", 0.0)
live_weight_kg = results.get("live_bird_kg", 0.0)
birds_required = results.get("birds_required", 0.0)
birds_per_day = results.get("birds_per_day", 0.0)
traders_required = max(1, math.ceil(birds_required / avg_trader_capacity)) if avg_trader_capacity else 1
farms_required = max(1, math.ceil(birds_required / avg_farm_capacity)) if avg_farm_capacity else 1
production_lines = plant_capacity_output["production_lines_required"]
employees = manpower_output["total_employees"]
warehouse_need = results["warehouse_need"]
distribution_centre_need = results["distribution_centre_need"]
live_bird_procurement_spend = results.get("live_bird_procurement_spend_month", 0.0)
processing_spend = results.get("processing_spend_month", results.get("processing_expense", 0.0))
packaging_spend = results.get("packaging_spend_month", 0.0)
transport_spend = results.get("transport_spend_month", 0.0)
other_direct_variable_spend = results.get("other_direct_variable_spend_month", results.get("other_direct_variable_spend", 0.0))
procurement_spend = results.get("total_direct_variable_spend_month", 0.0)
direct_variable_component_sum = (
    float(live_bird_procurement_spend)
    + float(processing_spend)
    + float(packaging_spend)
    + float(transport_spend)
    + float(other_direct_variable_spend)
)
direct_variable_spend_variance = float(procurement_spend) - direct_variable_component_sum
direct_variable_spend_reconciled = abs(direct_variable_spend_variance) <= 1.0
gross_contribution = results.get("gross_contribution", 0.0) - gt_distributor_margin_value
marketing_spend = results.get("marketing_cost", 0.0)
warehouse_opex = results.get("warehouse_opex", 0.0)
ebitda = results.get("ebitda", 0.0) - gt_distributor_margin_value
pat = ebitda * 0.75
working_capital = results["working_capital"]
capex = production_lines * stage["capex_per_line"]


def render_corporate_manpower_drilldown():
    st.write("This is the total workforce required for the current corporate and plant plan.")
    render_display_dataframe(st, "corporate_manpower_drilldown", pd.DataFrame([
        {"Team": "Production", "Headcount": manpower_output["production"]},
        {"Team": "Warehouse + Cold Room", "Headcount": manpower_output["warehouse"]},
        {"Team": "Sales", "Headcount": manpower_output["sales"]},
        {"Team": "Marketing", "Headcount": manpower_output["marketing"]},
        {"Team": "Finance", "Headcount": manpower_output["finance"]},
        {"Team": "HR", "Headcount": manpower_output["hr"]},
        {"Team": "Admin", "Headcount": manpower_output["admin"]},
        {"Team": "QA / Food Safety", "Headcount": manpower_output["qa_food_safety"]},
        {"Team": "Procurement", "Headcount": manpower_output["procurement"]},
        {"Team": "Total Employees", "Headcount": manpower_output["total_employees"]},
    ]), hide_index=True, width="stretch")
    st.write("If multiple plants are added later:")
    st.write("Corporate Manpower = sum of plant manpower minus shared corporate manpower and shared roles already consolidated.")


def show_corporate_manpower_drilldown():
    if hasattr(st, "dialog"):
        @st.dialog("Corporate Manpower")
        def _corporate_manpower_dialog():
            render_corporate_manpower_drilldown()

        _corporate_manpower_dialog()
    else:
        with st.expander("Corporate Manpower", expanded=True):
            render_corporate_manpower_drilldown()


def render_procurement_driver_drilldown():
    waterfall = results.get("cost_waterfall", {})
    impact_map = results.get("procurement_driver_impact_map", {})
    st.write("Input assumptions")
    render_display_dataframe(st, "procurement_driver_assumptions", pd.DataFrame([
        {"Driver": "Live Bird Rate", "Value": fmt_rate_per_kg(waterfall.get("live_bird_base_rate_per_kg", live_bird_rate))},
        {"Driver": "Dressed Yield", "Value": f"{waterfall.get('dressed_yield_pct', yield_pct):,.1f}%"},
        {"Driver": "Mortality", "Value": f"{waterfall.get('mortality_pct', mortality_pct):,.1f}%"},
        {"Driver": "Processing Loss", "Value": f"{waterfall.get('processing_loss_pct', processing_loss_pct):,.1f}%"},
        {"Driver": "Effective Finished-Goods Yield", "Value": f"{waterfall.get('effective_finished_goods_yield_pct', results.get('weighted_yield', 0.0) * 100.0):,.1f}%"},
        {"Driver": "Packaging Cost", "Value": f"{fmt_currency_plain(waterfall.get('packaging_cost_per_kg', packaging_cost), 2)}/kg"},
        {"Driver": "Transport Cost", "Value": f"{fmt_currency_plain(waterfall.get('transport_cost_per_kg', transport_cost), 2)}/kg"},
        {"Driver": "Sourcing Assumption", "Value": waterfall.get("sourcing_assumption", "MVP sourcing route assumption")},
    ]), hide_index=True, width="stretch")
    st.write("Quantity impact")
    render_display_dataframe(st, "procurement_quantity_impact", pd.DataFrame([
        {"Metric": "Finished goods", "Value": f"{finished_goods_kg:,.0f} kg/month"},
        {"Metric": "Net birds required before mortality", "Value": f"{results.get('net_birds_required', 0.0):,.0f}"},
        {"Metric": "Gross birds required after mortality", "Value": f"{birds_required:,.0f}"},
        {"Metric": "Live weight required", "Value": f"{live_weight_kg:,.0f} kg/month"},
        {"Metric": "Birds/day", "Value": f"{birds_per_day:,.0f}"},
    ]), hide_index=True, width="stretch")
    st.write("Cost impact")
    render_display_dataframe(st, "procurement_cost_impact", pd.DataFrame([
        {"Metric": "Live Bird Rate", "Value": f"{fmt_currency_plain(waterfall.get('live_bird_rate_per_kg', live_bird_rate), 2)}/kg"},
        {"Metric": "Raw-material cost/kg", "Value": f"{fmt_currency_plain(waterfall.get('raw_material_cost_per_finished_kg', 0.0), 2)}/kg"},
        {"Metric": "Packaging cost/kg", "Value": f"{fmt_currency_plain(waterfall.get('packaging_cost_per_kg', 0.0), 2)}/kg"},
        {"Metric": "Transport cost/kg", "Value": f"{fmt_currency_plain(waterfall.get('transport_cost_per_kg', 0.0), 2)}/kg"},
        {"Metric": "Ex-factory cost/kg", "Value": f"{fmt_currency_plain(waterfall.get('total_ex_factory_cost_per_kg', 0.0), 2)}/kg"},
        {"Metric": "Delivered cost/kg", "Value": f"{fmt_currency_plain(waterfall.get('total_delivered_cost_per_kg', 0.0), 2)}/kg"},
        {"Metric": "Recommended delivered price/kg", "Value": f"{fmt_currency_plain(waterfall.get('recommended_delivered_price_per_kg', 0.0), 0)}/kg"},
    ]), hide_index=True, width="stretch")
    st.write("KPI impact")
    render_display_dataframe(st, "procurement_kpi_impact", pd.DataFrame([
        {"KPI": "Live Bird Procurement Spend", "Value": fmt_currency(live_bird_procurement_spend)},
        {"KPI": "Processing Spend", "Value": fmt_currency(processing_spend)},
        {"KPI": "Packaging Spend", "Value": fmt_currency(packaging_spend)},
        {"KPI": "Transport Spend", "Value": fmt_currency(transport_spend)},
        {"KPI": "Other Direct Variable Spend", "Value": fmt_currency(other_direct_variable_spend)},
        {"KPI": "Component Sum", "Value": fmt_currency(direct_variable_component_sum)},
        {"KPI": "Total Direct Variable Spend", "Value": fmt_currency(procurement_spend)},
        {"KPI": "Component Variance vs Total", "Value": fmt_currency(direct_variable_spend_variance)},
        {"KPI": "Direct Variable Reconciliation", "Value": "Reconciled" if direct_variable_spend_reconciled else "Not Reconciled"},
        {"KPI": "Gross Contribution", "Value": fmt_currency(gross_contribution)},
        {"KPI": "EBITDA", "Value": fmt_currency(ebitda)},
        {"KPI": "PAT", "Value": fmt_currency(pat)},
    ]), hide_index=True, width="stretch")
    st.write("Driver impact map")
    render_display_dataframe(st, "procurement_driver_impact_map", pd.DataFrame([
        {"Driver": driver, "Affected KPIs": ", ".join(affected)}
        for driver, affected in impact_map.items()
    ]), hide_index=True, width="stretch")
    st.markdown("### Formula & Assumptions")
    effective_yield_pct_value = float(waterfall.get("effective_finished_goods_yield_pct", results.get("weighted_yield", 0.0) * 100.0) or 0.0)
    dressed_yield_pct_value = float(waterfall.get("dressed_yield_pct", yield_pct) or 0.0)
    processing_loss_pct_value = float(waterfall.get("processing_loss_pct", processing_loss_pct) or 0.0)
    mortality_pct_value = float(waterfall.get("mortality_pct", mortality_pct) or 0.0)
    live_bird_rate_value = float(waterfall.get("live_bird_rate_per_kg", live_bird_rate) or 0.0)
    raw_material_cost_per_kg_value = float(waterfall.get("raw_material_cost_per_finished_kg", 0.0) or 0.0)
    ex_factory_cost_per_kg_value = float(waterfall.get("total_ex_factory_cost_per_kg", 0.0) or 0.0)
    delivered_cost_per_kg_value = float(waterfall.get("total_delivered_cost_per_kg", 0.0) or 0.0)
    recommended_price_per_kg_value = float(waterfall.get("recommended_delivered_price_per_kg", 0.0) or 0.0)
    processing_cost_per_kg_value = float(waterfall.get("processing_cost_per_kg", 0.0) or 0.0)
    packaging_cost_per_kg_value = float(waterfall.get("packaging_cost_per_kg", packaging_cost) or 0.0)
    transport_cost_per_kg_value = float(waterfall.get("transport_cost_per_kg", transport_cost) or 0.0)
    target_margin_pct_value = float(waterfall.get("target_margin_pct", 0.0) or 0.0)
    live_weight_required_month = float(live_weight_kg or 0.0)
    gross_birds_required_month = float(birds_required or 0.0)
    net_birds_required_month = float(results.get("net_birds_required", 0.0) or 0.0)
    finished_goods_kg_month = float(finished_goods_kg or 0.0)

    render_formula_section("effective_yield", build_formula_rows(
        "effective_yield",
        current_value=f"{effective_yield_pct_value:,.1f}%",
        unit="%",
        status="Reconciled",
        worked_calculation=f"{dressed_yield_pct_value:,.1f}% × (1 − {processing_loss_pct_value:,.1f}%) = {effective_yield_pct_value:,.1f}%",
        assumptions="Planning yield converts live weight to dressed output. Processing loss reduces dressed output to saleable finished goods. Mortality is not part of finished-goods yield.",
    ))
    render_formula_section("birds_per_day", build_formula_rows(
        "birds_per_day",
        current_value=f"{birds_per_day:,.0f} birds/day",
        unit="birds/day",
        status="Reconciled",
        worked_calculation=(
            f"{finished_goods_kg_month:,.0f} kg/month ÷ {effective_yield_pct_value / 100.0:,.3f} = {live_weight_required_month:,.0f} kg/month live weight\n"
            f"{live_weight_required_month:,.0f} kg/month ÷ {avg_bird_weight:,.1f} kg = {net_birds_required_month:,.0f} net birds/month\n"
            f"Gross birds required after {mortality_pct_value:,.1f}% mortality = {gross_birds_required_month:,.0f} birds/month\n"
            f"{gross_birds_required_month:,.0f} birds/month ÷ {working_days:,.0f} working days = {birds_per_day:,.0f} birds/day"
        ),
        assumptions="Finished goods volume is monthly. Average bird weight is the current planning input. Mortality is applied after conversion to gross birds. Working days are the current planning days.",
    ))
    render_formula_section("live_bird_procurement_spend", build_formula_rows(
        "live_bird_procurement_spend",
        current_value=fmt_currency(live_bird_procurement_spend),
        unit="₹/month",
        status="Reconciled",
        worked_calculation=f"{live_weight_required_month:,.0f} kg/month × {fmt_rate_per_kg(live_bird_rate_value)} = {fmt_currency(live_bird_procurement_spend)}",
        assumptions="Live Bird Rate is the final all-inclusive procurement or lifting rate. Live weight requirement already reflects yield and mortality logic.",
        related_kpis="Raw Material Cost/kg, Birds/day, Traders Required, Farms Required",
    ))
    render_formula_section("raw_material_cost_per_kg", build_formula_rows(
        "raw_material_cost_per_kg",
        current_value=f"{fmt_currency_plain(raw_material_cost_per_kg_value, 2)}/kg",
        unit="₹/kg finished goods",
        status="Reconciled",
        worked_calculation=(
            f"{fmt_currency(live_bird_procurement_spend)} ÷ {finished_goods_kg_month:,.0f} kg = {fmt_currency_plain(raw_material_cost_per_kg_value, 2)}/kg\n"
            f"Equivalent: {fmt_rate_per_kg(live_bird_rate_value)} × {live_weight_required_month:,.0f} kg ÷ {finished_goods_kg_month:,.0f} kg"
        ),
        assumptions="Live Bird Procurement Spend already reflects the gross bird requirement, so mortality is not counted again here.",
    ))
    render_formula_section("packaging_spend", build_formula_rows(
        "packaging_spend",
        current_value=fmt_currency(packaging_spend),
        unit="₹/month",
        status="Reconciled",
        worked_calculation=f"{finished_goods_kg_month:,.0f} kg/month × {fmt_currency_plain(packaging_cost_per_kg_value, 2)}/kg = {fmt_currency(packaging_spend)}",
        assumptions="Packaging cost is a per-kg direct variable cost. It changes profitability but does not change birds/day.",
    ))
    render_formula_section("processing_spend", build_formula_rows(
        "processing_spend",
        current_value=fmt_currency(processing_spend),
        unit="₹/month",
        status="Reconciled",
        worked_calculation=f"{finished_goods_kg_month:,.0f} kg/month × {fmt_currency_plain(processing_cost_per_kg_value, 2)}/kg = {fmt_currency(processing_spend)}",
        assumptions="Processing cost is a per-kg direct variable cost from the governed engine waterfall.",
    ))
    render_formula_section("transport_spend", build_formula_rows(
        "transport_spend",
        current_value=fmt_currency(transport_spend),
        unit="₹/month",
        status="Reconciled",
        worked_calculation=f"{finished_goods_kg_month:,.0f} kg/month × {fmt_currency_plain(transport_cost_per_kg_value, 2)}/kg = {fmt_currency(transport_spend)}",
        assumptions="Transport cost is a per-kg direct variable cost. It affects delivered cost, gross contribution, EBITDA and PAT, but not procurement quantity.",
    ))
    render_formula_section("total_direct_variable_spend", build_formula_rows(
        "total_direct_variable_spend",
        current_value=fmt_currency(procurement_spend),
        unit="₹/month",
        status="Reconciled" if direct_variable_spend_reconciled else "Not Reconciled",
        worked_calculation=(
            f"{fmt_currency(live_bird_procurement_spend)} + {fmt_currency(processing_spend)} + {fmt_currency(packaging_spend)} + {fmt_currency(transport_spend)} + {fmt_currency(other_direct_variable_spend)} = {fmt_currency(direct_variable_component_sum)}\n"
            f"Component Sum {fmt_currency(direct_variable_component_sum)} vs Reported Total {fmt_currency(procurement_spend)} (Variance {fmt_currency(direct_variable_spend_variance)})"
        ),
        assumptions="Only governed direct-variable components are included. No hidden balancing amount is applied.",
        extra_rows=[
            {"Item": "Live Bird Procurement Spend", "Value": fmt_currency(live_bird_procurement_spend)},
            {"Item": "Processing Spend", "Value": fmt_currency(processing_spend)},
            {"Item": "Packaging Spend", "Value": fmt_currency(packaging_spend)},
            {"Item": "Transport Spend", "Value": fmt_currency(transport_spend)},
            {"Item": "Other Direct Variable Spend", "Value": fmt_currency(other_direct_variable_spend)},
            {"Item": "Component Sum", "Value": fmt_currency(direct_variable_component_sum)},
            {"Item": "Reported Total Direct Variable Spend", "Value": fmt_currency(procurement_spend)},
            {"Item": "Variance", "Value": fmt_currency(direct_variable_spend_variance)},
            {"Item": "Reconciliation Status", "Value": "Reconciled" if direct_variable_spend_reconciled else "Not Reconciled"},
        ],
        related_kpis="Gross Contribution, EBITDA, PAT",
    ))
    render_formula_section("ex_factory_cost_per_kg", build_formula_rows(
        "ex_factory_cost_per_kg",
        current_value=f"{fmt_currency_plain(ex_factory_cost_per_kg_value, 2)}/kg",
        unit="₹/kg",
        status="Reconciled",
        worked_calculation=(
            f"{fmt_currency_plain(raw_material_cost_per_kg_value, 2)}/kg + {fmt_currency_plain(processing_cost_per_kg_value, 2)}/kg + {fmt_currency_plain(packaging_cost_per_kg_value, 2)}/kg + {fmt_currency_plain(float(waterfall.get('factory_overhead_per_kg', 0.0) or 0.0), 2)}/kg = {fmt_currency_plain(ex_factory_cost_per_kg_value, 2)}/kg"
        ),
        assumptions="Uses the canonical engine waterfall components only. Fixed opex stays below contribution.",
    ))
    render_formula_section("delivered_cost_per_kg", build_formula_rows(
        "delivered_cost_per_kg",
        current_value=f"{fmt_currency_plain(delivered_cost_per_kg_value, 2)}/kg",
        unit="₹/kg",
        status="Reconciled",
        worked_calculation=f"{fmt_currency_plain(ex_factory_cost_per_kg_value, 2)}/kg + {fmt_currency_plain(transport_cost_per_kg_value, 2)}/kg = {fmt_currency_plain(delivered_cost_per_kg_value, 2)}/kg",
        assumptions="Delivered cost adds outbound transport to the ex-factory stack.",
    ))
    render_formula_section("recommended_delivered_price_per_kg", build_formula_rows(
        "recommended_delivered_price_per_kg",
        current_value=f"{fmt_currency_plain(recommended_price_per_kg_value, 2)}/kg",
        unit="₹/kg",
        status="Reconciled",
        worked_calculation=f"{fmt_currency_plain(delivered_cost_per_kg_value, 2)}/kg ÷ (1 − {target_margin_pct_value:,.1f}%) = {fmt_currency_plain(recommended_price_per_kg_value, 2)}/kg",
        assumptions="Margin convention is used, not markup. Target margin comes from the current cost registry or assumption input.",
    ))
    render_formula_section("gross_contribution", build_formula_rows(
        "gross_contribution",
        current_value=fmt_currency(gross_contribution),
        unit="₹/month",
        status="Reconciled",
        worked_calculation=(
            f"Revenue {fmt_currency(revenue_rupees)} − Total Direct Variable Spend {fmt_currency(procurement_spend)} = Engine Gross Contribution {fmt_currency(results.get('gross_contribution', 0.0))}\n"
            f"Engine Gross Contribution {fmt_currency(results.get('gross_contribution', 0.0))} − GT Distributor Margin {fmt_currency(gt_distributor_margin_value)} = Displayed Gross Contribution {fmt_currency(gross_contribution)}"
        ),
        assumptions="Direct variable spend includes live bird procurement, processing, packaging and transport. Fixed OPEX is below contribution.",
        extra_rows=[
            {"Item": "Direct Variable Breakdown", "Value": f"Live bird procurement {fmt_currency(live_bird_procurement_spend)}; processing {fmt_currency(processing_spend)}; packaging {fmt_currency(packaging_spend)}; transport {fmt_currency(transport_spend)}; other {fmt_currency(other_direct_variable_spend)}"},
            {"Item": "GT Distributor Margin Value", "Value": fmt_currency(gt_distributor_margin_value)},
        ],
    ))
    render_formula_section("ebitda", build_formula_rows(
        "ebitda",
        current_value=fmt_currency(ebitda),
        unit="₹/month",
        status="Reconciled",
        worked_calculation=f"Engine EBITDA {fmt_currency(results.get('ebitda', 0.0))} − GT Distributor Margin {fmt_currency(gt_distributor_margin_value)} = Displayed EBITDA {fmt_currency(ebitda)}",
        assumptions="The page-level corporate summary applies a GT distributor margin deduction on top of the engine output before displaying EBITDA.",
        extra_rows=[
            {"Item": "Marketing Spend", "Value": fmt_currency(marketing_spend)},
            {"Item": "Warehouse Opex", "Value": fmt_currency(warehouse_opex)},
        ],
    ))
    render_formula_section("pat", build_formula_rows(
        "pat",
        current_value=fmt_currency(pat),
        unit="₹/month",
        status="Reconciled",
        worked_calculation=f"Displayed EBITDA {fmt_currency(ebitda)} × 75% = {fmt_currency(pat)}",
        assumptions="Tax factor is the current simplified page model. The page-level corporate summary applies the GT distributor margin deduction before PAT.",
        extra_rows=[
            {"Item": "Tax Factor", "Value": "75% of EBITDA"},
        ],
    ))


def show_procurement_driver_drilldown():
    if hasattr(st, "dialog"):
        @st.dialog("Procurement Driver Impact")
        def _procurement_dialog():
            render_procurement_driver_drilldown()

        _procurement_dialog()
    else:
        with st.expander("Procurement Driver Impact", expanded=True):
            render_procurement_driver_drilldown()


def render_traders_required_drilldown():
    primary_logistics = logistics_output["primary"]
    total_network_capacity = float(avg_trader_capacity * traders_required)
    supply_coverage_pct = (total_network_capacity / max(1.0, float(birds_required))) * 100.0 if birds_required else 0.0
    capacity_utilization_pct = (float(birds_required) / max(1.0, total_network_capacity)) * 100.0 if total_network_capacity else 0.0
    capacity_gap_surplus = total_network_capacity - float(birds_required)
    procurement_risk_signal = "Capacity Modelled" if capacity_gap_surplus >= 0 else "Additional Trader Capacity Required"
    st.write("This network represents upstream live-bird sourcing partners supplying the plant. It is separate from downstream product distributors.")
    render_display_dataframe(st, "traders_required_summary", pd.DataFrame([
        {"Item": "Traders Required", "Value": f"{traders_required:,.0f}"},
        {"Item": "Birds/day", "Value": f"{birds_per_day:,.0f}"},
        {"Item": "Birds/month", "Value": f"{birds_required:,.0f}"},
        {"Item": "Live Weight/day", "Value": f"{(live_weight_kg / working_days):,.0f} kg"},
        {"Item": "Live Weight/month", "Value": f"{live_weight_kg:,.0f} kg"},
        {"Item": "Capacity per Trader", "Value": f"{avg_trader_capacity:,.0f} birds"},
        {"Item": "Total Trader Network Capacity", "Value": f"{total_network_capacity:,.0f} birds"},
        {"Item": "Live Bird Procurement Spend/month", "Value": fmt_currency(live_bird_procurement_spend)},
        {"Item": "Supply Coverage %", "Value": f"{supply_coverage_pct:,.1f}%"},
        {"Item": "Capacity Utilization %", "Value": f"{capacity_utilization_pct:,.1f}%"},
        {"Item": "Actual Trader Count Status", "Value": "Not Connected"},
        {"Item": "Capacity Gap / Surplus", "Value": f"{capacity_gap_surplus:,.0f} birds"},
        {"Item": "Procurement Risk Signal", "Value": procurement_risk_signal},
        {"Item": "Planning Status", "Value": "Capacity Modelled"},
        {"Item": "Actual Network Status", "Value": "Not Connected"},
    ]), hide_index=True, width="stretch")
    st.markdown("### Formula & Assumptions")
    render_formula_section("traders_required", build_formula_rows(
        "traders_required",
        current_value=f"{traders_required:,.0f} traders",
        unit="partners",
        status="Capacity Modelled",
        worked_calculation=f"ceil({birds_required:,.0f} birds/month ÷ {avg_trader_capacity:,.0f} birds/trader) = {traders_required:,.0f} traders",
        extra_rows=[
            {"Item": "Capacity per Trader", "Value": f"{avg_trader_capacity:,.0f} birds"},
            {"Item": "Total Trader Network Capacity", "Value": f"{total_network_capacity:,.0f} birds"},
            {"Item": "Supply Coverage %", "Value": f"{supply_coverage_pct:,.1f}%"},
            {"Item": "Capacity Utilization %", "Value": f"{capacity_utilization_pct:,.1f}%"},
            {"Item": "Capacity Gap / Surplus", "Value": f"{capacity_gap_surplus:,.0f} birds"},
            {"Item": "Actual Trader Count Status", "Value": "Not Connected"},
            {"Item": "Procurement Risk Signal", "Value": procurement_risk_signal},
            {"Item": "Primary Vehicles Required", "Value": f"{primary_logistics['vehicles_required']:,.0f}"},
            {"Item": "Primary Trips/day", "Value": f"{primary_logistics['trips_day']:,.0f}"},
            {"Item": "Primary Cost/month", "Value": fmt_currency(primary_logistics['cost_month'])},
        ],
        planning_status="Capacity Modelled",
        actual_status="Not Connected",
        related_kpis="Birds/day, Live Bird Procurement Spend, Farms Required, Primary Trips/day, Primary Vehicles Required",
    ))
    st.write("CEO Recommendation")
    if capacity_gap_surplus < 0:
        st.write(f"Add {abs(int(math.ceil(capacity_gap_surplus / max(1.0, avg_trader_capacity))))} trader partner(s) to close the projected daily supply gap.")
    else:
        st.write("Current planned trader capacity supports the required live-bird demand.")


def show_traders_required_drilldown():
    if hasattr(st, "dialog"):
        @st.dialog("Live Bird Trader Network")
        def _traders_dialog():
            render_traders_required_drilldown()

        _traders_dialog()
    else:
        with st.expander("Live Bird Trader Network", expanded=True):
            render_traders_required_drilldown()


def render_farms_required_drilldown():
    primary_logistics = logistics_output["primary"]
    total_network_capacity = float(avg_farm_capacity * farms_required)
    supply_coverage_pct = (total_network_capacity / max(1.0, float(birds_required))) * 100.0 if birds_required else 0.0
    capacity_utilization_pct = (float(birds_required) / max(1.0, total_network_capacity)) * 100.0 if total_network_capacity else 0.0
    capacity_gap_surplus = total_network_capacity - float(birds_required)
    supply_risk_signal = "Capacity Modelled" if capacity_gap_surplus >= 0 else "Additional Farm Capacity Required"
    st.write("This network represents the farms required to support live-bird demand under the current sourcing and operating model.")
    render_display_dataframe(st, "farms_required_summary", pd.DataFrame([
        {"Item": "Farms Required", "Value": f"{farms_required:,.0f}"},
        {"Item": "Birds/day", "Value": f"{birds_per_day:,.0f}"},
        {"Item": "Birds/month", "Value": f"{birds_required:,.0f}"},
        {"Item": "Live Weight/day", "Value": f"{(live_weight_kg / working_days):,.0f} kg"},
        {"Item": "Live Weight/month", "Value": f"{live_weight_kg:,.0f} kg"},
        {"Item": "Capacity per Farm", "Value": f"{avg_farm_capacity:,.0f} birds"},
        {"Item": "Total Farm Supply Capacity", "Value": f"{total_network_capacity:,.0f} birds"},
        {"Item": "Growing Cycle assumption", "Value": "Not separately modelled in the current engine; capacity is treated on the same monthly bird-capacity basis as Birds Required."},
        {"Item": "Mortality assumption", "Value": f"{mortality_pct:,.1f}% mortality is already reflected upstream."},
        {"Item": "Supply Coverage %", "Value": f"{supply_coverage_pct:,.1f}%"},
        {"Item": "Capacity Utilization %", "Value": f"{capacity_utilization_pct:,.1f}%"},
        {"Item": "Actual Farm Count Status", "Value": "Not Connected"},
        {"Item": "Capacity Gap / Surplus", "Value": f"{capacity_gap_surplus:,.0f} birds"},
        {"Item": "Supply Risk Signal", "Value": supply_risk_signal},
        {"Item": "Planning Status", "Value": "Capacity Modelled"},
        {"Item": "Actual Network Status", "Value": "Not Connected"},
    ]), hide_index=True, width="stretch")
    st.markdown("### Formula & Assumptions")
    render_formula_section("farms_required", build_formula_rows(
        "farms_required",
        current_value=f"{farms_required:,.0f} farms",
        unit="farms",
        status="Capacity Modelled",
        worked_calculation=f"ceil({birds_required:,.0f} birds/month ÷ {avg_farm_capacity:,.0f} birds/farm) = {farms_required:,.0f} farms",
        extra_rows=[
            {"Item": "Capacity per Farm", "Value": f"{avg_farm_capacity:,.0f} birds"},
            {"Item": "Total Farm Supply Capacity", "Value": f"{total_network_capacity:,.0f} birds"},
            {"Item": "Supply Coverage %", "Value": f"{supply_coverage_pct:,.1f}%"},
            {"Item": "Capacity Utilization %", "Value": f"{capacity_utilization_pct:,.1f}%"},
            {"Item": "Capacity Gap / Surplus", "Value": f"{capacity_gap_surplus:,.0f} birds"},
            {"Item": "Growing Cycle assumption", "Value": "Not separately modelled in the current engine; capacity is treated on the same monthly bird-capacity basis as Birds Required."},
            {"Item": "Mortality assumption", "Value": f"{mortality_pct:,.1f}% mortality is already reflected upstream."},
            {"Item": "Actual Farm Count Status", "Value": "Not Connected"},
            {"Item": "Supply Risk Signal", "Value": supply_risk_signal},
            {"Item": "Primary Vehicles Required", "Value": f"{primary_logistics['vehicles_required']:,.0f}"},
            {"Item": "Primary Trips/day", "Value": f"{primary_logistics['trips_day']:,.0f}"},
            {"Item": "Primary Cost/month", "Value": fmt_currency(primary_logistics['cost_month'])},
        ],
        planning_status="Capacity Modelled",
        actual_status="Not Connected",
        related_kpis="Birds/day, Live Bird Procurement Spend, Traders Required, Primary Trips/day, Primary Vehicles Required",
    ))
    st.write("CEO Recommendation")
    if capacity_gap_surplus < 0:
        st.write(f"Add {abs(int(math.ceil(capacity_gap_surplus / max(1.0, avg_farm_capacity))))} farm equivalent(s) or increase farm capacity before increasing the revenue target.")
    else:
        st.write("Current planned farm supply capacity supports the required live-bird demand.")


def show_farms_required_drilldown():
    if hasattr(st, "dialog"):
        @st.dialog("Live Bird Farm Supply Base")
        def _farms_dialog():
            render_farms_required_drilldown()

        _farms_dialog()
    else:
        with st.expander("Live Bird Farm Supply Base", expanded=True):
            render_farms_required_drilldown()


log_section_start("Corporate Summary")
st.markdown("<div class='pbos-section-card'>", unsafe_allow_html=True)
st.markdown("<div class='pbos-section-title'>Corporate Summary</div>", unsafe_allow_html=True)
st.markdown("<div class='pbos-section-subtitle'>Executive snapshot of revenue, demand, capacity and staffing.</div>", unsafe_allow_html=True)
col1, col2, col3, col4 = st.columns(4)
with col1:
    render_kpi_card("Corporate Revenue", fmt_currency(corporate_plant_revenue), subtitle="Planned | Monthly Revenue", icon_key="corporate_revenue")
with col2:
    render_kpi_card("Corporate Birds / Day", fmt_birds(corporate_birds_day, "day"), subtitle="Across All Active Markets", icon_key="corporate_birds_day")
with col3:
    render_kpi_card("Corporate Capacity", f"{corporate_capacity_mt_day:,.1f} MT/day", subtitle="Installed Capacity", icon_key="corporate_capacity")
with col4:
    render_kpi_card("Corporate Manpower", f"{corporate_manpower:,.0f}", subtitle="Total Employees", icon_key="corporate_manpower", button_label="View team mix", key="corporate_manpower_drilldown", button_action=show_corporate_manpower_drilldown)
st.markdown("</div>", unsafe_allow_html=True)
log_section_end("Corporate Summary")

log_section_start("Channel Business Ownership")
st.markdown("<div class='pbos-section-card'>", unsafe_allow_html=True)
st.markdown("<div class='pbos-section-title'>Channel Business Ownership</div>", unsafe_allow_html=True)
st.markdown("<div class='pbos-section-subtitle'>Revenue ownership and accountable commercial leadership by channel.</div>", unsafe_allow_html=True)
commercial_reconciliation_gap = float(channel_sales_output.get("reconciliation_gap", 0.0) or 0.0)
total_commercial_revenue_display = float(channel_sales_output.get("total_commercial_revenue", selected_market_revenue) or selected_market_revenue)
summary_subtitle = "Fully reconciled to selected market revenue"
if abs(commercial_reconciliation_gap) > 1.0:
    summary_subtitle = f"Revenue Reconciliation Gap: {fmt_currency(abs(commercial_reconciliation_gap))}"
render_kpi_card(
    "Total Commercial Revenue",
    fmt_currency(total_commercial_revenue_display),
    subtitle=summary_subtitle,
    status=None if abs(commercial_reconciliation_gap) <= 1.0 else "Revenue Reconciliation Gap",
    status_type="pbos-status-warn",
    icon_key="total_commercial_revenue",
)

own_col1, own_col2, own_col3, own_col4 = st.columns(4)
with own_col1:
    render_kpi_card(
        "Sales Manager / Head of Sales",
        fmt_currency(total_commercial_revenue_display),
        subtitle=f"Required HC: {channel_sales_output['sales_manager']:,.0f} | Owns all channel verticals",
        icon_key="sales_manager",
        button_label="View details",
        key="channel_sales_manager",
        button_action=lambda: show_distributor_channel_drilldown("Sales Manager"),
    )
with own_col2:
    render_kpi_card(
        "General Trade",
        fmt_currency(channel_sales_output["general_trade"]["revenue"]),
        subtitle=f"Required HC: {channel_sales_output['gt_sales_executives']:,.0f} | Distributor and outlet execution",
        icon_key="general_trade",
        button_label="View details",
        key="channel_gt",
        button_action=lambda: show_distributor_channel_drilldown("GT Sales Executives"),
    )
with own_col3:
    render_kpi_card(
        "Modern Trade",
        fmt_currency(channel_sales_output["modern_trade"]["revenue"]),
        subtitle=f"Required HC: {channel_sales_output['mt_kam']:,.0f} | Chain and account ownership",
        icon_key="modern_trade",
        button_label="View details",
        key="channel_mt_kam",
        button_action=lambda: show_distributor_channel_drilldown("MT KAM"),
    )
with own_col4:
    render_kpi_card(
        "Quick Commerce",
        fmt_currency(channel_sales_output["quick_commerce"]["revenue"]),
        subtitle=f"Required HC: {channel_sales_output['qcom_kam']:,.0f} | Platform and buying-account ownership",
        icon_key="quick_commerce",
        button_label="View details",
        key="channel_qcom_kam",
        button_action=lambda: show_distributor_channel_drilldown("QCom KAM"),
    )

own_col5, own_col6, own_col7, own_col8 = st.columns(4)
with own_col5:
    render_kpi_card(
        "E-commerce",
        fmt_currency(channel_sales_output.get("ecommerce", {}).get("revenue", channel_sales_output.get("ecommerce_revenue", 0.0))),
        subtitle=f"Required HC: {channel_sales_output.get('ecommerce_kam', 0):,.0f} | Digital commerce ownership",
        icon_key="ecommerce",
    )
with own_col6:
    render_kpi_card(
        "Exports",
        fmt_currency(channel_sales_output.get("exports", {}).get("revenue", channel_sales_output.get("exports_revenue", 0.0))),
        subtitle=f"Required HC: {channel_sales_output.get('exports_manager', 0):,.0f} | Export commercial ownership",
        icon_key="exports",
    )
with own_col7:
    render_kpi_card(
        "HoReCa",
        fmt_currency(channel_sales_output["horeca"].get("planned_revenue", channel_sales_output["horeca"]["revenue"])),
        subtitle=f"Calculated rate/kg: ₹{channel_sales_output['horeca']['contract_rate_per_kg']:,.0f} | Required volume: {channel_sales_output['horeca']['required_volume_kg_month']:,.0f} kg | HC: {channel_sales_output['horeca_sales_hc']:,.0f}",
        icon_key="horeca",
        button_label="View details",
        key="channel_horeca_sales",
        button_action=lambda: show_distributor_channel_drilldown("HoReCa Revenue"),
    )
with own_col8:
    render_kpi_card(
        "Institutional / Government",
        fmt_currency(channel_sales_output["institution"].get("planned_revenue", channel_sales_output["institution"]["revenue"])),
        subtitle=f"Calculated rate/kg: ₹{channel_sales_output['institution']['contract_rate_per_kg']:,.0f} | Volume: {channel_sales_output['institution']['required_volume_kg_month']:,.0f} kg | Packs: {channel_sales_output['institution']['institutional_required_packs_month']:,.0f} | HC: {channel_sales_output['institution_government_manager']:,.0f}",
        icon_key="institutional_government",
        button_label="View details",
        key="channel_inst_gov",
        button_action=lambda: show_distributor_channel_drilldown("Institutional / Government Revenue"),
    )

own_col9 = st.columns(1)[0]
with own_col9:
    render_kpi_card(
        "Total Commercial HC",
        f"{channel_sales_output['total_commercial_hc']:,.0f}",
        subtitle="Total commercial manpower",
        icon_key="sales_hc",
        button_label="View details",
        key="channel_total_commercial",
        button_action=lambda: show_distributor_channel_drilldown("Total Commercial HC"),
    )
st.markdown("</div>", unsafe_allow_html=True)
log_section_end("Channel Business Ownership")

if channel_sales_output.get("reconciliation_warning"):
    st.error(channel_sales_output["reconciliation_warning"])
if channel_sales_output["horeca"]["revenue_mode"] != "PLANNING" and abs(channel_sales_output["horeca"]["reconciliation_variance"]) > 0:
    st.warning(f"HoReCa contract revenue differs from channel mix allocation by {fmt_currency(channel_sales_output['horeca']['reconciliation_variance'])}.")
if channel_sales_output["institution"]["revenue_mode"] != "PLANNING" and abs(channel_sales_output["institution"]["reconciliation_variance"]) > 0:
    st.warning(f"Institutional / Government contract revenue differs from channel mix allocation by {fmt_currency(channel_sales_output['institution']['reconciliation_variance'])}.")

log_section_start("Market-specific Planning")
st.markdown("<div class='pbos-section-card'>", unsafe_allow_html=True)
st.markdown("<div class='pbos-section-title'>Market-specific Planning</div>", unsafe_allow_html=True)
st.markdown("<div class='pbos-section-subtitle'>Selected market view with market-only presentation.</div>", unsafe_allow_html=True)
col5, col6, col7, col8 = st.columns(4)
with col5:
    render_kpi_card("Selected Market", selected_market_name, subtitle="Current market focus", icon_key="selected_market")
with col6:
    render_kpi_card("Revenue Allocation", fmt_currency(market_revenue_rupees), subtitle="Market allocation", icon_key="revenue_allocation")
with col7:
    render_kpi_card("Assigned Plant", selected_plant_name, subtitle="Plant serving this market", icon_key="assigned_plant")
with col8:
    if market_distance_km == 0 or selected_market_city.strip().lower() == selected_plant_city.strip().lower():
        market_status = "Base Market"
    elif 0 < market_distance_km <= 300:
        market_status = "Regional Market"
    else:
        market_status = "Expansion Market"
    render_kpi_card("Market Status", market_status, subtitle="Market positioning", icon_key="market_status")
st.markdown("<div class='pbos-info-banner'>Revenue Share: <b>{:.1f}%</b> | One-way Distance: <b>{:.0f} km</b></div>".format((market_revenue_rupees / corporate_revenue_rupees * 100.0) if corporate_revenue_rupees else 0.0, market_distance_km), unsafe_allow_html=True)
st.markdown("</div>", unsafe_allow_html=True)
log_section_end("Market-specific Planning")

log_section_start("Commercial & Distribution Planning")
st.markdown("<div class='pbos-section-card'>", unsafe_allow_html=True)
st.markdown("<div class='pbos-section-title'>Commercial & Distribution Planning</div>", unsafe_allow_html=True)
st.markdown("<div class='pbos-section-subtitle'>Portfolio-wise route-to-market, distribution capacity and commercial coverage.</div>", unsafe_allow_html=True)
product_revenue_tolerance = 0.01
st.markdown("<div class='pbos-section-title' style='font-size:0.94rem; margin-top:6px;'>Product Revenue Reconciliation</div>", unsafe_allow_html=True)
render_display_dataframe(st, "product_revenue_reconciliation", pd.DataFrame([
    {"Metric": "Corporate Revenue Target", "Value": fmt_currency(corporate_revenue_rupees)},
    {"Metric": "Fresh Chilled", "Value": fmt_currency(distributor_output["fresh_chilled_revenue"])},
    {"Metric": "Frozen Raw", "Value": fmt_currency(distributor_output["frozen_raw_revenue"])},
    {"Metric": "Ready To Eat", "Value": fmt_currency(distributor_output["rte_revenue"])},
    {"Metric": "Further Value Added", "Value": fmt_currency(distributor_output["fva_revenue"])},
    {"Metric": "Total Product Revenue", "Value": fmt_currency(distributor_output["total_product_revenue"])},
    {"Metric": "Reconciliation Status", "Value": "Reconciled" if distributor_output["product_revenue_reconciled"] else "Not Reconciled"},
]), hide_index=True, width="stretch")
if abs(distributor_output["product_revenue_variance"]) > product_revenue_tolerance:
    st.warning(f"Product revenue allocation differs from corporate revenue target by {fmt_currency(abs(distributor_output['product_revenue_variance']))}.")

st.markdown("<div class='pbos-section-title' style='font-size:0.94rem; margin-top:6px;'>A. Portfolio Distribution Network</div>", unsafe_allow_html=True)
dcol1, dcol2 = st.columns(2)
with dcol1:
    distribution_business_card(
        "Fresh Chilled Business",
        distributor_output["fresh_chilled_revenue"],
        distributor_output["fresh_distributors"],
        distributor_output["fresh_network_capacity"],
        distributor_output["fresh_utilization_pct"],
        distributor_output["fresh_capacity_status"],
        "dist_fresh_chilled_business",
    )
with dcol2:
    distribution_business_card(
        "Frozen Raw Business",
        distributor_output["frozen_raw_revenue"],
        distributor_output["frozen_raw_distributors"],
        distributor_output["frozen_network_capacity"],
        distributor_output["frozen_utilization_pct"],
        distributor_output["frozen_capacity_status"],
        "dist_frozen_raw_business",
    )
dcol3, dcol4 = st.columns(2)
with dcol3:
    distribution_business_card(
        "Ready To Eat Business",
        distributor_output["rte_revenue"],
        distributor_output["rte_distributors"],
        distributor_output["rte_network_capacity"],
        distributor_output["rte_utilization_pct"],
        distributor_output["rte_capacity_status"],
        "dist_rte_business",
    )
with dcol4:
    distribution_business_card(
        "Further Value Added Business",
        distributor_output["fva_revenue"],
        distributor_output["fva_distributors"],
        distributor_output["fva_network_capacity"],
        distributor_output["fva_utilization_pct"],
        distributor_output["fva_capacity_status"],
        "dist_fva_business",
    )

st.markdown("<div class='pbos-section-title' style='font-size:0.94rem; margin-top:10px;'>B. Portfolio Account & Network Capacity</div>", unsafe_allow_html=True)
st.markdown("<div class='pbos-section-subtitle'>Channel-account coverage, distributor capacity and route-to-market execution requirements.</div>", unsafe_allow_html=True)
exec_col1, exec_col2, exec_col3 = st.columns(3)
with exec_col1:
    gt_execution = channel_sales_output["general_trade"]
    render_kpi_card(
        "GT Distributor / Outlet Coverage",
        f"{gt_execution['required_distributors']:,.0f} distributors",
        subtitle=f"{gt_execution['target_outlets']:,.0f} target outlets | {gt_execution['outlets_per_distributor']:,.0f} outlets/distributor",
        status=gt_execution["coverage_status"],
        status_type="pbos-status-neutral",
        icon_key="general_trade",
        button_label="View details",
        key="commercial_exec_gt",
        button_action=lambda: show_distributor_channel_drilldown("GT Sales Executives"),
    )
with exec_col2:
    render_kpi_card(
        "Modern Trade Accounts",
        f"{channel_sales_output['modern_trade']['accounts']:,.0f}",
        subtitle="Modern Trade accounts",
        icon_key="modern_trade",
        button_label="View details",
        key="commercial_exec_mt",
        button_action=lambda: show_distributor_channel_drilldown("MT KAM"),
    )
with exec_col3:
    render_kpi_card(
        "Quick Commerce Network",
        f"{channel_sales_output['quick_commerce']['active_platforms']:,.0f}",
        subtitle=f"{channel_sales_output['quick_commerce']['buying_accounts']:,.0f} buying accounts | {channel_sales_output['quick_commerce']['buying_regions']:,.0f} buying regions",
        icon_key="quick_commerce",
        button_label="View details",
        key="commercial_exec_qcom",
        button_action=lambda: show_distributor_channel_drilldown("QCom KAM"),
    )

exec_col4, exec_col5, exec_col6 = st.columns(3)
with exec_col4:
    render_kpi_card(
        "HoReCa Accounts",
        f"{channel_sales_output['horeca']['accounts']:,.0f}",
        subtitle="HoReCa active contracts and accounts",
        icon_key="horeca",
        button_label="View details",
        key="commercial_exec_horeca",
        button_action=lambda: show_distributor_channel_drilldown("HoReCa Revenue"),
    )
with exec_col5:
    render_kpi_card(
        "Institutional / Government Accounts",
        f"{channel_sales_output['institution']['accounts']:,.0f}",
        subtitle="Institutional and government tenders",
        icon_key="institutional_government",
        button_label="View details",
        key="commercial_exec_inst",
        button_action=lambda: show_distributor_channel_drilldown("Institutional / Government Revenue"),
    )
with exec_col6:
    render_kpi_card(
        "Total Commercial HC",
        f"{channel_sales_output['total_commercial_hc']:,.0f}",
        subtitle="Total commercial manpower",
        icon_key="sales_hc",
        button_label="View details",
        key="commercial_exec_total_hc",
        button_action=lambda: show_distributor_channel_drilldown("Total Commercial HC"),
    )
st.markdown("</div>", unsafe_allow_html=True)
log_section_end("Commercial & Distribution Planning")

log_section_start("Plant Capacity Planning")
st.markdown("<div class='pbos-section-card'>", unsafe_allow_html=True)
st.markdown("<div class='pbos-section-title'>Plant Capacity Planning</div>", unsafe_allow_html=True)
st.markdown("<div class='pbos-section-subtitle'>Capacity required by the plant to support assigned market demand.</div>", unsafe_allow_html=True)
colp1, colp2, colp3, colp4 = st.columns(4)
required_output_mt_day = float(plant_capacity_output.get("required_capacity_mt_day", plant_capacity_output.get("finished_goods_mt_day", 0.0)) or 0.0)
installed_lines = int(round(float(plant_capacity_output.get("current_installed_lines", plant_capacity_output.get("installed_lines", plant_capacity_output.get("production_lines_required", 1))) or 1)))
active_shifts = int(round(float(plant_capacity_output.get("current_active_shifts", plant_capacity_output.get("active_shifts", plant_capacity_output.get("shifts_required", 1))) or 1)))
current_configuration_label = str(plant_capacity_output.get("current_configuration_label", f"{installed_lines:,.0f} {'line' if installed_lines == 1 else 'lines'} × {active_shifts:,.0f} {'shift' if active_shifts == 1 else 'shifts'}"))
capacity_recommendation_mode = str(plant_capacity_output.get("capacity_recommendation_mode", "")).strip()
recommended_lines = int(round(float(plant_capacity_output.get("recommended_lines", 1) or 1)))
recommended_shifts = int(round(float(plant_capacity_output.get("recommended_shifts", 1) or 1)))
recommended_configuration_label = str(plant_capacity_output.get("recommended_configuration_label", "")).strip()
if not recommended_configuration_label and capacity_recommendation_mode == "CURRENT_SITE_OPTIMIZATION":
    recommended_configuration_label = format_configuration(recommended_lines, recommended_shifts)
maximum_site_lines = int(round(float(plant_capacity_output.get("maximum_site_lines", plant_capacity_output.get("maximum_lines_in_current_plant", installed_lines)) or installed_lines)))
maximum_site_shifts = int(round(float(plant_capacity_output.get("maximum_site_shifts", plant_capacity_output.get("maximum_shifts_per_line", 1)) or 1)))
maximum_site_configuration_label = str(plant_capacity_output.get("maximum_site_configuration_label", "")).strip()
if not maximum_site_configuration_label:
    maximum_site_configuration_label = format_configuration(maximum_site_lines, maximum_site_shifts)
base_capacity = float(plant_capacity_output.get("plant_base_capacity_mt_day", plant_capacity_output.get("capacity_per_line_mt_day", 0.0)) or 0.0)
installed_capacity_mt_day = float(plant_capacity_output.get("current_installed_capacity_mt_day", plant_capacity_output.get("installed_capacity_mt_day", 0.0)) or 0.0)
recommended_capacity_mt_day = float(plant_capacity_output.get("recommended_capacity_mt_day", installed_capacity_mt_day) or installed_capacity_mt_day)
max_capacity_mt_day = float(plant_capacity_output.get("maximum_current_plant_capacity_mt_day", installed_capacity_mt_day) or installed_capacity_mt_day)
additional_capacity_required_mt_day = float(plant_capacity_output.get("additional_capacity_required_mt_day", plant_capacity_output.get("current_site_capacity_deficit_mt_day", 0.0)) or 0.0)
recommended_new_plant_capacity_mt_day = float(plant_capacity_output.get("recommended_new_plant_capacity_mt_day", 0.0) or 0.0)
total_future_capacity_mt_day = float(plant_capacity_output.get("total_future_capacity_mt_day", 0.0) or 0.0)
projected_future_utilization_pct = float(plant_capacity_output.get("projected_future_utilization_pct", 0.0) or 0.0)

third_card_title = "Recommended Plant Configuration"
third_card_value = recommended_configuration_label
third_card_subtitle = f"{recommended_capacity_mt_day:,.1f} MT/day recommended capacity"
if capacity_recommendation_mode == "NEW_PLANT_EXPANSION":
    third_card_title = "Maximum Current-Site Configuration"
    third_card_value = maximum_site_configuration_label
    third_card_subtitle = f"{max_capacity_mt_day:,.1f} MT/day maximum at current site"

expected_recommended_capacity_mt_day = base_capacity * recommended_lines * recommended_shifts
capacity_consistency_tolerance = 1e-6
if capacity_recommendation_mode == "CURRENT_SITE_OPTIMIZATION" and abs(expected_recommended_capacity_mt_day - recommended_capacity_mt_day) > capacity_consistency_tolerance:
    log_runtime_event(
        "plant_configuration_reconciliation_mismatch",
        expected_capacity_mt_day=f"{expected_recommended_capacity_mt_day:.4f}",
        reported_recommended_capacity_mt_day=f"{recommended_capacity_mt_day:.4f}",
        recommended_lines=recommended_lines,
        recommended_shifts=recommended_shifts,
        recommended_configuration_label=recommended_configuration_label,
    )
    third_card_value = "Configuration Review Required"
    third_card_subtitle = f"Expected {expected_recommended_capacity_mt_day:,.1f} MT/day from {format_configuration(recommended_lines, recommended_shifts)}"
    st.warning("Configuration Review Required")
if capacity_recommendation_mode not in {"CURRENT_SITE_OPTIMIZATION", "NEW_PLANT_EXPANSION"}:
    log_runtime_event(
        "plant_capacity_mode_missing_main_card",
        required_output_mt_day=f"{required_output_mt_day:.4f}",
        maximum_current_site_capacity_mt_day=f"{max_capacity_mt_day:.4f}",
        recommended_action=str(plant_capacity_output.get("recommended_action", "")),
    )
    third_card_value = "Configuration Review Required"
    third_card_subtitle = "Recommendation mode missing"
    st.warning("Configuration Review Required")

current_load_ratio_pct = float(plant_capacity_output.get("current_load_ratio_pct", plant_capacity_output.get("plant_utilization_pct", 0.0)) or 0.0)
recommended_action = str(plant_capacity_output.get("recommended_action", "Continue Current Configuration"))
new_plant_required = str(plant_capacity_output.get("new_plant_required", "No"))
action_subtitle = _recommended_action_subtitle(plant_capacity_output)
if capacity_recommendation_mode == "NEW_PLANT_EXPANSION":
    action_subtitle = (
        f"Required output exceeds maximum current-site capacity by {additional_capacity_required_mt_day:,.1f} MT/day. "
        f"Operate current site at {maximum_site_configuration_label} ({max_capacity_mt_day:,.1f} MT/day), "
        f"then add {recommended_new_plant_capacity_mt_day:,.1f} MT/day new-plant capacity."
    )
cold_storage_required_mt = float(plant_capacity_output.get("cold_storage_required_mt", 0.0) or 0.0)
with colp1:
    plant_kpi_card("Required Output", f"{required_output_mt_day:,.1f} MT/day", "plant_kpi_required_output", subtitle="Demand output")
with colp2:
    plant_kpi_card("Current Installed Capacity", f"{installed_capacity_mt_day:,.1f} MT/day", "plant_kpi_installed_capacity", subtitle="Base x lines x shifts")
with colp3:
    plant_kpi_card(third_card_title, third_card_value, "plant_kpi_recommended_configuration", subtitle=third_card_subtitle)
with colp4:
    plant_kpi_card("Maximum Current-Site Capacity", f"{max_capacity_mt_day:,.1f} MT/day", "plant_kpi_max_site_capacity", subtitle="Within current-site governance")

colp5, colp6, colp7, colp8 = st.columns(4)
with colp5:
    render_kpi_card(
        "Plant Utilization",
        f"{current_load_ratio_pct:,.1f}%",
        subtitle="Demand load vs current installed capacity",
        status="Normal" if current_load_ratio_pct <= 85 else "Monitor" if current_load_ratio_pct <= 90 else "Expansion Review" if current_load_ratio_pct <= 95 else "Critical" if current_load_ratio_pct <= 100 else "Capacity Deficit",
        status_type="pbos-status-positive" if current_load_ratio_pct <= 85 else "pbos-status-warn" if current_load_ratio_pct <= 95 else "pbos-status-alert",
        icon_key=PLANT_ICON_KEYS.get("Plant Utilization"),
        button_label="View details",
        key="plant_kpi_utilization_details",
        button_action=show_plant_capacity_governance_dialog,
    )
with colp6:
    plant_kpi_card("Recommended Capacity Action", recommended_action, "plant_kpi_recommended_action", subtitle=action_subtitle, status=recommended_action, status_type="pbos-status-warn" if recommended_action in {"Add Shift", "Add Production Line", "Expand Existing Plant"} else "pbos-status-alert" if recommended_action == "Build New Plant" else "pbos-status-positive")
with colp7:
    new_plant_subtitle = (
        f"{additional_capacity_required_mt_day:,.1f} MT/day additional capacity required"
        f"<br>{recommended_new_plant_capacity_mt_day:,.1f} MT/day recommended new plant"
        f"<br>{total_future_capacity_mt_day:,.1f} MT/day total future capacity | {projected_future_utilization_pct:,.1f}% projected future utilization"
        if new_plant_required == "Yes"
        else "No additional capacity required"
    )
    plant_kpi_card("New Plant Required", new_plant_required, "plant_kpi_new_plant_required", subtitle=new_plant_subtitle, status=new_plant_required, status_type="pbos-status-alert" if new_plant_required == "Yes" else "pbos-status-positive")
with colp8:
    plant_kpi_card("Cold Storage Required", f"{cold_storage_required_mt:,.1f} MT", "plant_kpi_cold_storage_required", subtitle="Buffer stock requirement")
st.markdown("</div>", unsafe_allow_html=True)
log_section_end("Plant Capacity Planning")

log_section_start("Raw Material & Procurement Planning")
st.markdown("<div class='pbos-section-card'>", unsafe_allow_html=True)
st.markdown("<div class='pbos-section-title'>Raw Material & Procurement Planning</div>", unsafe_allow_html=True)
st.markdown("<div class='pbos-section-subtitle'>Live bird procurement and raw material conversion for the selected market.</div>", unsafe_allow_html=True)
proc_col1, proc_col2, proc_col3, proc_col4 = st.columns(4)
with proc_col1:
    render_kpi_card("Live Bird Rate", fmt_rate_per_kg(live_bird_rate), subtitle="Assumption | Registry default can be overridden", icon_key="live_bird_rate")
with proc_col2:
    render_kpi_card("Yield", f"{yield_pct:,.1f}%", subtitle="Conversion efficiency", icon_key="yield")
with proc_col3:
    render_kpi_card("Birds / Day", fmt_birds(birds_per_day, "day"), subtitle="Live bird demand", icon_key="birds_day")
with proc_col4:
    render_kpi_card("Live Weight / Day", f"{live_weight_kg / working_days:,.0f} kg", subtitle="Daily live weight", icon_key="live_weight_day")
proc_col5, proc_col6, proc_col7, proc_col8 = st.columns(4)
with proc_col5:
    render_kpi_card("Live Bird Procurement Spend", fmt_currency(live_bird_procurement_spend), subtitle="Live bird landed spend", icon_key="procurement_spend", button_label="View details", key="procurement_driver_details", button_action=show_procurement_driver_drilldown)
with proc_col6:
    render_kpi_card("Packaging Spend", fmt_currency(packaging_spend), subtitle=f"{fmt_currency_plain(cost_waterfall.get('packaging_cost_per_kg', packaging_cost), 0)}/kg finished goods", icon_key="procurement_spend")
with proc_col7:
    render_kpi_card("Transport Spend", fmt_currency(transport_spend), subtitle=f"{fmt_currency_plain(cost_waterfall.get('transport_cost_per_kg', transport_cost), 0)}/kg finished goods", icon_key="procurement_spend")
with proc_col8:
    render_kpi_card("Total Direct Variable Spend", fmt_currency(procurement_spend), subtitle="Bird + processing + packing + transport", icon_key="procurement_spend", button_label="View details", key="procurement_total_direct_details", button_action=show_procurement_driver_drilldown)
proc_col9, proc_col10 = st.columns(2)
with proc_col9:
    render_kpi_card("Traders Required", f"{traders_required:,.0f}", subtitle="Supply sourcing support", icon_key="traders_required", button_label="View details", key="proc_traders_required", button_action=show_traders_required_drilldown)
with proc_col10:
    render_kpi_card("Farms Required", f"{farms_required:,.0f}", subtitle="Supply base support", icon_key="farms_required", button_label="View details", key="proc_farms_required", button_action=show_farms_required_drilldown)
st.markdown("</div>", unsafe_allow_html=True)
log_section_end("Raw Material & Procurement Planning")

log_section_start("Logistics Planning")
st.markdown("<div class='pbos-section-card'>", unsafe_allow_html=True)
st.markdown("<div class='pbos-section-title'>Logistics Planning</div>", unsafe_allow_html=True)
st.markdown("<div class='pbos-section-subtitle'>Primary live-bird movement and secondary finished-goods delivery.</div>", unsafe_allow_html=True)
primary_logistics = logistics_output["primary"]
secondary_logistics = logistics_output["secondary"]
st.markdown("<div class='pbos-section-title' style='font-size:0.94rem; margin-top:6px;'>A. Primary Logistics</div>", unsafe_allow_html=True)
st.markdown("<div class='pbos-section-subtitle'>Live bird sourcing → plant</div>", unsafe_allow_html=True)
coll1, coll2, coll3, coll4 = st.columns(4)
with coll1:
    logistics_kpi_card("Primary Vehicles Required", f"{primary_logistics['vehicles_required']:,.0f}", "logistics_primary_vehicles", subtitle="Primary transport")
with coll2:
    logistics_kpi_card("Primary Trips / Day", f"{primary_logistics['trips_day']:,.0f}", "logistics_primary_trips", subtitle="Lifting cadence")
with coll3:
    logistics_kpi_card("Primary Cost / Month", fmt_currency(primary_logistics["cost_month"]), "logistics_primary_cost", subtitle="Live bird sourcing")
with coll4:
    logistics_kpi_card("Average Primary Distance", f"{average_primary_distance_km:,.0f} km", "logistics_total_cost", subtitle="Sourcing radius")

st.markdown("<div class='pbos-section-title' style='font-size:0.94rem; margin-top:10px;'>B. Secondary Logistics</div>", unsafe_allow_html=True)
st.markdown("<div class='pbos-section-subtitle'>Plant → market / distributor / customer</div>", unsafe_allow_html=True)
coll5, coll6, coll7, coll8, coll9 = st.columns(5)
with coll5:
    logistics_kpi_card("Secondary Vehicles Required", f"{secondary_logistics['vehicles_required']:,.0f}", "logistics_secondary_vehicles", subtitle="Outbound fleet")
with coll6:
    logistics_kpi_card("Secondary Trips / Day", f"{secondary_logistics['trips_day']:,.0f}", "logistics_secondary_trips", subtitle="Delivery frequency")
with coll7:
    logistics_kpi_card("Secondary Cost / Month", fmt_currency(secondary_logistics["cost_month"]), "logistics_secondary_cost", subtitle="Channel delivery")
with coll8:
    logistics_kpi_card("Cold Chain Required", secondary_logistics["cold_chain_required"], "logistics_cold_chain", subtitle="Cold-chain signal")
with coll9:
    logistics_kpi_card("Market Distance", f"{secondary_logistics['market_distance_km']:,.0f} km", "logistics_market_distance", subtitle="Plant to market")
st.markdown("</div>", unsafe_allow_html=True)
log_section_end("Logistics Planning")

log_section_start("Order & Capacity Intelligence")
st.markdown("<div class='pbos-section-card'>", unsafe_allow_html=True)
st.markdown("<div class='pbos-section-title'>Order & Capacity Intelligence</div>", unsafe_allow_html=True)
st.markdown("<div class='pbos-section-subtitle'>Actual order demand compared with planned volume, inventory and plant capacity.</div>", unsafe_allow_html=True)
order_col1, order_col2, order_col3, order_col4 = st.columns(4)
with order_col1:
    render_kpi_card("Scenario Mode", order_capacity_intelligence.get("scenario_mode", "No Scenario"), subtitle="Scenario", icon_key="scenario_mode")
with order_col2:
    render_kpi_card("Order Source", order_capacity_intelligence.get("order_source", "NONE"), subtitle="Planning source", icon_key="order_source")
with order_col3:
    render_kpi_card("Planned Demand", f"{order_capacity_intelligence['planned_demand_mt_day']:,.2f} MT/day", subtitle="Channel mix demand", icon_key="planned_demand")
with order_col4:
    render_kpi_card("Scenario Order Demand", f"{order_capacity_intelligence['scenario_order_demand_mt_day']:,.2f} MT/day", subtitle="Scenario demand", icon_key="scenario_orders")
order_col5, order_col6, order_col7, order_col8 = st.columns(4)
with order_col5:
    render_kpi_card("Overall Achievement %", f"{order_capacity_intelligence['overall_achievement_pct']:,.1f}%", subtitle="Scenario vs plan", icon_key="achievement")
with order_col6:
    render_kpi_card("Available Cold Inventory", f"{order_capacity_intelligence['available_inventory_mt']:,.1f} MT", subtitle="Scenario input | Actual feed: Not Connected", icon_key="available_inventory")
with order_col7:
    render_kpi_card("Available Plant Capacity", f"{order_capacity_intelligence['available_plant_capacity_mt_day']:,.1f} MT/day", subtitle="Production capacity", icon_key="available_plant_capacity")
with order_col8:
    render_kpi_card("Total Fulfilment Capability", f"{order_capacity_intelligence['total_fulfilment_capability_mt']:,.1f} MT", subtitle="Plant + releasable stock", icon_key="capacity_gap")
variance_mt_day = order_capacity_intelligence.get("demand_variance_mt_day", 0.0)
variance_kg_day = order_capacity_intelligence.get("demand_variance_kg_day", 0.0)
variance_status = order_capacity_intelligence.get("demand_variance_status", "On Plan")
if variance_status == "Above Plan":
    variance_subtitle = f"{abs(variance_kg_day):,.0f} kg/day above plan"
elif variance_status == "Below Plan":
    variance_subtitle = f"{abs(variance_kg_day):,.0f} kg/day below plan"
elif variance_status == "Not Simulated":
    variance_subtitle = "Not simulated"
else:
    variance_subtitle = "On plan"
order_col9, order_col10, order_col11, order_col12 = st.columns(4)
with order_col9:
    render_kpi_card("Demand Variance", f"{variance_mt_day:+,.2f} MT/day", subtitle=variance_subtitle, status=variance_status, status_type="pbos-status-positive" if variance_status == "On Plan" else "pbos-status-neutral" if variance_status == "Not Simulated" else "pbos-status-warn", icon_key="scenario_orders")
with order_col10:
    render_kpi_card("Production Required", f"{order_capacity_intelligence['production_required_mt_day']:,.1f} MT/day", subtitle="After inventory release", icon_key="available_plant_capacity")
with order_col11:
    render_kpi_card("Capacity Gap / Surplus", f"{order_capacity_intelligence['capacity_gap_mt']:,.1f} MT", subtitle="Supply minus orders", icon_key="capacity_gap")
with order_col12:
    render_kpi_card("Scenario Plant Utilization", f"{order_capacity_intelligence['scenario_plant_utilization_pct']:,.1f}%", subtitle="Against installed capacity", icon_key="scenario_plant_utilization")
order_col13, _, _, _ = st.columns(4)
with order_col13:
    capacity_status = order_capacity_intelligence.get("capacity_status", order_capacity_intelligence["status"])
    capacity_status_label = "Not Simulated" if capacity_status == "NOT_SIMULATED" else capacity_status
    render_kpi_card("Capacity Status", capacity_status_label, subtitle=order_capacity_intelligence["warning_type"], status=order_capacity_intelligence["persistence_status"], status_type="pbos-status-positive" if capacity_status == "HEALTHY" else "pbos-status-warn", button_label="View details", key="order_capacity_intelligence_details", button_action=show_order_capacity_drilldown, icon_key="capacity_status")
st.markdown("</div>", unsafe_allow_html=True)
log_section_end("Order & Capacity Intelligence")

log_section_start("Manpower Planning")
st.markdown("<div class='pbos-section-card'>", unsafe_allow_html=True)
st.markdown("<div class='pbos-section-title'>Manpower Planning</div>", unsafe_allow_html=True)
st.markdown("<div class='pbos-section-subtitle'>Department-wise staffing for the selected plant and market plan.</div>", unsafe_allow_html=True)
colm1, colm2, colm3, colm4, colm5 = st.columns(5)
with colm1:
    manpower_kpi_card("Production", manpower_output["production"], "manpower_kpi_production", subtitle="Plant execution")
with colm2:
    manpower_kpi_card("Warehouse + Cold Room", manpower_output["warehouse"], "manpower_kpi_warehouse", subtitle="Handling and dispatch")
with colm3:
    manpower_kpi_card("Sales", manpower_output["sales"], "manpower_kpi_sales", subtitle="Channel execution")
with colm4:
    manpower_kpi_card("Marketing", manpower_output["marketing"], "manpower_kpi_marketing", subtitle="Trade and activation")
with colm5:
    manpower_kpi_card("Finance", manpower_output["finance"], "manpower_kpi_finance", subtitle="Controls and MIS")

colm6, colm7, colm8, colm9, colm10 = st.columns(5)
with colm6:
    manpower_kpi_card("HR", manpower_output["hr"], "manpower_kpi_hr", subtitle="People operations")
with colm7:
    manpower_kpi_card("Admin", manpower_output["admin"], "manpower_kpi_admin", subtitle="Site support")
with colm8:
    manpower_kpi_card("QA / Food Safety", manpower_output["qa_food_safety"], "manpower_kpi_qa", subtitle="Compliance")
with colm9:
    manpower_kpi_card("Procurement", manpower_output["procurement"], "manpower_kpi_procurement", subtitle="Bird sourcing")
with colm10:
    manpower_kpi_card("Total Employees", manpower_output["total_employees"], "manpower_kpi_total", subtitle="Overall operating team", status="Overall capacity", status_type="pbos-status-positive")
if manpower_output.get("staffing_bands"):
    staffing_rows = []
    for function_name, band in manpower_output["staffing_bands"].items():
        staffing_rows.append({
            "Function": function_name.replace("_", " ").title(),
            "Current Workload": f"{float(band.get('current_workload', 0.0) or 0.0):,.1f}",
            "Unit": band.get("workload_unit", ""),
            "Staffing Band": band.get("current_staffing_band", ""),
            "Lower Threshold": f"{float(band.get('lower_threshold', 0.0) or 0.0):,.1f}",
            "Upper Threshold": f"{float(band.get('upper_threshold', 0.0) or 0.0):,.1f}",
            "Current HC": f"{int(band.get('current_hc', 0) or 0):,.0f}",
            "Recommended HC": f"{int(band.get('recommended_hc', 0) or 0):,.0f}",
            "Threshold Status": band.get("threshold_status", ""),
            "Business Reason": band.get("business_reason", ""),
        })
    staffing_df = pd.DataFrame(staffing_rows)
    log_dataframe_shape("manpower_staffing_bands", staffing_df)
    render_staffing_bands_table(staffing_df)
st.markdown("</div>", unsafe_allow_html=True)
log_section_end("Manpower Planning")

with st.expander("Reverse Manpower Planning", expanded=False):
    target_sales_hc = st.number_input("CEO Sales Headcount", min_value=int(1), value=int(manpower_output["sales"]), step=int(1), key="reverse_sales_hc")
    sales_coverage_pct = min(100.0, target_sales_hc / max(1, manpower_output["sales"]) * 100.0)
    sales_supported_revenue = selected_plant_result["assigned_market_revenue"] * sales_coverage_pct / 100.0
    sales_revenue_impact = max(0.0, selected_plant_result["assigned_market_revenue"] - sales_supported_revenue)
    outlet_coverage_pct = sales_coverage_pct
    st.write("Sales Reverse Planning")
    st.write(f"Lower market coverage: {sales_coverage_pct:,.1f}% of planned revenue coverage remains when sales headcount moves from {manpower_output['sales']:,.0f} to {target_sales_hc:,.0f}.")
    st.write("Slower GT expansion: fewer field reps means fewer new outlets opened and slower repeat-order building.")
    st.write(f"Lower outlet visits: outlet coverage decreases to {outlet_coverage_pct:,.1f}% because each salesperson carries a defined market coverage load.")
    st.write(f"Revenue at risk: {fmt_currency(sales_revenue_impact)}.")
    st.write(f"Expected revenue impact is {fmt_currency(sales_revenue_impact)}.")
    if target_sales_hc < manpower_output["sales"]:
        st.warning("Recommendation: reduce the revenue target, improve salesperson productivity, or restore sales coverage before committing the plan.")
    else:
        st.success("Recommendation: sales coverage is sufficient for the current revenue ambition.")

    target_production_hc = st.number_input("CEO Production Headcount", min_value=int(1), value=int(manpower_output["production"]), step=int(1), key="reverse_production_hc")
    max_mt_day_possible = target_production_hc * manpower_output["production_mt_per_person_day"]
    production_utilization = min(100.0, plant_raw_material_output["finished_goods_mt_day"] / max(0.1, max_mt_day_possible) * 100.0)
    lost_capacity_mt_day = max(0.0, plant_raw_material_output["finished_goods_mt_day"] - max_mt_day_possible)
    production_revenue_impact = selected_plant_result["assigned_market_revenue"] * lost_capacity_mt_day / max(0.1, plant_raw_material_output["finished_goods_mt_day"])
    st.write("Production Reverse Planning")
    st.write(f"Lower throughput: maximum MT/day possible is {max_mt_day_possible:,.1f} MT/day.")
    st.write("Overtime risk increases when fewer people have to cover the same production and packing load.")
    st.write("Quality and sanitation risk increases because cleaning, shift handover, and line discipline get compressed.")
    st.write(f"Utilization against available production manpower is {production_utilization:,.1f}%.")
    st.write(f"Lost capacity is {lost_capacity_mt_day:,.1f} MT/day.")
    st.write(f"Revenue capacity impact is {fmt_currency(production_revenue_impact)}.")
    if target_production_hc < manpower_output["production"]:
        st.warning("Recommendation: do not reduce production headcount unless demand is lowered or productivity improves.")
    else:
        st.success("Recommendation: production manpower can support the current finished goods plan.")

    target_warehouse_hc = st.number_input("CEO Warehouse + Cold Room Headcount", min_value=int(1), value=int(manpower_output["warehouse"]), step=int(1), key="reverse_warehouse_hc")
    warehouse_coverage_pct = min(100.0, target_warehouse_hc / max(1, manpower_output["warehouse"]) * 100.0)
    st.write("Warehouse + Cold Room Reverse Planning")
    st.write(f"Loading delay risk rises when warehouse coverage drops to {warehouse_coverage_pct:,.1f}% of the planned team.")
    st.write("Cold room mismatch risk increases because receiving, put-away, picking, and dispatch checks become compressed.")
    st.write("FEFO and inventory risk increases when fewer people manage batch rotation and stock accuracy.")
    st.write("Dispatch SLA risk increases because loading and route handover depend on timely cold room execution.")
    if target_warehouse_hc < manpower_output["warehouse"]:
        st.warning("Recommendation: keep warehouse and cold room staffing intact unless dispatch frequency or finished goods volume is reduced.")
    else:
        st.success("Recommendation: warehouse and cold room staffing can support the current dispatch plan.")

with st.expander("Reverse Distributor and GT Sales Planning", expanded=False):
    gt = channel_sales_output["general_trade"]
    target_gt_sales_executives = st.number_input("CEO GT Sales Executives", min_value=int(0), value=int(gt["sales_executives"]), step=int(1), key="reverse_gt_sales_exec")
    max_gt_revenue_supported = target_gt_sales_executives * gt["revenue_per_sales_executive"]
    outlet_coverage_supported = target_gt_sales_executives * gt["outlets_per_sales_executive"]
    calls_supported = target_gt_sales_executives * gt["calls_per_sales_executive_day"]
    gt_revenue_at_risk = max(0.0, gt["revenue"] - max_gt_revenue_supported)
    st.write("GT Sales Executives Reverse Planning")
    st.write(f"Maximum GT revenue supportable: {fmt_currency(max_gt_revenue_supported)}.")
    st.write(f"Outlet coverage supported: {outlet_coverage_supported:,.0f} outlets.")
    st.write(f"Calls/day supported: {calls_supported:,.0f}.")
    st.write(f"Market revenue at risk: {fmt_currency(gt_revenue_at_risk)}.")
    if target_gt_sales_executives < gt["sales_executives"]:
        st.warning("Recommendation: reduce GT revenue ambition, improve salesperson productivity, or restore field coverage before committing the plan.")
    else:
        st.success("Recommendation: GT sales coverage supports the current market plan.")

    target_mt_kam = st.number_input("CEO MT KAM", min_value=int(0), value=int(channel_sales_output["mt_kam"]), step=int(1), key="reverse_mt_kam")
    st.write("MT KAM Reverse Planning")
    if target_mt_kam < channel_sales_output["mt_kam"]:
        st.warning("Reducing MT ownership creates chain negotiation risk, listing delays, weaker promotion execution, claims backlog, and revenue at risk.")
    else:
        st.success("Recommendation: MT account ownership is protected for the current startup plan.")

    target_qcom_kam = st.number_input("CEO QCom KAM", min_value=int(0), value=int(channel_sales_output["qcom_kam"]), step=int(1), key="reverse_qcom_kam")
    st.write("QCom KAM Reverse Planning")
    if target_qcom_kam < channel_sales_output["qcom_kam"]:
        st.warning("Reducing QCom ownership creates platform fill-rate risk, dark-store stock-out risk, slower replenishment, weaker visibility, and revenue at risk.")
    else:
        st.success("Recommendation: QCom platform ownership is protected for the current startup plan.")

    target_horeca_sales = st.number_input("CEO HoReCa Sales HC", min_value=int(0), value=int(channel_sales_output["horeca_sales_hc"]), step=int(1), key="reverse_horeca_sales_hc")
    st.write("HoReCa Sales Reverse Planning")
    if target_horeca_sales < channel_sales_output["horeca_sales_hc"]:
        st.warning("Reducing HoReCa sales coverage slows account acquisition, sampling, repeat orders, and payment follow-up.")
    else:
        st.success("Recommendation: HoReCa coverage supports acquisition and repeat-order building.")

    target_inst_gov_manager = st.number_input("CEO Institutional / Government Manager", min_value=int(0), value=int(channel_sales_output["institution_government_manager"]), step=int(1), key="reverse_inst_gov_manager")
    st.write("Institutional / Government Reverse Planning")
    if target_inst_gov_manager < channel_sales_output["institution_government_manager"]:
        st.warning("Reducing this role creates tender ownership risk, slower government opportunity conversion, weaker documentation follow-up, and payment risk.")
    else:
        st.success("Recommendation: institutional and government ownership supports tenders, rate contracts, and collections follow-up.")

    distributor_choice = st.selectbox("Distributor Type", ["Frozen Raw", "Ready To Eat", "Shared Frozen + Ready To Eat Distribution Network"], key="reverse_distributor_type")
    distributor_map = {
        "Frozen Raw": ("frozen_raw_revenue", "frozen_raw_distributors", "frozen_revenue_capacity_per_distributor"),
        "Ready To Eat": ("rte_revenue", "rte_distributors", "rte_revenue_capacity_per_distributor"),
        "Shared Frozen + Ready To Eat Distribution Network": ("shared_frozen_rte_revenue_served", "shared_frozen_rte_distributors", "shared_frozen_rte_revenue_per_distributor"),
    }
    revenue_key, count_key, capacity_key = distributor_map[distributor_choice]
    target_distributors = st.number_input("CEO Distributor Count", min_value=int(0), value=int(distributor_output[count_key]), step=int(1), key="reverse_distributor_count")
    distributor_capacity = target_distributors * distributor_output[capacity_key]
    overload_value = max(0.0, distributor_output[revenue_key] - distributor_capacity)
    st.write("Distributor Reverse Planning")
    st.write(f"Revenue capacity per distributor: {fmt_currency(distributor_output[capacity_key])}.")
    st.write(f"Overloaded distributor capacity: {fmt_currency(overload_value)}.")
    st.write("Service frequency risk increases if planned revenue is forced through fewer distributors.")
    st.write("Cold-chain risk increases when distributor capacity is overloaded.")
    if target_distributors < distributor_output[count_key]:
        st.warning("Recommendation: do not reduce distributor count unless revenue, service frequency, or delivery geography is reduced.")
    else:
        st.success("Recommendation: distributor capacity supports the current market plan.")

log_section_start("Financial Planning")
st.markdown("<div class='pbos-section-card'>", unsafe_allow_html=True)
st.markdown("<div class='pbos-section-title'>Financial Planning</div>", unsafe_allow_html=True)
st.markdown("<div class='pbos-section-subtitle'>Revenue bridge from procurement to EBITDA and PAT.</div>", unsafe_allow_html=True)
chain_cols = st.columns(5)
with chain_cols[0]:
    render_kpi_card("Revenue", fmt_currency(revenue_rupees), subtitle="Starting point", icon_key="revenue")
with chain_cols[1]:
    render_kpi_card("Direct Variable Spend", fmt_currency(procurement_spend), subtitle="Bird + processing + packing + transport", icon_key="procurement_spend", button_label="View details", key="financial_procurement_driver_details", button_action=show_procurement_driver_drilldown)
with chain_cols[2]:
    render_kpi_card("Gross Contribution", fmt_currency(gross_contribution), subtitle="Gross contribution", icon_key="gross_contribution", value_class="negative" if gross_contribution < 0 else None)
with chain_cols[3]:
    render_kpi_card("EBITDA", fmt_currency(ebitda), subtitle="Operating profit", icon_key="ebitda", value_class="negative" if ebitda < 0 else None)
with chain_cols[4]:
    render_kpi_card("PAT", fmt_currency(pat), subtitle="Net profit", icon_key="pat", value_class="negative" if pat < 0 else None)
st.markdown("</div>", unsafe_allow_html=True)
log_section_end("Financial Planning")

log_section_start("CEO Recommendation")
st.markdown("<div class='pbos-section-card'>", unsafe_allow_html=True)
st.markdown("<div class='pbos-section-title'>CEO Recommendation</div>", unsafe_allow_html=True)
st.markdown("<div class='pbos-section-subtitle'>Concise executive view for the current operating plan.</div>", unsafe_allow_html=True)
horeca_pricing = channel_sales_output.get("horeca", {})
key_constraint = "Plant utilization requires expansion review." if plant_capacity_output['plant_utilization_pct'] > 85 else "Capacity is within the current operating range."
st.markdown(
        f"""
        <div class='pbos-ceo-summary'>
            <div class='pbos-ceo-row'><b>Current Plan:</b> {selected_plant_name} is serving {selected_market_name} with planned revenue of {fmt_currency(revenue_rupees)}.</div>
            <div class='pbos-ceo-row'><b>Key Constraint:</b> {key_constraint} Current utilization is {plant_capacity_output['plant_utilization_pct']:,.1f}%.</div>
            <div class='pbos-ceo-row'><b>Financial Signal:</b> Direct variable spend {fmt_currency(procurement_spend)}, gross contribution {fmt_currency(gross_contribution)}, EBITDA {fmt_currency(ebitda)}, PAT {fmt_currency(pat)}.</div>
            <div class='pbos-ceo-row'><b>Recommended Management Action:</b> Maintain staffing and cold-chain readiness, and monitor live-bird rate sensitivity. Current calculated pricing status is {horeca_pricing.get('pricing_status', 'Not Available')} at an achieved margin of {horeca_pricing.get('actual_margin_pct', 0.0):,.1f}%.</div>
        </div>
        """,
        unsafe_allow_html=True,
)
st.markdown("</div>", unsafe_allow_html=True)
log_section_end("CEO Recommendation")

st.caption(f"Current stage: {business_stage}. {stage['automation_note']}")
st.markdown(
        """
        <div class='pbos-footer'>
            <div><b>PBOS — Business Planning Operating System</b></div>
            <div>Version 1.0 MVP</div>
            <div>Created by Sumit Kumar Mukherjee</div>
            <div>© 2026 Sumit Kumar Mukherjee</div>
            <div>Live Demo: <a href='https://pbos-business-planning.streamlit.app' target='_blank'>https://pbos-business-planning.streamlit.app</a></div>
            <div>GitHub: <a href='https://github.com/fundusumit/PBOS' target='_blank'>https://github.com/fundusumit/PBOS</a></div>
        </div>
        """,
        unsafe_allow_html=True,
)
log_runtime_event("page_completion")

