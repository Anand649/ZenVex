from app.engine.analyzer import analyze_text, analyze_url_only
from app.engine.language import detect_language
from app.engine.rules import find_indicators
from app.engine.urls import analyze_url, extract_urls, registered_domain


def ids(text):
    return {i.id for i in find_indicators(text)}


# ---- language ----
def test_language_detection():
    assert detect_language("Your account is blocked") == "en"
    assert detect_language("మీ ఖాతా బ్లాక్ అవుతుంది") == "te"
    assert detect_language("आपका खाता बंद हो जाएगा") == "hi"
    assert detect_language("Mee account block avutundi, link click cheyandi") == "te-rom"
    assert detect_language("Aapka account band ho jayega, kripya turant karein") == "hi-rom"


# ---- indicators: true positives ----
def test_kyc_scam_indicators():
    found = ids("Your account will be blocked today. Update KYC immediately")
    assert {"account_threat", "kyc_pressure", "urgency"} <= found


def test_credential_request_detected():
    assert "credential_request" in ids("Please share your OTP to continue")
    assert "credential_request" in ids("Enter your card number and PIN to reactivate")


def test_romanised_and_native_scripts():
    assert "account_threat" in ids("Mee bank account block avutundi")
    assert "kyc_pressure" in ids("మీ ఖాతా కోసం KYC అప్‌డేట్ చేయండి")
    assert "account_threat" in ids("आपका बैंक खाता आज बंद हो जाएगा")
    assert "credential_request" in ids("Kripya turant OTP bhejiye")


# ---- indicators: false-positive guards ----
def test_otp_warning_is_not_a_request():
    assert "credential_request" not in ids("Do not share your OTP with anyone")
    assert "credential_request" not in ids("Never enter your PIN anywhere")
    assert "credential_request" not in ids("Enter OTP 123456 to complete your login")


def test_genuine_messages_score_low():
    genuine = [
        "123456 is your OTP for HDFC Bank NetBanking. Do not share it with anyone.",
        "Rs 2,000.00 debited from A/c XX1234 via UPI. If not done by you, call 1930.",
        "Your KYC has been updated successfully. Thank you for banking with us.",
        "Your Amazon order has shipped. Track at https://www.amazon.in/orders",
        "Salary credited Rs 45,000 to A/c XX5678.",
    ]
    for g in genuine:
        r = analyze_text(g)
        assert r["risk"]["band"] == "low", (g, r["risk"])


def test_urgency_alone_is_not_enough():
    r = analyze_text("Please call me immediately, it is urgent.")
    assert r["risk"]["band"] == "low"


# ---- urls ----
def test_url_extraction_trims_punctuation_and_skips_emails():
    found = [u for u, _, _ in extract_urls("Open http://a.xyz/x?y=1, or www.test.in. Mail a@gmail.com")]
    assert "http://a.xyz/x?y=1" in found and "www.test.in" in found
    assert not any("gmail" in u for u in found)


def test_registered_domain():
    assert registered_domain("www.sbi.co.in") == "sbi.co.in"
    assert registered_domain("a.b.evil.com") == "evil.com"


def test_official_domain_not_flagged():
    r = analyze_url("https://www.sbi.co.in/web/personal-banking")
    assert r.verdict == "official_domain_match" and not r.flags


def test_brand_in_wrong_domain_flagged():
    r = analyze_url("https://sbi.co.in.evil-site.com/login")
    assert r.registered_domain == "evil-site.com"
    assert any(f["id"] == "brand_mismatch" for f in r.flags)


def test_ip_shortener_and_never_safe_wording():
    assert any(f["id"] == "ip_host" for f in analyze_url("http://192.168.1.1/login").flags)
    assert any(f["id"] == "shortener" for f in analyze_url("bit.ly/abc").flags)
    clean = analyze_url("https://example.org/page")
    assert clean.verdict == "no_flags_found" and clean.reputation_checked is False
    assert "safe" not in clean.verdict


def test_url_analyser_does_not_touch_network(monkeypatch):
    import socket

    def boom(*a, **k):
        raise AssertionError("network access attempted")

    monkeypatch.setattr(socket, "socket", boom)
    monkeypatch.setattr(socket, "getaddrinfo", boom)
    analyze_text("Click http://sbi-kyc-update.xyz now")


# ---- pipeline ----
def test_full_pipeline_shape():
    r = analyze_text("Dear Customer, your bank account will be blocked today due to incomplete KYC. Update immediately: http://sbi-kyc-update.xyz")
    assert r["risk"]["band"] in {"high", "very_high"}
    assert r["scam_type"]["id"] == "kyc_account_block"
    assert r["urls"] and r["spans"] and r["actions"]
    assert all(a["en"] for a in r["actions"])
    assert r["explanation"]["source"] == "template"


def test_url_only_pipeline():
    r = analyze_url_only("https://sbi.co.in.evil-site.com/login")
    assert r["input_type"] == "url" and r["risk"]["score"] > 0


# ---- regressions ----
def test_indicator_matching_ignores_url_text_and_sentence_boundaries():
    t = "Dear Customer, your bank account will be blocked today due to incomplete KYC. Update immediately: http://sbi-kyc-update.xyz"
    r = analyze_text(t)
    kyc = next(i for i in r["indicators"] if i["id"] == "kyc_pressure")
    assert all("http" not in e and "." not in e for e in kyc["evidence"]), kyc
    url_span = next(s for s in r["spans"] if s["kind"] == "url")
    for s in r["spans"]:
        if s["kind"] == "indicator":
            assert s["end"] <= url_span["start"] or s["start"] >= url_span["end"], s


def test_upi_refund_collect_request_scores_caution():
    text = "Approve the collect request of Rs 1 on your UPI app to receive your refund of Rs 4,999."
    result = analyze_text(text, use_ml=False)
    assert result["risk"]["band"] == "caution"
    assert result["scam_type"]["id"] == "payment_request"
    span = next(s for s in result["spans"] if s["id"] == "upi_refund_collect")
    assert text[span["start"]:span["end"]].endswith("to receive your refund")


def test_upi_payment_and_refund_controls_stay_low():
    for text in (
        "Please approve the UPI collect request for your monthly subscription.",
        "Your UPI refund was credited today.",
        "Never approve a UPI collect request to receive a refund.",
        "Approve the collect request in your UPI app. Your refund has been sent.",
    ):
        result = analyze_text(text, use_ml=False)
        assert result["risk"]["band"] == "low"
        assert "upi_refund_collect" not in ids(text)


def test_scan_results_isolate_helplines():
    from app.config import HELPLINES

    expected = HELPLINES.copy()
    for result in (analyze_text("Synthetic example", use_ml=False),
                   analyze_url_only("example.invalid")):
        result["helplines"]["note"] = "synthetic mutation"
        assert HELPLINES == expected
        assert analyze_text("Synthetic example", use_ml=False)["helplines"] == expected
        assert analyze_url_only("example.invalid")["helplines"] == expected
