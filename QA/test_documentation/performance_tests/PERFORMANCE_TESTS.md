# Performance & Reliability Test Execution Records

## Test Record: PERF-001
- **Test ID:** PERF-001
- **Test Name:** Single-Core Throughput & Analysis Latency
- **Module:** `engine/analyzer.py`
- **Category:** Performance / Reliability
- **Execution Date:** 2026-11-24
- **Objective:** Benchmark the execution time and throughput of `analyze_text()` over 200 consecutive scans of complex messages containing multilingual text, urgency hooks, credential requests, and phishing URLs.
- **Hardware / OS:** Windows 11, CPython 3.14.7, 64-bit.
- **Input:** Complex synthetic scam text: `"Your bank account will be blocked today due to incomplete KYC. Update immediately: http://sbi-kyc-update.xyz"`
- **Iterations:** 200 sequential executions.
- **Measurements:**
  - Total elapsed time: `0.0284 seconds`
  - Average latency per scan: `0.142 milliseconds` (0.000142s)
  - Estimated throughput: `~7,042 scans per second` per CPU core
  - Pass Criteria: Average latency < 50.0 ms
- **Status:** **PASS**
- **Evidence:** `QA/evidence/outputs/PERF-001_RUN-001.json`
- **Observation:** Pure algorithmic in-memory execution produces sub-millisecond threat dossier generation with negligible memory footprint.
