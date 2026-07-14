# PBOS Copilot Operating Boundary

## 1. Purpose

PBOS is a governed Business Planning Operating System.

Copilot must operate as a controlled engineering agent, not as an autonomous redesign agent.

Every task must:

1. understand the stated business requirement;
2. identify the canonical calculation path;
3. patch the smallest controlling source;
4. preserve related working behaviour;
5. validate actual live output;
6. stop after the approved scope is complete.

---

## 2. Core Rule

Do not replace a dynamic model with a static value merely to pass one test.

Dynamic but non-linear is not the same as static.

Example:

Sales staffing must not scale directly and linearly with revenue.

Correct:

Revenue scenario
→ governed channel workload assumptions
→ outlets/accounts/distributors/territories/contracts
→ productivity-capacity formulas
→ recommended sales HC

Incorrect:

Revenue × fixed HC ratio

Also incorrect:

Hardcoded outlets/accounts/default HC that never change with the scenario

---

## 3. Canonical Architecture

All calculated outputs must follow:

Scenario Inputs
→ Calculation Engine
→ Canonical Output Object
→ UI Rendering

The Streamlit page must not independently rebuild business formulas.

The page may:

- format;
- label;
- display;
- provide controlled inputs.

The page must not:

- override canonical values;
- hardcode corrected outputs;
- rebuild manpower logic;
- create parallel recommendation logic;
- patch visible rows independently of the engine.

---

## 4. Single Source of Truth

Before editing, identify:

- canonical input;
- canonical calculation function;
- canonical output key;
- exact UI consumer.

Do not create:

- duplicate calculation helpers;
- page-level override dictionaries;
- emergency visible-row substitutions;
- hidden balancing values;
- multiple competing output fields.

If the UI displays an incorrect value, trace:

Input
→ engine function
→ output key
→ dataframe/card/dialog binding

Patch the first incorrect controlling point.

---

## 5. Requirement Preservation

For every task, write a requirement lock before editing:

### Requested Change

What must change.

### Must Remain Dynamic

Which values must continue reacting to scenarios.

### Must Not Change

Which modules, formulas and outputs are outside scope.

### Acceptance Example

At least two before/after scenarios.

No code change may begin before this lock is written in the agent response.

---

## 6. Sales Manpower Governance

Sales HC must be dynamic and non-linear.

### Prohibited

Sales HC = Revenue × fixed ratio

Sales HC permanently fixed to static defaults

Page-level hardcoded Sales HC

Revenue values displayed as operational workload

### Required Flow

Revenue and channel mix may influence planned commercial scale.

Commercial scale must resolve into governed workload drivers such as:

- GT target outlets;
- GT distributors;
- territories or beats;
- MT active accounts;
- Quick Commerce buying accounts and regions;
- HoReCa active accounts;
- institutional tenders/contracts;
- export buyers/markets;
- service frequency;
- account complexity.

Then:

Role HC
=
ceil(Operational Workload ÷ Effective Role Capacity)

### Revenue Behaviour

Revenue is a scenario signal, not the direct HC formula.

Revenue can change workload through explicit governed conversion assumptions.

Examples:

Higher GT revenue may require more outlets or distributor throughput.

Higher MT revenue may be absorbed by existing accounts before a new KAM is required.

Higher QCom revenue may increase regions or account complexity in steps.

Therefore HC should change in bands or when operational thresholds are crossed.

It must not:

- rise proportionately for every revenue increase;
- remain frozen for every revenue increase.

---

## 7. Scenario Behaviour Tests

Every dynamic calculation patch must test at least three scenarios.

Example for Sales:

### Scenario A

Revenue = ₹4 Cr

Operational workload:
- 400 outlets
- 6 distributors
- 8 MT accounts
- 3 QCom accounts

Expected HC:
calculated from workload capacity

### Scenario B

Revenue = ₹7 Cr

Same operational workload

Expected:
HC unchanged

### Scenario C

Revenue = ₹7 Cr

Operational workload increases:
- 600 outlets
- 8 distributors
- 12 MT accounts

Expected:
HC increases according to role-capacity thresholds

A two-scenario test proving only that HC remains unchanged is insufficient.

---

## 8. No Hardcoded Runtime Overrides

Do not insert logic similar to:

if function_name == "Sales":
    row = hardcoded_sales_row

Do not replace missing runtime values with fixed operational defaults inside the visible table renderer.

Defaults belong in governed assumptions or registries and must be scenario-aware.

The UI must render canonical engine outputs.

---

## 9. No Blind UI Patching

CSS and UI fixes must not alter business data.

Business logic fixes must not redesign the UI unless explicitly requested.

Do not solve:

- a calculation bug with a display override;
- a display bug with a calculation rewrite;
- a mobile layout issue with duplicated content;
- a binding issue with hardcoded values.

---

## 10. One Patch, One Objective

Every task must have one primary objective.

If another related issue is discovered:

1. record it;
2. report it separately;
3. do not patch it unless it blocks the approved objective or the user explicitly approved it.

Do not expand scope merely because another potential improvement was found.

---

## 11. Minimal Diff Rule

Before editing:

- inspect git status;
- confirm clean working tree;
- identify exact files;
- state expected diff.

After editing:

- run git diff --check;
- inspect exact diff;
- ensure no unrelated files changed.

Avoid 100-line rewrites for a one-line binding issue.

---

## 12. No Repeated Hypothesis Loop

Maximum workflow:

1. one primary hypothesis;
2. one cheap disconfirming test;
3. one patch;
4. one validation cycle.

If validation fails twice:

Stop editing.

Return:

- evidence gathered;
- exact unresolved path;
- recommended next diagnostic.

Do not continue creating successive speculative patches.

---

## 13. Temporary Debugging Rules

Temporary probes are allowed only when necessary.

They must:

- be clearly labelled;
- be removed before commit;
- never alter business output;
- never remain in production.

Do not repeatedly restart, clear caches and patch code without first proving whether the issue is engine, binding, state or deployment.

---

## 14. DataFrame and PyArrow Safety

Calculation data and display data must remain separate.

Numeric calculation dataframe:
- retains numeric dtypes.

Display dataframe:
- uses explicit strings where mixed human-readable values are required.

Do not place long text workload descriptions into a mostly numeric column without creating a dedicated display dataframe.

---

## 15. Live Validation Standard

Success requires validation of the actual visible component.

Do not claim success only because:

- unit tests pass;
- a helper exists;
- a field exists;
- compile passes;
- local engine output is correct.

For UI defects, validate:

- exact visible card/table/dialog;
- correct row;
- correct scenario;
- no duplicate output;
- mobile and desktop where relevant.

For scenario calculations, capture the exact displayed values for all required scenarios.

---

## 16. Deployment Standard

Local startup is not Streamlit Cloud redeployment.

Report separately:

- local validation;
- git push;
- cloud deployment;
- cloud UI verification.

Never claim cloud redeployment succeeded merely because localhost started.

---

## 17. Stop Conditions

Stop and ask for review when:

- requirement semantics are ambiguous;
- the requested fix conflicts with an existing architecture rule;
- more than two validation attempts fail;
- the patch requires changing unrelated modules;
- the only apparent solution is a page-level hardcoded override;
- canonical source cannot be identified.

---

## 18. Required Agent Response Before Coding

Before every patch, return:

1. requirement understood;
2. canonical source identified;
3. expected files;
4. protected behaviour;
5. acceptance scenarios;
6. one primary hypothesis.

Only then begin editing.

---

## 19. Required Final Response

Return:

1. requirement implemented;
2. canonical source changed;
3. scenario A result;
4. scenario B result;
5. scenario C result;
6. protected behaviour confirmed;
7. exact files changed;
8. tests;
9. live UI validation;
10. commit SHA;
11. push result;
12. cloud deployment result.

Do not provide long narration of every search and retry.

---

## 20. Current Locked Sales Requirement

The PBOS Sales manpower model must remain:

DYNAMIC
NON-LINEAR
WORKLOAD-DRIVEN
SCENARIO-AWARE
RECONCILED

It must not be:

REVENUE-LINEAR
STATIC
HARDCODED IN THE PAGE
DUPLICATED BETWEEN ENGINE AND UI

Current intended behaviour:

- changing revenue alone does not automatically change HC;
- changing revenue may change governed operational workload;
- when operational thresholds are crossed, HC changes;
- the visible workload must describe operational scale;
- the calculation engine remains the single authority.

---

## 21. Responsive UI Boundary

For any table or dialog UI fix:

1. trace the active renderer;
2. patch the active renderer only;
3. do not create a second parallel renderer;
4. validate desktop and mobile visible DOM;
5. prove duplicate visible renderer count is one;
6. stop after two failed validation attempts.

---

## 22. Display Data Boundary

Calculation fields and display fields must remain separate.

Numeric calculation fields must not be replaced with formatted strings.

Display dataframes must contain type-stable string columns.

Do not use UI formatting to alter business values.

---

## 23. Dialog Content Boundary

Long formulas, explanations and recommendations must wrap inside their container.

No fixed-height cell may truncate text.

No text may cross the dialog border.

---

## 24. Success Evidence

A UI fix is successful only when:

- the exact live dialog is tested;
- no clipped text remains;
- no horizontal overflow remains;
- no duplicate renderer is visible;
- desktop behavior is preserved.

---

## 25. Executive Detail Density Rule

Do not combine multiple business fields into one long display string when the
user needs to compare them.

For executive detail views:

- one concept per field;
- structured columns on desktop;
- stacked labelled fields on mobile;
- explanations separated from metrics;
- no dense pipe-separated paragraphs.
