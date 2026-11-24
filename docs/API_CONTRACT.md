# API Contract (v1)

Source of truth for shapes: `backend/app/schemas.py`. Change both together. Interactive docs when running: `/docs`.

Base path: `/api/v1`. All bodies are JSON (UTF-8). The API is stateless; nothing is stored.

## Endpoints

| Method | Path | Purpose | Status |
|---|---|---|---|
| GET | `/health` | Liveness check | built |
| POST | `/api/v1/scan/text` | Analyse a pasted message | built |
| POST | `/api/v1/scan/url` | Analyse a single link (structure only) | built |
| GET | `/api/v1/examples` | Demo messages for the UI | built |
| POST | `/api/v1/scan/image` | OCR then analyse a screenshot | planned L2 |
| POST | `/api/v1/feedback` | Opt-in "correct / incorrect" | planned L2 |

Scan results are **not retrievable** by id (`GET /api/v1/scan/{id}` returns 404 by design).

## POST /api/v1/scan/text

Request
```json
{ "text": "Dear Customer, your bank account will be blocked today due to incomplete KYC. Update immediately: http://sbi-kyc-update.xyz" }
```
Rules: `text` required, not blank, at most 5000 characters. Violations return `422`.

Response (`200`, abridged)
```json
{
  "scan_id": "a1b2c3d4e5f6",
  "input_type": "text",
  "text": "...",
  "language": "en",
  "risk": {
    "score": 100, "band": "very_high", "label": "Very high risk",
    "breakdown": { "text": 52, "url": 50, "ml": 0 },
    "disclaimer": "This score summarises detected warning signs. It is not a probability of fraud."
  },
  "scam_type": { "id": "kyc_account_block", "label": "KYC or account-block impersonation" },
  "indicators": [
    { "id": "account_threat", "label": "Threatens to block, suspend or close an account or service",
      "weight": 20, "evidence": ["account will be blocked"] }
  ],
  "urls": [
    { "url": "http://sbi-kyc-update.xyz", "host": "sbi-kyc-update.xyz",
      "registered_domain": "sbi-kyc-update.xyz", "verdict": "suspicious", "score": 70,
      "flags": [ { "id": "brand_mismatch", "label": "...", "weight": 35 } ],
      "official_domain_match": false, "reputation_checked": false,
      "note": "Structure-only check. The link was not opened ..." }
  ],
  "spans": [ { "start": 98, "end": 123, "kind": "url", "id": "url" } ],
  "explanation": { "text": "This message resembles: ...", "source": "template" },
  "actions": [ { "en": "Do not open links or call numbers in this message.", "te": "..." } ],
  "helplines": { "cybercrime_helpline": "1930", "cybercrime_portal": "cybercrime.gov.in", "...": "..." },
  "ml_used": false
}
```

Field notes
- `language`: `en`, `te`, `hi`, `te-rom`, `hi-rom` or `mixed` (heuristic).
- `risk.band`: `low` (<30), `caution` (30-59), `high` (60-79), `very_high` (80+). Thresholds are placeholders pending calibration.
- `scam_type` is `null` when the band is `low` or no playbook trigger fired.
- `spans`: character offsets into `text`, for highlighting. `kind` is `indicator` or `url`. Spans may overlap; the UI drops overlaps.
- `urls[].verdict`: `suspicious`, `some_flags`, `official_domain_match`, `no_flags_found`, `malformed`. **There is no "safe" value.**
- `actions[].te` may be `null` (type-specific steps are English only for now).
- `explanation.source`: `template` in Level 1; `llm` reserved for Level 2.

## POST /api/v1/scan/url

Request `{ "url": "bit.ly/abc" }` (3 to 2048 characters). Response has the same shape as the text scan with `input_type: "url"`, `indicators: []` and `spans: []`. The score equals the URL score.

## GET /api/v1/examples

Returns `[{ "id", "title", "text" }]`. All examples are synthetic or illustrative.

## Additional implemented routes

All three GET routes currently return HTTP 200.

- /api/v1/playbooks returns nine playbook objects with id, label, description, warning_signs, attacker_techniques, example_message, and prevention_tips.
- /api/v1/playbooks/{playbook_id} returns one playbook. Unknown IDs return {"error": "Playbook not found"} with HTTP 200.
- /api/v1/stats returns static demonstration figures. Its fields are total_analyses, threats_detected, high_risk_detections, safe_analyses, accuracy_benchmark, supported_languages, scam_category_distribution, timeline_activity, and recent_threats. These are illustrative figures, not measured traffic or validated accuracy.

## Errors

| Code | Meaning |
|---|---|
| 422 | Validation failed (blank, too long, missing field) |
| 500 | Unexpected server error; the message text is never included in error bodies or logs |

Scan validation failures return HTTP 422 with a `detail` array. Each entry
contains `type`, `loc`, and `msg`. The server omits rejected input and validation
context to avoid echoing submitted content.

## Versioning

Breaking changes go to `/api/v2`. Additive fields are allowed in v1.

