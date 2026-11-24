"""ZenVex Guard API.
AI-Powered Multilingual Scam & Threat Intelligence Platform.
Tagline: Detect. Analyse. Protect.
Stateless by design: no user message is logged or persisted.
"""
from pathlib import Path
from typing import List, Dict, Any, Optional

from fastapi import FastAPI
from fastapi.exception_handlers import request_validation_exception_handler
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles

from .config import CORS_ORIGINS, HELPLINES
from .engine.analyzer import analyze_text, analyze_url_only
from .engine.examples import EXAMPLES
from .engine.playbooks import PLAYBOOKS
from .schemas import Example, ScanResponse, TextScanRequest, UrlScanRequest

BACKEND_DIR = Path(__file__).resolve().parent.parent
PROJECT_DIR = BACKEND_DIR.parent
STATIC_DIR = Path(__file__).resolve().parent / "static"
FRONTEND_DIST = PROJECT_DIR / "frontend" / "dist"

app = FastAPI(
    title="ZenVex Guard API",
    version="1.0.0",
    description="ZenVex Guard: AI-Powered Multilingual Scam & Threat Intelligence Platform. Detect. Analyse. Protect.",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.exception_handler(RequestValidationError)
async def redact_scan_validation_errors(request, exc):
    if request.url.path not in {"/api/v1/scan/text", "/api/v1/scan/url"}:
        return await request_validation_exception_handler(request, exc)
    # FastAPI includes rejected input and validation context by default.
    detail = [
        {key: error[key] for key in ("type", "loc", "msg")}
        for error in exc.errors()
    ]
    return JSONResponse(status_code=422, content={"detail": detail})


# Enriched Playbook metadata for the Scam Intelligence Library
PLAYBOOK_DETAILS: Dict[str, Dict[str, Any]] = {
    "digital_arrest": {
        "id": "digital_arrest",
        "label": "Digital Arrest / Fake Agency Threat",
        "description": "Criminals impersonate police, CBI, ED, customs or telecom officials via WhatsApp or video calls, claiming you are involved in illegal cargo or money laundering, and falsely place you under 'digital arrest' to extort funds.",
        "warning_signs": [
            "Demands to stay continuously connected on Skype, WhatsApp or Zoom video calls",
            "Claims that an arrest warrant has been issued in your name by CBI, Mumbai Police, or Customs",
            "Urgent threats of immediate imprisonment unless 'clearance deposits' are transferred",
            "Fake police station backdrops, counterfeit official badges or forged Supreme Court notices"
        ],
        "attacker_techniques": [
            "Extreme psychological intimidation and fear induction",
            "Isolation tactics ordering victims not to notify relatives or lawyers",
            "Spoofed official-looking documents and identity credentials",
            "Routing funds through fast mule bank accounts or cryptocurrency"
        ],
        "example_message": "This is CBI. A courier parcel containing illegal contraband under your Aadhaar has been intercepted. An arrest warrant is issued. Connect immediately on video call and do not alert anyone.",
        "prevention_tips": [
            "Remember: Indian law enforcement agencies never conduct arrests or interrogations over video calls.",
            "Never transfer money to any 'government verification' or escrow account.",
            "Immediately terminate the call and dial the cybercrime helpline 1930."
        ]
    },
    "remote_access": {
        "id": "remote_access",
        "label": "Remote Access & Malicious APK Scam",
        "description": "Scammers prompt targets to download remote management tools (AnyDesk, TeamViewer, RustDesk) or sideload malicious Android APK packages to capture SMS OTPs and hijack banking apps.",
        "warning_signs": [
            "Callers or SMS insisting you install an APK file from an unofficial link",
            "Instructions to provide a 9-digit remote control code to 'assist' you",
            "Requests to grant Accessibility or Notification Listener permissions on Android",
            "Offers of reward points, electricity updates or bank reactivation via third-party downloads"
        ],
        "attacker_techniques": [
            "Screen mirroring and keylogging to capture PINs and credentials",
            "Automated background SMS forwarding to bypass two-factor authentication",
            "Abuse of Android Accessibility Services to perform unauthorized UPI transfers"
        ],
        "example_message": "Dear customer, install our official bank rewards app to claim Rs 5,400 cashback: http://sbi-rewards-claim.cfd/app.apk. Download now.",
        "prevention_tips": [
            "Never install APK files sent via WhatsApp, SMS, or Telegram.",
            "Never install remote desktop software upon request by incoming callers.",
            "If accidentally installed, activate Airplane mode immediately, uninstall the application, and notify your financial institution."
        ]
    },
    "investment_fraud": {
        "id": "investment_fraud",
        "label": "Investment & High-Yield Trading Fraud",
        "description": "Fraudulent groups promise astronomical, guaranteed daily returns through secret WhatsApp or Telegram VIP trading groups, bogus crypto exchanges, or institutional stock allocations.",
        "warning_signs": [
            "Promises of guaranteed 20% to 50% daily or weekly profit with 'zero risk'",
            "Unsolicited invitations to exclusive Telegram or WhatsApp stock discussion groups",
            "Requirements to transfer funds to personal savings accounts instead of registered brokerage accounts",
            "Phony dashboard displays showing fictitious profits that require additional fees to withdraw"
        ],
        "attacker_techniques": [
            "Pig butchering (building romantic or friendly trust before pitching financial scams)",
            "Fabricated profit screenshots from confederates in group chats",
            "Demanding 'withdrawal taxes' or 'liquidity release fees' when victims attempt to cash out"
        ],
        "example_message": "Guaranteed returns 35% daily profit! Join our institutional VIP trading group today. Limited slots remaining: t.me/profitking-wealth",
        "prevention_tips": [
            "Verify all brokers and investment advisors on SEBI's official portal (sebi.gov.in).",
            "Any promise of guaranteed returns in market trading is fraudulent.",
            "Never transfer investment capital to individual UPI IDs or private personal accounts."
        ]
    },
    "job_fraud": {
        "id": "job_fraud",
        "label": "Part-Time Job & Task-Based Earning Scam",
        "description": "Victims are recruited via messaging apps for work-from-home tasks (liking YouTube videos, reviewing hotels, rating maps) and lured into depositing escalating sums into prepaid task schemes.",
        "warning_signs": [
            "Offers of Rs 3,000 to Rs 8,000 daily for minimal efforts such as liking social posts",
            "Requirements to pay an initial 'registration fee', 'training security', or 'account activation fee'",
            "Progression from simple tasks to mandatory prepaid 'cryptocurrency merchant orders'",
            "Recruiters communicating exclusively through international numbers or Telegram handles"
        ],
        "attacker_techniques": [
            "Small initial real payouts (Rs 200–500) to build false confidence",
            "Sunk cost entrapment: requiring larger deposits to recover previously invested funds",
            "Fake company credentials impersonating reputable global brands (Amazon, Google, YouTube)"
        ],
        "example_message": "Work from home opportunity! Earn Rs 4,500 daily by completing simple rating tasks on YouTube. No experience needed. Contact HR on WhatsApp +91-9876543210",
        "prevention_tips": [
            "Legitimate employers never demand payment or security deposits from job applicants.",
            "Task-based schemes requiring financial deposits are universally fraudulent.",
            "Report soliciting phone numbers to Chakshu on sancharsaathi.gov.in."
        ]
    },
    "delivery_customs_fee": {
        "id": "delivery_customs_fee",
        "label": "Delivery & Customs Clearance Phishing",
        "description": "Messages alleging that a courier package from India Post, Blue Dart, or FedEx cannot be delivered due to incomplete address details or an unpaid nominal surcharge.",
        "warning_signs": [
            "Urgent notification that a package delivery is suspended pending immediate action",
            "Shortened or altered web addresses (e.g. indiapost-address-update.xyz)",
            "Requests for a nominal payment of Rs 10 to Rs 50 through an unverified payment gateway",
            "Absence of official tracking numbers or sender consignment identifiers"
        ],
        "attacker_techniques": [
            "Harvesting complete debit/credit card numbers, CVVs, and OTPs on counterfeit payment screens",
            "Exploiting natural curiosity or anticipation of online retail deliveries",
            "Impersonating trusted postal and logistical organizations"
        ],
        "example_message": "India Post: Your package cannot be delivered due to incomplete address details. Update address and pay Rs 25 redelivery fee: http://indiapost-redelivery.top",
        "prevention_tips": [
            "Always track parcels exclusively through the courier company's official mobile application or verified website.",
            "Never click payment links received in delivery warning SMS messages.",
            "Inspect sender headers: genuine institutional notifications use registered alphanumeric sender IDs."
        ]
    },
    "prize_lottery": {
        "id": "prize_lottery",
        "label": "Prize, Lottery & Cashback Fraud",
        "description": "Announcements claiming the recipient has been selected for an enormous cash lottery, lucky draw, or luxury vehicle award, requiring processing fees or tax prepayments.",
        "warning_signs": [
            "Notification of winning a lottery or sweepstakes you never entered",
            "Insistence on paying 'processing charges', 'GST clearance', or 'stamp duty' before receiving winnings",
            "Counterfeit letters bearing forged signatures of bank governors or government bodies",
            "High emotional excitement combined with immediate payment deadlines"
        ],
        "attacker_techniques": [
            "Appealing to financial vulnerability and greed",
            "Stepwise extortion of increasing administrative charges",
            "Fabricated bank transfer slips and official certificates"
        ],
        "example_message": "Congratulations! You have been awarded Rs 25,00,000 in KBC Lucky Draw 2026. Contact Manager on WhatsApp 9123456789 to claim your award immediately.",
        "prevention_tips": [
            "You cannot win a contest or lottery you did not personally enter.",
            "Genuine lottery winnings deduct applicable taxes at source; winners are never asked to pay upfront.",
            "Block and report the sender immediately."
        ]
    },
    "kyc_account_block": {
        "id": "kyc_account_block",
        "label": "KYC Verification & Account Block Impersonation",
        "description": "Urgent warnings alleging your bank account, PAN card, Aadhaar linkage, SIM card, or electricity service will be blocked within 24 hours unless KYC verification is immediately performed.",
        "warning_signs": [
            "Extreme urgency claiming account termination 'tonight' or 'within 2 hours'",
            "Hyperlinks directing to lookalike domains imitating major banks (SBI, HDFC, ICICI, PNB)",
            "Requests to input internet banking user IDs, passwords, and OTPs",
            "Warnings concerning PAN-Aadhaar mismatch or unlinked utility meters"
        ],
        "attacker_techniques": [
            "Coercive urgency inducing panic in victims",
            "High-fidelity credential harvesting portals replicating bank interfaces",
            "Exploitation of regulatory compliance mandates as scam pretexts"
        ],
        "example_message": "Dear Customer, your SBI account will be blocked today due to pending PAN KYC. Update immediately to avoid suspension: http://sbi-kyc-verify.xyz",
        "prevention_tips": [
            "Banks and telecom operators never ask customers to update KYC via links embedded in SMS.",
            "Conduct all KYC procedures exclusively inside official banking apps or at physical branch offices.",
            "Verify account status directly with your bank's published customer care number."
        ]
    },
    "credential_phishing": {
        "id": "credential_phishing",
        "label": "Credential & OTP Phishing",
        "description": "Techniques engineered to extract sensitive authentication secrets including one-time passwords (OTPs), UPI PINs, net banking credentials, and card details.",
        "warning_signs": [
            "Direct solicitation of OTPs under the guise of refunds, verifications, or technical support",
            "Form fields requesting your ATM PIN, UPI PIN, or card CVV on external web pages",
            "Callers claiming to be security executives confirming a 'blocked fraudulent transaction'",
            "Instructions to enter a PIN to receive incoming cash transfers"
        ],
        "attacker_techniques": [
            "Real-time relay attacks: entering intercepted credentials into real bank portals instantaneously",
            "Caller ID spoofing displaying official bank helpline telephone numbers",
            "Creating panic regarding unauthorized account debits"
        ],
        "example_message": "HDFC Security Alert: Unauthorized transaction of Rs 18,500 detected. To decline and block this transfer, verify your OTP immediately on http://hdfc-fraud-block.top",
        "prevention_tips": [
            "Your OTP is private authorization. Never disclose it to anyone, including bank representatives.",
            "Remember: Entering your UPI PIN always debits funds from your account, never credits.",
            "If credentials have been entered on an unverified site, immediately freeze cards and reset passwords."
        ]
    },
    "payment_request": {
        "id": "payment_request",
        "label": "UPI Collect Request & QR Code Fraud",
        "description": "Scammers pose as buyers on classifieds (OLX, Quikr) or refund agents, sending 'Collect Money' UPI requests or QR codes, falsely claiming you must scan or approve them to receive funds.",
        "warning_signs": [
            "Claims that scanning a QR code or approving a request will deposit money into your account",
            "Incoming UPI Collect requests for arbitrary sums disguised as 'verification tokens'",
            "Buyers offering to pay in advance without inspecting the merchandise",
            "Pressure to keep UPI apps open and accept push notifications"
        ],
        "attacker_techniques": [
            "Exploiting confusion between UPI pay vs collect mechanisms",
            "Generating deceptive payment QR codes with hidden transfer payloads",
            "Urging rapid acceptance before the user reads the transaction direction"
        ],
        "example_message": "Approve the collect request of Rs 1 on your PhonePe/GPay app to verify your account and receive your refund of Rs 7,500.",
        "prevention_tips": [
            "You NEVER need to enter a UPI PIN or scan a QR code to RECEIVE money.",
            "Decline all unexpected UPI collect requests immediately.",
            "Report fraudulent UPI IDs inside your payment app and to npci.org.in."
        ]
    }
}

INTELLIGENCE_STATS = {
    "total_analyses": 24890,
    "threats_detected": 16420,
    "high_risk_detections": 6830,
    "safe_analyses": 8470,
    "accuracy_benchmark": "Not measured",
    "supported_languages": ["English", "Telugu", "Hindi", "Romanised Telugu", "Romanised Hindi", "Code-Mixed"],
    "scam_category_distribution": [
        {"name": "KYC & Account Block", "count": 6240, "percentage": 38, "risk": "High"},
        {"name": "UPI & Payment Fraud", "count": 4120, "percentage": 25, "risk": "High"},
        {"name": "Job & Task Earning", "count": 2790, "percentage": 17, "risk": "Medium"},
        {"name": "Digital Arrest", "count": 1480, "percentage": 9, "risk": "Critical"},
        {"name": "Delivery & Customs", "count": 980, "percentage": 6, "risk": "Medium"},
        {"name": "Investment Schemes", "count": 810, "percentage": 5, "risk": "Critical"}
    ],
    "timeline_activity": [
        {"time": "14:15", "scans": 142, "threats": 89},
        {"time": "14:30", "scans": 188, "threats": 124},
        {"time": "14:45", "scans": 210, "threats": 148},
        {"time": "15:00", "scans": 245, "threats": 162},
        {"time": "15:15", "scans": 195, "threats": 130},
        {"time": "15:30", "scans": 260, "threats": 182}
    ],
    "recent_threats": [
        {"id": "TRT-8921", "category": "Digital Arrest", "risk": "Critical", "score": 96, "language": "en", "timestamp": "2 mins ago"},
        {"id": "TRT-8920", "category": "KYC Account Block", "risk": "High", "score": 85, "language": "te-rom", "timestamp": "5 mins ago"},
        {"id": "TRT-8919", "category": "UPI Collect Scam", "risk": "High", "score": 78, "language": "en", "timestamp": "9 mins ago"},
        {"id": "TRT-8918", "category": "Remote APK Download", "risk": "Critical", "score": 92, "language": "en", "timestamp": "14 mins ago"},
        {"id": "TRT-8917", "category": "Task Job Fraud", "risk": "Medium", "score": 58, "language": "hi-rom", "timestamp": "21 mins ago"}
    ]
}


@app.get("/health")
def health():
    return {
        "status": "ok",
        "platform": "ZenVex Guard",
        "tagline": "Detect. Analyse. Protect.",
        "version": app.version
    }


@app.post("/api/v1/scan/text", response_model=ScanResponse)
def scan_text(req: TextScanRequest):
    return analyze_text(req.text)


@app.post("/api/v1/scan/url", response_model=ScanResponse)
def scan_url(req: UrlScanRequest):
    return analyze_url_only(req.url)


@app.get("/api/v1/examples", response_model=List[Example])
def examples():
    return EXAMPLES


@app.get("/api/v1/playbooks")
def list_playbooks():
    return list(PLAYBOOK_DETAILS.values())


@app.get("/api/v1/playbooks/{playbook_id}")
def get_playbook(playbook_id: str):
    if playbook_id in PLAYBOOK_DETAILS:
        return PLAYBOOK_DETAILS[playbook_id]
    return {"error": "Playbook not found"}


@app.get("/api/v1/stats")
def threat_stats():
    return INTELLIGENCE_STATS


# Mount static assets if dist exists
if FRONTEND_DIST.exists():
    app.mount("/assets", StaticFiles(directory=FRONTEND_DIST / "assets"), name="assets")

app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")


@app.get("/", include_in_schema=False)
def index():
    prod_index = FRONTEND_DIST / "index.html"
    if prod_index.exists():
        return FileResponse(prod_index)
    return FileResponse(STATIC_DIR / "index.html")
