import streamlit as st
import requests
import pandas as pd
import os
import time

# =========================================================
# STREAMLIT PAGE CONFIG (🚨 MUST BE FIRST)
# =========================================================
st.set_page_config(
    page_title="NVIDIA Interview AI Agent",
    page_icon="🟢",
    layout="wide",
)

# =========================================================
# CONFIG
# =========================================================
API = os.getenv("API", "http://backend:8000")
MAX_RETRIES = 5
INITIAL_BACKOFF = 1.0  # seconds

# =========================================================
# THEME CSS (FUNCTION ONLY — SAFE)
# =========================================================
def apply_theme(theme: str):
    if theme == "dark":
        st.markdown(
            """
            <style>
            body, .stApp {
                background-color: #0E1117;
                color: #FAFAFA;
            }
            .stButton > button {
                background-color: #76B900;
                color: black;
                border-radius: 8px;
            }
            .stTextInput input,
            .stTextArea textarea {
                background-color: #161B22;
                color: #FAFAFA;
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
            }
            .stButton > button {
                background-color: #0E6FFF;
                color: white;
                border-radius: 8px;
            }
            .stTextInput input,
            .stTextArea textarea {
                background-color: #F2F2F2;
                color: #000000;
            }
            </style>
            """,
            unsafe_allow_html=True,
        )

# =========================================================
# SESSION STATE INIT
# =========================================================
if "theme" not in st.session_state:
    st.session_state.theme = "dark"

DEFAULTS = {
    "plan": None,
    "ask_ai": False,
    "ai_answer": None,
    "interview_started": False,
    "interview_prompt": "",
    "current_question": None,
    "evaluation": None,
    "latest_blog": None,
}

for k, v in DEFAULTS.items():
    st.session_state.setdefault(k, v)

# =========================================================
# APPLY THEME (✅ SAFE NOW)
# =========================================================
apply_theme(st.session_state.theme)

# =========================================================
# API HELPERS
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
                timeout=60,
            )
            resp.raise_for_status()
            return resp.json()
        except Exception as e:
            if attempt == MAX_RETRIES:
                st.error(f"Backend unavailable: {e}")
                return None
            time.sleep(backoff)
            backoff *= 2


def api_get(path, **kwargs):
    return api_request("GET", path, **kwargs)


def api_post(path, json=None, **kwargs):
    return api_request("POST", path, json=json, **kwargs)

# =========================================================
# SIDEBAR — THEME TOGGLE
# =========================================================
with st.sidebar:
    st.title("⚙️ Settings")

    if st.session_state.theme == "dark":
        if st.button("☀️ Switch to Light Mode"):
            st.session_state.theme = "light"
            st.experimental_rerun()
    else:
        if st.button("🌙 Switch to Dark Mode"):
            st.session_state.theme = "dark"
            st.experimental_rerun()

# =========================================================
# HEADER
# =========================================================
st.title("🧠 NVIDIA Interview AI Agent")
st.caption("Plan • Practice • Evaluate — NVIDIA-style")

# =========================================================
# TABS
# =========================================================
tabs = st.tabs(
    ["🎯 Plan", "💬 Interview", "📝 Interview Mode", "📊 Progress", "📜 History", "📰 Blogs"]
)

# =========================================================
# TAB 1: PLAN
# =========================================================
with tabs[0]:
    if st.button("Generate Plan"):
        resp = api_get("/plan/today")
        if resp:
            st.session_state.plan = resp.get("plan")

    if st.session_state.plan:
        st.markdown(st.session_state.plan)

# =========================================================
# TAB 2: ASK AI
# =========================================================
with tabs[1]:
    q = st.text_input("Interview Question")
    if st.button("Ask AI"):
        resp = api_post("/ask", json={"question": q})
        if resp:
            st.session_state.ai_answer = resp.get("answer")

    if st.session_state.ai_answer:
        st.success("AI Answer")
        st.write(st.session_state.ai_answer)

# =========================================================
# TAB 3: INTERVIEW MODE
# =========================================================
with tabs[2]:
    if not st.session_state.interview_started:
        st.session_state.interview_prompt = st.text_input("Interview focus (optional)")
        if st.button("🎤 Start Interview"):
            resp = api_get("/interview/question")
            if resp:
                st.session_state.current_question = resp["question"]
                st.session_state.interview_started = True

    if st.session_state.current_question:
        st.markdown(f"**Question:** {st.session_state.current_question}")
        ans = st.text_area("Your Answer")

        if st.button("Submit Answer"):
            resp = api_post("/evaluate", json={
                "question": st.session_state.current_question,
                "answer": ans,
            })
            if resp:
                st.session_state.evaluation = resp["evaluation"]

    if st.session_state.evaluation:
        st.subheader("Evaluation")
        st.write(st.session_state.evaluation)

# =========================================================
# TAB 4: PROGRESS
# =========================================================
with tabs[3]:
    scores = api_get("/history/scores")
    if scores:
        df = pd.DataFrame(scores)
        df["timestamp"] = pd.to_datetime(df["timestamp"])
        st.line_chart(df.set_index("timestamp")["score"])

# =========================================================
# TAB 5: HISTORY
# =========================================================
with tabs[4]:
    data = api_get("/history/chat")
    if data:
        df = pd.DataFrame(data)
        df["timestamp"] = pd.to_datetime(df["timestamp"])
        for _, r in df.iterrows():
            st.markdown(f"**Q:** {r['question']}\n\n**AI:** {r['answer']}")

# =========================================================
# TAB 6: BLOGS
# =========================================================
with tabs[5]:
    if st.button("Generate Today's Blog"):
        resp = api_get("/blog/daily")
        if resp:
            st.session_state.latest_blog = resp

    if st.session_state.latest_blog:
        st.markdown(f"## {st.session_state.latest_blog['title']}")
        st.write(st.session_state.latest_blog["content"])

