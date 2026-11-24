# AI/ML & Language Test Execution Records

## Test Record: ML-001
- **Test ID:** ML-001
- **Test Name:** Model Artifact Integrity Verification
- **Module:** `backend/models`
- **Category:** AI/ML Artifact
- **Execution Date:** 2026-11-24
- **Objective:** Check whether `models/baseline.joblib` is present or required.
- **Expected:** Level 1 design allows absence of ML model, falling back to heuristic rules.
- **Actual:** `models/baseline.joblib` is absent; directory contains only `.gitkeep`.
- **Status:** **PASS**
- **Evidence:** `QA/evidence/ML/ML-001/RUN-001_model_check.json`

---

## Test Record: ML-002
- **Test ID:** ML-002
- **Test Name:** Predictor Uninitialized Fallback
- **Module:** `app/ml/predictor.py`
- **Category:** AI/ML Inference
- **Execution Date:** 2026-11-24
- **Objective:** Verify `predict_proba()` returns `None` gracefully without crashing or throwing exceptions.
- **Input:** `"Your account will be blocked today"`
- **Expected:** `predict_proba(...) is None`.
- **Actual:** Returned `None`.
- **Status:** **PASS**
- **Evidence:** `QA/evidence/ML/ML-002/RUN-001_predict_none.json`

---

## Test Record: ML-004
- **Test ID:** ML-004
- **Test Name:** Independent Metric Calculation on Evaluation Set
- **Module:** `scripts/evaluate.py` + `data/eval_set.csv`
- **Category:** AI/ML Evaluation
- **Execution Date:** 2026-11-24
- **Objective:** Run evaluation script across 42 labelled synthetic instances.
- **Input:** `python scripts/evaluate.py --threshold 30`
- **Expected:** Metrics successfully calculated across languages and categories.
- **Actual:** TP=22, FP=0, TN=20, FN=0. Precision=1.00, Recall=1.00, F1=1.00, FPR=0.00.
- **Status:** **PASS**
- **Evidence:** `QA/evidence/ML/ML-004/RUN-001_eval_output.txt`
- **Limitation Note:** 100% metrics reflect rule-calibration on team-written starter data, not real-world generalization.

---

## Test Record: ML-006
- **Test ID:** ML-006
- **Test Name:** Development & Held-out Dataset Population Check
- **Module:** `backend/data/`
- **Category:** Dataset Inventory
- **Execution Date:** 2026-11-24
- **Objective:** Verify that `dev_set.csv` and `heldout_set.csv` contain training and independent validation samples.
- **Expected:** Row count > 0 in both files.
- **Actual:** Both files contain 0 data rows (header only).
- **Status:** **FAIL**
- **Evidence:** `QA/evidence/ML/ML-006/RUN-001_dataset_check.txt`
- **Impact:** Model retraining and independent validation are blocked until datasets are populated.
