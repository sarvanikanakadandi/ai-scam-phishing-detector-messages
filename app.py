import streamlit as st
import os
import re
from urllib.parse import urlparse
from datetime import datetime
from dotenv import load_dotenv
from google import genai


load_dotenv()

API_KEY = os.getenv("GEMINI_API_KEY")

if not API_KEY:
    st.error("⚠️ GEMINI_API_KEY is missing from your .env file.")
    st.info(
        "Create a .env file and add: GEMINI_API_KEY=your_api_key"
    )
    st.stop()

client = genai.Client(api_key=API_KEY)

# =========================================================
# PAGE CONFIGURATION
# =========================================================

st.set_page_config(
    page_title="AI Scam & Phishing Detector",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="collapsed"
)


# =========================================================
# SESSION STATE
# =========================================================

if "history" not in st.session_state:
    st.session_state.history = []

if "total_scans" not in st.session_state:
    st.session_state.total_scans = 0

if "safe_count" not in st.session_state:
    st.session_state.safe_count = 0

if "suspicious_count" not in st.session_state:
    st.session_state.suspicious_count = 0

if "scam_count" not in st.session_state:
    st.session_state.scam_count = 0

if "risk_scores" not in st.session_state:
    st.session_state.risk_scores = []


# =========================================================
# CUSTOM CSS
# =========================================================

st.markdown("""
<style>

@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&family=Space+Grotesk:wght@500;600;700&display=swap');


/* =====================================================
   GLOBAL
   ===================================================== */

.stApp {
    background:
        radial-gradient(circle at 10% 10%, rgba(0,212,255,0.12), transparent 28%),
        radial-gradient(circle at 90% 20%, rgba(99,102,241,0.15), transparent 30%),
        radial-gradient(circle at 50% 100%, rgba(14,165,233,0.10), transparent 35%),
        linear-gradient(135deg,#07111f 0%,#0a1628 45%,#08111f 100%);

    color:#eaf4ff;
    font-family:'Inter',sans-serif;
}


.block-container {
    max-width:1250px;
    padding-top:2rem;
    padding-bottom:3rem;
}


#MainMenu {
    visibility:hidden;
}

footer {
    visibility:hidden;
}

header {
    visibility:hidden;
}


/* =====================================================
   HEADINGS
   ===================================================== */

h1,h2,h3 {
    font-family:'Space Grotesk',sans-serif !important;
}

h1 {
    font-size:3.1rem !important;
    font-weight:800 !important;
    text-align:center;

    background:linear-gradient(
        90deg,
        #ffffff,
        #67e8f9,
        #38bdf8,
        #818cf8
    );

    -webkit-background-clip:text;
    -webkit-text-fill-color:transparent;
}


/* =====================================================
   HERO
   ===================================================== */

.hero-badge {
    display:inline-block;

    padding:8px 18px;

    margin-bottom:15px;

    border-radius:50px;

    background:rgba(14,165,233,0.12);

    border:1px solid rgba(56,189,248,0.35);

    color:#67e8f9;

    font-size:0.82rem;

    font-weight:700;

    letter-spacing:1.5px;

    text-transform:uppercase;
}


.intro-box {
    text-align:center;

    max-width:850px;

    margin:0 auto 30px auto;
}

.intro-box p {
    color:#a9bdd2;

    font-size:1.05rem;

    line-height:1.8;
}



/* =====================================================
   BUTTONS
   ===================================================== */

.stButton > button {

    width:100%;

    border:none !important;

    border-radius:14px !important;

    padding:13px 20px !important;

    background:
        linear-gradient(
            135deg,
            #0284c7,
            #2563eb,
            #4f46e5
        ) !important;

    color:white !important;

    font-family:'Space Grotesk',sans-serif !important;

    font-weight:700 !important;

    transition:all 0.25s ease !important;
}

.stButton > button:hover {

    transform:translateY(-2px);

    box-shadow:
        0 12px 35px rgba(37,99,235,0.35);
}


/* =====================================================
   TEXT INPUTS
   ===================================================== */

.stTextArea textarea,
.stTextInput input {

    background:rgba(3,15,28,0.92) !important;

    color:#ecf9ff !important;

    border:1px solid rgba(56,189,248,0.25) !important;

    border-radius:15px !important;

    padding:15px !important;

    font-family:'Inter',sans-serif !important;
}


.stTextArea textarea:focus,
.stTextInput input:focus {

    border:1px solid #38bdf8 !important;

    box-shadow:
        0 0 0 2px rgba(56,189,248,0.12) !important;
}


.stTextArea label,
.stTextInput label {

    color:#dff6ff !important;

    font-weight:700 !important;
}


/* =====================================================
   CARDS
   ===================================================== */

.card {

    background:
        linear-gradient(
            145deg,
            rgba(16,36,59,0.92),
            rgba(9,25,43,0.92)
        );

    border:1px solid rgba(148,163,184,0.15);

    border-radius:20px;

    padding:25px;

    margin-bottom:20px;

    box-shadow:
        0 15px 40px rgba(0,0,0,0.20);
}


.card:hover {

    border-color:rgba(56,189,248,0.32);

    box-shadow:
        0 20px 45px rgba(0,0,0,0.28);
}


.card-icon {

    font-size:2.1rem;

    margin-bottom:10px;
}


.card-title {

    color:#f0f9ff;

    font-family:'Space Grotesk',sans-serif;

    font-size:1.15rem;

    font-weight:700;

    margin-bottom:8px;
}


.card-text {

    color:#9fb4c9;

    line-height:1.65;

    font-size:0.94rem;
}


/* =====================================================
   DASHBOARD METRICS
   ===================================================== */

.metric-card {

    background:
        linear-gradient(
            145deg,
            rgba(13,37,61,0.95),
            rgba(8,23,40,0.95)
        );

    border:1px solid rgba(56,189,248,0.20);

    border-radius:20px;

    padding:22px;

    text-align:center;

    min-height:135px;
}


.metric-number {

    color:#67e8f9;

    font-family:'Space Grotesk',sans-serif;

    font-size:2rem;

    font-weight:800;
}


.metric-label {

    color:#91a9bd;

    font-size:0.88rem;

    margin-top:5px;
}


/* =====================================================
   SECTION TITLES
   ===================================================== */

.section-title {

    font-family:'Space Grotesk',sans-serif;

    font-size:1.8rem;

    font-weight:700;

    color:#f1f5f9;

    margin-bottom:20px;
}


/* =====================================================
   RESULT
   ===================================================== */

.result-card {

    background:
        linear-gradient(
            145deg,
            rgba(13,37,61,0.95),
            rgba(8,23,40,0.95)
        );

    border:1px solid rgba(56,189,248,0.25);

    border-radius:22px;

    padding:28px;

    margin-top:20px;

    box-shadow:
        0 20px 60px rgba(0,0,0,0.30);
}


.result-title {

    font-family:'Space Grotesk',sans-serif;

    font-size:1.7rem;

    font-weight:700;

    color:#67e8f9;

    margin-bottom:15px;
}


/* =====================================================
   HISTORY
   ===================================================== */

.history-item {

    background:rgba(8,24,42,0.75);

    border:1px solid rgba(56,189,248,0.13);

    border-radius:16px;

    padding:17px;

    margin-bottom:12px;
}


.history-message {

    color:#dbeafe;

    font-size:0.92rem;

    line-height:1.5;
}


.history-meta {

    color:#7f9bb3;

    font-size:0.78rem;

    margin-top:7px;
}


/* =====================================================
   INFO BOX
   ===================================================== */

.tip-box {

    background:rgba(14,165,233,0.08);

    border:1px solid rgba(56,189,248,0.20);

    border-radius:16px;

    padding:18px;

    color:#bdeeff;

    line-height:1.6;

    margin-bottom:20px;
}


/* =====================================================
   FOOTER
   ===================================================== */

.simple-footer {

    text-align:center;

    margin-top:45px;

    padding:28px 20px;

    border-top:1px solid rgba(56,189,248,0.18);

    background:rgba(8,24,42,0.65);

    border-radius:18px;
}


.simple-footer-title {

    color:#eaf8ff;

    font-family:'Space Grotesk',sans-serif;

    font-size:1.15rem;

    font-weight:700;

    margin-bottom:8px;
}


.simple-footer-text {

    color:#91a9bd;

    font-size:0.88rem;

    margin-bottom:12px;
}


.simple-footer-warning {

    color:#fbbf24;

    font-size:0.82rem;
}


/* =====================================================
   SECURITY STATUS
   ===================================================== */

.security-status {

    text-align:center;

    margin-top:25px;

    color:#86efac;

    font-size:0.85rem;

    font-weight:600;
}


/* =====================================================
   MOBILE
   ===================================================== */

@media(max-width:768px) {

    h1 {
        font-size:2.2rem !important;
    }

    .block-container {
        padding-left:1rem;
        padding-right:1rem;
    }
}
/* =====================================================
   NAVIGATION - STREAMLIT SELECTBOX
   ===================================================== */

div[data-testid="stSelectbox"] {
    margin-top: 5px;
    margin-bottom: 25px;
}

/* Navigate label */
div[data-testid="stSelectbox"] label {
    color: #67e8f9 !important;
    font-family: 'Space Grotesk', sans-serif !important;
    font-size: 0.9rem !important;
    font-weight: 700 !important;
    letter-spacing: 0.8px !important;
    margin-bottom: 8px !important;
}

/* Main dropdown */
div[data-testid="stSelectbox"] [data-baseweb="select"] {
    background: linear-gradient(
        135deg,
        rgba(13, 37, 61, 0.98),
        rgba(8, 24, 42, 0.98)
    ) !important;

    border: 1px solid rgba(56, 189, 248, 0.35) !important;

    border-radius: 14px !important;

    min-height: 52px !important;

    box-shadow:
        0 8px 25px rgba(0, 0, 0, 0.20),
        inset 0 1px 0 rgba(255,255,255,0.04) !important;

    transition: all 0.25s ease !important;
}

/* Hover */
div[data-testid="stSelectbox"] [data-baseweb="select"]:hover {
    border-color: #38bdf8 !important;

    box-shadow:
        0 0 0 1px rgba(56, 189, 248, 0.18),
        0 10px 30px rgba(14, 165, 233, 0.18) !important;
}

/* Selected text */
div[data-testid="stSelectbox"] [data-baseweb="select"] * {
    color: #eaf8ff !important;
    font-family: 'Inter', sans-serif !important;
}

/* Arrow */
div[data-testid="stSelectbox"] [data-baseweb="select"] svg {
    color: #67e8f9 !important;
}

/* Dropdown popup */
div[data-baseweb="popover"] {
    background: #0b1b2d !important;
    border: 1px solid rgba(56, 189, 248, 0.30) !important;
    border-radius: 14px !important;
    box-shadow: 0 20px 50px rgba(0,0,0,0.45) !important;
}

/* Dropdown list */
div[data-baseweb="popover"] [role="listbox"] {
    background: #0b1b2d !important;
    border-radius: 14px !important;
    padding: 6px !important;
}

/* Options */
div[data-baseweb="popover"] [role="option"] {
    color: #dff6ff !important;
    background: transparent !important;
    border-radius: 10px !important;
    padding: 12px 14px !important;
    font-family: 'Inter', sans-serif !important;
}

/* Option hover */
div[data-baseweb="popover"] [role="option"]:hover {
    background: rgba(14, 165, 233, 0.16) !important;
    color: #67e8f9 !important;
}

/* Selected option */
div[data-baseweb="popover"] [aria-selected="true"] {
    background: rgba(37, 99, 235, 0.20) !important;
    color: #67e8f9 !important;
    font-weight: 700 !important;
}
</style>
""", unsafe_allow_html=True)


# =========================================================
# GEMINI SETUP
# =========================================================

load_dotenv()

API_KEY = os.getenv("GEMINI_API_KEY")

if not API_KEY:

    st.error("⚠️ GEMINI_API_KEY is missing from your .env file.")

    st.info(
        "Create a .env file and add: GEMINI_API_KEY=your_api_key"
    )

    st.stop()

client = genai.Client(api_key=API_KEY)


# =========================================================
# HELPER FUNCTIONS
# =========================================================

def add_to_history(category, content, risk_level, score):

    st.session_state.history.insert(
        0,
        {
            "category": category,
            "content": content[:180],
            "risk": risk_level,
            "score": score,
            "time": datetime.now().strftime("%d %b %Y, %I:%M %p")
        }
    )

    st.session_state.total_scans += 1

    st.session_state.risk_scores.append(score)

    if "SAFE" in risk_level.upper():
        st.session_state.safe_count += 1

    elif "SUSPICIOUS" in risk_level.upper():
        st.session_state.suspicious_count += 1

    else:
        st.session_state.scam_count += 1


def extract_score(result):

    match = re.search(
        r"Risk Score\s*:\s*(\d+)",
        result,
        re.IGNORECASE
    )

    if match:
        return int(match.group(1))

    return 0


def extract_risk(result):

    match = re.search(
        r"Risk Level\s*:\s*(.+)",
        result,
        re.IGNORECASE
    )

    if match:

        risk = match.group(1).strip()

        return risk[:40]

    return "UNKNOWN"


def analyze_with_gemini(content, category="Message"):

    prompt = f"""
You are an AI Scam and Phishing Detection system.

Analyze this {category} carefully.

---------------- CONTENT ----------------
{content}
------------------------------------------

Classify it as one of:

1. SAFE
2. SUSPICIOUS
3. SCAM / PHISHING

Analyze:

- Urgency or pressure
- Threats or fear
- Requests for money
- Password or OTP requests
- Banking information
- Suspicious links
- Fake rewards
- Impersonation
- Unusual language
- Unknown downloads
- Personal information requests
- Emotional manipulation
- Suspicious domains
- Social engineering techniques

Return EXACTLY this structure:

Risk Level: SAFE / SUSPICIOUS / SCAM / PHISHING

Risk Score: 0-100

Detected Factors:
- factor 1
- factor 2
- factor 3

Explanation:
Explain clearly why this content received this risk level.

Safety Advice:
Give practical advice to the user.

Do not claim something is definitely fraudulent unless evidence is very strong.
"""

    response = client.models.generate_content(
        model="gemini-3.5-flash-lite",
        contents=prompt
    )

    return response.text


# =========================================================
# URL ANALYZER
# =========================================================

def analyze_url(url):

    checks = []

    score = 0

    url = url.strip()

    if not url.startswith(("http://", "https://")):

        url_for_parse = "https://" + url

    else:

        url_for_parse = url

    try:

        parsed = urlparse(url_for_parse)

        domain = parsed.netloc.lower()

        if not domain:

            return {
                "score": 90,
                "risk": "INVALID / SUSPICIOUS",
                "checks": ["Unable to identify a valid domain."]
            }

        # HTTPS
        if parsed.scheme == "https":

            checks.append("✅ Uses HTTPS")

        else:

            checks.append("⚠️ Does not use HTTPS")

            score += 20

        # IP address
        if re.match(r"^\d{1,3}(\.\d{1,3}){3}$", domain):

            checks.append("🚨 URL uses an IP address instead of a normal domain")

            score += 30

        # @ symbol
        if "@" in url:

            checks.append("🚨 URL contains @ symbol")

            score += 25

        # Long URL
        if len(url) > 100:

            checks.append("⚠️ Unusually long URL")

            score += 15

        else:

            checks.append("✅ URL length appears normal")

        # Suspicious keywords
        suspicious_words = [
            "verify",
            "login",
            "secure",
            "account",
            "update",
            "claim",
            "reward",
            "bonus",
            "password",
            "otp",
            "wallet",
            "bank"
        ]

        found_words = [
            word for word in suspicious_words
            if word in url.lower()
        ]

        if found_words:

            checks.append(
                "⚠️ Suspicious keywords: "
                + ", ".join(found_words)
            )

            score += min(25, len(found_words) * 5)

        # Shortened URLs
        shorteners = [
            "bit.ly",
            "tinyurl.com",
            "t.co",
            "is.gd",
            "goo.gl",
            "ow.ly"
        ]

        if any(shortener in domain for shortener in shorteners):

            checks.append("⚠️ URL appears to use a URL shortener")

            score += 20

        # Too many subdomains
        if domain.count(".") >= 3:

            checks.append("⚠️ Multiple subdomains detected")

            score += 10

        # Hyphens
        if domain.count("-") >= 2:

            checks.append("⚠️ Domain contains multiple hyphens")

            score += 10

        score = min(score, 100)

        if score >= 60:

            risk = "HIGH RISK"

        elif score >= 30:

            risk = "SUSPICIOUS"

        else:

            risk = "LOW RISK"

        return {
            "score": score,
            "risk": risk,
            "domain": domain,
            "checks": checks
        }

    except Exception:

        return {
            "score": 90,
            "risk": "INVALID / SUSPICIOUS",
            "checks": ["Could not parse the URL."]
        }


# =========================================================
# DEMO EXAMPLES
# =========================================================

SAFE_EXAMPLE = """
Hi Rahul, your appointment with ABC Dental Clinic is confirmed
for tomorrow at 10:00 AM. Please arrive 10 minutes early.
Thank you.
"""

SUSPICIOUS_EXAMPLE = """
You have been selected for a special reward from our company.
Please confirm your details by clicking the link below.
You may be asked to provide your phone number and email address
to claim your reward.
"""

SCAM_EXAMPLE = """
URGENT: Your bank account has been suspended due to suspicious
activity. Verify your account within 30 minutes or it will be
permanently blocked. Click the link below and enter your account
number, password and OTP immediately.
"""


# =========================================================
# HERO
# =========================================================

st.markdown(
    """
    <div style="text-align:center;">
        <div class="hero-badge">
            🛡️ AI-POWERED CYBERSECURITY PLATFORM
        </div>
    </div>
    """,
    unsafe_allow_html=True
)

st.title("AI Scam & Phishing Detector")

st.markdown(
    """
    <div class="intro-box">
        <p>
            An intelligent cybersecurity platform that helps identify
            <strong>scams, phishing attempts, suspicious URLs and
            fraudulent digital communication</strong> using AI.
        </p>
    </div>
    """,
    unsafe_allow_html=True
)


# =========================================================
# NAVIGATION
# =========================================================

st.markdown(
    """
    <div class="section-title" style="
        font-size:1.05rem;
        margin-bottom:5px;
        color:#67e8f9;
    ">
        🧭 Security Navigation
    </div>
    """,
    unsafe_allow_html=True
)

page = st.selectbox(
    "Navigate",
    [
        "🏠 Dashboard",
        "🔍 Message Scanner",
        "🔗 URL Scanner",
        "📧 Email Analyzer",
        "📱 SMS / WhatsApp Analyzer",
        "🧪 Demo Mode",
        "📊 Scan History",
        "🎓 Cyber Safety Center"
    ],
    key="main_navigation"
)


# =========================================================
# DASHBOARD
# =========================================================

if page == "🏠 Dashboard":

    st.markdown(
        '<div class="section-title">📊 Security Dashboard</div>',
        unsafe_allow_html=True
    )

    total = st.session_state.total_scans

    average = (
        sum(st.session_state.risk_scores)
        / len(st.session_state.risk_scores)
        if st.session_state.risk_scores
        else 0
    )

    c1, c2, c3, c4 = st.columns(4)

    with c1:

        st.markdown(
            f"""
            <div class="metric-card">
                <div class="metric-number">
                    {total}
                </div>
                <div class="metric-label">
                    Total Scans
                </div>
            </div>
            """,
            unsafe_allow_html=True
        )

    with c2:

        st.markdown(
            f"""
            <div class="metric-card">
                <div class="metric-number">
                    {st.session_state.safe_count}
                </div>
                <div class="metric-label">
                    🟢 Safe
                </div>
            </div>
            """,
            unsafe_allow_html=True
        )

    with c3:

        st.markdown(
            f"""
            <div class="metric-card">
                <div class="metric-number">
                    {st.session_state.suspicious_count}
                </div>
                <div class="metric-label">
                    🟡 Suspicious
                </div>
            </div>
            """,
            unsafe_allow_html=True
        )

    with c4:

        st.markdown(
            f"""
            <div class="metric-card">
                <div class="metric-number">
                    {st.session_state.scam_count}
                </div>
                <div class="metric-label">
                    🔴 Threats
                </div>
            </div>
            """,
            unsafe_allow_html=True
        )

    st.markdown("<br>", unsafe_allow_html=True)

    c1, c2 = st.columns(2)

    with c1:

        st.markdown(
            f"""
            <div class="card">
                <div class="card-icon">📈</div>
                <div class="card-title">
                    Average Risk Score
                </div>
                <div class="card-text">
                    {average:.1f} / 100
                </div>
            </div>
            """,
            unsafe_allow_html=True
        )

    with c2:

        st.markdown(
            """
            <div class="card">
                <div class="card-icon">🤖</div>
                <div class="card-title">
                    AI Detection Engine
                </div>
                <div class="card-text">
                    Gemini-powered analysis evaluates messages,
                    emails and suspicious digital content for
                    social engineering and phishing indicators.
                </div>
            </div>
            """,
            unsafe_allow_html=True
        )

    st.markdown(
        '<div class="section-title">🚀 Security Tools</div>',
        unsafe_allow_html=True
    )

    c1, c2, c3 = st.columns(3)

    with c1:

        st.markdown(
            """
            <div class="card">
                <div class="card-icon">🔍</div>
                <div class="card-title">Message Scanner</div>
                <div class="card-text">
                    Analyze suspicious messages with AI.
                </div>
            </div>
            """,
            unsafe_allow_html=True
        )

    with c2:

        st.markdown(
            """
            <div class="card">
                <div class="card-icon">🔗</div>
                <div class="card-title">URL Scanner</div>
                <div class="card-text">
                    Inspect suspicious links and domains.
                </div>
            </div>
            """,
            unsafe_allow_html=True
        )

    with c3:

        st.markdown(
            """
            <div class="card">
                <div class="card-icon">🎓</div>
                <div class="card-title">Safety Center</div>
                <div class="card-text">
                    Learn how to recognize common cyber scams.
                </div>
            </div>
            """,
            unsafe_allow_html=True
        )


# =========================================================
# MESSAGE SCANNER
# =========================================================

elif page == "🔍 Message Scanner":

    st.markdown(
        '<div class="section-title">🔍 AI Message Scanner</div>',
        unsafe_allow_html=True
    )

    st.markdown(
        """
        <div class="tip-box">
            Paste a suspicious SMS, social media message, banking
            message or other text below. Gemini will analyze its
            risk indicators.
        </div>
        """,
        unsafe_allow_html=True
    )

    user_text = st.text_area(
        "Enter suspicious message",
        height=220,
        placeholder=(
            "Example:\n\n"
            "Your bank account will be blocked today. "
            "Click this link immediately to verify your account..."
        )
    )

    if st.button(
        "🔎 ANALYZE MESSAGE",
        use_container_width=True
    ):

        if not user_text.strip():

            st.warning(
                "⚠️ Please enter a message first."
            )

        else:

            with st.spinner(
                "🤖 AI is analyzing the message..."
            ):

                try:

                    result = analyze_with_gemini(
                        user_text,
                        "message"
                    )

                    score = extract_score(result)

                    risk = extract_risk(result)

                    add_to_history(
                        "Message",
                        user_text,
                        risk,
                        score
                    )

                    st.success(
                        "✅ Analysis completed successfully!"
                    )

                    st.markdown(
                        """
                        <div class="result-card">
                            <div class="result-title">
                                📊 Detection Result
                            </div>
                        </div>
                        """,
                        unsafe_allow_html=True
                    )

                    st.markdown(result)

                except Exception as e:

                    st.error(
                        "❌ Gemini is temporarily unavailable. "
                        "Please try again in a moment."
                    )

                    st.caption(
                        f"Technical detail: {str(e)}"
                    )


# =========================================================
# URL SCANNER
# =========================================================

elif page == "🔗 URL Scanner":

    st.markdown(
        '<div class="section-title">🔗 Suspicious URL Scanner</div>',
        unsafe_allow_html=True
    )

    st.markdown(
        """
        <div class="tip-box">
            Enter a suspicious website link. The scanner checks
            URL structure, HTTPS usage, IP addresses, URL shorteners,
            suspicious keywords and other indicators.
        </div>
        """,
        unsafe_allow_html=True
    )

    url = st.text_input(
        "Enter website URL",
        placeholder="https://example.com/login"
    )

    if st.button(
        "🔗 SCAN URL",
        use_container_width=True
    ):

        if not url.strip():

            st.warning("⚠️ Please enter a URL.")

        else:

            result = analyze_url(url)

            # =================================================
            # URL SECURITY RESULT
            # =================================================

            result_html = f"""
            <div class="result-card">

                <div class="result-title">
                    🔗 URL Security Result
                </div>

                <h3>
                    Risk Level: {result["risk"]}
                </h3>

                <h3>
                    Risk Score: {result["score"]}/100
                </h3>

                <p>
                    <strong>Domain:</strong>
                    {result.get("domain", "Unknown")}
                </p>

            </div>
            """

            st.html(result_html)

            # =================================================
            # URL CHECKS
            # =================================================

            st.markdown(
                '<div class="section-title">🔎 URL Checks</div>',
                unsafe_allow_html=True
            )

            for check in result["checks"]:

                st.markdown(
                    f"- {check}"
                )
# =========================================================
# EMAIL ANALYZER
# =========================================================

elif page == "📧 Email Analyzer":

    st.markdown(
        '<div class="section-title">📧 Email Scam Analyzer</div>',
        unsafe_allow_html=True
    )

    sender = st.text_input(
        "Sender Email",
        placeholder="example@gmail.com"
    )

    subject = st.text_input(
        "Email Subject",
        placeholder="Urgent: Verify your account"
    )

    email_body = st.text_area(
        "Email Content",
        height=260,
        placeholder="Paste the complete email here..."
    )

    if st.button(
        "📧 ANALYZE EMAIL",
        use_container_width=True
    ):

        if not email_body.strip():

            st.warning(
                "⚠️ Please enter the email content."
            )

        else:

            combined = f"""
Sender: {sender}

Subject: {subject}

Email Body:
{email_body}
"""

            with st.spinner(
                "🤖 AI is analyzing the email..."
            ):

                try:

                    result = analyze_with_gemini(
                        combined,
                        "email"
                    )

                    score = extract_score(result)

                    risk = extract_risk(result)

                    add_to_history(
                        "Email",
                        email_body,
                        risk,
                        score
                    )

                    st.success(
                        "✅ Email analysis completed!"
                    )

                    st.markdown(
                        '<div class="result-card">'
                        '<div class="result-title">'
                        '📧 Email Detection Result'
                        '</div>'
                        '</div>',
                        unsafe_allow_html=True
                    )

                    st.markdown(result)

                except Exception as e:

                    st.error(
                        "❌ Gemini is temporarily unavailable."
                    )

                    st.caption(
                        f"Technical detail: {str(e)}"
                    )


# =========================================================
# SMS / WHATSAPP ANALYZER
# =========================================================

elif page == "📱 SMS / WhatsApp Analyzer":

    st.markdown(
        '<div class="section-title">'
        '📱 SMS / WhatsApp Scam Analyzer'
        '</div>',
        unsafe_allow_html=True
    )

    st.markdown(
        """
        <div class="tip-box">
            Analyze suspicious SMS, WhatsApp messages and social
            media messages such as OTP scams, KYC scams, fake
            delivery messages and job scams.
        </div>
        """,
        unsafe_allow_html=True
    )

    sms = st.text_area(
        "Enter SMS / WhatsApp message",
        height=240,
        placeholder=(
            "Example:\n\n"
            "Your KYC has expired. Click the link to update "
            "your details immediately..."
        )
    )

    if st.button(
        "📱 ANALYZE SMS",
        use_container_width=True
    ):

        if not sms.strip():

            st.warning(
                "⚠️ Please enter a message."
            )

        else:

            with st.spinner(
                "🤖 AI is analyzing the message..."
            ):

                try:

                    result = analyze_with_gemini(
                        sms,
                        "SMS or WhatsApp message"
                    )

                    score = extract_score(result)

                    risk = extract_risk(result)

                    add_to_history(
                        "SMS / WhatsApp",
                        sms,
                        risk,
                        score
                    )

                    st.success(
                        "✅ SMS analysis completed!"
                    )

                    st.markdown(
                        '<div class="result-card">'
                        '<div class="result-title">'
                        '📱 Detection Result'
                        '</div>'
                        '</div>',
                        unsafe_allow_html=True
                    )

                    st.markdown(result)

                except Exception as e:

                    st.error(
                        "❌ Gemini is temporarily unavailable."
                    )

                    st.caption(
                        f"Technical detail: {str(e)}"
                    )


# =========================================================
# DEMO MODE
# =========================================================

elif page == "🧪 Demo Mode":

    st.markdown(
        '<div class="section-title">🧪 Interactive Demo Mode</div>',
        unsafe_allow_html=True
    )

    st.markdown(
        """
        <div class="tip-box">
            Use these examples to demonstrate the detector during
            your project presentation.
        </div>
        """,
        unsafe_allow_html=True
    )

    c1, c2, c3 = st.columns(3)

    with c1:

        st.markdown(
            """
            <div class="card">
                <div class="card-icon">🟢</div>
                <div class="card-title">
                    Safe Example
                </div>
                <div class="card-text">
                    Normal appointment notification.
                </div>
            </div>
            """,
            unsafe_allow_html=True
        )

        if st.button(
            "🟢 TEST SAFE",
            key="safe_demo"
        ):

            with st.spinner("Analyzing..."):

                try:

                    result = analyze_with_gemini(
                        SAFE_EXAMPLE,
                        "message"
                    )

                    score = extract_score(result)

                    risk = extract_risk(result)

                    add_to_history(
                        "Demo - Safe",
                        SAFE_EXAMPLE,
                        risk,
                        score
                    )

                    st.markdown(result)

                except Exception as e:

                    st.error(
                        "Gemini is temporarily unavailable."
                    )

    with c2:

        st.markdown(
            """
            <div class="card">
                <div class="card-icon">🟡</div>
                <div class="card-title">
                    Suspicious Example
                </div>
                <div class="card-text">
                    Reward message requesting personal information.
                </div>
            </div>
            """,
            unsafe_allow_html=True
        )

        if st.button(
            "🟡 TEST SUSPICIOUS",
            key="suspicious_demo"
        ):

            with st.spinner("Analyzing..."):

                try:

                    result = analyze_with_gemini(
                        SUSPICIOUS_EXAMPLE,
                        "message"
                    )

                    score = extract_score(result)

                    risk = extract_risk(result)

                    add_to_history(
                        "Demo - Suspicious",
                        SUSPICIOUS_EXAMPLE,
                        risk,
                        score
                    )

                    st.markdown(result)

                except Exception:

                    st.error(
                        "Gemini is temporarily unavailable."
                    )

    with c3:

        st.markdown(
            """
            <div class="card">
                <div class="card-icon">🔴</div>
                <div class="card-title">
                    Phishing Example
                </div>
                <div class="card-text">
                    Fake bank verification requesting OTP.
                </div>
            </div>
            """,
            unsafe_allow_html=True
        )

        if st.button(
            "🔴 TEST PHISHING",
            key="scam_demo"
        ):

            with st.spinner("Analyzing..."):

                try:

                    result = analyze_with_gemini(
                        SCAM_EXAMPLE,
                        "message"
                    )

                    score = extract_score(result)

                    risk = extract_risk(result)

                    add_to_history(
                        "Demo - Phishing",
                        SCAM_EXAMPLE,
                        risk,
                        score
                    )

                    st.markdown(result)

                except Exception:

                    st.error(
                        "Gemini is temporarily unavailable."
                    )


# =========================================================
# SCAN HISTORY
# =========================================================

elif page == "📊 Scan History":

    st.markdown(
        '<div class="section-title">📊 Scan History</div>',
        unsafe_allow_html=True
    )

    if not st.session_state.history:

        st.info(
            "No scans yet. Start analyzing messages to build your history."
        )

    else:

        if st.button(
            "🗑️ CLEAR HISTORY",
            key="clear_history"
        ):

            st.session_state.history = []

            st.session_state.total_scans = 0

            st.session_state.safe_count = 0

            st.session_state.suspicious_count = 0

            st.session_state.scam_count = 0

            st.session_state.risk_scores = []

            st.rerun()
