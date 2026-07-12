# CURRENT MVP Milestones

## Milestone 1 — MVP Stabilization

Purpose:
Ensure the existing app loads and all current controls and View-details actions work without runtime errors.

Candidate issues:

- Audit View-details output contracts.
- Correct remaining stale sidebar-to-engine bindings.
- Validate revenue-to-channel/product-tonnage chain.
- Validate GT distributor planning presentation.
- Validate Quick Commerce platform assumptions.
- Confirm manpower threshold behaviour.
- Confirm currency and icon rendering.
- Confirm requirements and deployment startup.

Exit criteria:

- clean initial app load;
- no known ImportError or KeyError in existing dialogs;
- compile checks pass;
- critical scenario paths tested.

## Milestone 2 — Shareable Demo

Purpose:
Deploy and verify the current PBOS Streamlit prototype.

Candidate issues:

- deploy main branch on Streamlit Community Cloud;
- validate app startup from requirements.txt;
- verify registries load in Linux/cloud environment;
- test current planning inputs;
- test View-details dialogs;
- test order scenario;
- prepare one stable demo configuration.

Exit criteria:

- public Streamlit URL works;
- app can be opened by an external viewer;
- no local absolute path dependency;
- README includes the verified demo URL.

## Milestone 3 — Current MVP Presentation Polish

Purpose:
Improve only the clarity of existing outputs after deployment stability.

Candidate issues:

- consistent KPI labels and units;
- clearer planned-versus-scenario language;
- section-specific icons;
- no duplicate KPI presentation;
- concise CEO recommendations;
- consistent Not Connected versus known-zero presentation.

Exit criteria:

- existing dashboard is presentation-ready;
- no additional business module is introduced.
