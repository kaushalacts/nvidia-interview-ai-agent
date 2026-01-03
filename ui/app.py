import streamlit as st
import requests
import pandas as pd

if "current_question" not in st.session_state:
    st.session_state.current_question = None

if "evaluation_result" not in st.session_state:
    st.session_state.evaluation_result = None

BACKEND_URL = "http://backend:8000"

st.set_page_config(
    page_title="NVIDIA Interview AI Agent",
    page_icon="🟢",
    layout="wide"
)

st.title("🧠 NVIDIA Interview AI Agent")
st.caption("Plan • Practice • Evaluate — NVIDIA-style")

tabs = st.tabs([
    "🎯 Plan",
    "💬 Interview",
    "📝 Interview Mode",
    "📊 Progress",
    "📜 History"
])


# ---------------- PLAN ----------------
# ---------------- PLAN ----------------
with tabs[0]:
    st.subheader("🎯 Daily Study Plan")

    if "plan" not in st.session_state:
        st.session_state.plan = None

    if st.button("Generate Plan", key="plan_btn"):
        st.session_state.plan = None
        with st.spinner("Generating plan..."):
            try:
                resp = requests.get("http://localhost:8000/plan/today", timeout=60)
                st.session_state.plan = resp.json()["plan"]
            except Exception as e:
                st.error(f"API error: {e}")

    if st.session_state.plan:
        st.markdown(st.session_state.plan)

# ---------------- INTERVIEW ----------------
# ---------------- INTERVIEW ----------------
with tabs[1]:
    st.subheader("💬 Ask Interview AI")

    if "ask_clicked" not in st.session_state:
        st.session_state.ask_clicked = False

    if "ai_answer" not in st.session_state:
        st.session_state.ai_answer = None

    question = st.text_input("Interview Question", key="ask_input")

    if st.button("Ask AI", key="ask_ai_btn"):
        st.session_state.ask_clicked = True
        st.session_state.ai_answer = None

    if st.session_state.ask_clicked and question:
        with st.spinner("Calling interview agent..."):
            try:
                resp = requests.post(
                    "http://localhost:8000/ask",
                    json={"question": question},
                    timeout=60
                )
                st.session_state.ai_answer = resp.json()["answer"]
            except Exception as e:
                st.error(f"API error: {e}")

        st.session_state.ask_clicked = False

    if st.session_state.ai_answer:
        st.success("AI Answer")
        st.write(st.session_state.plan)
# ---------------- EVALUATE ----------------
# ---------------- EVALUATION ----------------
# ---------------- INTERVIEW MODE (AGENT-LED) ----------------
with tabs[2]:
    st.subheader("📝 Interview Mode (Agent as Interviewer)")
    st.write("The AI acts as the interviewer. You answer. It evaluates. Repeat.")

    # -------- Session State --------
    if "interview_started" not in st.session_state:
        st.session_state.interview_started = False

    if "interview_prompt" not in st.session_state:
        st.session_state.interview_prompt = ""

    if "current_question" not in st.session_state:
        st.session_state.current_question = None

    if "evaluation" not in st.session_state:
        st.session_state.evaluation = None

    # -------- Step 1: Start Interview --------
    if not st.session_state.interview_started:
        st.session_state.interview_prompt = st.text_input(
            "Interview focus (optional)",
            placeholder="CUDA, GPU architecture, performance optimization"
        )

        if st.button("🎤 Start Interview", key="start_interview"):
            with st.spinner("Preparing interview..."):
                resp = requests.get(
                    "http://localhost:8000/interview/question",
                    params={"prompt": st.session_state.interview_prompt}
                )
                st.session_state.current_question = resp.json()["question"]
                st.session_state.interview_started = True
                st.session_state.evaluation = None

    # -------- Step 2: Ask Question --------
    if st.session_state.interview_started and st.session_state.current_question:
        st.markdown(f"""
        <div class="card accent">
        <b>Interview Question</b><br>
        {st.session_state.current_question}
        </div>
        """, unsafe_allow_html=True)

        user_answer = st.text_area(
            "Your Answer",
            height=180,
            key="interview_answer"
        )

        # -------- Step 3: Evaluate --------
        if st.button("✅ Submit Answer", key="submit_answer"):
            with st.spinner("Evaluating like an NVIDIA interviewer..."):
                resp = requests.post(
                    "http://localhost:8000/evaluate",
                    json={
                        "question": st.session_state.current_question,
                        "answer": user_answer
                    }
                )
                st.session_state.evaluation = resp.json()["evaluation"]

    # -------- Step 4: Show Evaluation --------
    if st.session_state.evaluation:
        st.markdown("""
        <div class="card">
        <b>Evaluation</b>
        </div>
        """, unsafe_allow_html=True)

        st.write(st.session_state.evaluation)

        # -------- Step 5: Next Question --------
        if st.button("➡️ Next Question", key="next_q"):
            with st.spinner("Generating next question..."):
                resp = requests.get(
                    "http://localhost:8000/interview/question",
                    params={"prompt": st.session_state.interview_prompt}
                )
                st.session_state.current_question = resp.json()["question"]
                st.session_state.evaluation = None
                st.session_state.interview_answer = ""

# ---------------- PROGRESS ----------------
with tabs[3]:
    scores = requests.get(f"{API}/history/scores").json()

    if scores:
        df = pd.DataFrame(scores)
        df["timestamp"] = pd.to_datetime(df["timestamp"])
        st.line_chart(df.set_index("timestamp")["score"])
    else:
        st.info("No evaluation data yet.")
# ---------------- HISTORY ----------------
with tabs[4]:
    st.subheader("📜 Interview Chat History")
    st.write("Review your past interview practice sessions, grouped by date.")

    try:
        resp = requests.get("http://localhost:8000/history/chat", timeout=30)
        data = resp.json()
    except Exception as e:
        st.error(f"Failed to load history: {e}")
        data = []

    if not data:
        st.info("No chat history available yet.")
    else:
        df = pd.DataFrame(data)
        df["timestamp"] = pd.to_datetime(df["timestamp"])
        df["date"] = df["timestamp"].dt.date
        df["time"] = df["timestamp"].dt.strftime("%H:%M")

        # Group by date
        for date, group in df.groupby("date", sort=False):
            st.markdown(f"### 🗓️ {date}")

            for _, row in group.iterrows():
                st.markdown(f"""
                <div class="card accent">
                <b>🕒 {row['time']}</b><br>
                <b>Q:</b> {row['question']}<br><br>
                <b>AI:</b> {row['answer']}
                </div>
                """, unsafe_allow_html=True)


