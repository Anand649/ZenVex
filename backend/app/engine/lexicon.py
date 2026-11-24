"""Scam indicator lexicon.

Each indicator has an id, a user-facing label, a weight (points added to the risk score
when the indicator fires) and regex patterns covering English, Telugu script, Romanised
Telugu, Hindi script and Romanised Hindi.

IMPORTANT
- Regexes are matched against the ORIGINAL text so that match offsets can be used for
  highlighting in the UI.
- `credential_request` is handled by custom code in rules.py (it needs negation and
  OTP-delivery handling) so its patterns here are only used for the Indic/Romanised forms.
- Telugu and Hindi terms must be reviewed by a native speaker before being demonstrated.
- Weights are starting values, not calibrated probabilities.
"""
from dataclasses import dataclass


@dataclass(frozen=True)
class IndicatorDef:
    id: str
    label: str
    weight: int
    patterns: tuple


INDICATORS = (
    IndicatorDef(
        "urgency",
        "Creates urgency or a deadline",
        12,
        (
            r"\b(immediately|urgent(ly)?|right now|asap|today only|last chance|within\s+\d+\s*(hours?|hrs?|minutes?|mins?)|expires?\s+(today|soon|tonight)|act now|without delay|final (notice|warning))\b",
            r"\b(ventane|ippude|twaraga|turant|abhi|jaldi)\b",
            r"వెంటనే|తక్షణం|ఈరోజే",
            r"तुरंत|अभी|जल्दी|आज ही",
        ),
    ),
    IndicatorDef(
        "account_threat",
        "Threatens to block, suspend or close an account or service",
        20,
        (
            r"\b(account|a/c|card|sim|number|service|connection|wallet|upi|yono)\b[^.!?।\n]{0,40}\b(block(ed)?|suspend(ed)?|deactivat(ed|e)|terminat(ed|e)|clos(ed|ure)|frozen|freeze|disconnect(ed)?|restricted)\b",
            r"\b(block(ed)?|suspend(ed)?|deactivat(ed|e))\b[^.!?।\n]{0,30}\b(account|a/c|card|sim|number)\b",
            r"\b(account|khata|khaata)\s+(band|bandh|block)\b",
            r"\b(block|band|bandh|suspend)\s+(ho\s+(jayega|jaayega|jayegi|jaegi)|avutundi|avuthundi|avutadi)\b",
            r"(ఖాతా|అకౌంట్)[^.!?।\n]{0,30}(బ్లాక్|నిలిపివేయ|మూసివేయ|రద్దు)",
            r"(खाता|अकाउंट)[^.!?।\n]{0,30}(बंद|ब्लॉक|निलंबित)",
        ),
    ),
    IndicatorDef(
        "kyc_pressure",
        "Pressures you to update or verify KYC, PAN or Aadhaar",
        20,
        (
            r"\b(re-?kyc|e-?kyc|kyc|pan|aadhaar|aadhar)\b[^.!?।\n]{0,50}\b(update|verify|verification|expire[sd]?|pending|incomplete|suspend(ed)?|mandatory)\b",
            r"\b(update|verify|complete|incomplete|pending|expired|mandatory|renew|link)\b[^.!?।\n]{0,30}\b(re-?kyc|e-?kyc|kyc|pan|aadhaar|aadhar)\b",
            r"కేవైసీ|కేవైసి|केवाईसी",
            r"(kyc|కేవైసీ)[^.!?।\n]{0,20}(అప్.?డేట్|నవీకరించ|వెరిఫై)",
        ),
    ),
    IndicatorDef(
        "credential_request",
        "Asks for an OTP, PIN, password or card details",
        25,
        (
            r"\botp\b\s*(cheppandi|pampandi|share cheyandi|send cheyandi|ivvandi|batayein|bataiye|batao|bhejein|bhejiye|share karein|de dijiye|dijiye)",
            r"(ఓటీపీ|otp)[^.!?।\n]{0,20}(చెప్పండి|పంపండి|ఇవ్వండి)",
            r"(ओटीपी|otp)[^.!?।\n]{0,20}(बताएं|बताइए|बताओ|भेजें|भेजिए|दें|शेयर)",
        ),
    ),
    IndicatorDef(
        "payment_pressure",
        "Asks you to pay a fee, deposit or approve a payment request",
        15,
        (
            r"\b(pay|send|transfer|deposit|remit)\b[^.!?।\n]{0,30}(₹|\brs\.?|\binr|\brupees?)\s?\d",
            r"(₹|\brs\.?|\binr)\s?\d[\d,]*(\.\d+)?[^.!?।\n]{0,30}\b(fee|fees|charges?|deposit|penalty|fine|tax|advance|refundable)\b",
            r"\b(registration|processing|customs|clearance|redelivery|release|activation|security|verification|joining) (fee|fees|charges?|deposit)\b",
            r"\b(collect request|approve (the |this )?(collect )?request|accept (the |this )?(collect )?request)\b",
            r"\b(paise|paisa|amount|rupaye)\s+(bhejein|bhejiye|transfer karein|jama karein)\b",
            r"\b(dabbulu|money|amount)\s+(pampandi|pay cheyandi)\b",
            r"\bpay\s+cheyandi\b",
            r"డబ్బు[^.!?।\n]{0,20}(పంపండి|చెల్లించండి)",
            r"पैसे[^.!?।\n]{0,15}(भेजें|भेजिए|जमा)",
        ),
    ),
    IndicatorDef(
        "upi_refund_collect",
        "Asks you to approve a UPI collect request to receive a refund",
        15,
        (
            r"(?:^|(?<=[.!?।\n]))[^\S\r\n]*(?:please[^\S\r\n]+)?"
            r"(?:approve|accept) (?:the |this |a )?(?:upi collect request|"
            r"collect request\b[^.!?।;\r\n]{0,60}\bupi)\b"
            r"[^.!?।;\r\n]{0,30}\bto receive (?:your |a |the )?refund\b",
        ),
    ),
    IndicatorDef(
        "reward_bait",
        "Promises a prize, lottery win, cashback or reward",
        12,
        (
            r"\b(you (have )?won|congratulations|lucky (winner|draw|customer)|lottery|prize|cashback|reward points?|free gift|claim (your )?(prize|reward|gift|cashback)|kbc)\b",
            r"\b(gelchukunnaru|gelichaaru|bahumati|bahumathi|inaam|jeet (liya|gaye)|jeete)\b",
            r"బహుమతి|లాటరీ|గెలుచుకున్నారు|గెలిచారు",
            r"इनाम|लॉटरी|जीत लिया|जीते",
        ),
    ),
    IndicatorDef(
        "investment_bait",
        "Promises guaranteed or unrealistic investment returns",
        30,
        (
            r"\b(guaranteed (returns?|profits?|income)|double your (money|investment)|daily (profit|income|returns?)|100\s?% (profit|returns?|safe|guaranteed)|risk[- ]free (returns?|profit)|assured returns?)\b",
            r"\bjoin (our |my )?(vip|trading|investment|stock|crypto)[a-z ]{0,15}(group|channel)\b",
        ),
    ),
    IndicatorDef(
        "job_scam",
        "Offers an easy online job or task-based earnings",
        20,
        (
            r"\b(work from home|part[- ]time job|online job|typing job|data entry job|like (and )?subscribe|(complete|do) (simple )?tasks? (and )?earn|task[- ]based)\b",
            r"\bearn\s*(upto |up to )?(₹|rs\.?|inr)?\s?\d[\d,]*\s*(/|per|a|every)\s*(day|hour|week)\b",
            r"\bhiring\b[^.!?।\n]{0,30}\b(whatsapp|telegram)\b",
            r"घर बैठे (कमाएं|कमाई|पैसे)",
            r"ఇంటి నుంచి పని|ఇంటి నుండి పని",
        ),
    ),
    IndicatorDef(
        "remote_access",
        "Asks you to install a remote-access app or an APK",
        30,
        (
            r"\b(anydesk|teamviewer|quick ?support|rustdesk|airdroid|alpemix)\b",
            r"\b(install|download)\b[^.!?।\n]{0,20}\b(apk|app)\b[^.!?।\n]{0,40}\b(verify|kyc|update|support|refund|reward)\b",
            r"\.apk\b",
        ),
    ),
    IndicatorDef(
        "delivery_customs",
        "Claims a parcel is held and asks for a fee or details",
        12,
        (
            r"\b(parcel|package|courier|shipment|consignment|customs)\b[^.!?।\n]{0,60}\b(held|stuck|on hold|undelivered|fee|charges?|pay|incomplete address|address (is )?incomplete)\b",
        ),
    ),
    IndicatorDef(
        "digital_arrest",
        "Claims police or an agency case, arrest or legal action against you",
        35,
        (
            r"\b(digital arrest|arrest warrant|money laundering|narcotics|illegal items?|fake passport|case (has been |is |was )?(registered|filed|lodged))\b",
            r"\b(cbi|ncb|trai|customs|cyber ?crime|income tax|police|enforcement directorate)\b[^.!?।\n]{0,80}\b(arrest|warrant|legal action|disconnect)\b",
            r"\bstay on (the )?(video )?call\b",
        ),
    ),
    IndicatorDef(
        "unofficial_contact",
        "Asks you to contact a personal mobile number",
        10,
        (
            r"\b(call|contact|whatsapp|message|text)\b[^.!?।\n]{0,25}(\+?91[-\s]?)?\b[6-9]\d{9}\b",
        ),
    ),
)

INDICATOR_BY_ID = {i.id: i for i in INDICATORS}

# --- credential request (custom matcher, see rules.py) ---
CRED_VERBS = r"(share|send|enter|provide|tell|give|submit|confirm|verify|update|reply with|type)"
CRED_TARGETS = (
    r"(otp|pin|password|passcode|cvv|card (?:number|details)|atm pin|upi pin|mpin|"
    r"aadhaar number|pan number|net ?banking (?:id|password))"
)
CRED_EN = rf"\b{CRED_VERBS}\b[^.!?।\n]{{0,25}}\b{CRED_TARGETS}\b"
# Verbs that merely instruct the user to use an OTP that was delivered in the same message.
CRED_SOFT_VERBS = {"enter", "type", "verify", "confirm"}
NEGATION = r"(do not|don't|dont|never|not)\b"

# Romanised markers used by the language detector.
TE_ROM_MARKERS = {
    "mee", "meeru", "meeku", "cheyandi", "avutundi", "avuthundi", "ledu", "kosam",
    "vachindi", "pampandi", "cheppandi", "ventane", "ippude", "undi", "undandi",
    "dayachesi", "sampadinchandi", "roju",
}
HI_ROM_MARKERS = {
    "aapka", "aapke", "kripya", "turant", "karein", "kijiye", "hai", "hain", "jayega",
    "batayein", "bhejein", "abhi", "apna", "apne", "nahi", "tarikh", "jama",
}
