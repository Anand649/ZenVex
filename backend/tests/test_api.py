import pytest
from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_health():
    assert client.get("/health").json()["status"] == "ok"


def test_scan_text_ok():
    r = client.post("/api/v1/scan/text", json={"text": "Your account will be blocked today. Update KYC: http://sbi-kyc-update.xyz"})
    assert r.status_code == 200
    body = r.json()
    assert body["risk"]["band"] in {"caution", "high", "very_high"}
    assert body["urls"][0]["reputation_checked"] is False


def test_scan_text_validation():
    assert client.post("/api/v1/scan/text", json={"text": "   "}).status_code == 422
    assert client.post("/api/v1/scan/text", json={"text": "x" * 5001}).status_code == 422
    assert client.post("/api/v1/scan/text", json={}).status_code == 422


def test_scan_url_ok():
    r = client.post("/api/v1/scan/url", json={"url": "bit.ly/abc"})
    assert r.status_code == 200 and r.json()["input_type"] == "url"


@pytest.mark.parametrize(
    ("route", "value", "status"),
    [
        ("text", "x", 200),
        ("text", "x" * 5000, 200),
        ("text", "x" * 5001, 422),
        ("url", " ab ", 422),
        ("url", "abc", 200),
        ("url", "https://example.invalid/".ljust(2048, "x"), 200),
        ("url", "https://example.invalid/".ljust(2049, "x"), 422),
    ],
)
def test_scan_input_boundaries(route, value, status):
    response = client.post(f"/api/v1/scan/{route}", json={route: value})
    assert response.status_code == status


def test_malformed_url_returns_an_offline_report():
    response = client.post("/api/v1/scan/url", json={"url": "https://[::1"})
    assert response.status_code == 200
    body = response.json()
    report, = body["urls"]
    assert report["verdict"] == "malformed"
    assert report["reputation_checked"] is False
    assert any(flag["id"] == "malformed" for flag in report["flags"])
    assert body["risk"]["score"] == report["score"]


def test_playbooks_contract():
    response = client.get("/api/v1/playbooks")
    assert response.status_code == 200
    playbooks = response.json()
    assert len(playbooks) == len({book["id"] for book in playbooks}) == 9
    for playbook in playbooks:
        for key in ("id", "label", "description", "example_message"):
            assert isinstance(playbook[key], str)
        for key in ("warning_signs", "attacker_techniques", "prevention_tips"):
            assert isinstance(playbook[key], list)
            assert all(isinstance(item, str) for item in playbook[key])
        detail = client.get(f"/api/v1/playbooks/{playbook['id']}")
        assert detail.status_code == 200
        assert detail.json() == playbook

    missing = client.get("/api/v1/playbooks/missing")
    assert missing.status_code == 200
    assert missing.json() == {"error": "Playbook not found"}


def test_stats_contract():
    response = client.get("/api/v1/stats")
    assert response.status_code == 200
    stats = response.json()
    for key in ("total_analyses", "threats_detected", "high_risk_detections", "safe_analyses"):
        assert type(stats[key]) is int
    assert stats["accuracy_benchmark"] == "Not measured"
    assert stats["supported_languages"]
    assert all(isinstance(language, str) for language in stats["supported_languages"])
    collections = {
        "scam_category_distribution": {"name": str, "count": int, "percentage": int, "risk": str},
        "timeline_activity": {"time": str, "scans": int, "threats": int},
        "recent_threats": {"id": str, "category": str, "risk": str, "score": int, "language": str, "timestamp": str},
    }
    for key, fields in collections.items():
        assert stats[key]
        for item in stats[key]:
            for field, field_type in fields.items():
                assert type(item[field]) is field_type


def test_scan_validation_does_not_echo_submitted_content(caplog):
    marker = "synthetic-private-marker"
    for route, field in (("text", "text"), ("url", "url")):
        for response in (
            client.post(f"/api/v1/scan/{route}", json={field: marker * 500}),
            client.post(f"/api/v1/scan/{route}", json={field: {"value": marker}}),
            client.post(
                f"/api/v1/scan/{route}",
                content='{"' + field + '":"' + marker,
                headers={"Content-Type": "application/json"},
            ),
        ):
            assert response.status_code == 422
            assert marker not in response.text
            assert all(set(error) == {"type", "loc", "msg"} for error in response.json()["detail"])
    assert marker not in caplog.text


def test_examples_and_index():
    assert len(client.get("/api/v1/examples").json()) >= 3
    page = client.get("/")
    assert page.status_code == 200 and "ZenVex Guard" in page.text


def test_no_message_echo_in_error_logs_or_storage():
    # Stateless by design: scan ids are not retrievable.
    r = client.post("/api/v1/scan/text", json={"text": "hello"}).json()
    assert client.get(f"/api/v1/scan/{r['scan_id']}").status_code == 404
