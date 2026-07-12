# ADR-004: Planning vs Order Scenario

- Status: Accepted
- Date: 2026-07-12
- Decision Owner: Founder / PBOS Product Owner
- Implementation Scope: Current planning baseline and order-scenario simulation behavior

## Context

PBOS supports baseline planning and optional scenario testing in the same interface. Scenario controls are used for planning analysis and capacity interpretation, not confirmed transactional execution.

## Decision

Maintain the current distinction between planning baseline and order scenario simulation.

Planning includes:

- corporate revenue target
- channel mix
- product mix
- planned channel revenue
- planned channel and product volume
- plant and resource requirement

Order Scenario includes current implemented behavior:

- no scenario by default
- achievement-percentage or manual-order simulation where implemented
- scenario values are not confirmed ERP purchase orders
- scenario demand is compared with available plant capacity and scenario inventory assumptions
- signals explain overachievement, underachievement, capacity pressure, and underutilization

## Current Implementation

The sidebar includes Order Scenario Testing controls. The Order & Capacity Intelligence section compares planned demand with scenario demand, available inventory, and plant capacity, and then renders status and recommendations.

## Consequences

### Positive

- Enables stress-testing of plan assumptions without claiming operational order truth.
- Supports capacity and inventory impact interpretation within the MVP.

### Trade-offs

- Scenario analysis is simulation-oriented and must not be treated as live order ingestion.
- Scenario quality depends on user-entered assumptions.

## Files Affected

- pages/Business_Requirement_Planning.py
- calculation_engine.py
- strategy_drivers.csv
- dashboard_data.csv

## Validation

- Confirmed existing Order Scenario modes and explanatory text in current PBOS page logic.
- Confirmed language excludes ERP order ingestion claims.
