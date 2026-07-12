# ADR-003: Calculation Engine Separation

- Status: Accepted
- Date: 2026-07-12
- Decision Owner: Founder / PBOS Product Owner
- Implementation Scope: Separation of calculation logic and UI rendering in current PBOS MVP

## Context

PBOS currently separates business-calculation functions from Streamlit UI composition. The planning page imports and consumes outputs from the engine module.

## Decision

Retain the existing separation of responsibilities:

- calculation_engine.py owns business formulas and output construction.
- pages/Business_Requirement_Planning.py binds user inputs, calls calculation functions, and renders outputs and details.

Governance rule for current MVP:

- Business formulas should not be recreated independently inside KPI-card rendering.
- UI presentation should consume stable engine outputs.
- Missing output keys should be corrected at the output-contract source instead of hidden through invented UI values.

## Current Implementation

The planning page calls engine functions and validates required keys before rendering. Drilldowns and KPI cards display values from output contracts.

## Consequences

### Positive

- Formula ownership is centralized.
- UI and business logic are easier to validate independently.
- Output-contract defects can be fixed at source.

### Trade-offs

- Output schema changes require disciplined coordination between engine and UI.
- Contract mismatches can block rendering until corrected.

## Files Affected

- calculation_engine.py
- pages/Business_Requirement_Planning.py

## Validation

- Confirmed engine imports and usage patterns in the existing planning page.
- Confirmed this ADR records architecture governance only and does not refactor code.
