import hashlib
import hmac
import os
import time
import requests
import streamlit as st
from dotenv import load_dotenv
from streamlit_cookies_controller import CookieController

from app.database.database import (
    initialize_database,
    create_conversation,
    get_user_conversations,
    get_conversation_messages,
    save_message,
    get_documents,
    delete_conversation,
    get_user_by_id,
)

from app.services.auth import (
    register_user,
    login_user,
)


# ============================================================
# PAGE CONFIG
# ============================================================

st.set_page_config(
    page_title="Knowledge AI",
    page_icon="🧠",
    layout="wide",
    initial_sidebar_state="expanded",
)


# ============================================================
# CONFIG
# ============================================================

API_URL = "http://127.0.0.1:8000"

# ============================================================
# AUTHENTICATION COOKIE
# ============================================================

cookie_controller = CookieController()
AUTH_COOKIE_NAME = "knowledge_ai_session"

# ============================================================
# AUTHENTICATION SESSION HELPERS
# ============================================================

load_dotenv()
SESSION_SECRET = os.getenv("SESSION_SECRET")


def create_session_token(user_id):
    """
    Create a signed authentication session token.
    """

    if not SESSION_SECRET:
        raise RuntimeError(
            "SESSION_SECRET is not configured."
        )

    user_id = str(user_id)

    signature = hmac.new(
        SESSION_SECRET.encode("utf-8"),
        user_id.encode("utf-8"),
        hashlib.sha256,
    ).hexdigest()

    return f"{user_id}:{signature}"


def verify_session_token(token):
    """
    Verify the authentication session token.

    Returns the user ID when valid.
    Returns None when invalid or tampered with.
    """

    if not SESSION_SECRET:
        return None

    if not token:
        return None

    try:

        user_id, signature = token.split(
            ":",
            1,
        )

        expected_signature = hmac.new(
            SESSION_SECRET.encode("utf-8"),
            user_id.encode("utf-8"),
            hashlib.sha256,
        ).hexdigest()

        if hmac.compare_digest(
            signature,
            expected_signature,
        ):

            return int(user_id)

    except (
        ValueError,
        TypeError,
    ):

        return None

    return None

# ============================================================
# DATABASE
# ============================================================

initialize_database()

if "show_knowledge_base" not in st.session_state:
    st.session_state.show_knowledge_base = False


# ============================================================
# SESSION STATE
# ============================================================

if "authenticated" not in st.session_state:
    st.session_state.authenticated = False

if "user" not in st.session_state:
    st.session_state.user = None

if "auth_mode" not in st.session_state:
    st.session_state.auth_mode = "login"

if "conversation_id" not in st.session_state:
    st.session_state.conversation_id = None

if "messages" not in st.session_state:
    st.session_state.messages = []


# ============================================================
# CUSTOM CSS
# ============================================================

st.markdown(
    """
<style>

/* ============================================================
   PAGE
   ============================================================ */

.stApp {
    background:
        radial-gradient(
            circle at 8% 10%,
            rgba(58, 54, 190, 0.30),
            transparent 35%
        ),
        radial-gradient(
            circle at 92% 10%,
            rgba(0, 153, 190, 0.15),
            transparent 34%
        ),
        linear-gradient(
            135deg,
            #070918 0%,
            #07101c 55%,
            #06131d 100%
        );

    color:
        #f8fafc;
}


/* ============================================================
   MAIN CONTENT POSITION
   ============================================================ */

.main .block-container {
    max-width:
        1180px;

    padding-top:
        4px;

    padding-bottom:
        30px;

    padding-left:
        20px;

    padding-right:
        20px;
}


/* ============================================================
   HIDE STREAMLIT DEFAULT UI
   ============================================================ */

#MainMenu {
    visibility:
        hidden;
}

footer {
    visibility:
        hidden;
}


/* ============================================================
   AUTH OUTER BOX
   ============================================================ */

.st-key-auth_box {

    max-width:
        1080px;

    margin-left:
        auto;

    margin-right:
        auto;

    border:
        1px solid
        rgba(78, 111, 255, 0.78);

    border-radius:
        22px;

    overflow:
        hidden;

    background:
        rgba(3, 8, 18, 0.82);

    box-shadow:
        0 28px 65px
        rgba(0, 0, 0, 0.52),

        0 20px 55px
        rgba(48, 58, 190, 0.18);
}


/* ============================================================
   AUTH COLUMNS
   ============================================================ */

.st-key-auth_left {

    width:
        100%;

    height:
        100%;

    padding:
        48px 54px;

    box-sizing:
        border-box;

    background:
        linear-gradient(
            145deg,
            #1b2d6b 0%,
            #14264e 48%,
            #0b1a30 100%
        );

    border-right:
        1px solid
        rgba(105, 134, 255, 0.70);
}


.st-key-auth_right {

    width:
        100%;

    height:
        100%;

    padding:
        48px 54px;

    box-sizing:
        border-box;

    background:
        linear-gradient(
            145deg,
            #060d19 0%,
            #040914 58%,
            #020710 100%
        );
}


/* ============================================================
   FULL AUTH PANEL
   ============================================================ */

.st-key-auth_box div[data-testid="stHorizontalBlock"] {

    gap:
        0 !important;

    align-items:
        stretch !important;

    min-height:
        650px !important;
}


/* LEFT COLUMN */

.st-key-auth_box div[data-testid="stHorizontalBlock"]
div[data-testid="column"]:first-child {

    background:
        linear-gradient(
            145deg,
            #1d3475 0%,
            #162c5c 50%,
            #102342 100%
        ) !important;

    min-height:
        650px !important;

    height:
        650px !important;

    padding:
        0 !important;

    margin:
        0 !important;

    border-right:
        1px solid
        rgba(105, 134, 255, 0.70) !important;

    box-sizing:
        border-box !important;
}


/* RIGHT COLUMN */

.st-key-auth_box div[data-testid="stHorizontalBlock"]
div[data-testid="column"]:last-child {

    background:
        linear-gradient(
            145deg,
            #060d19 0%,
            #040914 58%,
            #020710 100%
        ) !important;

    min-height:
        650px !important;

    height:
        650px !important;

    padding:
        0 !important;

    margin:
        0 !important;

    box-sizing:
        border-box !important;
}


/* LEFT CONTENT */

.st-key-auth_left {

    background:
        linear-gradient(
            145deg,
            #162c5c 100%,
            #102342 100%
        ) !important;

    min-height:
        650px !important;

    height:
        100% !important;

    padding:
        48px 54px !important;

    margin:
        0 !important;

    box-sizing:
        border-box !important;
}


/* RIGHT CONTENT */

.st-key-auth_right {

    background:
        transparent !important;

    min-height:
        650px !important;

    height:
        100% !important;

    padding:
        48px 54px !important;

    margin:
        0 !important;

    box-sizing:
        border-box !important;
}


/* ============================================================
   LEFT AUTH CONTENT
   ============================================================ */

.brand-logo {

    width:
        66px;

    height:
        66px;

    display:
        flex;

    align-items:
        center;

    justify-content:
        center;

    border-radius:
        18px;

    background:
        linear-gradient(
            135deg,
            #604df2,
            #08bce9
        );

    box-shadow:
        0 12px 32px
        rgba(50, 80, 220, 0.35);

    font-size:
        50px;

    margin-bottom:
        22px;
}


.brand-title {

    font-size:
        40px;

    font-weight:
        850;

    line-height:
        1.05;

    letter-spacing:
        -1.7px;

    color:
        #f8fafc;
}


.brand-gradient {

    background:
        linear-gradient(
            90deg,
            #9da9ff,
            #39d8ff
        );

    -webkit-background-clip:
        text;

    -webkit-text-fill-color:
        transparent;
}


.brand-description {

    max-width:
        455px;

    margin-top:
        18px;

    color:
        #bdc9df;

    font-size:
        15px;

    line-height:
        1.75;
}


.feature-heading {

    margin-top:
        31px;

    margin-bottom:
        18px;

    color:
        #91a0c0;

    font-size:
        13px;

    font-weight:
        800;

    letter-spacing:
        1.5px;
}


.feature-row {

    display:
        flex;

    align-items:
        center;

    margin-bottom:
        12px;

    color:
        #edf2fa;

    font-size:
        13px;

    font-weight:
        600;
}


.feature-icon {

    width:
        40px;

    height:
        40px;

    margin-right:
        13px;

    display:
        flex;

    align-items:
        center;

    justify-content:
        center;

    border-radius:
        10px;

    background:
        rgba(80, 107, 211, 0.20);

    border:
        1px solid
        rgba(139, 157, 234, 0.20);

    font-size:
        15px;
}


/* ============================================================
   RIGHT AUTH CONTENT
   ============================================================ */

.auth-kicker {

    color:
        #8290ff;

    font-size:
        11px;

    font-weight:
        850;

    letter-spacing:
        1.5px;

    margin-bottom:
        8px;
}


.auth-title {

    color:
        #f8fafc;

    font-size:
        30px;

    font-weight:
        850;

    line-height:
        1.1;

    letter-spacing:
        -1.2px;
}


.auth-subtitle {

    color:
        #8290a8;

    font-size:
        12px;

    line-height:
        1.6;

    margin-top:
        7px;

    margin-bottom:
        20px;
}


/* ============================================================
   INPUTS
   ============================================================ */

div[data-testid="stTextInput"] label {

    color:
        #dce4f1 !important;

    font-size:
        11px !important;

    font-weight:
        650 !important;
}


div[data-testid="stTextInput"] input {

    height:
        44px !important;

    border-radius:
        9px !important;

    background:
        #111c31 !important;

    border:
        1px solid
        rgba(105, 125, 160, 0.32) !important;

    color:
        #f8fafc !important;

    font-size:
        12px !important;
}


div[data-testid="stTextInput"] input:focus {

    border-color:
        #6675ff !important;

    box-shadow:
        0 0 0 2px
        rgba(102, 117, 255, 0.12) !important;
}


/* ============================================================
   SIGN IN BUTTON
   ============================================================ */

.stFormSubmitButton > button {

    height:
        44px !important;

    margin-top:
        5px !important;

    border:
        none !important;

    border-radius:
        9px !important;

    background:
        linear-gradient(
            90deg,
            #513ee8,
            #286eea,
            #08afe6
        ) !important;

    color:
        #ffffff !important;

    font-size:
        12px !important;

    font-weight:
        750 !important;
}


/* ============================================================
   GOOGLE + CREATE ACCOUNT
   ============================================================ */

.st-key-google_login button,
.st-key-create_account button,
.st-key-back_to_login button {

    height:
        44px !important;

    border-radius:
        9px !important;

    background:
        rgba(9, 19, 34, 0.78) !important;

    border:
        1px solid
        rgba(111, 130, 164, 0.42) !important;

    color:
        #edf2fa !important;

    font-size:
        12px !important;

    font-weight:
        650 !important;
}


.st-key-google_login button:hover,
.st-key-create_account button:hover {

    border-color:
        rgba(129, 145, 255, 0.72) !important;
}


/* ============================================================
   OR DIVIDER
   ============================================================ */

.or-divider {

    display:
        flex;

    align-items:
        center;

    gap:
        12px;

    margin:
        15px 0 12px 0;

    color:
        #697891;

    font-size:
        9px;
}


.or-line {

    flex:
        1;

    height:
        1px;

    background:
        rgba(105, 124, 153, 0.25);
}


/* ============================================================
   CREATE ACCOUNT LABEL
   ============================================================ */

.create-label {

    text-align:
        center;

    color:
        #6d7b96;

    font-size:
        9px;

    margin-top:
        17px;

    margin-bottom:
        7px;
}


/* ============================================================
   SIDEBAR BASE
   ============================================================ */

section[data-testid="stSidebar"] {

    background:
        linear-gradient(
            180deg,
            #060b15 0%,
            #070d18 55%,
            #060a13 100%
        ) !important;

    border-right:
        1px solid
        rgba(148, 163, 184, 0.10) !important;
}


/* ============================================================
   SIDEBAR CONTENT
   ============================================================ */

section[data-testid="stSidebar"]
div[data-testid="stSidebarContent"] {

    padding:
        8px 18px 14px 18px !important;
}


/* ============================================================
   SIDEBAR BRAND
   ============================================================ */

section[data-testid="stSidebar"]
div[data-testid="stMarkdownContainer"] p {

    margin-top:
        0 !important;

    margin-bottom:
        3px !important;

    line-height:
        1.4 !important;
}


/* ============================================================
   SIDEBAR BRAND SUBTITLE
   ============================================================ */

section[data-testid="stSidebar"]
div[data-testid="stCaptionContainer"] p {

    color:
        #56657d !important;

    font-size:
        10px !important;

    line-height:
        1.3 !important;

    margin-top:
        2px !important;

    margin-bottom:
        4px !important;
}


/* ============================================================
   SIDEBAR BUTTONS
   ============================================================ */

section[data-testid="stSidebar"] button {

    min-height:
        36px !important;

    height:
        36px !important;

    border-radius:
        8px !important;

    border:
        1px solid
        rgba(111, 130, 164, 0.28) !important;

    background:
        rgba(15, 24, 41, 0.72) !important;

    color:
        #dbe5f5 !important;

    font-size:
        13px !important;

    font-weight:
        600 !important;

    padding:
        5px 11px !important;

    margin-bottom:
        4px !important;

    transition:
        all 0.18s ease !important;
}


/* Sidebar button text */

section[data-testid="stSidebar"] button p {

    font-size:
        13px !important;

    font-weight:
        600 !important;

    white-space:
        nowrap !important;

    overflow:
        hidden !important;

    text-overflow:
        ellipsis !important;
}


/* Sidebar button hover */

section[data-testid="stSidebar"] button:hover {

    border-color:
        rgba(105, 134, 255, 0.55) !important;

    background:
        rgba(38, 51, 82, 0.82) !important;

    color:
        #ffffff !important;
}


/* ============================================================
   SIDEBAR SECTION TITLES
   ============================================================ */

.sidebar-section-title {

    margin-top:
        15px;

    margin-bottom:
        7px;

    color:
        #7183a5;

    font-size:
        11px;

    font-weight:
        800;

    letter-spacing:
        1.4px;
}


/* ============================================================
   KNOWLEDGE BASE CARD
   ============================================================ */

.sidebar-info-card {

    padding:
        10px 11px;

    margin-bottom:
        5px;

    border:
        1px solid
        rgba(105, 134, 255, 0.18);

    border-radius:
        8px;

    background:
        rgba(17, 28, 49, 0.62);
}


.sidebar-info-title {

    color:
        #dce6f6;

    font-size:
        13px;

    font-weight:
        700;

    margin-bottom:
        3px;
}


.sidebar-info-text {

    color:
        #7f90ad;

    font-size:
        10px;

    line-height:
        1.35;
}


.sidebar-info-status {

    color:
        #6ee7b7;

    font-size:
        10px;

    font-weight:
        700;

    margin-top:
        5px;
}


/* ============================================================
   SIDEBAR SPACING
   ============================================================ */

.sidebar-spacer {

    min-height:
        12px !important;
}


/* ============================================================
   SIDEBAR DIVIDER
   ============================================================ */

section[data-testid="stSidebar"] hr {

    border:
        none !important;

    border-top:
        1px solid
        rgba(148, 163, 184, 0.10) !important;

    margin:
        8px 0 !important;
}


/* ============================================================
   USER NAME
   ============================================================ */

section[data-testid="stSidebar"]
div[data-testid="stMarkdownContainer"] strong {

    color:
        #edf3fb !important;

    font-size:
        14px !important;
}


/* ============================================================
   SIGNED IN
   ============================================================ */

section[data-testid="stSidebar"]
div[data-testid="stCaptionContainer"] p {

    color:
        #56657d !important;

    font-size:
        10px !important;

    line-height:
        1.3 !important;
}


/* ============================================================
   SIGN OUT
   ============================================================ */

.st-key-sign_out_button {

    margin-top:
        0 !important;
}


.st-key-sign_out_button button {

    height:
        34px !important;

    min-height:
        34px !important;

    margin-top:
        0 !important;

    background:
        rgba(12, 19, 32, 0.85) !important;

    border-color:
        rgba(148, 163, 184, 0.20) !important;

    color:
        #94a3b8 !important;
}


.st-key-sign_out_button button p {

    font-size:
        12px !important;
}


.st-key-sign_out_button button:hover {

    color:
        #f1f5f9 !important;

    border-color:
        rgba(148, 163, 184, 0.38) !important;

    background:
        rgba(25, 35, 52, 0.92) !important;
}


/* ============================================================
   WORKSPACE
   ============================================================ */

.workspace-header {

    color:
        #e2e8f0;

    font-size:
        15px;

    font-weight:
        750;

    padding-bottom:
        13px;

    border-bottom:
        1px solid
        rgba(148, 163, 184, 0.08);
}


.workspace-subtitle {

    color:
        #64748b;

    font-size:
        10px;

    margin-top:
        4px;
}


.chat-hero {

    padding-top:
        42px;

    padding-bottom:
        22px;
}


.chat-title {

    color:
        #f8fafc;

    font-size:
        44px;

    font-weight:
        850;

    line-height:
        1.08;

    letter-spacing:
        -2px;
}


.chat-gradient {

    background:
        linear-gradient(
            90deg,
            #a5b4fc,
            #67e8f9
        );

    -webkit-background-clip:
        text;

    -webkit-text-fill-color:
        transparent;
}


.chat-description {

    color:
        #94a3b8;

    font-size:
        13px;

    line-height:
        1.7;

    max-width:
        760px;

    margin-top:
        12px;
}


/* ============================================================
   MOBILE
   ============================================================ */

@media (max-width: 850px) {

    .st-key-auth_box {
        margin-top:
            10px;
    }

    .st-key-auth_left {

        min-height:
            auto;

        padding:
            35px 28px;

        border-right:
            none;

        border-bottom:
            1px solid
            rgba(105, 134, 255, 0.70);
    }

    .st-key-auth_right {

        min-height:
            auto;

        padding:
            35px 28px;
    }

    .brand-title {
        font-size:
            32px;
    }

    .auth-title {
        font-size:
            27px;
    }
}


.stAppDeployButton {
    display: none !important;
}


/* Keep Streamlit header for sidebar toggle */

header[data-testid="stHeader"] {
    background: transparent !important;
    border-bottom: none !important;
    box-shadow: none !important;
}


/* ============================================================
   KNOWLEDGE WORKSPACE - CHAT INPUT
   ============================================================ */

div[data-testid="stChatInput"] {
    background: transparent !important;
    border: none !important;
    box-shadow: none !important;
}


/* Make the entire chat-input area blend with workspace */

div[data-testid="stChatInputContainer"] {
    background: linear-gradient(
        135deg,
        #0b1530 0%,
        #071d29 100%
    ) !important;

    border: none !important;
    box-shadow: none !important;
}


/* Actual input box */

div[data-testid="stChatInput"] > div {
    background: rgba(17, 27, 55, 0.92) !important;

    border: 1px solid rgba(105, 134, 255, 0.28) !important;
    border-radius: 12px !important;

    box-shadow: 0 8px 25px rgba(0, 0, 0, 0.18) !important;
}


div[data-testid="stChatInput"] textarea {
    background: transparent !important;
    color: #e5e7eb !important;
}


div[data-testid="stChatInput"] textarea::placeholder {
    color: #94a3b8 !important;
}


/* ============================================================
   CHAT INPUT BACKGROUND AREA
   ============================================================ */

div[data-testid="stBottom"] {
    background: transparent !important;
    border-top: none !important;
    box-shadow: none !important;
}


div[data-testid="stBottomBlockContainer"] {
    background: transparent !important;
    border: none !important;
    box-shadow: none !important;
}


div[data-testid="stBottom"] {
    background: #07101c !important;
}

/* ============================================================
   UPLOAD AREA - SLIGHTLY LARGER
   ============================================================ */

div[data-testid="stFileUploader"] {
    padding: 8px 12px 14px 12px !important;
    border-radius: 10px !important;
}

div[data-testid="stFileUploader"] section {
    min-height: 72px !important;
}

div[data-testid="stFileUploader"] button {
    min-height: 38px !important;
    padding: 0 14px !important;
}

</style>
""",
    unsafe_allow_html=True,
)


# ============================================================
# AUTH PAGE
# ============================================================

# ============================================================
# RESTORE AUTHENTICATION FROM COOKIE
# ============================================================

if not st.session_state.authenticated:

    # Initialize the cookie controller and allow
    # the browser component to provide existing cookies.
    cookie_controller.getAll()

    time.sleep(0.3)

    session_token = cookie_controller.get(
        AUTH_COOKIE_NAME
    )

    user_id = verify_session_token(
        session_token
    )

    if user_id is not None:

        restored_user = get_user_by_id(
            user_id
        )

        if restored_user is not None:

            st.session_state.authenticated = True

            st.session_state.user = (
                restored_user
            )

            st.session_state.conversation_id = (
                None
            )

            st.session_state.messages = []

            st.rerun()

    # ========================================================
    # SINGLE OUTER BOX
    # ========================================================

    with st.container(
        key="auth_box",
        border=False,
    ):

        left_col, right_col = st.columns(
            [1, 1],
            gap="small",
        )

        # ====================================================
        # LEFT SIDE
        # ====================================================

        with left_col:

            with st.container(
                key="auth_left",
                border=False,
            ):

                st.markdown(
                    """
<div class="brand-logo">🧠</div>

<div class="brand-title">
Knowledge <span class="brand-gradient">AI.</span>
</div>

<div class="brand-description">
A professional enterprise knowledge assistant that turns
your private documents into an intelligent, searchable
knowledge workspace.
</div>

<div class="feature-heading">
BUILT FOR INTELLIGENT KNOWLEDGE
</div>

<div class="feature-row">
<span class="feature-icon">🔎</span>
Intelligent Retrieval
</div>

<div class="feature-row">
<span class="feature-icon">🎯</span>
Neural Reranking
</div>

<div class="feature-row">
<span class="feature-icon">⚙️</span>
Agentic Reasoning
</div>

<div class="feature-row">
<span class="feature-icon">📚</span>
Source Grounding
</div>
""",
                    unsafe_allow_html=True,
                )

        # ====================================================
        # RIGHT SIDE
        # ====================================================

        with right_col:

            with st.container(
                key="auth_right",
                border=False,
            ):

                st.markdown(
                    """
<div class="auth-kicker">
SECURE AI WORKSPACE
</div>

<div class="auth-title">
Welcome back
</div>

<div class="auth-subtitle">
Sign in to continue to your knowledge workspace.
</div>
""",
                    unsafe_allow_html=True,
                )

                # ============================================
                # LOGIN
                # ============================================

                if st.session_state.auth_mode == "login":

                    with st.form(
                        "login_form"
                    ):

                        email = st.text_input(
                            "Email",
                            placeholder="you@example.com",
                        )

                        password = st.text_input(
                            "Password",
                            type="password",
                            placeholder="Enter your password",
                        )

                        sign_in = st.form_submit_button(
                            "Sign In",
                            use_container_width=True,
                        )

                        if sign_in:

                            result = login_user(
                                email,
                                password,
                            )

                            if result["success"]:

                                session_token = create_session_token(
                                    result["user"]["id"]
                                    )

                                cookie_controller.set(
                                    AUTH_COOKIE_NAME,
                                    session_token,
                                    )

                                time.sleep(0.5)

                                st.session_state.authenticated = True

                                st.session_state.user = (
                                    result["user"]
                                )

                                st.session_state.conversation_id = (
                                    None
                                )

                                st.session_state.messages = []

                                st.rerun()

                            else:

                                st.error(
                                    result["message"]
                                )

                    # ========================================
                    # OR
                    # ========================================

                    st.markdown(
                        """
<div class="or-divider">
<span class="or-line"></span>
<span>OR</span>
<span class="or-line"></span>
</div>
""",
                        unsafe_allow_html=True,
                    )

                

                    # ========================================
                    # CREATE ACCOUNT
                    # ========================================

                    st.markdown(
                        """
<div class="create-label">
Don't have an account?
</div>
""",
                        unsafe_allow_html=True,
                    )

                    if st.button(
                        "Create Account",
                        use_container_width=True,
                        key="create_account",
                    ):

                        st.session_state.auth_mode = "signup"

                        st.rerun()

                # ============================================
                # SIGN UP
                # ============================================

                else:

                    st.markdown(
                        """
<div class="auth-title">
Create account
</div>

<div class="auth-subtitle">
Create your secure AI knowledge workspace.
</div>
""",
                        unsafe_allow_html=True,
                    )

                    with st.form(
                        "signup_form"
                    ):

                        name = st.text_input(
                            "Full Name",
                            placeholder="Your name",
                        )

                        email = st.text_input(
                            "Email",
                            placeholder="you@example.com",
                        )

                        password = st.text_input(
                            "Password",
                            type="password",
                            placeholder="Minimum 8 characters",
                        )

                        confirm_password = st.text_input(
                            "Confirm Password",
                            type="password",
                            placeholder="Repeat your password",
                        )

                        create_account = st.form_submit_button(
                            "Create Account",
                            use_container_width=True,
                        )

                        if create_account:

                            if password != confirm_password:

                                st.error(
                                    "Passwords do not match."
                                )

                            else:

                                result = register_user(
                                    name,
                                    email,
                                    password,
                                )

                                if result["success"]:

                                    st.success(
                                        "Account created successfully."
                                    )

                                    st.session_state.auth_mode = (
                                        "login"
                                    )

                                    st.rerun()

                                else:

                                    st.error(
                                        result["message"]
                                    )

                    if st.button(
                        "←  Back to Sign In",
                        use_container_width=True,
                        key="back_to_login",
                    ):

                        st.session_state.auth_mode = "login"

                        st.rerun()

    st.stop()


# ============================================================
# LOGGED-IN WORKSPACE
# ============================================================

user = st.session_state.user


# ============================================================
# DOCUMENTS
# ============================================================

documents = get_documents()

document_count = len(documents)


# ============================================================
# SIDEBAR
# ============================================================

with st.sidebar:

    # --------------------------------------------------------
    # BRAND
    # --------------------------------------------------------

    st.markdown(
        "🧠  **Knowledge AI**"
    )

    st.caption(
        "PRIVATE AI WORKSPACE"
    )

    # --------------------------------------------------------
    # NEW CHAT
    # --------------------------------------------------------

    if st.button(
        "＋  New Chat",
        use_container_width=True,
        key="new_chat_button",
    ):

        st.session_state.conversation_id = None
        st.session_state.messages = []

        st.rerun()

    # --------------------------------------------------------
    # QUICK ACCESS
    # --------------------------------------------------------

    st.markdown(
        """
        <div class="sidebar-section-title">
            QUICK ACCESS
        </div>
        """,
        unsafe_allow_html=True,
    )

    # --------------------------------------------------------
    # KNOWLEDGE BASE CARD
    # --------------------------------------------------------

    with st.container(
        border=True,
    ):

        st.markdown(
            "📚 **Knowledge Base**"
        )

        st.caption(
            f"{document_count} document"
            f"{'s' if document_count != 1 else ''} indexed"
        )

        st.caption(
            "● Ready for questions"
        )

    # --------------------------------------------------------
    # DOCUMENT UPLOAD
    # --------------------------------------------------------

    uploaded_file = st.file_uploader(
        "Upload a PDF",
        type=["pdf"],
        key="knowledge_base_uploader",
        label_visibility="collapsed",
    )

    if uploaded_file is not None:

        if st.button(
            "Upload & Index",
            use_container_width=True,
            key="upload_document_button",
        ):

            with st.spinner(
                "Indexing document..."
            ):

                try:

                    response = requests.post(
                        f"{API_URL}/documents/upload",
                        files={
                            "file": (
                                uploaded_file.name,
                                uploaded_file.getvalue(),
                                "application/pdf",
                            )
                        },
                        timeout=300,
                    )

                    if response.status_code == 200:

                        data = response.json()

                        st.success(
                            "Document indexed successfully."
                        )

                        st.caption(
                            f"{data['filename']} • "
                            f"{data['pages']} pages • "
                            f"{data['chunks']} chunks"
                        )

                        st.rerun()

                    else:

                        try:

                            error_data = response.json()

                            error_message = error_data.get(
                                "detail",
                                "Document upload failed.",
                            )

                        except ValueError:

                            error_message = (
                                "Document upload failed."
                            )

                        st.error(
                            error_message
                        )

                except requests.exceptions.ConnectionError:

                    st.error(
                        "FastAPI is not running. "
                        "Please start the API server."
                    )

                except requests.exceptions.Timeout:

                    st.error(
                        "Document indexing timed out. "
                        "Please try again."
                    )

                except Exception as error:

                    st.error(
                        f"Unexpected error: {error}"
                    )

    # --------------------------------------------------------
    # CONVERSATIONS
    # --------------------------------------------------------

    st.markdown(
        """
        <div class="sidebar-section-title">
            CONVERSATIONS
        </div>
        """,
        unsafe_allow_html=True,
    )

    conversations = get_user_conversations(
        user["id"]
    )

    if conversations:

        for conversation in conversations:

            conversation_id = conversation["id"]

            title = conversation["title"]

            if len(title) > 28:

                title = title[:28] + "..."

            # ------------------------------------------------
            # Conversation row
            # ------------------------------------------------

            conversation_col, delete_col = st.columns(
                [5, 1],
                gap="small",
            )

            # ------------------------------------------------
            # Open conversation
            # ------------------------------------------------

            with conversation_col:

                if st.button(
                    "○  " + title,
                    key=f"conversation_{conversation_id}",
                    use_container_width=True,
                ):

                    st.session_state.conversation_id = (
                        conversation_id
                    )

                    messages = get_conversation_messages(
                        conversation_id,
                        user["id"],
                    )

                    st.session_state.messages = [
                        {
                            "role": message["role"],
                            "content": message["content"],
                        }
                        for message in messages
                    ]

                    st.rerun()

            # ------------------------------------------------
            # Delete conversation
            # ------------------------------------------------

            with delete_col:

                if st.button(
                    "×",
                    key=f"delete_conversation_{conversation_id}",
                    help="Delete conversation",
                ):

                    delete_conversation(
                        conversation_id,
                        user["id"],
                    )

                    if (
                        st.session_state.conversation_id
                        == conversation_id
                    ):

                        st.session_state.conversation_id = None
                        st.session_state.messages = []

                    st.rerun()

    else:

        st.caption(
            "No conversations yet."
        )

    # --------------------------------------------------------
    # USER AREA
    # --------------------------------------------------------

    st.markdown(
        '<div class="sidebar-spacer"></div>',
        unsafe_allow_html=True,
    )

    st.markdown("---")

    st.markdown(
        f"**👤 {user['name']}**"
    )

    st.caption(
        "Signed in"
    )

    # --------------------------------------------------------
    # SIGN OUT
    # --------------------------------------------------------

    if st.button(
        "Sign out",
        use_container_width=True,
        key="sign_out_button",
    ):
        cookie_controller.remove(
            AUTH_COOKIE_NAME
        )

        time.sleep(0.3)

        st.session_state.authenticated = False
        st.session_state.user = None
        st.session_state.conversation_id = None
        st.session_state.messages = []

        st.rerun()

        
# ============================================================
# WORKSPACE HEADER
# ============================================================

header_left, header_right = st.columns(
    [4, 1]
)


with header_left:

    st.markdown(
        """
<div class="workspace-header">
Knowledge Workspace
</div>

<div class="workspace-subtitle">
Your private AI knowledge assistant
</div>
""",
        unsafe_allow_html=True,
    )


with header_right:

    st.markdown(
        """
<div style="
text-align:right;
color:#64748b;
font-size:10px;
padding-top:5px;
">
● System ready
</div>
""",
        unsafe_allow_html=True,
    )


# ============================================================
# EMPTY CHAT / WELCOME STATE
# ============================================================

if not st.session_state.messages:

    st.markdown(
        """
<div class="chat-hero">

<div class="auth-kicker">
✦ AI-POWERED KNOWLEDGE INTELLIGENCE
</div>

<div class="chat-title">
Ask your knowledge.
<br>
<span class="chat-gradient">
Get intelligent answers.
</span>
</div>

<div class="chat-description">
Search your private research knowledge base using semantic
retrieval, neural reranking and intelligent AI agents —
with transparent sources.
</div>

</div>
""",
        unsafe_allow_html=True,
    )

    # --------------------------------------------------------
    # ACTIVE KNOWLEDGE BASE
    # --------------------------------------------------------

    with st.container(
        border=True,
    ):

        active_document = (
            documents[0]
            if documents
            else None
        )

        if active_document:

            st.markdown(
                f"""
<div style="
color:#64748b;
font-size:9px;
font-weight:800;
letter-spacing:1px;
">
ACTIVE KNOWLEDGE BASE
</div>

<div style="
color:#e2e8f0;
font-size:14px;
font-weight:700;
margin-top:7px;
">
{active_document["filename"]}
</div>

<div style="
color:#64748b;
font-size:10px;
margin-top:5px;
">
{active_document["page_count"]} pages •
{active_document["chunk_count"]} chunks •
Ready for intelligent question answering.
</div>
""",
                unsafe_allow_html=True,
            )

        else:

            st.markdown(
                """
<div style="
color:#64748b;
font-size:9px;
font-weight:800;
letter-spacing:1px;
">
ACTIVE KNOWLEDGE BASE
</div>

<div style="
color:#e2e8f0;
font-size:14px;
font-weight:700;
margin-top:7px;
">
No documents indexed
</div>

<div style="
color:#64748b;
font-size:10px;
margin-top:5px;
">
Upload a PDF from the Knowledge Base section
to start asking questions.
</div>
""",
                unsafe_allow_html=True,
            )


# ============================================================
# CHAT HISTORY
# ============================================================

for message in st.session_state.messages:

    with st.chat_message(
        message["role"]
    ):

        st.markdown(
            message["content"]
        )


# ============================================================
# CHAT INPUT
# ============================================================

question = st.chat_input(
    "Ask anything about your knowledge base..."
)


# ============================================================
# CHAT PROCESSING
# ============================================================

if question:

    # --------------------------------------------------------
    # CREATE NEW CONVERSATION
    # --------------------------------------------------------

    if st.session_state.conversation_id is None:

        title = question.strip()

        if len(title) > 45:

            title = title[:45] + "..."

        st.session_state.conversation_id = (
            create_conversation(
                user["id"],
                title,
            )
        )

    conversation_id = (
        st.session_state.conversation_id
    )

    # --------------------------------------------------------
    # SAVE USER MESSAGE
    # --------------------------------------------------------

    save_message(
        conversation_id,
        "user",
        question,
    )

    st.session_state.messages.append(
        {
            "role": "user",
            "content": question,
        }
    )

    with st.chat_message(
        "user"
    ):

        st.markdown(
            question
        )

    # --------------------------------------------------------
    # GET AI RESPONSE
    # --------------------------------------------------------

    with st.chat_message(
        "assistant"
    ):

        with st.spinner(
            "Searching your knowledge base..."
        ):

            try:

                response = requests.post(
                    f"{API_URL}/chat",
                    json={
                        "question": question
                    },
                    timeout=120,
                )

                if response.status_code == 200:

                    data = response.json()

                    answer = data.get(
                        "answer",
                        "No answer returned.",
                    )

                    sources = data.get(
                        "sources",
                        [],
                    )

                    # ----------------------------------------
                    # SAVE ASSISTANT RESPONSE
                    # ----------------------------------------

                    save_message(
                        conversation_id,
                        "assistant",
                        answer,
                    )

                    st.session_state.messages.append(
                        {
                            "role": "assistant",
                            "content": answer,
                        }
                    )

                    st.markdown(
                        answer
                    )

                    # ----------------------------------------
                    # RETRIEVED SOURCES
                    # ----------------------------------------

                    if sources:

                        st.markdown(
                            "##### 📚 Retrieved Sources"
                        )

                        for index, source in enumerate(
                            sources,
                            start=1,
                        ):

                            source_name = source.get(
                                "source",
                                "Unknown source",
                            )

                            page = source.get(
                                "page",
                                "?",
                            )

                            st.caption(
                                f"Source {index} • "
                                f"Page {page} • "
                                f"{source_name}"
                            )

                else:

                    st.error(
                        f"API request failed "
                        f"({response.status_code})."
                    )

            except requests.exceptions.ConnectionError:

                st.error(
                    "FastAPI is not running. "
                    "Please start the API server."
                )

            except requests.exceptions.Timeout:

                st.error(
                    "The request timed out. "
                    "Please try again."
                )

            except Exception as error:

                st.error(
                    f"Unexpected error: {error}"
                )