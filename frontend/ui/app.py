import streamlit as st
import requests
import pandas as pd
import os
import time
import re

st.set_page_config(
    page_title="Interview Prep AI",
    page_icon="🧠",
    layout="wide",
)

API = os.getenv("API", "http://127.0.0.1:8000")
MAX_RETRIES = 3
EMAIL_REGEX = re.compile(r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$")

COMPANIES = ["NVIDIA", "Google", "Meta", "Apple"]

# ── Theme ─────────────────────────────────────────────────────────────────────

if "theme" not in st.session_state:
    st.session_state.theme = "dark"


def apply_theme():
    dark = st.session_state.theme == "dark"
    bg = "#0E1117" if dark else "#FFFFFF"
    fg = "#FAFAFA" if dark else "#000000"
    accent = "#76B900" if dark else "#0E6FFF"
    card_bg = "#161B22" if dark else "#F2F2F2"
    st.markdown(
        f"""<style>
        body, .stApp {{ background-color: {bg}; color: {fg}; font-family: 'Roboto', sans-serif; }}
        .stButton > button {{ background-color: {accent}; color: {"black" if dark else "white"};
            border-radius: 8px; padding: 8px 16px; font-weight: 600; }}
        .stTextInput input, .stTextArea textarea {{ background-color: {card_bg}; color: {fg}; }}
        .accent {{ color: {accent}; font-size: 22px; font-weight: 700; }}
        .card {{ border: 1px solid {"#2D3748" if dark else "#D1D5DB"}; border-radius: 10px;
            padding: 18px; margin-bottom: 16px; }}
        .stage-badge {{ background-color: {accent}; color: {"black" if dark else "white"};
            padding: 3px 10px; border-radius: 12px; font-size: 12px; font-weight: 700; }}
        </style>""",
        unsafe_allow_html=True,
    )


apply_theme()

# ── Auth ──────────────────────────────────────────────────────────────────────


def show_login_page():
    st.title("🧠 Interview Prep AI")
    st.markdown("### Multi-company technical interview preparation")

    tab1, tab2 = st.tabs(["Login", "Register"])

    with tab1:
        with st.form("login_form"):
            email = st.text_input("Email")
            password = st.text_input("Password", type="password")
            submitted = st.form_submit_button("Login")
            if submitted:
                if not email or not password:
                    st.error("All fields required")
                elif not EMAIL_REGEX.match(email):
                    st.error("Invalid email format")
                else:
                    try:
                        r = requests.post(f"{API}/api/auth/login", json={"email": email, "password": password}, timeout=10)
                        if r.status_code == 200:
                            d = r.json()
                            st.session_state.update(
                                token=d["token"],
                                user_id=d["user_id"],
                                email=d["email"],
                                role=d.get("role", "user"),
                                token_expires_at=time.time() + d.get("expires_in", 604800),
                            )
                            st.success("Login successful!")
                            st.rerun()
                        else:
                            st.error(r.json().get("detail", "Login failed"))
                    except Exception as e:
                        st.error(f"Connection error: {e}")

    with tab2:
        with st.form("register_form"):
            full_name = st.text_input("Full Name")
            email = st.text_input("Email")
            password = st.text_input("Password", type="password")
            confirm = st.text_input("Confirm Password", type="password")
            submitted = st.form_submit_button("Register")
            if submitted:
                if not all([full_name, email, password, confirm]):
                    st.error("All fields required")
                elif not EMAIL_REGEX.match(email):
                    st.error("Invalid email format")
                elif password != confirm:
                    st.error("Passwords do not match")
                elif len(password) < 8:
                    st.error("Password must be at least 8 characters")
                else:
                    try:
                        r = requests.post(
                            f"{API}/api/auth/register",
                            json={"email": email, "password": password, "full_name": full_name},
                            timeout=10,
                        )
                        if r.status_code == 201:
                            d = r.json()
                            st.session_state.update(
                                token=d["token"],
                                user_id=d["user_id"],
                                email=d["email"],
                                role="user",
                                token_expires_at=time.time() + 604800,
                            )
                            st.success("Account created!")
                            st.rerun()
                        else:
                            st.error(r.json().get("detail", "Registration failed"))
                    except Exception as e:
                        st.error(f"Connection error: {e}")


if "token" not in st.session_state:
    show_login_page()
    st.stop()

# ── Header ────────────────────────────────────────────────────────────────────

col_title, col_user = st.columns([5, 1])
with col_title:
    st.markdown(f"<span class='accent'>🧠 Interview Prep AI</span>", unsafe_allow_html=True)
with col_user:
    st.caption(st.session_state.get("email", ""))
    if st.button("Logout"):
        for k in ["token", "user_id", "email", "role", "token_expires_at"]:
            st.session_state.pop(k, None)
        st.rerun()

st.divider()

# ── Sidebar ───────────────────────────────────────────────────────────────────

with st.sidebar:
    st.markdown("### ⚙️ Settings")

    company = st.selectbox("Target Company", COMPANIES, key="company")
    st.caption(f"Questions, plans, and blogs will be tailored for **{company}**.")

    st.divider()
    label = "☀️ Light Mode" if st.session_state.theme == "dark" else "🌙 Dark Mode"
    if st.button(label):
        st.session_state.theme = "light" if st.session_state.theme == "dark" else "dark"
        st.rerun()

# ── API helpers ───────────────────────────────────────────────────────────────


def _headers():
    return {"Authorization": f"Bearer {st.session_state.token}"}


def api_get(path, params=None):
    if time.time() > st.session_state.get("token_expires_at", 0):
        st.error("Session expired. Please log in again.")
        st.stop()
    try:
        r = requests.get(f"{API}{path}", headers=_headers(), params=params, timeout=90)
        if r.status_code == 401:
            st.error("Session expired. Please log in again.")
            st.stop()
        r.raise_for_status()
        return r.json()
    except requests.HTTPError as e:
        st.error(f"API error: {e}")
        return None
    except Exception as e:
        st.error(f"Connection error: {e}")
        return None


def api_post(path, json=None, params=None, auth=True):
    if auth and time.time() > st.session_state.get("token_expires_at", 0):
        st.error("Session expired. Please log in again.")
        st.stop()
    headers = _headers() if auth else {}
    try:
        r = requests.post(f"{API}{path}", headers=headers, json=json, params=params, timeout=90)
        if auth and r.status_code == 401:
            st.error("Session expired. Please log in again.")
            st.stop()
        r.raise_for_status()
        return r.json()
    except requests.HTTPError as e:
        st.error(f"API error: {e}")
        return None
    except Exception as e:
        st.error(f"Connection error: {e}")
        return None


# ── Session state defaults ─────────────────────────────────────────────────────

for k, v in {
    "plan": None,
    "ai_answer": None,
    "interview_session_id": None,
    "interview_question": None,
    "interview_question_id": None,
    "interview_stage": None,
    "interview_difficulty": None,
    "interview_evaluation": None,
    "interview_history": [],
    "latest_blog": None,
    "blog_answer": None,
}.items():
    st.session_state.setdefault(k, v)

# ── Tabs ──────────────────────────────────────────────────────────────────────

tabs = st.tabs(["🎯 Plan", "💬 Ask AI", "📝 Interview", "📊 Progress", "📜 History", "📰 Blogs"])

# ─────────────────────────── TAB 1: DAILY PLAN ───────────────────────────────
with tabs[0]:
    st.markdown("<div class='accent'>🎯 Daily Study Plan</div>", unsafe_allow_html=True)
    st.caption(f"2-hour prep plan tailored for a **{company}** interview.")

    if st.button("Generate Plan", key="gen_plan"):
        with st.spinner(f"Building your {company} prep plan..."):
            resp = api_get("/plan/today", params={"company": company})
            if resp:
                st.session_state.plan = resp.get("plan")

    if st.session_state.plan:
        st.markdown(
            f"<div class='card'>{st.session_state.plan.replace(chr(10), '<br>')}</div>",
            unsafe_allow_html=True,
        )

# ─────────────────────────── TAB 2: ASK AI ───────────────────────────────────
with tabs[1]:
    st.markdown("<div class='accent'>💬 Ask AI (RAG-grounded)</div>", unsafe_allow_html=True)
    st.caption("Ask any technical question. The AI answers using context from your company's tech articles.")
    question = st.text_input("Your question", key="ask_question")

    if st.button("Ask", key="ask_btn"):
        if not question.strip():
            st.warning("Please enter a question.")
        else:
            with st.spinner("Searching knowledge base and generating answer..."):
                resp = api_post("/ask", json={"question": question})
                if resp:
                    st.session_state.ai_answer = resp.get("answer")

    if st.session_state.ai_answer:
        st.success("Answer")
        st.markdown(st.session_state.ai_answer)

# ─────────────────────────── TAB 3: INTERVIEW MODE ──────────────────────────
with tabs[2]:
    st.markdown("<div class='accent'>📝 Interview Mode</div>", unsafe_allow_html=True)

    # Stage badge
    stage = st.session_state.interview_stage
    if stage:
        diff = st.session_state.interview_difficulty or 3
        st.markdown(
            f"<span class='stage-badge'>{stage}</span> &nbsp; Difficulty: {'⭐' * diff}",
            unsafe_allow_html=True,
        )
        st.caption("")

    # Start / Next question
    col_start, col_next = st.columns([1, 1])
    with col_start:
        if st.button("🎤 Start New Interview", key="start_int"):
            with st.spinner("Starting interview..."):
                resp = api_post("/api/interview/start", json={"company": company})
                if resp:
                    st.session_state.interview_session_id = resp["session_id"]
                    st.session_state.interview_history = []
                    st.session_state.interview_evaluation = None
                    st.session_state.interview_question = None
                    st.success(f"Session started! Company: {company}")

    with col_next:
        if st.session_state.interview_session_id and st.button("➡️ Next Question", key="next_q"):
            with st.spinner("Generating question..."):
                resp = api_post(
                    "/api/interview/next",
                    json={"session_id": st.session_state.interview_session_id, "company": company},
                )
                if resp:
                    if resp.get("action") == "complete":
                        result = resp["result"]
                        st.success("Interview Complete!")
                        st.metric("Overall Score", f"{result.get('overall_score', 0):.0f}/100")
                        col_w, col_s = st.columns(2)
                        with col_w:
                            st.subheader("Weak Areas")
                            for a in (result.get("weak_areas") or []):
                                st.markdown(f"- {a}")
                        with col_s:
                            st.subheader("Strong Areas")
                            for a in (result.get("strong_areas") or []):
                                st.markdown(f"- {a}")
                        st.session_state.interview_session_id = None
                        st.session_state.interview_question = None
                    else:
                        st.session_state.interview_question = resp["question"]
                        st.session_state.interview_question_id = resp["question_id"]
                        st.session_state.interview_stage = resp["stage"]
                        st.session_state.interview_difficulty = resp["difficulty"]
                        st.session_state.interview_evaluation = None

    # Current question
    if st.session_state.interview_question:
        st.markdown("---")
        st.markdown(f"**Question:** {st.session_state.interview_question}")
        user_answer = st.text_area("Your Answer", height=200, key="user_answer_input")

        if st.button("Submit Answer", key="submit_ans"):
            if not user_answer.strip():
                st.warning("Please write an answer before submitting.")
            else:
                with st.spinner("Evaluating your answer..."):
                    resp = api_post(
                        "/api/interview/submit",
                        json={
                            "session_id": st.session_state.interview_session_id,
                            "question_id": st.session_state.interview_question_id,
                            "question": st.session_state.interview_question,
                            "answer": user_answer,
                        },
                    )
                    if resp:
                        st.session_state.interview_evaluation = resp.get("evaluation", {})
                        st.session_state.interview_history.append(
                            {
                                "stage": st.session_state.interview_stage,
                                "question": st.session_state.interview_question,
                                "answer": user_answer,
                                "evaluation": resp.get("evaluation", {}),
                            }
                        )

    # Evaluation result
    ev = st.session_state.interview_evaluation
    if ev:
        st.markdown("---")
        st.subheader("Evaluation")
        overall = ev.get("overall_score", 0)

        col1, col2, col3, col4, col5 = st.columns(5)
        col1.metric("Overall", f"{overall}/100")
        col2.metric("Technical", f"{ev.get('technical_accuracy', 0)}/100")
        col3.metric("Depth", f"{ev.get('depth_of_understanding', 0)}/100")
        col4.metric("Clarity", f"{ev.get('communication_clarity', 0)}/100")
        col5.metric("Problem-Solving", f"{ev.get('problem_solving_approach', 0)}/100")

        st.info(ev.get("feedback", ""))

        weak = ev.get("identified_weak_areas", [])
        strong = ev.get("identified_strong_areas", [])
        if weak or strong:
            col_w, col_s = st.columns(2)
            with col_w:
                if weak:
                    st.markdown("**Weak areas this answer:**")
                    for a in weak:
                        st.markdown(f"- {a}")
            with col_s:
                if strong:
                    st.markdown("**Strong areas this answer:**")
                    for a in strong:
                        st.markdown(f"- {a}")

# ─────────────────────────── TAB 4: PROGRESS ─────────────────────────────────
with tabs[3]:
    st.markdown("<div class='accent'>📊 Progress</div>", unsafe_allow_html=True)

    scores_data = api_get("/history/scores")
    if scores_data:
        df = pd.DataFrame(scores_data)
        df["timestamp"] = pd.to_datetime(df["timestamp"])
        df["score"] = pd.to_numeric(df["score"], errors="coerce").fillna(0)

        st.line_chart(df.set_index("timestamp")["score"])

        # Stage breakdown
        if "stage" in df.columns:
            stage_avg = df.groupby("stage")["score"].mean().reset_index()
            stage_avg.columns = ["Stage", "Avg Score"]
            st.bar_chart(stage_avg.set_index("Stage"))

        st.caption(f"Total questions answered: {len(df)}")
    else:
        st.info("No evaluation data yet. Complete an interview session to see your progress.")

# ─────────────────────────── TAB 5: HISTORY ──────────────────────────────────
with tabs[4]:
    st.markdown("<div class='accent'>📜 Session History</div>", unsafe_allow_html=True)

    # In-session history
    if st.session_state.interview_history:
        st.subheader("Current Session")
        for i, item in enumerate(reversed(st.session_state.interview_history), 1):
            with st.expander(f"Q{i} [{item['stage']}] — Score: {item['evaluation'].get('overall_score', '?')}/100"):
                st.markdown(f"**Question:** {item['question']}")
                st.markdown(f"**Your Answer:** {item['answer']}")
                st.markdown(f"**Feedback:** {item['evaluation'].get('feedback', '')}")

    st.divider()

    # Persistent chat history
    data = api_get("/history/chat")
    if data:
        df = pd.DataFrame(data)
        if "timestamp" in df.columns:
            df["timestamp"] = pd.to_datetime(df["timestamp"])
        for _, row in df.iterrows():
            with st.expander(f"Q: {str(row.get('question', ''))[:80]}"):
                st.markdown(f"**Q:** {row.get('question', '')}")
                st.markdown(f"**A:** {row.get('answer', '')}")
                if "timestamp" in row:
                    st.caption(str(row["timestamp"]))
    elif not st.session_state.interview_history:
        st.info("No history yet.")

# ─────────────────────────── TAB 6: BLOGS ────────────────────────────────────
with tabs[5]:
    st.markdown("<div class='accent'>📰 Company Tech Blogs</div>", unsafe_allow_html=True)
    st.caption(f"Fetches real articles from **{company}**'s engineering blog RSS feed.")

    col_fetch, col_gen = st.columns([1, 1])

    with col_fetch:
        if st.button(f"Fetch Latest {company} Articles", key="fetch_rss"):
            with st.spinner(f"Fetching real articles from {company} RSS..."):
                resp = api_post("/api/blogs/fetch", params={"company": company}, auth=False)
                if resp is not None:
                    fetched = resp.get("fetched", 0)
                    if fetched:
                        st.success(f"Fetched {fetched} new articles!")
                    else:
                        st.info("No new articles found (already up to date or feed unavailable).")

    with col_gen:
        if st.button(f"Generate AI Blog (offline)", key="gen_blog"):
            with st.spinner(f"Generating {company}-focused blog post..."):
                resp = api_get(f"/blog/daily", params={"company": company})
                if resp:
                    st.session_state.latest_blog = resp

    # Blog Q&A
    st.divider()
    st.subheader("Ask About Blog Articles (RAG)")
    blog_q = st.text_input("Ask a question about company tech articles", key="blog_question")
    if st.button("Ask", key="blog_ask_btn"):
        if not blog_q.strip():
            st.warning("Enter a question first.")
        else:
            with st.spinner("Searching articles..."):
                resp = api_post("/api/blogs/ask", json={"question": blog_q}, params={"company": company})
                if resp:
                    st.session_state.blog_answer = resp

    if st.session_state.blog_answer:
        ba = st.session_state.blog_answer
        st.success("Answer (from fetched articles)")
        st.markdown(ba.get("answer", ""))
        sources = [s for s in (ba.get("sources") or []) if s]
        if sources:
            st.caption("Sources: " + " | ".join(sources))

    # Latest generated blog
    if st.session_state.latest_blog:
        st.divider()
        st.markdown(f"## {st.session_state.latest_blog.get('title', '')}")
        st.markdown(st.session_state.latest_blog.get("content", ""))

    # Blog history
    st.divider()
    st.subheader("Recent Articles")
    blogs = api_get("/api/blogs/history", params={"company": company})
    if blogs:
        for blog in blogs[:20]:
            with st.expander(blog.get("title", "Untitled")):
                st.caption(blog.get("created_at", ""))
                st.write(blog.get("content", ""))
    else:
        st.info(f"No articles yet for {company}. Click 'Fetch Latest Articles' to pull from the RSS feed.")
