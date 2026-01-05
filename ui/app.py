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

st.title("🧠 NVIDIA Interview AI Agent")
st.caption("Plan • Practice • Evaluate — NVIDIA-style")

# =========================================================
# SESSION STATE INITIALIZATION (CRITICAL)
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
}

for k, v in DEFAULTS.items():
    st.session_state.setdefault(k, v)

# =========================================================
# TABS
# =========================================================
tabs = st.tabs(
    ["🎯 Plan", "💬 Interview", "📝 Interview Mode", "📊 Progress", "📜 History"]
)

# =========================================================
# TAB 1: DAILY PLAN
# =========================================================
with tabs[0]:
    st.subheader("🎯 Daily Study Plan")

    if st.button("Generate Plan", key="generate_plan_btn"):
        st.session_state.generate_plan = True

    if st.session_state.generate_plan:
        with st.spinner("Generating plan..."):
            resp = api_get("/plan/today")
            if resp:
                st.session_state.plan = resp.get("plan")
        st.session_state.generate_plan = False  # reset trigger

    if st.session_state.plan:
        st.markdown(st.session_state.plan)

# =========================================================
# TAB 2: ASK INTERVIEW AI
# =========================================================
with tabs[1]:
    st.subheader("💬 Ask Interview AI")

    question = st.text_input("Interview Question", key="ask_input")

    if st.button("Ask AI", key="ask_ai_btn"):
        st.session_state.ask_ai = True

    if st.session_state.ask_ai:
        with st.spinner("Calling interview agent..."):
            resp = api_post("/ask", json={"question": question})
            if resp:
                st.session_state.ai_answer = resp.get("answer")
        st.session_state.ask_ai = False

    if st.session_state.ai_answer:
        st.success("AI Answer")
        st.write(st.session_state.ai_answer)

# =========================================================
# TAB 3: INTERVIEW MODE (AGENT AS INTERVIEWER)
# =========================================================
with tabs[2]:
    st.subheader("📝 Interview Mode (Agent as Interviewer)")
    st.write("The AI acts as the interviewer. You answer. It evaluates.")

    if not st.session_state.interview_started:
        st.session_state.interview_prompt = st.text_input(
            "Interview focus (optional)",
            placeholder="CUDA, GPU architecture, performance optimization",
            key="interview_focus",
        )

        if st.button("🎤 Start Interview", key="start_interview_btn"):
            with st.spinner("Preparing interview..."):
                resp = api_get(
                    "/interview/question",
                    params={"prompt": st.session_state.interview_prompt},
                )
                if resp:
                    st.session_state.current_question = resp.get("question")
                    st.session_state.interview_started = True
                    st.session_state.evaluation = None

    if st.session_state.interview_started and st.session_state.current_question:
        st.markdown(
            f"""
            <div class="card accent">
            <b>Interview Question</b><br>
            {st.session_state.current_question}
            </div>
            """,
            unsafe_allow_html=True,
        )

        user_answer = st.text_area(
            "Your Answer",
            height=180,
            key="interview_answer",
        )

        if st.button("✅ Submit Answer", key="submit_answer_btn"):
            with st.spinner("Evaluating like an NVIDIA interviewer..."):
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
        st.markdown(
            "<div class='card'><b>Evaluation</b></div>",
            unsafe_allow_html=True,
        )
        st.write(st.session_state.evaluation)

        if st.button("➡️ Next Question", key="next_question_btn"):
            with st.spinner("Generating next question..."):
                resp = api_get(
                    "/interview/question",
                    params={"prompt": st.session_state.interview_prompt},
                )
                if resp:
                    st.session_state.current_question = resp.get("question")
                    st.session_state.evaluation = None
                    st.session_state.interview_answer = ""

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

