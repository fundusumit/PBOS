# PBOS Business Requirement Planning

PBOS Business Requirement Planning is a current working Streamlit planning prototype for poultry business planning.

## Live Demo

https://pbos-business-planning.streamlit.app

## Creator

Sumit Kumar Mukherjee
Founder & Product Architect

## Public Demo Status

Current working planning prototype.
Scenario values are planning assumptions and are not live ERP data.

## Portfolio Summary

PBOS is a scenario-based business planning platform built in Python and Streamlit. It connects revenue targets with channel allocation, plant capacity, procurement, logistics, manpower and profitability, while allowing users to test planning scenarios through interactive controls.

The application currently covers:

- corporate revenue planning
- channel business ownership
- market-specific planning
- commercial and distribution planning
- plant-capacity planning
- raw-material and procurement planning
- logistics planning
- manpower planning
- financial planning
- order and capacity scenario intelligence

## Current Status

Current working planning prototype. Scenario values are planning assumptions and are not live ERP data.

## Technology

- Python
- Streamlit
- pandas
- Plotly
- CSV registries and planning data

## Run Locally

```bash
python -m streamlit run app.py
```

## Project Structure

- `app.py` - main Streamlit entry point for the PBOS business plan dashboard.
- `pages/Business_Requirement_Planning.py` - Streamlit page for business requirement planning.
- `calculation_engine.py` - planning calculations and output contracts.
- `dashboard_data.csv` - exported dashboard KPI data.
- `strategy_drivers.csv` - exported scenario driver data.
- `business_assumptions.csv` - business planning assumptions.
- `product_registry.csv` - product planning registry.
- `channel_registry.csv` - channel planning registry.
- `pricing_registry.csv` - channel/product pricing registry.
- `cost_registry.csv` - cost assumption registry.
- `market_registry.csv` - market planning registry.
- `plant_registry.csv` - plant planning registry.
- `formula_registry.csv` - formula and KPI explanation registry.
- `dependency_registry.csv` - KPI dependency registry.
- `logic_registry.csv` - business logic registry.
- `AGENTS.md` - local agent/project instructions.

## Architecture Decisions

Architecture decisions for the current PBOS MVP are documented in:

- docs/adr/README.md
