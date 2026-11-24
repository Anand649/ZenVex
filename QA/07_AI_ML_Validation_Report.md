# AI/ML Validation & Experiment Report
**Project:** ZenVex Guard — AI-Powered Multilingual Scam & Digital Threat Intelligence Platform\
**QA Assessment Date:** 2026-11-24\
**Author:** Autonomous QA & AI/ML Validation Specialist\
**Validation Classification:** **VALIDATED WITH LIMITATIONS**\

---

## 1. Executive Summary

ZenVex Guard utilizes a hybrid classification architecture composed of:
1. A **12-Point Heuristic Rule Engine** with regex patterns spanning English, Telugu, Hindi, Romanised Telugu, and Romanised Hindi.
2. A **14-Point Offline URL Structural Isolation Analyzer**.
3. A priority-ordered **9 Indian Scam Playbook Correlation Engine**.
4. An optional **Machine Learning Baseline Scorer** (`app/ml/predictor.py` and `app/ml/train_baseline.py`) implementing a character n-gram TF-IDF vectorizer coupled with Logistic Regression.

This validation examines the data integrity, preprocessing consistency, model lifecycle, evaluation metrics, and independent verification.

---

## 2. Dataset Quality & Contamination Audit

### 2.1 Dataset Inventory

| Dataset File | Stated Purpose | Total Rows | Scam Labels (1) | Legit Labels (0) | Integrity Status |
|---|---|---|---|---|---|
| `backend/data/eval_set.csv` | Pipeline verification starter set | 42 | 22 (52.4%) | 20 (47.6%) | Valid, non-empty, synthetic |
| `backend/data/dev_set.csv` | Development training set | 0 | 0 | 0 | **EMPTY (Header only)** |
| `backend/data/heldout_set.csv` | Independent test evaluation | 0 | 0 | 0 | **EMPTY (Header only)** |

### 2.2 Data Quality Metrics (`eval_set.csv`)

- **Total Samples:** 42
- **Duplicate Records:** 0 (all sample IDs `s01`-`s22` and `l01`-`l20` are strictly unique)
- **Missing / Null Values:** 0 across all columns (`id`, `text`, `label`, `language`, `category`, `source`)
- **Class Balance:** 22 Scam vs 20 Legitimate (Balanced: 52.4% / 47.6%)
- **Language Distribution:**
  - English (`en`): 27 (64.3%)
  - Telugu Native (`te`): 5 (11.9%)
  - Romanised Telugu (`te-rom`): 4 (9.5%)
  - Hindi Native (`hi`): 3 (7.1%)
  - Romanised Hindi (`hi-rom`): 3 (7.1%)
- **Category Representation:** 17 distinct functional categories including `kyc` (5), `credential` (4), `delivery` (4), `otp` (4), `bank_alert` (4), `job` (3), `prize` (3), `bill` (2), `personal` (2), `marketing` (2), `travel` (2), `remote` (2), `digital_arrest` (1), `investment` (1), `payment` (1), `account` (1), `work` (1).
- **Source Provenance:** 100% of samples are tagged with `synthetic-starter`.

### 2.3 Contamination & Independence Finding
> [!WARNING]
> All 42 rows in `eval_set.csv` were crafted by the same engineering team while drafting the indicator regex patterns. Therefore, zero test samples represent an unseen, independent distribution. The empty state of `heldout_set.csv` means true out-of-distribution generalization has **not been independently measured**.

---

## 3. Preprocessing & Feature Extraction Analysis

### 3.1 Preprocessing Pipeline
1. **URL Masking (`_mask_urls`):** Replaces URL character spans with whitespace characters of identical length to prevent false positive regex triggers from URL paths while preserving precise character offsets.
2. **Regex Matching:** Case-insensitive multilingual matching against original offsets.
3. **Negation Guard (`_credential_matches`):** Looks back 30 characters for negation terms (`do not`, `never`, `dont`) to prevent safety warnings from triggering credential theft indicators.
4. **OTP Delivery Guard:** Differentiates between soft authorization verbs (`enter`, `verify`) when an OTP code is embedded in the same message versus credential exfiltration requests.

### 3.2 Preprocessing Defect: BUG-001 (APK Masking Maskout)
- **Defect Mechanism:** When an APK download link is analyzed in a message (e.g., `Download app apk from http://.../app.apk`), `_mask_urls()` strips the `.apk` extension inside the link. The lexicon pattern `\.apk\b` therefore fails to trigger on the masked text.
- **Consequence:** The message is classified under a secondary indicator (such as `prize_lottery`) instead of `remote_access`.
- **Recommendation:** Correlate URL structural flags (`apk_link`) directly with the playbook selector.

---

## 4. Model Training & Evaluation Metrics

### 4.1 Evaluation Execution (`scripts/evaluate.py`)
Executed on 2026-11-24:
```
Rows: 42  threshold: score >= 30  ML: off
Confusion  TP=22 FP=0 TN=20 FN=0
Precision=1.00 Recall=1.00 F1=1.00 False-positive rate=0.00
```

### 4.2 Confusion Matrix

| | Predicted Scam (1) | Predicted Legitimate (0) |
|---|---|---|
| **Actual Scam (1)** | **22 (TP)** | 0 (FN) |
| **Actual Legitimate (0)** | 0 (FP) | **20 (TN)** |

### 4.3 Sub-Group Breakdown

#### By Language
| Language | TP | FP | TN | FN | Recall | False Positive Rate |
|---|---|---|---|---|---|---|
| English (`en`) | 12 | 0 | 15 | 0 | 1.00 | 0.00 |
| Hindi Native (`hi`) | 2 | 0 | 1 | 0 | 1.00 | 0.00 |
| Romanised Hindi (`hi-rom`) | 2 | 0 | 1 | 0 | 1.00 | 0.00 |
| Telugu Native (`te`) | 3 | 0 | 2 | 0 | 1.00 | 0.00 |
| Romanised Telugu (`te-rom`) | 3 | 0 | 1 | 0 | 1.00 | 0.00 |

#### By Threat Category
- High-risk categories (`kyc`, `credential`, `digital_arrest`, `remote`, `job`, `prize`, `investment`, `payment`) all demonstrated 100% recall on the starter set.
- Legitimate categories (`bank_alert`, `otp`, `bill`, `delivery`, `marketing`, `personal`, `travel`) produced zero false positives.

---

## 5. Independent Metric Verification

The QA agent recalculated metrics independently using raw outputs and verified:
- **Accuracy:** \(\frac{22 + 20}{42} = 1.00\) (100.0%)
- **Precision:** \(\frac{22}{22 + 0} = 1.00\) (100.0%)
- **Recall:** \(\frac{22}{22 + 0} = 1.00\) (100.0%)
- **Specificity:** \(\frac{20}{20 + 0} = 1.00\) (100.0%)
- **F1-Score:** \(2 \times \frac{1.0 \times 1.0}{1.0 + 1.0} = 1.00\) (100.0%)

---

## 6. Machine Learning Model Lifecycle & Fallback

1. **Artifact Location:** `backend/models/baseline.joblib`
2. **Current State:** File does not exist on disk (intended for Level 1 baseline).
3. **Fallback Behavior:**
   - `predict_proba()` returns `None`.
   - `analyze_text(text, use_ml=True)` flags `ml_used: false` and computes risk based solely on rule and URL weights.
   - **Verification:** Verified via test `ML-002` and `ML-003`; zero runtime crashes or unhandled exceptions occurred.
4. **Training Script Verification:** `app/ml/train_baseline.py` incorporates character n-gram extraction (`char_wb`, ngrams 2 to 5) with balanced Logistic Regression. However, execution cannot take place until `dev_set.csv` is populated with real-world examples.

---

## 7. AI/ML Acceptance Classification

| Component | Status | Justification |
|---|---|---|
| Rule-Based Heuristic Engine | **VALIDATED WITH LIMITATIONS** | 100% precision/recall on starter dataset, but lacks independent held-out evaluation and exhibits URL-masking categorization bug on APK links. |
| Multilingual Language Detector | **VALIDATED** | Correctly distinguishes Latin, Devanagari, Telugu Unicode scripts and transliteration marker dictionaries without failure. |
| Machine Learning Subsystem | **NOT VALIDATED** | Model artifact not generated; `dev_set.csv` has 0 rows; runtime operates in fallback mode. |

**Overall AI/ML Classification: VALIDATED WITH LIMITATIONS**
