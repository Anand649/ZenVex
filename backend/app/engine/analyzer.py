"""Orchestrates the full analysis pipeline. Pure functions, no I/O, no storage."""
import uuid
from typing import Optional

from ..config import HELPLINES
from ..ml.predictor import predict_proba
from .explain import build_explanation
from .language import detect_language
from .playbooks import COMMON_ACTIONS, PLAYBOOKS, pick_playbook
from .risk import band_for, compute_risk
from .rules import find_indicators
from .urls import analyze_url, extract_urls


def _actions(playbook_id):
    actions = [dict(a) for a in COMMON_ACTIONS]
    if playbook_id:
        extra = [{"en": e, "te": None} for e in PLAYBOOKS[playbook_id]["extra_actions"]]
        actions = extra + actions
    return actions


def _url_dict(r):
    return {
        "url": r.url, "host": r.host, "registered_domain": r.registered_domain,
        "verdict": r.verdict, "score": r.score, "flags": r.flags,
        "official_domain_match": r.official_match,
        "reputation_checked": r.reputation_checked, "note": r.note,
    }


def analyze_text(text: str, use_ml: bool = True) -> dict:
    text = text.strip()
    found = extract_urls(text)
    url_reports = [analyze_url(u) for u, _, _ in found]
    indicators = find_indicators(text)
    ml_prob = predict_proba(text) if use_ml else None
    risk = compute_risk(indicators, [r.score for r in url_reports], ml_prob)
    playbook_id = pick_playbook([i.id for i in indicators]) if risk["band"] != "low" else None

    spans = []
    for (_, start, end), rep in zip(found, url_reports):
        spans.append({"start": start, "end": end, "kind": "url", "id": "url"})
    for ind in indicators:
        for s, e in ind.spans:
            spans.append({"start": s, "end": e, "kind": "indicator", "id": ind.id})

    return {
        "scan_id": uuid.uuid4().hex[:12],
        "input_type": "text",
        "text": text,
        "language": detect_language(text),
        "risk": risk,
        "scam_type": {"id": playbook_id, "label": PLAYBOOKS[playbook_id]["label"]} if playbook_id else None,
        "indicators": [
            {"id": i.id, "label": i.label, "weight": i.weight, "evidence": i.evidence}
            for i in indicators
        ],
        "urls": [_url_dict(r) for r in url_reports],
        "spans": spans,
        "explanation": {"text": build_explanation(risk, indicators, url_reports, playbook_id), "source": "template"},
        "actions": _actions(playbook_id),
        "helplines": HELPLINES.copy(),
        "ml_used": ml_prob is not None,
    }


def analyze_url_only(raw_url: str) -> dict:
    rep = analyze_url(raw_url.strip())
    risk = compute_risk([], [rep.score])
    # URL-only scans have no text indicators, so show the URL score directly (capped at 100).
    risk["score"] = min(100, rep.score)
    risk["band"], risk["label"] = band_for(risk["score"])
    risk["breakdown"] = {"text": 0, "url": risk["score"], "ml": 0}
    return {
        "scan_id": uuid.uuid4().hex[:12],
        "input_type": "url",
        "text": raw_url.strip(),
        "language": "en",
        "risk": risk,
        "scam_type": None,
        "indicators": [],
        "urls": [_url_dict(rep)],
        "spans": [],
        "explanation": {"text": build_explanation(risk, [], [rep], None), "source": "template"},
        "actions": _actions(None),
        "helplines": HELPLINES.copy(),
        "ml_used": False,
    }
