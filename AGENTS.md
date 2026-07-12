# PBOS Agent Instructions

Project: PBOS — Business Planning Operating System

This is not a generic dashboard. It is a Streamlit presentation layer over a Google Sheets business planning model.

## Architecture

Google Sheets is the source of truth.

dashboard_data.csv is exported from Google Sheets and contains KPI outputs.

strategy_drivers.csv is exported from Google Sheets and contains scenario inputs.

app.py is the Streamlit presentation layer.

## Rules

1. Do not redesign the architecture.
2. Do not replace Streamlit.
3. Do not introduce a database.
4. Do not introduce APIs unless explicitly requested.
5. Do not change CSV schemas without approval.
6. Preserve KPI meanings and business calculations.
7. Prefer small patches over full rewrites.
8. Review before modifying.
9. Keep the app runnable with:

```bash
python -m streamlit run app.py
```