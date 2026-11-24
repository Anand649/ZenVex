"""Central configuration. Everything tunable lives here or in lexicon.py."""
import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent

MAX_TEXT_LENGTH = 5000
MAX_URL_LENGTH = 2048

# Risk bands: (minimum score, id, label). PLACEHOLDER thresholds -- calibrate on the
# evaluation set (docs/TEST_AND_EVALUATION_PLAN.md) before claiming anything about them.
RISK_BANDS = (
    (80, "very_high", "Very high risk"),
    (60, "high", "High risk"),
    (30, "caution", "Caution"),
    (0, "low", "Low detected risk"),
)

# A message counts as "flagged" in evaluation when its score reaches this value.
FLAG_THRESHOLD = 30

# Maximum contribution of the URL module and the optional ML model to the score.
URL_MAX_POINTS = 50
ML_MAX_POINTS = 20

MODEL_PATH = Path(os.getenv("ZENVEX_MODEL_PATH", BASE_DIR / "models" / "baseline.joblib"))
CORS_ORIGINS = [
    origin.strip()
    for origin in os.getenv(
        "ZENVEX_CORS_ORIGINS", "http://localhost:5173,http://127.0.0.1:5173"
    ).split(",")
    if origin.strip()
]

HELPLINES = {
    "cybercrime_helpline": "1930",
    "cybercrime_portal": "cybercrime.gov.in",
    "suspected_fraud_reporting": "Chakshu on the Sanchar Saathi portal (sancharsaathi.gov.in)",
    "note": "Verify these details on official government websites before relying on them.",
}
