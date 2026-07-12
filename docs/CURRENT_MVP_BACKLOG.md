# CURRENT MVP Backlog

## 1. Audit all View-details output contracts

Issue title:
Audit all View-details output contracts

Scope:
Review existing View-details dialogs and confirm required output keys are present and consistent with engine output contracts.

Acceptance criteria:

- Every existing View-details dialog opens without runtime key errors.
- Missing key defects are mapped to source output contracts.
- No fallback invented values are introduced to mask missing contracts.

Suggested milestone:
MVP Stabilization

## 2. Validate live sidebar revenue binding across all sections

Issue title:
Validate live sidebar revenue binding across all sections

Scope:
Verify revenue target and core sidebar inputs propagate consistently to existing section outputs.

Acceptance criteria:

- Revenue target changes are reflected across existing planning sections.
- Channel and product demand outputs remain internally consistent.
- No stale binding remains in current implemented sections.

Suggested milestone:
MVP Stabilization

## 3. Validate channel × product tonnage consolidation

Issue title:
Validate channel × product tonnage consolidation

Scope:
Validate consolidation logic for planned tonnage across channel and product dimensions.

Acceptance criteria:

- Consolidated tonnage totals reconcile with displayed planning outputs.
- Section-level and summary-level tonnage values align.
- No duplicate counting in current MVP flow.

Suggested milestone:
MVP Stabilization

## 4. Correct and validate GT distributor/outlet-coverage presentation

Issue title:
Correct and validate GT distributor/outlet-coverage presentation

Scope:
Review GT planning presentation and distributor or outlet-coverage clarity in current cards and dialogs.

Acceptance criteria:

- GT coverage metrics and explanations are consistent.
- Distributor or outlet-coverage presentation is understandable and non-duplicative.
- Existing functionality remains unchanged outside correction scope.

Suggested milestone:
Current MVP Presentation Polish

## 5. Correct Quick Commerce platforms versus dark-store presentation

Issue title:
Correct Quick Commerce platforms versus dark-store presentation

Scope:
Improve clarity for currently rendered Quick Commerce platform assumptions versus dark-store related wording.

Acceptance criteria:

- Quick Commerce terminology is internally consistent.
- Current planning assumptions are clearly represented.
- No new module is introduced.

Suggested milestone:
Current MVP Presentation Polish

## 6. Validate planned versus scenario daily capacity comparison

Issue title:
Validate planned versus scenario daily capacity comparison

Scope:
Validate currently implemented planned-demand versus scenario-demand capacity comparison outputs.

Acceptance criteria:

- Capacity gap or surplus values reconcile with displayed demand and capacity inputs.
- Scenario utilization and status signals match current formulas.
- No claim of confirmed ERP order ingestion is introduced.

Suggested milestone:
MVP Stabilization

## 7. Validate manpower threshold bands

Issue title:
Validate manpower threshold bands

Scope:
Review existing manpower threshold behavior and status interpretation in current manpower outputs.

Acceptance criteria:

- Threshold bands produce stable and explainable status outputs.
- Manpower recommendations are aligned with current implemented logic.
- No additional manpower module is added.

Suggested milestone:
MVP Stabilization

## 8. Verify Linux/cloud file-path compatibility

Issue title:
Verify Linux/cloud file-path compatibility

Scope:
Check current path handling and data loading assumptions for Linux/cloud deployment.

Acceptance criteria:

- Existing app loads required files in a Linux/cloud runtime.
- No absolute local path dependency remains in startup path.
- Current MVP behavior is preserved.

Suggested milestone:
Shareable Demo

## 9. Deploy PBOS to Streamlit Community Cloud

Issue title:
Deploy PBOS to Streamlit Community Cloud

Scope:
Deploy current main branch and validate startup from requirements and current file set.

Acceptance criteria:

- App deploys from main branch.
- Initial page loads without blocking runtime errors.
- Public URL is available for demo testing.

Suggested milestone:
Shareable Demo

## 10. Perform external demo smoke test

Issue title:
Perform external demo smoke test

Scope:
Run a focused smoke test of current implemented planning and scenario flows as an external viewer.

Acceptance criteria:

- Core sections and current View-details dialogs open successfully.
- Baseline and scenario interactions can be executed end-to-end.
- Findings are documented as current-MVP issues where needed.

Suggested milestone:
Shareable Demo
