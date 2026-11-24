# Production readiness implementation

## Release packaging follow-up

`render.yaml` previously installed only backend dependencies under
`backend/`. It now builds from the repository root, installs the locked
frontend dependencies, and builds the bundle in `frontend/dist/` for the
existing FastAPI asset serving path. Uvicorn still starts from `backend/`.
The blueprint sets an empty cross-origin allowlist for its same-origin
deployment. A separate frontend origin would require an explicit allowlist.
`docs/BACKEND_RELEASE_RUNBOOK.md` records the updated packaging check.

Locally verified the parsed YAML, dependency installation, frontend build,
all 36 backend tests, and both packaged browser flows with the empty
allowlist. The Render build itself has not run. The frontend install still
reports one moderate and one high advisory. Dependency changes require
separate review. Held-out data, staging operational controls and first
deployment verification remain open.

## Backend priority pass

| Order | Task | Status and verification |
|---|---|---|
| 1 | Held-out evaluation | Blocked on independently authored and reviewed data and agreed release thresholds. The held-out file still contains only headers. The evaluator correctly rejected it with exit code 2. The starter run reproduced 22 true positives, 20 true negatives and zero errors across 42 rows. This is a regression result. |
| 2 | API contracts and edge cases | Complete. `backend/tests/test_api.py` now exercises inclusive limits and over-limit rejection for both scan routes, the existing HTTP 200 malformed URL report, playbook list/detail and unknown IDs, and stats field types. Previously these cases lacked API-level assertions. The existing engine test also blocks socket and DNS calls in the offline analyser. All 36 backend tests passed. API implementation and contracts are preserved. |
| 3 | Production protections and operations | Partial. `docs/BACKEND_RELEASE_RUNBOOK.md` records the ingress approach for body and rate limits, payload-free metrics, health checks and rollback. The packaged browser smoke test passed locally through Uvicorn in headless Edge. Actual limits, alerts, and packaging for the hosting platform need deployment configuration and a staging run. No quotas or runtime controls were assumed. |
| 4 | First deployment verification | Open release gate. The runbook records how to verify the deployed revision, CORS, scan behavior and payload exclusion across logs and monitoring. The service has not been deployed, so production checks remain unrun. |

Existing local changes were preserved. This pass changed only API tests and
release documentation.

| Priority item | Status | Before and after |
|---|---|---|
| P0 Dashboard claims | Implemented | `frontend/src/components/Dashboard.tsx` presented static samples as live telemetry and described low-risk scans as validated. It now labels the dataset as illustrative and describes low detected risk in terms of warning signs. `backend/app/main.py` and `frontend/src/services/api.ts` replace the unsupported benchmark with “Not measured.” The existing stats keys and types remain compatible. |
| P0 Scan privacy | Partial | FastAPI validation could echo rejected scan input. `backend/app/main.py` limits scan validation errors to type, location, and message. HTTP 422 and the detail array are preserved. `backend/tests/test_api.py` checks synthetic markers in malformed JSON, oversized values, wrong types, and captured application logs. `docs/API_CONTRACT.md` records the field change. |
| P1 Unicode highlights | Complete | `frontend/src/components/InvestigationReport.tsx` previously sliced UTF-16 strings with code-point offsets, shifting highlights after emoji. It now slices one code-point array per highlighted message. The API offset format and existing overlap handling are preserved. React rendering verified URL and indicator highlights after ASCII, emoji, and joined emoji prefixes. The frontend build and all 24 backend tests passed. |
| P1 UPI collect-request detection | Complete | The synthetic UPI refund example now scores 30, up from 15, and triggers the existing payment playbook. See the implementation and verification below. |
| P1 Browser CI and production CORS | Implemented | CI now builds the frontend and runs both scan flows in Chromium against the package served by FastAPI. CORS now honors the configured origin list. Deployment-specific verification remains a release gate. |
| Release-quality held-out evaluation | Partial | The evaluator now rejects empty datasets, reports language and category counts, and omits message excerpts from error output. The held-out CSV contains only headers. |
| Release end-to-end workflow verification | Partial | Both scan forms now have browser coverage for display and retry after an HTTP 503. Timeout, broader browser input validation, playbook and stats contract coverage, and native-language review remain open. |

### Browser outage recovery

`backend/scripts/browser_smoke.py` previously exercised only successful
submissions. It now simulates one HTTP 503 on each scan route, verifies the
visible error and enabled retry button, then removes the interception and
checks the real API response and rendered report. A temporary HTTP error
models service unavailability while keeping the packaged frontend loaded.
The check does not simulate network timeouts. The production application and
API are unchanged. Both flows passed locally in headless Edge.

### Held-out evaluation preparation

`backend/scripts/evaluate.py` previously printed zero-valued results for empty
datasets and included message excerpts for errors. It now exits with code 2
for an empty dataset, reports category counts alongside language counts, uses
`n/a` when a slice lacks a denominator, and identifies mistakes by row ID and
score. The CLI arguments, default dataset, and scoring behavior are preserved.
The 42-row starter result was unchanged and all 26 backend tests passed.

Use independently authored and reviewed labels, freeze the dataset and release
criteria before scoring, and keep tuning data separate. From `backend/`, run
`python scripts/evaluate.py --data data/heldout_set.csv` once the held-out set
is populated. Starter results remain regression checks.

The privacy review used the checked-in Render blueprint, which starts Uvicorn and
contains no body logging or monitoring configuration. Completing the audit requires
access to the deployed proxy, hosting logs, and any monitoring configuration.
The scan reports still return the submitted input on success for evidence highlighting.

### P1 UPI detection change

`backend/app/engine/lexicon.py` adds a 15-point English indicator for a
sentence-opening instruction to approve or accept a UPI collect request to
receive a refund in the same clause. This conservative pattern limits coverage
to direct instructions and provides a matched evidence span through the
existing pipeline. Scoring thresholds and the response schema are preserved.
`backend/tests/test_engine.py` verifies the positive case and protects low-risk
payment requests, refund notices, negated advice, and separate sentences.
All 26 tests passed. The 42-message starter evaluation moved from 21 to 22
true positives with 20 true negatives and zero false positives in both runs.
Held-out accuracy remains unverified.

### P1 browser CI and production CORS

`.github/workflows/ci.yml` previously ran backend checks only. It now installs
the locked frontend dependencies, builds the bundle, and runs
`backend/scripts/browser_smoke.py` in Chromium. The smoke test checks the text
and URL forms, their API responses, the rendered report, and a URL highlight
after emoji. Playwright is installed for CI only. The smoke test passed locally
using Edge, and all 26 backend tests passed. The hosted workflow has yet to run.

`backend/app/main.py` previously used a hardcoded wildcard. It now uses
`ZENVEX_CORS_ORIGINS` from `backend/app/config.py`. The default permits the
two Vite loopback origins on port 5173. For same-origin production, set the
variable to an empty value. For separately hosted clients, supply the exact
frontend origins as a comma-separated list. `.env.example` documents the setting.
Local preflight checks allowed a configured origin and rejected an unlisted
origin for both scan routes. Production origin verification awaits deployment.

### P0 privacy follow-up

Before this check, validation and captured application logs had been tested in
process. A local Uvicorn smoke test also exercised both scan routes over loopback,
using synthetic bodies. Both routes returned HTTP 200 for valid input and HTTP 422
for oversized input. The marker appeared in the successful reports as expected
and was absent from the rejected responses and captured server output. All 24
backend tests passed. This follow-up changes documentation only.

The project owner confirmed that ZenVex Guard has not been deployed. The local
P0 privacy checks are complete. The production audit is a release gate for the
first deployment, before accepting real submissions. Use synthetic markers on
both scan routes for successful and rejected requests. Confirm that rejected
responses omit the markers and that hosting logs, any proxy, monitoring, and
log drains do not capture submitted content.
