# QA review notes

Run the QA tools with the backend development requirements installed. Build
the frontend first if verifying the packaged React application.

```sh
python QA/test_scripts/generate_all_evidence.py
python QA/test_scripts/ml/dataset_analysis.py
```

The scripts locate the repository relative to their files and can run from
any working directory when invoked by path. The generator refreshes the
synthetic evidence under `QA/evidence/`. Its completion reports that evidence
was generated. Check individual outcomes and run pytest separately.

The original RUN-001 reports and register totals are historical observations.
The current disposition for BUG-002 is **passes the v1 contract**. An unknown
playbook returns HTTP 200 with `{"error":"Playbook not found"}`. A future HTTP
404 response would require a reviewed contract change. The evidence file
retains its historical filename to preserve links from the registers.

This review does not resolve the APK playbook observation, the lack of an
independent held-out dataset, or the hosted release gates. The starter set is
for regression checking.
