# ZenVex Guard — Backend Architecture & Developer Guide

This directory contains the core threat intelligence engine, deterministic heuristic rule matcher, offline URL isolation module, ML baseline classifier, and FastAPI REST gateway.

---

## 1. Directory Structure

```
backend/
├── app/
│   ├── engine/               # Core deterministic analysis engine
│   │   ├── analyzer.py       # Pipeline orchestrator (stateless pure functions)
│   │   ├── lexicon.py        # 12 indicator definitions, regexes & weights
│   │   ├── rules.py          # Indicator matching with exact offset spans
│   │   ├── urls.py           # 14-point offline structural URL isolation
│   │   ├── language.py       # Script detection & Romanised transliteration
│   │   ├── playbooks.py      # 9 Indian threat playbooks & safety actions
│   │   ├── risk.py           # Evidence scoring algorithm & risk bands
│   │   ├── explain.py        # Deterministic explainability synthesizer
│   │   └── examples.py       # Preset demonstration messages
│   ├── ml/                   # Machine learning components
│   │   ├── predictor.py      # Model loader & inference wrapper (fails soft)
│   │   └── train_baseline.py # TF-IDF + Logistic Regression trainer
│   ├── static/               # Fallback lightweight static HTML interface
│   ├── config.py             # Global constants, thresholds, helplines
│   ├── main.py               # FastAPI application, routes, and SPA mounting
│   └── schemas.py            # Pydantic v2 validation models
├── data/
│   ├── eval_set.csv          # Evaluation and benchmarking set
│   ├── dev_set.csv           # Development set
│   └── heldout_set.csv       # Held-out validation dataset
├── tests/
│   ├── test_api.py           # FastAPI endpoint tests
│   └── test_engine.py        # True/false-positive rule & URL tests
├── pytest.ini                # Pytest configuration
├── requirements.txt          # Production dependencies
└── requirements-dev.txt      # Testing & dev dependencies
```

---

## 2. Core Modules & Developer Contracts

### `app/engine/analyzer.py`
Orchestrates the entire detection flow. **Contract:** Pure functions only; zero database I/O, zero network calls, zero message logging.
- `analyze_text(text: str, use_ml: bool = True) -> dict`:
  1. Extracts URLs using `urls.extract_urls()`.
  2. Runs 14-point structural checks via `urls.analyze_url()`.
  3. Detects indicators via `rules.find_indicators()`.
  4. Optionally queries `ml.predictor.predict_proba()`.
  5. Computes risk band and score via `risk.compute_risk()`.
  6. Correlates with 9 Indian playbooks via `playbooks.pick_playbook()`.
  7. Formats highlighted evidence spans with exact start and end offsets.
  8. Returns structured `ScanResponse` dictionary.
- `analyze_url_only(raw_url: str) -> dict`:
  Directly evaluates a URL without message indicators.

### `app/engine/lexicon.py`
Defines the **12 scam indicators**. To add a new indicator, add an `IndicatorDef` to `INDICATORS`:
```python
IndicatorDef(
    id="custom_scam_hook",
    label="Human-readable description of threat",
    weight=15,  # Contribution to evidence score (0-100)
    patterns=(
        r"\b(pattern1|pattern2)\b",  # English regex
        r"\b(romanised_word1|romanised_word2)\b",  # Romanised Telugu/Hindi
        r"తెలుగు_పదం",  # Telugu script
        r"हिंदी_शब्द",   # Hindi script
    ),
)
```

### `app/engine/rules.py`
Executes compiled regexes against unmasked text while preserving original offsets:
- `_mask_urls(text)`: Replaces URLs with whitespace of identical length so domain keywords don't collide with text indicators.
- `_credential_matches(text)`: Special logic guarding against false positives:
  - Negation guard: *"do not share your OTP"* is recognized as advice, not a request.
  - OTP delivery guard: *"Enter OTP 123456 to login"* includes the OTP code itself, so soft verbs are not flagged as credential theft.

### `app/engine/urls.py`
Executes **14 structural offline checks**. **HARD RULE:** Never perform DNS queries or HTTP fetches.
- Checks: ip_host, at_symbol, punycode, shortener, suspicious_tld, many_subdomains, many_hyphens, long_url, explicit_http, phishing_words, brand_mismatch, lookalike_brand, apk_link, digit_heavy.
- `BRANDS`: Allowlist mapping legitimate brand registered domains (SBI, HDFC, ICICI, India Post, Amazon, Flipkart, etc.).

### `app/engine/playbooks.py`
Maps threat patterns to 9 named Indian fraud playbooks:
1. `digital_arrest`: Fake CBI, Police, Customs extortion via video call.
2. `remote_access`: AnyDesk, TeamViewer, or sideloaded APK.
3. `investment_fraud`: High-yield trading and secret Telegram wealth groups.
4. `job_fraud`: Work-from-home task deposit schemes.
5. `delivery_customs_fee`: India Post, Blue Dart, FedEx fake redelivery charges.
6. `prize_lottery`: KBC, sweepstakes, and cashback fees.
7. `kyc_account_block`: Bank account or PAN suspension warnings.
8. `credential_phishing`: Direct extraction of PINs, OTPs, or passwords.
9. `payment_request`: UPI QR code and incoming collect request fraud.

### `app/engine/risk.py`
Calculates the evidence score:
$$\text{Score} = \min(100, \text{text\_points} + \min(50, \text{url\_points}) + \text{ml\_points})$$
Bands:
- `80 - 100`: Very high risk / Critical
- `60 - 79`: High risk
- `30 - 59`: Caution
- `0 - 29`: Low detected risk

---

## 3. How to Extend the Backend Code

### Adding a New Threat Indicator
1. Open `app/engine/lexicon.py`.
2. Append a new `IndicatorDef(...)` to `INDICATORS`.
3. Add a test case in `tests/test_engine.py` verifying true positives and false-positive immunity.
4. Run `python -m pytest tests/` to verify.

### Adding a New Verified Brand to URL Allowlist
1. Open `app/engine/urls.py`.
2. Locate `BRANDS` dictionary.
3. Add brand name and set of registered domains:
   ```python
   "mybank": ("mybank", {"mybank.com", "mybank.co.in"}),
   ```

### Adding a New API Endpoint
1. Open `app/main.py`.
2. Create your route using standard FastAPI syntax:
   ```python
   @app.get("/api/v1/my-endpoint")
   def my_endpoint():
       return {"data": "example"}
   ```
3. Add validation schema in `app/schemas.py`.
4. Add endpoint verification test in `tests/test_api.py`.

---

## 4. Testing & Verification

Run the entire test suite:
```bash
python -m pytest -q tests/
```
All 22 unit tests verify text detection, Romanised language classification, URL safety, false-positive protection, and API schemas.
