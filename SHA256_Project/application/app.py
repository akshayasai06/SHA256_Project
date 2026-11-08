import streamlit as st
import hashlib
import base64
from pathlib import Path

from verilog_runner import generate_sha256_hash


# ==================================================
# PAGE CONFIGURATION
# ==================================================

st.set_page_config(
    page_title="HashLab | SHA-256 in Verilog",
    page_icon="🔐",
    layout="wide",
    initial_sidebar_state="collapsed"
)


# ==================================================
# PROJECT PATHS / BACKGROUND IMAGE
# ==================================================

PROJECT_FOLDER = Path(__file__).resolve().parent.parent

possible_images = [
    PROJECT_FOLDER / "assests" / "image.jpg",
    PROJECT_FOLDER / "assets" / "image.jpg"
]

BACKGROUND_IMAGE = next(
    (path for path in possible_images if path.exists()),
    None
)

if BACKGROUND_IMAGE:
    with open(BACKGROUND_IMAGE, "rb") as image_file:
        image_data = base64.b64encode(image_file.read()).decode()

    hero_background = (
        "background-image: linear-gradient(100deg, rgba(10,24,48,0.94) 0%, "
        "rgba(10,24,48,0.78) 55%, rgba(10,24,48,0.55) 100%), "
        f'url("data:image/jpeg;base64,{image_data}");'
    )
else:
    hero_background = "background: linear-gradient(115deg, #0A1830, #14305F);"


# ==================================================
# CUSTOM CSS
# ==================================================

import random
from urllib.parse import quote

_rnd = random.Random(7)
_rows = []
for _i in range(12):
    _hash_row = "".join(_rnd.choice("0123456789abcdef") for _ in range(64))
    _rows.append(f'<text x="{10 + (_i % 3) * 14}" y="{26 + _i * 28}">{_hash_row}</text>')
_svg = (
    '<svg xmlns="http://www.w3.org/2000/svg" width="540" height="350">'
    '<style>text{font-family:monospace;font-size:13px;fill:#1B3A8C;opacity:0.10}</style>'
    + "".join(_rows) + '</svg>'
)
pattern_uri = "data:image/svg+xml," + quote(_svg, safe="")


CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Manrope:wght@400;500;600;700;800&family=JetBrains+Mono:wght@400;500;700&display=swap');

:root {
    --ink: #0F2038;
    --ink-soft: #25354C;
    --line: #BCCADC;
    --paper: #FFFFFF;
    --bg: #ECF1F7;
    --blue: #2D5BFF;
    --blue-dark: #1F43CC;
    --signal: #FFB020;
    --ok: #12795A;
    --ok-bg: #E4F5EE;
    --bad: #B3322F;
    --bad-bg: #FCEAE9;
}

.stApp {
    background:
        url("__PATTERN__"),
        radial-gradient(900px 520px at 5% -8%, #E4EEFF 0%, rgba(228,238,255,0) 62%),
        radial-gradient(800px 560px at 100% 0%, #CDEFE5 0%, rgba(205,239,229,0) 58%),
        linear-gradient(180deg, #C6D5EB 0%, #B2C5E0 100%);
    background-attachment: fixed;
    color: var(--ink);
    font-family: 'Manrope', sans-serif;
}

header[data-testid="stHeader"] { background: transparent; }
#MainMenu, footer { visibility: hidden; }

.block-container {
    max-width: 1180px !important;
    padding: 28px clamp(18px, 4vw, 48px) 40px !important;
}

/* ---------- top bar ---------- */
.topbar {
    display: flex;
    align-items: center;
    justify-content: space-between;
    margin-bottom: 22px;
}
.brand {
    display: flex;
    align-items: center;
    gap: 12px;
    font-weight: 800;
    font-size: 30px;
    letter-spacing: -0.5px;
    color: var(--ink);
}
.brand-mark {
    width: 50px; height: 50px;
    border-radius: 13px;
    background: var(--ink);
    display: flex; align-items: center; justify-content: center;
    font-size: 19px;
}
.topbar-note {
    font-family: 'JetBrains Mono', monospace;
    font-size: 12px;
    color: var(--ink-soft);
}

/* ---------- hero ---------- */
.hero {
    __HERO_BG__
    background-size: cover;
    background-position: center;
    border-radius: 18px;
    padding: 56px clamp(24px, 5vw, 60px);
    margin-bottom: 36px;
    box-shadow: 0 18px 40px -22px rgba(15,32,56,0.55);
}
.hero h1 {
    font-weight: 800;
    font-size: clamp(30px, 4.2vw, 50px);
    line-height: 1.12;
    letter-spacing: -1px;
    color: #FFFFFF;
    max-width: 700px;
    margin: 0 0 16px 0;
}
.hero p {
    color: #C9D6EA;
    font-size: 16px;
    line-height: 1.75;
    max-width: 580px;
    margin: 0 0 24px 0;
}
.chips { display: flex; flex-wrap: wrap; gap: 10px; }
.chip {
    font-family: 'JetBrains Mono', monospace;
    font-size: 12px;
    color: #E8EEF9;
    border: 1px solid rgba(255,255,255,0.28);
    border-radius: 999px;
    padding: 6px 14px;
    background: rgba(255,255,255,0.06);
}

/* ---------- headings ---------- */
.section-title {
    font-weight: 800;
    font-size: 26px;
    letter-spacing: -0.5px;
    color: var(--ink);
    margin-bottom: 4px;
}
.section-subtitle {
    color: var(--ink-soft);
    font-size: 15px;
    margin-bottom: 22px;
}
.panel-heading {
    font-weight: 700;
    font-size: 21px;
    color: var(--ink);
    margin-bottom: 3px;
}
.panel-caption {
    color: var(--ink-soft);
    font-size: 16px;
    margin-bottom: 14px;
}

/* ---------- input ---------- */
.stTextArea textarea {
    background: var(--paper) !important;
    color: var(--ink) !important;
    border: 1.5px solid var(--line) !important;
    border-radius: 12px !important;
    font-family: 'JetBrains Mono', monospace !important;
    font-size: 14px !important;
    line-height: 1.7 !important;
    padding: 16px !important;
}
.stTextArea textarea:focus {
    border-color: var(--blue) !important;
    box-shadow: 0 0 0 3px rgba(45,91,255,0.15) !important;
}

/* ---------- metrics ---------- */
.metric-card {
    height: 52px;
    box-sizing: border-box;
    align-items: center !important;
    background: var(--paper);
    border: 1px solid var(--line);
    border-radius: 10px;
    padding: 0 16px;
    display: flex;
    justify-content: space-between;
}
.metric-label { color: var(--ink-soft); font-size: 13px; font-weight: 600; }
.metric-value {
    font-family: 'JetBrains Mono', monospace;
    font-size: 16px;
    font-weight: 700;
    color: var(--ink);
}

/* ---------- button ---------- */
.stButton > button {
    background: var(--blue);
    color: #FFFFFF;
    border: none;
    border-radius: 10px;
    min-height: 50px;
    font-family: 'Manrope', sans-serif;
    font-size: 15px;
    font-weight: 700;
    transition: background 0.15s ease, box-shadow 0.15s ease;
}
.stButton > button:hover {
    background: var(--blue-dark);
    color: #FFFFFF;
    border: none;
    box-shadow: 0 8px 18px -8px rgba(45,91,255,0.7);
}
.stButton > button:focus-visible {
    outline: 3px solid rgba(45,91,255,0.4);
    outline-offset: 2px;
}

/* ---------- result: register grid ---------- */
.result-card {
    background: var(--ink);
    border-radius: 14px;
    padding: 20px;
    box-shadow: 0 16px 34px -22px rgba(15,32,56,0.8);
}
.result-head {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 14px;
    color: #8FA3C2;
    font-size: 13px;
    font-weight: 600;
}
.result-head b { color: #FFFFFF; font-weight: 700; }
.reg-grid {
    display: grid;
    grid-template-columns: repeat(2, 1fr);
    gap: 8px;
}
.reg {
    background: #172C4A;
    border: 1px solid #243E66;
    border-radius: 8px;
    padding: 9px 12px;
}
.reg-name {
    font-family: 'JetBrains Mono', monospace;
    font-size: 11px;
    color: #7F96B8;
    margin-bottom: 3px;
}
.reg-val {
    font-family: 'JetBrains Mono', monospace;
    font-size: 17px;
    font-weight: 700;
    color: var(--signal);
    letter-spacing: 1.2px;
}

.empty-result {
    background: var(--paper);
    border: 1.5px dashed #B9C7D8;
    border-radius: 14px;
    height: 190px;
    box-sizing: border-box;
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    text-align: center;
    color: var(--ink-soft);
    font-size: 14.5px;
    line-height: 1.7;
    padding: 24px;
}
.empty-result b { color: var(--ink); }

.verification {
    border-radius: 10px;
    padding: 0 18px;
    margin: 0;
    min-height: 50px;
    display: flex;
    align-items: center;
    font-size: 14px;
    line-height: 1.5;
}
.verification.success { background: var(--ok-bg); color: var(--ok); border: 1px solid #BFE5D5; }
.verification.failure { background: var(--bad-bg); color: var(--bad); border: 1px solid #F0C9C7; }

/* copy box from st.code */
div[data-testid="stCode"] { margin-top: 12px; }
div[data-testid="stCode"] pre { border-radius: 10px !important; font-size: 12.5px !important; }

/* ---------- how it works ---------- */
.about-heading {
    font-weight: 800;
    font-size: 26px;
    letter-spacing: -0.5px;
    color: var(--ink);
    margin: 18px 0 6px 0;
}
.about-intro {
    color: var(--ink-soft);
    font-size: 15px;
    line-height: 1.7;
    max-width: 640px;
    margin-bottom: 22px;
}
.about-card {
    background: var(--paper);
    border: 1px solid var(--line);
    border-top: 3px solid var(--blue);
    border-radius: 10px;
    padding: 20px 22px 22px;
    box-sizing: border-box;
    height: 235px;
}
.about-step {
    font-family: 'JetBrains Mono', monospace;
    font-size: 12px;
    font-weight: 700;
    color: var(--blue);
    margin-bottom: 10px;
}
.about-card h3 {
    font-weight: 700;
    font-size: 18px;
    color: var(--ink);
    margin: 0 0 8px 0;
}
.about-card p {
    color: var(--ink-soft);
    font-size: 14.5px;
    line-height: 1.7;
    margin: 0;
}

.hash-box {
    height: 190px;
    box-sizing: border-box;
    background: var(--paper);
    border: 1.5px solid var(--line);
    border-radius: 12px;
    padding: 16px;
    font-family: 'JetBrains Mono', monospace;
    font-size: 14px;
    line-height: 1.7;
    color: var(--ink);
    word-break: break-all;
    overflow: auto;
    user-select: all;
}
.hash-label {
    display: flex;
    justify-content: space-between;
    align-items: baseline;
    font-size: 13.5px;
    color: var(--ink-soft);
    margin-bottom: 2px;
}
.hash-label b { color: var(--ink); font-size: 15px; }
div[data-testid="stCode"] { margin-top: 0 !important; }
div[data-testid="stCode"] pre {
    box-sizing: border-box !important;
    height: 190px !important;
    min-height: 190px !important;
    background: var(--paper) !important;
    border: 1.5px solid var(--line) !important;
    border-radius: 12px !important;
    padding: 16px !important;
    font-family: 'JetBrains Mono', monospace !important;
    font-size: 14px !important;
    line-height: 1.7 !important;
    color: var(--ink) !important;
    overflow: auto !important;
}
div[data-testid="stCode"] code { font-size: 14px !important; line-height: 1.7 !important; }
.kv-card {
    background: var(--paper);
    border: 1.5px solid #7F96B8;
    border-radius: 12px;
    box-sizing: border-box;
    height: 350px;
    padding: 0 22px;
    display: flex;
    flex-direction: column;
    overflow: hidden;
}
.kv-title {
    font-weight: 700;
    font-size: 17px;
    color: var(--ink);
    padding: 15px 0 13px;
    border-bottom: 2px solid var(--blue);
}
.kv-row {
    flex: 1;
    display: flex;
    justify-content: space-between;
    align-items: center;
    gap: 16px;
    border-bottom: 1px solid #A9BAD3;
    font-size: 14.5px;
}
.kv-row:last-child { border-bottom: none; }
.kv-key { color: var(--ink-soft); }
.kv-val { color: var(--ink); font-weight: 700; text-align: right; }

.footer {
    border-top: 2px solid #4F6890;
    margin-top: 80px;
    padding-top: 18px;
    text-align: center;
    color: var(--ink);
    font-size: 14px;
    font-weight: 500;
    line-height: 1.8;
}

hr, div[data-testid="stMarkdownContainer"] hr {
    border: none !important;
    border-top: 2px solid #4F6890 !important;
    border-bottom: none !important;
    background: none !important;
    opacity: 1 !important;
    height: 0 !important;
    margin: 64px 0 28px 0 !important;
}

@media (max-width: 640px) {
    .topbar-note { display: none; }
    .reg-val { font-size: 15px; }
}
</style>
""".replace("__HERO_BG__", hero_background).replace("__PATTERN__", pattern_uri)

st.markdown(CSS, unsafe_allow_html=True)


# ==================================================
# TOP BAR + HERO
# ==================================================

st.markdown("""
<div class="topbar">
<div class="brand"><div class="brand-mark"><svg width="26" height="26" viewBox="0 0 24 24" fill="none" stroke="#FFFFFF" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><rect x="3" y="11" width="18" height="11" rx="2"/><path d="M7 11V7a5 5 0 0 1 10 0v4"/></svg></div>HashLab</div>
<div class="topbar-note">sha256.v · simulated with Icarus Verilog</div>
</div>

<div class="hero">
<h1>SHA-256 Hash Generator</h1>
<p>Generate a secure 256-bit hash of any message using a SHA-256 design written in Verilog. Every result is checked against Python to confirm it is correct.</p>
<div class="chips">
<span class="chip">256-bit hash</span>
<span class="chip">512-bit blocks</span>
<span class="chip">Up to 1024 bytes</span>
</div>
</div>
""", unsafe_allow_html=True)


# ==================================================
# WORKSPACE
# ==================================================

st.markdown("""
<div class="section-title">Generate a hash</div>
<div class="section-subtitle">Enter a message, then run it through the Verilog design.</div>
""", unsafe_allow_html=True)

COLS = [1.05, 0.95]

# Row 1: message box | generated hash box (identical size)
row1_left, row1_right = st.columns(COLS, gap="large")

with row1_left:
    st.markdown(
        '<div class="panel-heading">Message</div>'
        '<div class="panel-caption">Type or paste the text to hash.</div>',
        unsafe_allow_html=True
    )
    message = st.text_area(
        "Input Message",
        height=190,
        placeholder="Type or paste your message here...",
        label_visibility="collapsed"
    )

message_bytes = message.encode("utf-8")

with row1_right:
    st.markdown(
        '<div class="panel-heading">Generated hash</div>'
        '<div class="panel-caption">Your 256-bit SHA-256 hash. Click it to select all.</div>',
        unsafe_allow_html=True
    )
    hash_slot = st.empty()

# Row 2: counters
row2_left, row2_right = st.columns(COLS, gap="large")

with row2_left:
    metric_col1, metric_col2 = st.columns(2)

    with metric_col1:
        st.markdown(f"""
<div class="metric-card">
<div class="metric-label">Characters</div>
<div class="metric-value">{len(message)}</div>
</div>
""", unsafe_allow_html=True)

    with metric_col2:
        st.markdown(f"""
<div class="metric-card">
<div class="metric-label">UTF-8 size</div>
<div class="metric-value">{len(message_bytes)} / 1024 B</div>
</div>
""", unsafe_allow_html=True)

# Small gap between counters and button
st.markdown('<div style="height:12px"></div>', unsafe_allow_html=True)

# Row 3: generate button | verification
row3_left, row3_right = st.columns(COLS, gap="large")

with row3_left:
    generate_clicked = st.button(
        "Generate SHA-256 hash",
        use_container_width=True
    )

with row3_right:
    verify_slot = st.empty()


# ==================================================
# GENERATE HASH (logic unchanged)
# ==================================================

if generate_clicked:

    if len(message_bytes) > 1024:

        st.session_state["hash_result"] = None
        st.session_state["hash_error"] = (
            "Message too long. Maximum supported input is 1024 UTF-8 bytes."
        )
        st.session_state["hash_message"] = message

    else:

        try:

            with hash_slot.container():
                with st.spinner("Running your message through the Verilog design..."):

                    generated_hash = generate_sha256_hash(message)

                    expected_hash = hashlib.sha256(
                        message_bytes
                    ).hexdigest()

            st.session_state["hash_result"] = generated_hash
            st.session_state["expected_hash"] = expected_hash
            st.session_state["hash_error"] = None
            st.session_state["hash_message"] = message

        except Exception as error:

            st.session_state["hash_result"] = None
            st.session_state["hash_error"] = str(error)
            st.session_state["hash_message"] = message


# ==================================================
# SHOW RESULT
# ==================================================

current_result = st.session_state.get("hash_result")
current_error = st.session_state.get("hash_error")
result_message = st.session_state.get("hash_message")

valid_result = (
    result_message == message
    and current_result is not None
)

valid_error = (
    result_message == message
    and current_error is not None
)

if valid_result:

    digest = str(current_result).strip()

    hash_slot.markdown(
        f'<div class="hash-box">{digest}</div>',
        unsafe_allow_html=True
    )

    if digest.lower() == st.session_state["expected_hash"].lower():

        verify_slot.markdown("""
<div class="verification success">
<span><b>✓ Verified.</b> The Verilog output matches Python's SHA-256 result.</span>
</div>
""", unsafe_allow_html=True)

    else:

        verify_slot.markdown("""
<div class="verification failure">
<span><b>✕ Mismatch.</b> The Verilog output differs from Python's SHA-256 result.</span>
</div>
""", unsafe_allow_html=True)

elif valid_error:

    hash_slot.error(current_error)

else:

    hash_slot.markdown("""
<div class="empty-result">
<div style="margin-bottom:10px;"><svg width="34" height="34" viewBox="0 0 24 24" fill="none" stroke="#25354C" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><rect x="3" y="11" width="18" height="11" rx="2"/><path d="M7 11V7a5 5 0 0 1 10 0v4"/></svg></div>
<div><b>No hash yet.</b></div>
<div>Enter a message and select Generate SHA-256 hash.</div>
</div>
""", unsafe_allow_html=True)


# ==================================================
# ABOUT THIS PROJECT
# ==================================================

st.markdown("---")

st.markdown("""
<div class="about-heading">About this project</div>
<div class="about-intro">
HashLab is a SHA-256 hash generator whose hashing is done by a design written in Verilog,
a hardware description language, instead of ordinary software code. The Verilog design is
run in the Icarus Verilog simulator, and this Streamlit page sends your message to it and shows the result.
Every hash is also checked against Python's built-in SHA-256, so you can see that the hardware design is correct.
</div>
<div class="panel-heading" style="margin-bottom:12px;padding-top:28px;">What happens when you press Generate</div>
""", unsafe_allow_html=True)

step1, step2, step3, step4 = st.columns(4, gap="small")

with step1:
    st.markdown("""
<div class="about-card">
<div class="about-step">STEP 1</div>
<h3>You enter a message</h3>
<p>The text is converted to UTF-8 bytes. Up to 1024 bytes are supported.</p>
</div>
""", unsafe_allow_html=True)

with step2:
    st.markdown("""
<div class="about-card">
<div class="about-step">STEP 2</div>
<h3>Verilog processes it</h3>
<p>The message is padded, split into 512-bit blocks and passed through 64 rounds per block in the simulated hardware.</p>
</div>
""", unsafe_allow_html=True)

with step3:
    st.markdown("""
<div class="about-card">
<div class="about-step">STEP 3</div>
<h3>The hash comes back</h3>
<p>The design outputs a 256-bit result, shown here as 64 hexadecimal characters.</p>
</div>
""", unsafe_allow_html=True)

with step4:
    st.markdown("""
<div class="about-card">
<div class="about-step">STEP 4</div>
<h3>Python double-checks</h3>
<p>Python's hashlib computes the same hash. If both match, you see a green Verified message.</p>
</div>
""", unsafe_allow_html=True)

st.write("")

details_col, notes_col = st.columns([1, 1], gap="large")

with details_col:
    st.markdown("""
<div class="kv-card"><div class="kv-title">Project details</div>
<div class="kv-row"><span class="kv-key">Algorithm</span><span class="kv-val">SHA-256</span></div>
<div class="kv-row"><span class="kv-key">Hardware design</span><span class="kv-val">Verilog HDL</span></div>
<div class="kv-row"><span class="kv-key">Simulator</span><span class="kv-val">Icarus Verilog</span></div>
<div class="kv-row"><span class="kv-key">Interface</span><span class="kv-val">Python + Streamlit</span></div>
<div class="kv-row"><span class="kv-key">Maximum input</span><span class="kv-val">1024 UTF-8 bytes</span></div>
<div class="kv-row"><span class="kv-key">Output</span><span class="kv-val">256 bits (64 hex characters)</span></div>
</div>
""", unsafe_allow_html=True)

with notes_col:
    st.markdown("""
<div class="kv-card"><div class="kv-title">Good to know</div>
<div class="kv-row"><span class="kv-key">Same message</span><span class="kv-val">Always gives the same hash</span></div>
<div class="kv-row"><span class="kv-key">Tiny change</span><span class="kv-val">Gives a completely different hash</span></div>
<div class="kv-row"><span class="kv-key">Reverse it</span><span class="kv-val">Not possible, SHA-256 is one-way</span></div>
<div class="kv-row"><span class="kv-key">Message too long</span><span class="kv-val">Shows an error, nothing is hashed</span></div>
</div>
""", unsafe_allow_html=True)


# ==================================================
# FOOTER
# ==================================================

st.markdown("""
<div class="footer">
SHA-256 hashing algorithm using Verilog<br>
Verilog HDL, Icarus Verilog, Python, Streamlit
</div>
""", unsafe_allow_html=True)