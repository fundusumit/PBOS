# ADR-005: Streamlit Presentation Layer

- Status: Accepted
- Date: 2026-07-12
- Decision Owner: Founder / PBOS Product Owner
- Implementation Scope: Current Streamlit-based MVP interface and dependencies

## Context

PBOS currently presents planning outputs through Streamlit with KPI cards, detail dialogs, and sidebar controls.

## Decision

Keep Streamlit as the current presentation layer for this MVP.

Current-state statements:

- Streamlit is the current user interface.
- KPI cards summarize planning outputs.
- View-details dialogs provide calculation and business explanations.
- Sidebar inputs drive planning and scenario changes.
- The current application is a planning prototype.
- It is not presently an ERP, transaction engine, or live production system.

Current dependencies in this repository:

- streamlit
- pandas
- plotly

## Current Implementation

The planning interface renders sectioned KPI cards and dialog-based details, with sidebar controls feeding scenario recalculation in-session.

## Consequences

### Positive

- Fast MVP iteration with low setup overhead.
- Clear demonstration surface for planning outputs.

### Trade-offs

- Streamlit session behavior is not equivalent to transactional enterprise workflow execution.
- Prototype usability and governance still depend on disciplined output-contract handling.

## Files Affected

- app.py
- pages/Business_Requirement_Planning.py
- requirements.txt

## Validation

- Confirmed dependency list from requirements.txt.
- Confirmed sidebar, KPI card, and View-details patterns in the current planning page.
