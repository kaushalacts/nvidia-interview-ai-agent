import streamlit as st
import requests
import pandas as pd
import os
import time

# =========================================================
# CONFIG
# =========================================================
API = os.getenv("API", "http://backend:8000")
MAX_RETRIES = 5
INITIAL_BACKOFF = 1.0  # seconds

# =========================================================
# THEME STATE (🆕)
# =========================================================
if "theme" not in st.session_state:
    st.session_state.theme = "dark"  # default theme

# =========================================================
# THEME CSS (🆕)
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
                timeout=60,
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
# STREAMLIT PAGE CONFIG
# =========================================================
st.set_page_config(
    page_title="NVIDIA Interview AI Agent",
    page_icon="🟢",
    layout="wide",
)

# =========================================================
# SIDEBAR (🆕 THEME TOGGLE)
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
# SESSION STATE INITIALIZATION
# =========================================================
DEFAULTS = {
    "plan": None,
    "generate_plan": False,
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
# TABS
# =========================================================
tabs = st.tabs(
    ["🎯 Plan", "💬 Interview", "📝 Interview Mode", "📊 Progress", "📜 History", "📰 Blogs"]
)

# =========================================================
# TAB 1: DAILY PLAN
# =========================================================
with tabs[0]:
    st.subheader("🎯 Daily Study Plan")

    if st.button("Generate Plan"):
        with st.spinner("Generating plan..."):
            resp = api_get("/plan/today")
            if resp:
                st.session_state.plan = resp.get("plan")

    if st.session_state.plan:
        st.markdown(st.session_state.plan)

# =========================================================
# TAB 2: ASK INTERVIEW AI
# =========================================================
with tabs[1]:
    st.subheader("💬 Ask Interview AI")

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
# TAB 3: INTERVIEW MODE
# =========================================================
with tabs[2]:
    st.subheader("📝 Interview Mode (Agent as Interviewer)")
    st.write("The AI acts as the interviewer. You answer. It evaluates.")

    if not st.session_state.interview_started:
        st.session_state.interview_prompt = st.text_input(
            "Interview focus (optional)",
            placeholder="CUDA, GPU architecture, performance optimization",
        )

        if st.button("🎤 Start Interview"):
            resp = api_get("/interview/question")
            if resp:
                st.session_state.current_question = resp.get("question")
                st.session_state.interview_started = True

    if st.session_state.current_question:
        st.markdown(f"**Interview Question:** {st.session_state.current_question}")

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
# TAB 4: PROGRESS
# =========================================================
with tabs[3]:
    scores = api_get("/history/scores")

    if scores:
        df = pd.DataFrame(scores)
        df["timestamp"] = pd.to_datetime(df["timestamp"])
        st.line_chart(df.set_index("timestamp")["score"])
    else:
        st.info("No evaluation data yet.")

# =========================================================
# TAB 5: HISTORY
# =========================================================
with tabs[4]:
    st.subheader("📜 Interview Chat History")

    data = api_get("/history/chat")

    if not data:
        st.info("No chat history available yet.")
    else:
        df = pd.DataFrame(data)
        df["timestamp"] = pd.to_datetime(df["timestamp"])
        df["date"] = df["timestamp"].dt.date
        df["time"] = df["timestamp"].dt.strftime("%H:%M")

        for date, group in df.groupby("date", sort=False):
            st.markdown(f"### 🗓️ {date}")
            for _, row in group.iterrows():
                st.markdown(
                    f"""
                    <div class="card accent">
                    <b>🕒 {row['time']}</b><br>
                    <b>Q:</b> {row['question']}<br><br>
                    <b>AI:</b> {row['answer']}
                    </div>
                    """,
                    unsafe_allow_html=True,
                )

# =========================================================
# TAB 6: BLOGS
# =========================================================
with tabs[5]:
    st.subheader("📰 Daily DevOps Blogs")

    if st.button("Generate Today's Blog"):
        with st.spinner("Generating senior DevOps blog..."):
            resp = api_get("/blog/daily")
            if resp:
                st.session_state.latest_blog = resp

    if st.session_state.latest_blog:
        st.markdown(f"## {st.session_state.latest_blog['title']}")
        st.write(st.session_state.latest_blog["content"])

    st.divider()
    st.subheader("📚 Blog History")

    blogs = api_get("/blog/history")
    if blogs:
        for blog in blogs:
            st.markdown(f"### {blog['title']}")
            st.caption(blog["created_at"])
            st.write(blog["content"])
