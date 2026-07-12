# ADR-002: Registry-Driven Assumptions

- Status: Accepted
- Date: 2026-07-12
- Decision Owner: Founder / PBOS Product Owner
- Implementation Scope: Current CSV registry baseline and Streamlit session overrides

## Context

PBOS planning assumptions and metadata are maintained through CSV registries. The app also exposes sidebar controls that allow scenario adjustments during a Streamlit session.

## Decision

Keep baseline assumptions and business metadata in the existing registry CSV files instead of scattering baseline values across UI logic where registry support already exists.

Existing registries:

- business_assumptions.csv
- product_registry.csv
- channel_registry.csv
- pricing_registry.csv
- cost_registry.csv
- market_registry.csv
- plant_registry.csv
- formula_registry.csv
- dependency_registry.csv
- logic_registry.csv
- strategy_drivers.csv
- dashboard_data.csv

Explicit constraints for current MVP:

- Existing sidebar values may override registry defaults during a Streamlit session.
- Registry files define baseline assumptions and business metadata.
- No database or ERP is currently connected.
- Scenario inputs are planning assumptions, not live operational data.

## Current Implementation

The MVP loads baseline data from CSV files and applies user-supplied input changes during the current app run. Registry data remains the baseline source.

## Consequences

### Positive

- Baseline assumptions are centralized and auditable in version control.
- Scenario testing remains quick through session-level overrides.

### Trade-offs

- CSV governance is required to prevent accidental inconsistency.
- No direct transactional reconciliation exists because there is no connected ERP or database.

## Files Affected

- business_assumptions.csv
- product_registry.csv
- channel_registry.csv
- pricing_registry.csv
- cost_registry.csv
- market_registry.csv
- plant_registry.csv
- formula_registry.csv
- dependency_registry.csv
- logic_registry.csv
- strategy_drivers.csv
- dashboard_data.csv
- pages/Business_Requirement_Planning.py
- app.py

## Validation

- Verified the active registry set in the repository root.
- Confirmed current behavior: session controls can adjust scenario values without changing baseline registry files.
