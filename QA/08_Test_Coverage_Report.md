# Test Coverage & Quality Dashboard Report

> Historical RUN-001 snapshot. The v1 playbook contract disposition was corrected after this run. See [QA review notes](README.md) for the current disposition. Original aggregate results are retained as recorded.

**Project:** ZenVex Guard\
**Date:** 2026-11-24\
**Author:** Autonomous QA & Test Automation Specialist\

---

## 1. Test Coverage Executive Dashboard

```
┌─────────────────────────────────────────────────────────────┐
│                   ZENVEX GUARD QA DASHBOARD                 │
├──────────────────────────────┬──────────────────────────────┤
│ Total Identified Test Cases  │ 48                           │
│ Total Tests Executed         │ 48                           │
│ Total Tests Passed           │ 45                           │
│ Total Tests Failed           │ 2 (FUNC-003, ML-006)         │
│ Total Tests Needing Review   │ 1 (API-007 / FUNC-012)       │
│ Total Tests Blocked          │ 0                            │
│ Total Open Defects           │ 3 (BUG-001, BUG-002, BUG-003)│
│ Total Resolved Defects       │ 0 (Authorization Required)   │
└──────────────────────────────┴──────────────────────────────┘
```

---

## 2. Key Quality Metrics & Formulas

### 2.1 Execution Coverage
\[
\text{Execution Coverage} = \left( \frac{\text{Executed Test Cases}}{\text{Total Identified Test Cases}} \right) \times 100
\]
\[
\text{Execution Coverage} = \left( \frac{48}{48} \right) \times 100 = \mathbf{100.0\%} \quad (48 / 48)
\]

### 2.2 Test Pass Rate
\[
\text{Pass Rate} = \left( \frac{\text{Passed Test Cases}}{\text{Executed Test Cases}} \right) \times 100
\]
\[
\text{Pass Rate} = \left( \frac{45}{48} \right) \times 100 = \mathbf{93.75\%} \quad (45 / 48)
\]

### 2.3 Requirement Coverage
\[
\text{Requirement Coverage} = \left( \frac{\text{Requirements with } \ge 1 \text{ Mapped Test}}{\text{Total Identified Requirements}} \right) \times 100
\]
\[
\text{Requirement Coverage} = \left( \frac{46}{46} \right) \times 100 = \mathbf{100.0\%} \quad (46 / 46)
\]

### 2.4 Defect Resolution Rate
\[
\text{Defect Resolution Rate} = \left( \frac{\text{Resolved Defects}}{\text{Total Identified Defects}} \right) \times 100
\]
\[
\text{Defect Resolution Rate} = \left( \frac{0}{3} \right) \times 100 = \mathbf{0.0\%} \quad (0 / 3)
\]
*(Note: Per QA protocol rules, source code modifications require user authorization and were deliberately withheld during testing).*

---

## 3. Coverage by Subsystem & Module

| Module / Component | Identified Tests | Executed Tests | Passed | Failed | Review | Status |
|---|---|---|---|---|---|---|
| **API Endpoints & Routing** (`app/main.py`) | 12 | 12 | 11 | 0 | 1 | Partially Tested |
| **Pydantic Schemas & Boundaries** (`app/schemas.py`) | 6 | 6 | 6 | 0 | 0 | Fully Tested |
| **Heuristic Indicator Rules** (`engine/rules.py`) | 12 | 12 | 11 | 1 | 0 | Partially Tested (Bug Found) |
| **Offline URL Structural Sandbox** (`engine/urls.py`) | 7 | 7 | 7 | 0 | 0 | Fully Tested |
| **Multilingual Script Processor** (`engine/language.py`)| 5 | 5 | 5 | 0 | 0 | Fully Tested |
| **Scam Playbooks & Correlation** (`engine/playbooks.py`) | 3 | 3 | 2 | 1 | 0 | Partially Tested |
| **Risk Scoring & Explanations** (`engine/risk.py`) | 4 | 4 | 4 | 0 | 0 | Fully Tested |
| **Machine Learning Predictor** (`app/ml/predictor.py`) | 4 | 4 | 3 | 1 | 0 | Partially Tested (Data Gap) |
| **Data Quality & Contamination** (`data/`) | 3 | 3 | 2 | 1 | 0 | Partially Tested (Empty Sets)|
| **Frontend Production Build** (`frontend/src`) | 1 | 1 | 1 | 0 | 0 | Fully Tested |
| **System Performance & Latency** | 1 | 1 | 1 | 0 | 0 | Fully Tested |
| **Stateless Security & Data Redaction** | 2 | 2 | 2 | 0 | 0 | Fully Tested |
| **Regression Suite** | 1 | 1 | 1 | 0 | 0 | Fully Tested |

---

## 4. Analysis of Failed & Review Scenarios

1. **FUNC-003 (Failed - BUG-001):**
   - *Scenario:* Detection of APK link scam vector in messages.
   - *Impact:* Misclassification of threat playbook from `remote_access` to `prize_lottery`.
2. **ML-006 (Failed - Data Gap):**
   - *Scenario:* Population of `dev_set.csv` and `heldout_set.csv`.
   - *Impact:* Prevents training ML baseline and evaluating real-world generalization on unseen data.
3. **API-007 / FUNC-012 (Needs Review - BUG-002):**
   - *Scenario:* Querying an unknown playbook ID at `/api/v1/playbooks/{id}`.
   - *Impact:* Returns HTTP 200 with `{"error": "Playbook not found"}` instead of standard REST HTTP 404.
