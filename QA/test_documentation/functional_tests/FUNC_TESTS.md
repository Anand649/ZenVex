# Functional Test Execution Records

## Test Record: FUNC-001
- **Test ID:** FUNC-001
- **Test Name:** Health Check Liveness
- **Module:** `app/main.py`
- **Category:** API / Functional
- **Execution Date:** 2026-11-24
- **Objective:** Verify that `/health` returns service operational status and version.
- **Preconditions:** FastAPI backend initialized.
- **Input:** `GET /health`
- **Expected Result:** HTTP 200 with `status: "ok"`, `platform: "ZenVex Guard"`.
- **Actual Result:** HTTP 200 with `{"status": "ok", "platform": "ZenVex Guard", "tagline": "Detect. Analyse. Protect.", "version": "1.0.0"}`.
- **Status:** **PASS**
- **Evidence:** `QA/evidence/logs/pytest_run_RUN001_2026-11-24.txt`

---

## Test Record: FUNC-002
- **Test ID:** FUNC-002
- **Test Name:** Text Scan Scam Message Execution
- **Module:** `engine/analyzer.py`
- **Category:** Functional / Integration
- **Execution Date:** 2026-11-24
- **Objective:** Verify analysis of high-risk KYC scam SMS text with embedded suspicious URL.
- **Input:** `Your account will be blocked today. Update KYC: http://sbi-kyc-update.xyz`
- **Expected Result:** HTTP 200 with `risk.band` in `caution|high|very_high`, `urls[0].reputation_checked == false`.
- **Actual Result:** Risk band `very_high`, score 82, `reputation_checked: false`.
- **Status:** **PASS**
- **Evidence:** `QA/evidence/logs/pytest_run_RUN001_2026-11-24.txt`

---

## Test Record: FUNC-003
- **Test ID:** FUNC-003
- **Test Name:** Malicious APK Download Playbook Association
- **Module:** `engine/rules.py` + `engine/lexicon.py`
- **Category:** Functional / Defect Discovery
- **Execution Date:** 2026-11-24
- **Objective:** Verify that an APK download message triggers the `remote_access` threat playbook.
- **Input:** `Download the SBI Reward app apk from http://sbi-rewards-claim.cfd/app.apk to redeem your reward points today.`
- **Expected Result:** `scam_type.id == "remote_access"`.
- **Actual Result:** `scam_type.id == "prize_lottery"`.
- **Status:** **FAIL**
- **Defect Reference:** `BUG-001`
- **Evidence:** `QA/evidence/outputs/T3_investigation_RUN001.json`
- **Analysis:** `_mask_urls()` strips the `.apk` string from the URL path prior to indicator evaluation, causing `.apk\b` regex to miss the pattern and falling back to `reward_bait`.

---

## Test Record: FUNC-024
- **Test ID:** FUNC-024
- **Test Name:** OTP Sharing Negation Guard
- **Module:** `engine/rules.py`
- **Category:** False Positive Guard
- **Execution Date:** 2026-11-24
- **Objective:** Verify security notices advising users *not* to share OTPs do not trigger credential theft indicators.
- **Input:** `Do not share your OTP with anyone`
- **Expected Result:** `credential_request` indicator NOT present.
- **Actual Result:** Zero indicators detected. Score = 0 (`low`).
- **Status:** **PASS**
- **Evidence:** `QA/evidence/logs/pytest_run_RUN001_2026-11-24.txt`

---

## Test Record: FUNC-025
- **Test ID:** FUNC-025
- **Test Name:** Legitimate Transactional Message Evaluation
- **Module:** `engine/rules.py` + `engine/risk.py`
- **Category:** False Positive Guard
- **Execution Date:** 2026-11-24
- **Objective:** Verify legitimate banking, shopping, and utility alerts are placed in the `low` risk band.
- **Input:** 5 standard legitimate notifications (Amazon order, Swiggy rider, HDFC netbanking OTP, salary credit, electricity bill reminder).
- **Expected Result:** `risk.band == "low"` across all 5 messages.
- **Actual Result:** All 5 messages evaluated as `risk.band == "low"`.
- **Status:** **PASS**
- **Evidence:** `QA/evidence/logs/pytest_run_RUN001_2026-11-24.txt`
