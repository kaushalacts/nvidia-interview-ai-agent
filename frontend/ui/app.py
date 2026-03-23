import streamlit as st
import requests
import pandas as pd
import os
import time

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
# API HELPERS (RETRY + BACKOFF)
# =========================================================
def api_request(method, path, json=None, params=None):
    url = f"{API}{path}"
    backoff = INITIAL_BACKOFF

    for attempt in range(1, MAX_RETRIES + 1):
        try:
            resp = requests.request(
                method=method,
                url=url,
                json=json,
                params=params,
                timeout=180,
            )
            resp.raise_for_status()
            return resp.json()

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
