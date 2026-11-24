# Backend release runbook

## Staging handoff

The current local release candidate passed all 36 backend tests and the
packaged Edge smoke test with an empty CORS allowlist on 24 November 2026.
Uvicorn served the React index and built assets, and both scans recovered from
an intercepted HTTP 503 and completed against the real API. The release
candidate includes uncommitted changes and has no deployed revision yet.

Before deploying, identify the authorized staging workspace and service,
review and publish the exact candidate revision, and confirm how staging
access is restricted. Keep tests synthetic. Confirm which ingress and
observability tools are available before configuring limits and alerts.

## Before opening traffic

1. Build the frontend with the lockfile and run the backend suite and
   packaged browser smoke test. Confirm the deployment artifact contains
   `frontend/dist/index.html` and its assets where FastAPI expects them.
   The Render blueprint builds from the repository root, installs backend
   requirements, and builds the locked frontend. It starts Uvicorn from
   `backend/`. Verify the built assets on staging because FastAPI's static
   fallback can otherwise mask a missing build.
2. Confirm the deployed revision and configure the platform health check to
   use `GET /health`. Expect HTTP 200 and `status: ok`. Use synthetic scans
   as separate readiness checks for the end-to-end flow.
3. Set `ZENVEX_CORS_ORIGINS` to an empty value for same-origin hosting, or
   list exact frontend origins for split hosting. Verify browser scans and,
   for cross-origin requests, preflight responses for one allowed and one
   unlisted origin.

## Production controls to configure and verify

- **Body limit.** Enforce the byte limit at the ingress before forwarding to
  FastAPI. Choose it using the largest supported JSON payload, including
  Unicode escaping and envelope bytes. The application field limits count
  characters, so the numbers cannot be reused as byte limits. Test accepted
  boundary payloads and confirm oversized bodies receive HTTP 413 without
  exposing submitted content. Preserve HTTP 422 for field validation within
  the body limit.
- **Rate limit.** Use shared ingress enforcement for the two scan routes so
  limits apply across workers without adding application state. Select the
  quota and burst from expected traffic and measured capacity. Verify that a
  staging burst receives HTTP 429 and that traffic recovers after the window.
- **Operational metrics.** Use hosting or ingress metrics for counts, latency
  and errors. Group by route template, method and status class. Keep scan
  bodies, scanned URLs, query strings and credentials out of logs, metrics,
  traces and their labels. Choose alert thresholds after measuring staging
  traffic. Inspect the actual metrics and log settings before release.

The production topology, expected traffic and provider capabilities are needed
to choose limits and alert thresholds. Keep this gate open until those values
are configured and verified in a deployment.

## Synthetic deployment check and rollback

1. Run successful text and URL scans with unique synthetic markers, then send
   rejected requests to both routes. Verify normal reports, HTTP 422 responses
   without marker echoes, and `reputation_checked: false` for URL results.
   Search the test time window for the markers across hosting, any reverse
   proxy, error monitoring, traces and log drains. Confirm payload capture is
   disabled. Record the revision, UTC time window, statuses and each layer's
   result without including real submissions.
2. Before release, record the last known-good artifact and its configuration.
   If health, scan, or privacy checks fail, keep traffic closed or use the
   hosting platform to restore that artifact and settings. Recheck health,
   both scan flows, CORS and privacy before reopening traffic. On a first
   release with no previous artifact, keep traffic closed until a corrected
   release passes.
