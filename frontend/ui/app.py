import streamlit as st
import requests
import pandas as pd
import os
import time
import re

# =========================================================
# STREAMLIT PAGE CONFIG (⚠️ MUST BE FIRST)
# =========================================================
st.set_page_config(
    page_title="NVIDIA Interview AI Agent",
    page_icon="🟢",
    layout="wide",
)

# =========================================================
# CONFIG
# =========================================================
API = os.getenv("API", "http://127.0.0.1:8000")
MAX_RETRIES = 5
INITIAL_BACKOFF = 1.0  # seconds
EMAIL_REGEX = re.compile(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$')

# =========================================================
# THEME STATE
# =========================================================
if "theme" not in st.session_state:
    st.session_state.theme = "light"

# =========================================================
# THEME CSS (Custom Styling for Each Task Type)
# =========================================================
def apply_theme(theme: str):
    if theme == "dark":
        st.markdown(
            """
            <style>
            body, .stApp {
                background-color: #0E1117;
                color: #FAFAFA;
                font-family: 'Roboto', sans-serif;
            }
            .stButton > button {
                background-color: #76B900;
                color: black;
                border-radius: 8px;
                padding: 10px;
            }
            .stTextInput input,
            .stTextArea textarea {
                background-color: #161B22;
                color: #FAFAFA;
            }
            .task-card {
                border: 1px solid #2D3748;
                border-radius: 8px;
                padding: 20px;
                box-shadow: 0px 4px 6px rgba(0, 0, 0, 0.1);
                margin-bottom: 20px;
            }
            .task-header {
                font-size: 24px;
                color: #76B900;
            }
            .task-subheader {
                font-size: 18px;
                color: #E2E8F0;
                margin-bottom: 15px;
            }
            </style>
            """,
            unsafe_allow_html=True,
        )
    else:
        st.markdown(
            """
            <style>
            body, .stApp {
                background-color: #FFFFFF;
                color: #000000;
                font-family: 'Roboto', sans-serif;
            }
            .stButton > button {
                background-color: #0E6FFF;
                color: white;
                border-radius: 8px;
                padding: 10px;
            }
            .stTextInput input,
            .stTextArea textarea {
                background-color: #F2F2F2;
                color: #000000;
            }
            .task-card {
                border: 1px solid #D1D5DB;
                border-radius: 8px;
                padding: 20px;
                box-shadow: 0px 4px 6px rgba(0, 0, 0, 0.1);
                margin-bottom: 20px;
            }
            .task-header {
                font-size: 24px;
                color: #0E6FFF;
            }
            .task-subheader {
                font-size: 18px;
                color: #2D3748;
                margin-bottom: 15px;
            }
            </style>
            """,
            unsafe_allow_html=True,
        )

apply_theme(st.session_state.theme)

# =========================================================
# AUTHENTICATION
# =========================================================

def show_login_page():
    """Display login/registration form"""
    st.title("🟢 NVIDIA Interview AI Agent")
    st.markdown("### Welcome! Please login or register to continue")
    
    # Tab for Login vs Register
    tab1, tab2 = st.tabs(["Login", "Register"])
    
    with tab1:
        with st.form("login_form"):
            email = st.text_input("Email")
            password = st.text_input("Password", type="password")
            submitted = st.form_submit_button("Login")
            
            if submitted:
                # Validate fields
                if not email or not password:
                    st.error("Email and password are required")
                elif not EMAIL_REGEX.match(email):
                    st.error("Please enter a valid email address")
                else:
                    try:
                        response = requests.post(
                            f"{API}/api/auth/login",
                            json={"email": email, "password": password}
                        )
                        if response.status_code == 200:
                            data = response.json()
                            st.session_state.token = data["token"]
                            st.session_state.user_id = data["user_id"]
                            st.session_state.email = data["email"]
                            st.session_state.role = data.get("role", "user")
                            st.session_state.token_expires_at = time.time() + data.get("expires_in", 604800)
                            st.success("Login successful!")
                            st.rerun()
                        else:
                            st.error(f"Login failed: {response.json().get('detail', 'Unknown error')}")
                    except Exception as e:
                        st.error(f"Error: {str(e)}")
    
    with tab2:
        with st.form("register_form"):
            full_name = st.text_input("Full Name")
            email = st.text_input("Email")
            password = st.text_input("Password", type="password")
            password_confirm = st.text_input("Confirm Password", type="password")
            submitted = st.form_submit_button("Register")
            
            if submitted:
                # Validate fields
                if not full_name or not email or not password or not password_confirm:
                    st.error("All fields are required")
                elif not EMAIL_REGEX.match(email):
                    st.error("Please enter a valid email address")
                elif password != password_confirm:
                    st.error("Passwords do not match")
                elif len(password) < 8:
                    st.error("Password must be at least 8 characters")
                else:
                    try:
                        response = requests.post(
                            f"{API}/api/auth/register",
                            json={"email": email, "password": password, "full_name": full_name}
                        )
                        if response.status_code == 201:
                            data = response.json()
                            st.session_state.token = data["token"]
                            st.session_state.user_id = data["user_id"]
                            st.session_state.email = data["email"]
                            st.session_state.role = "user"
                            st.session_state.token_expires_at = time.time() + data.get("expires_in", 604800)
                            st.success("Registration successful!")
                            st.rerun()
                        else:
                            st.error(f"Registration failed: {response.json().get('detail', 'Unknown error')}")
                    except Exception as e:
                        st.error(f"Error: {str(e)}")

def show_user_header():
    """Display logged-in user info and logout button"""
    col1, col2 = st.columns([4, 1])
    with col1:
        st.markdown(f"**Logged in as:** {st.session_state.get('email', 'Unknown')}")
    with col2:
        if st.button("Logout"):
            # Clear session state
            for key in ['token', 'user_id', 'email', 'role', 'token_expires_at']:
                if key in st.session_state:
                    del st.session_state[key]
            st.rerun()

# Check if user is logged in
if "token" not in st.session_state:
    show_login_page()
    st.stop()  # Stop execution if not logged in

# Show user header if logged in
show_user_header()
st.divider()

# =========================================================
# API HELPERS (RETRY + BACKOFF)
# =========================================================
def api_request(method, path, json=None, params=None):
    # Check if token is expired BEFORE making request
    if "token_expires_at" in st.session_state:
        if time.time() > st.session_state.token_expires_at:
            # Clear expired token
            for key in ['token', 'user_id', 'email', 'role', 'token_expires_at']:
                if key in st.session_state:
                    del st.session_state[key]
            st.error("Your session has expired. Please log in again.")
            st.rerun()
    
    url = f"{API}{path}"
    backoff = INITIAL_BACKOFF
    
    # Build headers with auth token if available
    headers = {}
    if "token" in st.session_state:
        headers["Authorization"] = f"Bearer {st.session_state.token}"

    for attempt in range(1, MAX_RETRIES + 1):
        try:
            resp = requests.request(
                method=method,
                url=url,
                json=json,
                params=params,
                headers=headers,
                timeout=60,
            )
            resp.raise_for_status()
            return resp.json()

        except requests.exceptions.HTTPError as e:
            # Handle 401 Unauthorized - clear invalid token
            if e.response.status_code == 401:
                for key in ['token', 'user_id', 'email', 'role', 'token_expires_at']:
                    if key in st.session_state:
                        del st.session_state[key]
                st.error("Your session has expired. Please log in again.")
                st.rerun()
            
            if attempt == MAX_RETRIES:
                st.error(
                    f"❌ Backend unavailable after {MAX_RETRIES} attempts\n\n"
                    f"Endpoint: `{path}`\n\nError: {e}"
                )
                return None

            time.sleep(backoff)
            backoff *= 2
        
        except Exception as e:
            if attempt == MAX_RETRIES:
                st.error(
                    f"❌ Backend unavailable after {MAX_RETRIES} attempts\n\n"
                    f"Endpoint: `{path}`\n\nError: {e}"
                )
                return None

            time.sleep(backoff)
            backoff *= 2

def api_get(path, **kwargs):
    return api_request("GET", path, **kwargs)

def api_post(path, json=None, **kwargs):
    return api_request("POST", path, json=json, **kwargs)

# =========================================================
# SIDEBAR (THEME TOGGLE)
# =========================================================
with st.sidebar:
    st.title("⚙️ Settings")

    theme_button = "☀️ Switch to Light Mode" if st.session_state.theme == "dark" else "🌙 Switch to Dark Mode"
    if st.button(theme_button):
        st.session_state.theme = "light" if st.session_state.theme == "dark" else "dark"
        st.rerun()

# =========================================================
# HEADER
# =========================================================
st.title("🧠 NVIDIA Interview AI Agent")
st.caption("Plan • Practice • Evaluate — NVIDIA-style")

# =========================================================
# SESSION STATE DEFAULTS
# =========================================================
DEFAULTS = {
    "plan": None,
    "ai_answer": None,
    "interview_started": False,
    "current_question": None,
    "evaluation": None,
    "latest_blog": None,
}

for k, v in DEFAULTS.items():
    st.session_state.setdefault(k, v)

# =========================================================
# TABS WITH DYNAMIC STYLING
# =========================================================
tabs = st.tabs(
    ["🎯 Plan", "💬 Ask AI", "📝 Interview Mode", "📊 Progress", "📜 History", "📰 Blogs"]
)

# =========================================================
# TASK 1: DAILY PLAN (TASK CARD DESIGN)
# =========================================================
with tabs[0]:
    st.markdown("<div class='task-header'>🎯 Daily Study Plan</div>", unsafe_allow_html=True)
    with st.expander("Generate Plan", expanded=True):
        if st.button("Generate Plan"):
            with st.spinner("Generating plan..."):
                resp = api_get("/plan/today")

                st.write("DEBUT:", resp)

                if resp:
                    plan = resp.get("plan")

                    if plan: 
                        st.session_state.plan = plan
                    else: 
                        st.error("Empty plan received")
                else: 
                    st.error("API failed")


 #               if resp:
 #                   st.session_state.plan = resp.get("plan")

#    if st.session_state.plan:
#        st.markdown(
#            f"<div class='task-card'>{st.session_state.plan}</div>", unsafe_al#low_html=True)

# =========================================================
# TASK 2: ASK INTERVIEW AI (TASK CARD DESIGN)
# =========================================================
with tabs[1]:
    st.markdown("<div class='task-header'>💬 Ask Interview AI</div>", unsafe_allow_html=True)
    question = st.text_input("Interview Question")

    if st.button("Ask AI"):
        with st.spinner("Calling interview agent..."):
            resp = api_post("/ask", json={"question": question})
            if resp:
                st.session_state.ai_answer = resp.get("answer")

    if st.session_state.ai_answer:
        st.success("AI Answer")
        st.write(st.session_state.ai_answer)

# =========================================================
# TASK 3: INTERVIEW MODE (TASK CARD DESIGN)
# =========================================================
with tabs[2]:
    st.markdown("<div class='task-header'>📝 Interview Mode (AI as Interviewer)</div>", unsafe_allow_html=True)
    
    if not st.session_state.interview_started:
        if st.button("🎤 Start Interview"):
            resp = api_get("/interview/question")
            if resp:
                st.session_state.current_question = resp.get("question")
                st.session_state.interview_started = True

    if st.session_state.current_question:
        st.markdown(f"**Question:** {st.session_state.current_question}")
        user_answer = st.text_area("Your Answer", height=180)

        if st.button("Submit Answer"):
            resp = api_post(
                "/evaluate",
                json={
                    "question": st.session_state.current_question,
                    "answer": user_answer,
                },
            )
            if resp:
                st.session_state.evaluation = resp.get("evaluation")

    if st.session_state.evaluation:
        st.subheader("Evaluation")
        st.write(st.session_state.evaluation)

# =========================================================
# TASK 4: PROGRESS (TASK CARD DESIGN)
# =========================================================
with tabs[3]:
    st.markdown("<div class='task-header'>📊 Progress</div>", unsafe_allow_html=True)
    
    scores = api_get("/history/scores")

    if scores:
        df = pd.DataFrame(scores)
        df["timestamp"] = pd.to_datetime(df["timestamp"])
        st.line_chart(df.set_index("timestamp")["score"])
    else:
        st.info("No evaluation data yet.")

# =========================================================
# TASK 5: HISTORY (TASK CARD DESIGN)
# =========================================================
with tabs[4]:
    st.markdown("<div class='task-header'>📜 History</div>", unsafe_allow_html=True)
    
    data = api_get("/history/chat")

    if not data:
        st.info("No chat history available.")
    else:
        df = pd.DataFrame(data)
        df["timestamp"] = pd.to_datetime(df["timestamp"])

        for _, row in df.iterrows():
            st.markdown(
                f"""
                **Q:** {row['question']}  
                **AI:** {row['answer']}  
                🕒 {row['timestamp']}
                ---
                """
            )

# =========================================================
# TASK 6: BLOGS (TASK CARD DESIGN)
# =========================================================
with tabs[5]:
    st.markdown("<div class='task-header'>📰 Blogs</div>", unsafe_allow_html=True)
    
    if st.button("Generate Today's Blog"):
        with st.spinner("Generating DevOps blog..."):
            resp = api_get("/blog/daily")
            if resp:
                st.session_state.latest_blog = resp

    if st.session_state.latest_blog:
        st.markdown(f"## {st.session_state.latest_blog['title']}")
        st.write(st.session_state.latest_blog["content"])

    st.divider()

    blogs = api_get("/blog/history")
    if blogs:
        for blog in blogs:
            st.markdown(f"### {blog['title']}")
            st.caption(blog["created_at"])
            st.write(blog["content"])
