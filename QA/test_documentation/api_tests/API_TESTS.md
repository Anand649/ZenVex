# API Test Execution Records

## Test Record: API-001
- **Test ID:** API-001
- **Route:** `GET /health`
- **Category:** API Liveness
- **Execution Date:** 2026-11-24
- **Objective:** Verify health check returns valid JSON with platform name and version.
- **Expected:** Status 200, valid JSON.
- **Actual:** `{"status": "ok", "platform": "ZenVex Guard", "tagline": "Detect. Analyse. Protect.", "version": "1.0.0"}`.
- **Status:** **PASS**
- **Evidence:** `QA/evidence/logs/pytest_run_RUN001_2026-11-24.txt`

---

## Test Record: API-004
- **Test ID:** API-004
- **Route:** `POST /api/v1/scan/url`
- **Category:** API Input Validation
- **Execution Date:** 2026-11-24
- **Objective:** Verify submitting non-string data types to the URL scanner returns HTTP 422 without echoing submitted data.
- **Input:** `{"url": {"value": "synthetic-marker"}}`
- **Expected:** Status 422, detail only containing type/loc/msg.
- **Actual:** HTTP 422, detail: `[{"type": "string_type", "loc": ["body", "url"], "msg": "Input should be a valid string"}]`.
- **Status:** **PASS**
- **Evidence:** `QA/evidence/logs/pytest_run_RUN001_2026-11-24.txt`

---

## Test Record: API-007
- **Test ID:** API-007
- **Route:** `GET /api/v1/playbooks/{playbook_id}`
- **Category:** API Contract & Design
- **Execution Date:** 2026-11-24
- **Objective:** Verify response when an unlisted playbook ID is requested.
- **Input:** `GET /api/v1/playbooks/nonexistent_id`
- **Expected:** HTTP 404 per standard REST conventions.
- **Actual:** HTTP 200 with body `{"error": "Playbook not found"}`.
- **Status:** **NEEDS REVIEW**
- **Defect Reference:** `BUG-002`
- **Evidence:** `QA/evidence/outputs/T11_playbook_404_RUN001.json`
- **Recommendation:** Change handler to raise `HTTPException(status_code=404, detail="Playbook not found")`.

---

## Test Record: API-008
- **Test ID:** API-008
- **Route:** `GET /api/v1/stats`
- **Category:** Telemetry Consistency
- **Execution Date:** 2026-11-24
- **Objective:** Validate mathematical integrity of threat distribution percentages.
- **Expected:** Percentages across all categories sum to 100%.
- **Actual:** `38 + 25 + 17 + 9 + 6 + 5 = 100%`.
- **Status:** **PASS**
- **Evidence:** `QA/evidence/outputs/T10_stats_RUN-001.json`
