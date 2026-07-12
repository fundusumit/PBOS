# ADR-001: Current PBOS Architecture

- Status: Accepted
- Date: 2026-07-12
- Decision Owner: Founder / PBOS Product Owner
- Implementation Scope: Current PBOS MVP repository structure and runtime flow

## Context

PBOS currently runs as a Streamlit planning prototype. The repository already contains the app entry point, one primary planning page, one calculation engine module, and CSV registries used for baseline planning metadata and outputs.

## Decision

Use the current repository architecture as the accepted MVP baseline:

- app.py is the Streamlit entry point.
- pages/Business_Requirement_Planning.py is the primary planning interface.
- calculation_engine.py contains business calculations and planning outputs.
- CSV registries provide assumptions, product, channel, plant, pricing, cost, formula, logic, dependency, market, strategy, and dashboard data.
- Streamlit reruns calculations when live controls change.
- GitHub is the source-code and version-history repository.

Current executive page flow in the planning interface:

1. Corporate Summary
2. Channel Business Ownership
3. Market-specific Planning
4. Commercial & Distribution Planning
5. Plant Capacity Planning
6. Raw Material & Procurement Planning
7. Logistics Planning
8. Order & Capacity Intelligence
9. Manpower Planning
10. Financial Planning
11. CEO Recommendation

## Current Implementation

The MVP reflects a file-based architecture where Streamlit UI composition and interaction happen in pages/Business_Requirement_Planning.py, while formula and output logic is executed through calculation_engine.py and CSV-backed assumptions.

## Consequences

### Positive

- Clear entry-point and planning-page structure for MVP demonstration.
- Fast iteration using CSV-backed planning assumptions.
- Versioned architectural baseline in GitHub.

### Trade-offs

- Runtime state is session-oriented in Streamlit, not persisted in a transaction system.
- CSV-backed planning data requires controlled manual updates.

## Files Affected

- app.py
- pages/Business_Requirement_Planning.py
- calculation_engine.py
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

## Validation

- Verified repository structure and current section flow from existing PBOS MVP files.
- Confirmed this ADR documents implemented architecture only, without speculative modules.
