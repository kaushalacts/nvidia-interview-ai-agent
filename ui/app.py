import streamlit as st
import requests
import time

API_BASE = "http://localhost:8000"

# -------------------------------------------------
# Page Config
# -------------------------------------------------
st.set_page_config(
    page_title="NVIDIA Interview AI Agent",
    page_icon="🟢",
    layout="wide"
)

# -------------------------------------------------
# Custom CSS (Dark + NVIDIA Style)
# -------------------------------------------------
st.markdown("""
<style>
.main {
    padding: 2rem;
}

.card {
    background: linear-gradient(145deg, #161B22, #0E1117);
    border-radius: 14px;
    padding: 1.6rem;
    border: 1px solid #222;
    margin-bottom: 1.2rem;
}

.accent {
    border-left: 5px solid #76B900;
    padding-left: 1rem;
}

.stButton button {
    background: linear-gradient(90deg, #76B900, #5fa300);
    color: black;
    font-weight: 600;
    border-radius: 10px;
    padding: 0.6rem 1.2rem;
    border: none;
    transition: all 0.25s ease-in-out;
}

.stButton button:hover {
    transform: scale(1.03);
    background: linear-gradient(90deg, #8edb00, #76B900);
}

input, textarea {
    border-radius: 8px !important;
}

.status {
    display: inline-block;
    padding: 0.35rem 0.8rem;
    border-radius: 20px;
    font-size: 0.75rem;
    background-color: #1f6f43;
    color: #eaffea;
}
</style>
""", unsafe_allow_html=True)

# -------------------------------------------------
# Header
# -------------------------------------------------
st.title("🧠 NVIDIA Interview AI Agent")
st.markdown("<span class='status'>SYSTEM ONLINE</span>", unsafe_allow_html=True)
st.caption("Plan • Practice • Evaluate — like a real NVIDIA engineer")

st.markdown("---")

# -------------------------------------------------
# Sidebar (Reset replaces Stop button)
# -------------------------------------------------
with st.sidebar:
    st.header("⚙️ Controls")
    st.write("Session & system controls")

    if st.button("🔄 Reset Session", use_container_width=True, key="reset_session"):
        st.session_state.clear()
        st.rerun()

    st.markdown("---")
    st.write("Theme: Dark (NVIDIA)")
    st.write("LLM: Ollama (Local)")
    st.write("RAG: ChromaDB")

# -------------------------------------------------
# Tabs
# -------------------------------------------------
tabs = st.tabs([
    "🎯 Daily Plan",
    "💬 Interview AI",
    "📝 Evaluation"
])

# =================================================
# TAB 1 — DAILY PLAN
# =================================================
with tabs[0]:
    st.subheader("🎯 Today’s Focus Plan")
    st.write("Auto-generated daily study plan based on NVIDIA interview expectations.")

    if st.button("Generate Plan", use_container_width=True, key="generate_plan_btn"):
        with st.spinner("Building your focused study plan..."):
            time.sleep(0.5)
            resp = requests.get(f"{API_BASE}/plan/today")
            plan = resp.json()["plan"]

        st.markdown(f"""
        <div class="card accent">
        {plan}
        </div>
        """, unsafe_allow_html=True)

# =================================================
# TAB 2 — INTERVIEW AI
# =================================================
with tabs[1]:
    st.subheader("💬 Ask the Interview AI")
    st.write("Ask questions and get NVIDIA-style answers.")

    question = st.text_input(
        "Interview Question",
        placeholder="Explain CUDA memory coalescing and why it matters",
        key="ask_question_input"
    )

    col1, col2 = st.columns([3, 1])

    with col1:
        ask = st.button("Ask AI", use_container_width=True, key="ask_ai_btn")
    with col2:
        clear_ai = st.button("Clear", use_container_width=True, key="clear_ai_btn")

    if clear_ai:
        st.session_state.pop("ai_answer", None)

    if ask and question:
        with st.spinner("Thinking like a senior NVIDIA engineer..."):
            resp = requests.get(
                f"{API_BASE}/ask",
                params={"question": question}
            )
            st.session_state["ai_answer"] = resp.json()["answer"]

    if "ai_answer" in st.session_state:
        st.markdown("""
        <div class="card accent">
        <b>AI Response</b>
        </div>
        """, unsafe_allow_html=True)
        st.write(st.session_state["ai_answer"])

# =================================================
# TAB 3 — EVALUATION
# =================================================
with tabs[2]:
    st.subheader("📝 Evaluate Your Answer")
    st.write("Get honest, NVIDIA-style interview feedback.")

    q_eval = st.text_input(
        "Interview Question",
        placeholder="Explain CUDA memory hierarchy",
        key="eval_question_input"
    )

    a_eval = st.text_area(
        "Your Answer",
        height=180,
        placeholder="Answer as you would in a real interview...",
        key="eval_answer_input"
    )

    col1, col2 = st.columns([3, 1])

    with col1:
        eval_btn = st.button("Evaluate Answer", use_container_width=True, key="eval_btn")
    with col2:
        clear_eval = st.button("Clear", use_container_width=True, key="clear_eval_btn")

    if clear_eval:
        st.session_state.pop("evaluation", None)

    if eval_btn and q_eval and a_eval:
        with st.spinner("Evaluating your answer..."):
            resp = requests.post(
                f"{API_BASE}/evaluate",
                json={
                    "question": q_eval,
                    "answer": a_eval
                }
            )
            st.session_state["evaluation"] = resp.json()["evaluation"]

    if "evaluation" in st.session_state:
        st.markdown("""
        <div class="card accent">
        <b>Evaluation Result</b>
        </div>
        """, unsafe_allow_html=True)
        st.write(st.session_state["evaluation"])

# -------------------------------------------------
# Footer
# -------------------------------------------------
st.markdown("---")
st.caption("FastAPI • ChromaDB • Ollama • Streamlit • RAG • Agentic AI")

