# Project Architecture Report
**QA Session:** SESSION-001  
**Date:** 2026-11-24  
**Project:** ZenVex Guard — AI-Powered Multilingual Scam & Digital Threat Intelligence Platform  
**QA Engineer:** Autonomous QA Agent (Antigravity)  

---

## 1. Executive Summary

ZenVex Guard is a cybersecurity threat-intelligence platform engineered to detect deceptive messages, malicious URLs, and digital financial fraud patterns across Indian messaging channels (SMS, WhatsApp, Telegram, Email, Social Media). It is stateless by design — no user messages are persisted.

---

## 2. Technology Stack

| Layer | Technology | Version |
|---|---|---|
| Backend Framework | FastAPI | 0.165.0 |
| ASGI Server | Uvicorn | >=0.29 |
| Data Validation | Pydantic v2 | 2.14.4 |
| ML Library | scikit-learn | 1.9.1 |
| Model Persistence | joblib | 1.6.0 |
| Test Framework | pytest | 9.2.0 |
| Python Runtime | CPython | 3.14.7 |
| Frontend Framework | React 18 + TypeScript + Vite | 18.3.1 / 5.6.3 / 5.4.11 |
| Styling | Tailwind CSS | 3.4.15 |
| Charts | Recharts | 2.13.0 |
| Icons | Lucide React | 1.16.0 |
| CI Platform | GitHub Actions | Ubuntu 24.04 |

---

## 3. Project Structure

```
d:\zenvex\ZenVex\
├── backend/
│   ├── app/
│   │   ├── engine/
│   │   │   ├── analyzer.py      — Orchestrates full analysis pipeline (pure functions, no I/O)
│   │   │   ├── examples.py      — Demo messages for the UI (synthetic)
│   │   │   ├── explain.py       — Deterministic explanation builder from detected findings
│   │   │   ├── language.py      — Heuristic language detector (en/te/hi/te-rom/hi-rom/mixed)
│   │   │   ├── lexicon.py       — Scam indicator lexicon (12 indicators, multilingual regex)
│   │   │   ├── playbooks.py     — 9 Indian scam playbooks with extra safety actions
│   │   │   ├── risk.py          — Risk scoring engine (text + URL + ML combination)
│   │   │   ├── rules.py         — Rule engine: finds indicators with offset spans
│   │   │   └── urls.py          — Offline URL structural analysis (never touches network)
│   │   ├── ml/
│   │   │   ├── predictor.py     — Optional ML scorer (graceful fallback if model absent)
│   │   │   └── train_baseline.py — TF-IDF + Logistic Regression training script
│   │   ├── static/
│   │   │   └── index.html       — Fallback static UI (12KB)
│   │   ├── config.py            — Central configuration (risk bands, model path, CORS, helplines)
│   │   ├── main.py              — FastAPI app, all endpoints, CORS middleware, static serving
│   │   └── schemas.py           — Pydantic request/response models
│   ├── data/
│   │   ├── eval_set.csv         — 42-row labeled evaluation dataset (all synthetic-starter)
│   │   ├── dev_set.csv          — EMPTY (header only)
│   │   └── heldout_set.csv      — EMPTY (header only)
│   ├── models/
│   │   └── .gitkeep             — Directory placeholder (NO trained model present)
│   ├── scripts/
│   │   ├── browser_smoke.py     — Playwright smoke test for packaged app
│   │   └── evaluate.py          — Evaluation script: rules vs rules+ML on labelled CSV
│   ├── tests/
│   │   ├── test_api.py          — 17 API-level tests
│   │   └── test_engine.py       — 19 engine-level unit/integration tests
│   ├── pytest.ini               — testpaths=tests, pythonpath=.
│   ├── requirements.txt         — fastapi, uvicorn, pydantic, scikit-learn, joblib
│   └── requirements-dev.txt     — pytest (+ httpx for TestClient)
├── frontend/
│   └── src/
│       ├── components/
│       │   ├── Dashboard.tsx
│       │   ├── Footer.tsx
│       │   ├── InvestigationReport.tsx
│       │   ├── LandingPage.tsx
│       │   ├── MessageScanner.tsx
│       │   ├── Navbar.tsx
│       │   ├── ProtectionCentre.tsx
│       │   ├── ScamLibrary.tsx
│       │   └── UrlScanner.tsx
│       ├── services/api.ts      — API integration layer with error handling
│       ├── types/intelligence.ts — TypeScript interfaces
│       ├── App.tsx              — Main router and application controller
│       └── main.tsx             — React entry point
├── docs/                        — HLD, LLD, API Contract, Test & Evaluation Plan
├── .github/workflows/ci.yml     — CI: Python tests → evaluate → frontend build → Playwright smoke
└── QA/                          — This directory (created by QA process)
```

---

## 4. API Endpoints

| Method | Path | Status | Description |
|---|---|---|---|
| GET | /health | BUILT | Service liveness check |
| POST | /api/v1/scan/text | BUILT | Analyse a message (5000 char max) |
| POST | /api/v1/scan/url | BUILT | Offline URL structural check (2048 char max) |
| GET | /api/v1/examples | BUILT | Demo scenarios for UI |
| GET | /api/v1/playbooks | BUILT | List all 9 scam playbooks |
| GET | /api/v1/playbooks/{id} | BUILT | Single playbook detail |
| GET | /api/v1/stats | BUILT | Hardcoded demonstration statistics |
| POST | /api/v1/scan/image | PLANNED (L2) | OCR + analyse screenshot |
| POST | /api/v1/feedback | PLANNED (L2) | User feedback |
| GET | / | BUILT | Serves frontend (React build or static fallback) |

---

## 5. Key Architectural Decisions

1. **Stateless Design:** No scan ID is retrievable (GET /api/v1/scan/{id} → 404 by design). No message persistence.
2. **Privacy-first Error Handling:** Validation errors strip submitted content, returning only type/loc/msg.
3. **Offline URL Analysis:** URL module never makes network requests (verified by test).
4. **Graceful ML Fallback:** If no trained model exists, `predict_proba` returns None; rules still work.
5. **12-Indicator Rule Engine:** Multilingual (en/te/hi/te-rom/hi-rom) pattern matching with offset spans.
6. **9 Scam Playbooks:** Priority-ordered selection of the highest-risk playbook for detected indicators.

---

## 6. Known Limitations and Gaps

| Item | Description | Severity |
|---|---|---|
| ML model absent | `models/baseline.joblib` does not exist. ML is never used at runtime. | Medium |
| dev_set.csv empty | Only header row present — no development dataset. | Medium |
| heldout_set.csv empty | Only header row present — no independent held-out test set. | High |
| eval_set.csv synthetic only | All 42 rows are `synthetic-starter` written by team while writing rules. Not independent. | High |
| BUG-001 | APK-link scam in URL classified as `prize_lottery` not `remote_access` due to URL masking | Medium |
| BUG-002 | `/api/v1/playbooks/{id}` returns HTTP 200 for unknown IDs (should be 404 per REST semantics) | Low |
| BUG-003 | `StarletteDeprecationWarning` on `httpx` — should use `httpx2` | Low |
| No frontend tests | Zero automated frontend tests (no Vitest/Jest/Playwright from frontend side) | Medium |
| Stats endpoint hardcoded | INTELLIGENCE_STATS is static demo data, not live telemetry | Low (by design) |
| Risk band thresholds uncalibrated | RISK_BANDS are explicitly marked PLACEHOLDER in config.py | Medium |
| No authentication/authorization | API is fully open — no API keys, rate limiting, or auth | Medium |

---

## 7. Critical Execution Workflows

### Text Scan Flow
```
POST /api/v1/scan/text
  → TextScanRequest (Pydantic validation, 422 on fail)
  → analyze_text(text)
    → extract_urls(text)         → list of (url, start, end)
    → analyze_url(u)             → UrlReport per URL (offline, no network)
    → find_indicators(text)      → List[Indicator] with spans
      → _mask_urls(text)         → URLs replaced with spaces (preserves offsets)
      → regex matching per indicator
      → _credential_matches()    → custom negation + OTP delivery guard
    → predict_proba(text)        → Optional[float] (None if no model)
    → compute_risk(indicators, url_scores, ml_prob) → risk dict
    → pick_playbook(indicator_ids) → playbook_id or None
    → build_explanation()
  → ScanResponse (Pydantic validation)
  → JSON 200
```

### URL Scan Flow
```
POST /api/v1/scan/url
  → UrlScanRequest (Pydantic validation)
  → analyze_url_only(url)
    → analyze_url(url) → UrlReport
    → compute_risk([], [url_score])
    → risk.score = url_score (capped at 100)
  → ScanResponse with input_type="url", indicators=[], spans=[]
```
