# Security & Privacy Test Execution Records

## Test Record: SEC-001
- **Test ID:** SEC-001
- **Test Name:** Sensitive Payload Redaction in Validation Failures
- **Module:** `app/main.py` (`redact_scan_validation_errors`)
- **Category:** Security / Privacy
- **Execution Date:** 2026-11-24
- **Objective:** Verify that when oversized or malformed payloads fail Pydantic validation, the submitted string is completely excluded from the HTTP 422 error response.
- **Input:** Oversized payload containing sensitive marker `"CONFIDENTIAL_TEST_TOKEN_XYZ98765"` repeated 300 times.
- **Expected:** HTTP 422 response. Token does NOT appear in response body.
- **Actual:** HTTP 422 response. Token not present in response text. Detail array only contains `{type, loc, msg}` keys.
- **Status:** **PASS**
- **Evidence:** `QA/evidence/outputs/SEC-001_RUN-001.json`

---

## Test Record: SEC-002
- **Test ID:** SEC-002
- **Test Name:** Network Socket Air-Gap Isolation
- **Module:** `engine/urls.py`
- **Category:** Security / Network Isolation
- **Execution Date:** 2026-11-24
- **Objective:** Verify that URL structural analysis never opens network sockets or initiates DNS lookups.
- **Methodology:** Patched `socket.socket` and `socket.getaddrinfo` to raise `AssertionError` if invoked.
- **Input:** URLs with lookalikes, raw IPs, and shorteners (`http://sbi-kyc-update.xyz`, `http://192.168.1.1/login`, `bit.ly/abc`).
- **Expected:** Full analysis completes with zero socket exceptions.
- **Actual:** Zero socket exceptions. Zero network packets generated.
- **Status:** **PASS**
- **Evidence:** `QA/evidence/logs/pytest_run_RUN001_2026-11-24.txt` (covered by `test_url_analyser_does_not_touch_network`)
