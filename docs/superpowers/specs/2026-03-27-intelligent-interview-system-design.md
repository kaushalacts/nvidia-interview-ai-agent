# Intelligent Multi-Stage Interview System - Design Specification

**Date**: 2026-03-27  
**Project**: NVIDIA Interview AI Agent  
**Goal**: Transform simple Q&A system into realistic multi-stage interview simulator with adaptive intelligence, n8n content automation, and multi-user support  
**Timeline**: 2 weeks  
**Target Users**: Small team (5-10 people)

---

## 1. Overview

### Current State
- Agentic AI interview system with RAG architecture
- FastAPI backend + Streamlit UI
- Single-user, basic Q&A flow
- Local LLM (Ollama) + ChromaDB
- Docker-based deployment

### Vision
An intelligent interview simulator that:
- Conducts realistic multi-stage technical interviews
- Adapts difficulty based on performance
- Maintains context across interview rounds
- Integrates with n8n for automated content generation
- Supports team usage with personal tracking
- Provides detailed evaluation and improvement recommendations

---

## 2. Architecture

### High-Level System Design

```
┌─────────────────────────────────────────────────────────┐
│                     Streamlit UI                         │
│  - Login/Registration                                    │
│  - Interview Stages Display                              │
│  - Progress Tracking                                     │
│  - History & Analytics                                   │
│  - Admin Dashboard                                       │
└─────────────────────┬───────────────────────────────────┘
                      │ HTTP/REST
┌─────────────────────▼───────────────────────────────────┐
│                  FastAPI Backend                         │
│                                                          │
│  ┌──────────────────────────────────────────────────┐   │
│  │         Interview Orchestrator (NEW)             │   │
│  │  - State machine for interview stages            │   │
│  │  - Coordinates all agents                        │   │
│  │  - Manages transitions and flow                  │   │
│  └──────────────────────────────────────────────────┘   │
│                                                          │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐  │
│  │ Session      │  │ User Auth    │  │ Content      │  │
│  │ Manager      │  │ Service      │  │ Manager      │  │
│  │ (NEW)        │  │ (NEW)        │  │ (NEW)        │  │
│  └──────────────┘  └──────────────┘  └──────────────┘  │
│                                                          │
│  ┌────────────────────────────────────────────────┐     │
│  │         Enhanced Agent Pool                    │     │
│  │  ┌──────────┐ ┌──────────┐ ┌──────────┐      │     │
│  │  │Interview │ │Question  │ │Evaluator │      │     │
│  │  │Agent     │ │Agent     │ │Agent     │      │     │
│  │  └──────────┘ └──────────┘ └──────────┘      │     │
│  │  ┌──────────┐                                 │     │
│  │  │Planner   │   (All context-aware)           │     │
│  │  │Agent     │                                 │     │
│  │  └──────────┘                                 │     │
│  └────────────────────────────────────────────────┘     │
│                                                          │
└─────────────────────┬───────────────────────────────────┘
                      │
    ┌─────────────────┼─────────────────┬────────────┐
    ▼                 ▼                 ▼            ▼
┌─────────┐    ┌─────────────┐   ┌──────────┐  ┌────────┐
│ SQLite  │    │  ChromaDB   │   │  n8n     │  │ Ollama │
│ (Users, │    │  (RAG +     │   │(Content  │  │ (LLM)  │
│Sessions,│    │  Question   │   │Pipeline) │  └────────┘
│Content) │    │  Embeddings)│   └──────────┘
└─────────┘    └─────────────┘
```

### Component Responsibilities

**Interview Orchestrator** (New Core Component)
- Manages interview state machine
- Coordinates agent invocations based on current stage
- Handles stage transitions
- Enforces interview flow logic
- Provides context to all agents

**Session Manager** (New)
- Tracks active interview sessions
- Persists state for resume capability
- Manages session lifecycle (create, pause, resume, complete)
- Provides session context to agents

**User Auth Service** (New)
- JWT-based authentication
- User registration and login
- Role-based access (admin, user)
- Token validation middleware

**Content Manager** (New)
- API interface for n8n webhooks
- Question ingestion and validation
- Deduplication via embedding similarity
- Quality control and filtering

---

## 3. Multi-Stage Interview Flow

### Interview State Machine

```
IDLE → WARMUP → TECHNICAL_DEEP_DIVE → PROBLEM_SOLVING → BEHAVIORAL → WRAP_UP → COMPLETED
  ↑                                                                                  │
  └──────────────────────────────────────────────────────────────────────────────────┘
                              (Start New Interview)
```

### Stage Definitions

**1. WARMUP (5-7 minutes)**
- Purpose: Establish baseline, build rapport, assess comfort level
- Question types: Introductory, basic technical concepts
- Behavior: Easy questions, encouraging feedback
- Transition: Time-based (5 min) OR 3+ questions answered
- Metrics collected: Response confidence, speed, accuracy

**2. TECHNICAL_DEEP_DIVE (15-20 minutes)**
- Purpose: Core technical assessment on target topics
- Question types: In-depth technical, scenario-based
- Behavior: Adaptive difficulty, follow-up probes based on answers
- Transition: Time-based (15 min) OR quality threshold met
- Metrics collected: Technical depth, weak areas, strong topics

**3. PROBLEM_SOLVING (10-15 minutes)**
- Purpose: Algorithmic thinking, system design
- Question types: Coding challenges, architecture design
- Behavior: Can provide hints if struggling, track approach quality
- Transition: Time-based (10 min) OR problem completed
- Metrics collected: Problem-solving approach, optimization awareness

**4. BEHAVIORAL (5-10 minutes)**
- Purpose: Communication, experience, situational handling
- Question types: Past experience, hypothetical scenarios
- Behavior: Open-ended, evaluates communication clarity
- Transition: Time-based (5 min) OR 2+ questions answered
- Metrics collected: Communication clarity, experience relevance

**5. WRAP_UP (3-5 minutes)**
- Purpose: Summary, feedback, recommendations
- Question types: None (agent provides assessment)
- Behavior: Summarize performance, highlight strengths/weaknesses
- Transition: Automatic to COMPLETED
- Output: Overall score, detailed feedback, study recommendations

### Transition Logic

**Time-Based Transitions**:
- Each stage has minimum time threshold
- Prevents rushing through stages

**Quality-Based Transitions**:
- If performance < 40% in current stage → extend stage, add support questions
- If performance > 80% → can move faster, add bonus/challenge questions
- Stage transition requires minimum questions answered (prevents empty stages)

**Adaptive Difficulty**:
```python
if warmup_score < 40:
    technical_difficulty = 2  # Easy
elif warmup_score < 70:
    technical_difficulty = 3  # Medium
else:
    technical_difficulty = 4  # Hard

# Further adjustments within stage based on ongoing performance
```

---

## 4. Database Schema

### New Tables

**users**
```sql
CREATE TABLE users (
    user_id TEXT PRIMARY KEY,
    email TEXT UNIQUE NOT NULL,
    password_hash TEXT NOT NULL,
    full_name TEXT,
    role TEXT DEFAULT 'user',  -- 'user' or 'admin'
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_login TIMESTAMP
);
```

**interview_sessions**
```sql
CREATE TABLE interview_sessions (
    session_id TEXT PRIMARY KEY,
    user_id TEXT NOT NULL,
    current_stage TEXT NOT NULL,
    stage_start_time TIMESTAMP,
    difficulty_level INTEGER DEFAULT 3,
    weak_areas TEXT,  -- JSON array
    strong_areas TEXT,  -- JSON array
    conversation_history TEXT,  -- JSON array
    overall_score REAL,
    status TEXT DEFAULT 'in_progress',  -- in_progress, completed, abandoned
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    completed_at TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(user_id)
);
```

**question_responses**
```sql
CREATE TABLE question_responses (
    response_id TEXT PRIMARY KEY,
    session_id TEXT NOT NULL,
    question_text TEXT NOT NULL,
    user_answer TEXT NOT NULL,
    evaluation_score REAL,
    evaluation_feedback TEXT,
    technical_accuracy REAL,
    depth_score REAL,
    clarity_score REAL,
    time_taken INTEGER,  -- seconds
    stage TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (session_id) REFERENCES interview_sessions(session_id)
);
```

**question_bank**
```sql
CREATE TABLE question_bank (
    question_id TEXT PRIMARY KEY,
    question_text TEXT NOT NULL,
    expected_answer TEXT,
    topic_tags TEXT,  -- JSON array: ["python", "async"]
    difficulty_level INTEGER,  -- 1-5
    stage_suitable TEXT,  -- warmup, technical, problem_solving, behavioral
    source_url TEXT,
    created_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    usage_count INTEGER DEFAULT 0,
    avg_user_score REAL,
    is_active BOOLEAN DEFAULT 1
);
```

**Existing Tables** (Keep)
- `chat_history` (for backward compatibility)
- ChromaDB collections for embeddings

---

## 5. Enhanced Agent Intelligence

### Interview Agent (Enhanced)

**Input Context**:
```python
{
    "session_id": "uuid",
    "current_stage": "TECHNICAL_DEEP_DIVE",
    "difficulty_level": 3,
    "weak_areas": ["concurrency", "system design"],
    "strong_areas": ["algorithms"],
    "conversation_history": [...],
    "questions_asked_count": 5,
    "time_in_stage": 180  # seconds
}
```

**Responsibilities**:
- Decide next action: ask question / transition stage / provide hint
- Select appropriate question from RAG based on context
- Generate follow-up questions based on user answers
- Detect when user is struggling (offer hints)
- Decide when stage transition is appropriate

**Output**:
```python
{
    "action": "ask_question",  # or "transition_stage", "provide_hint"
    "question": "Explain the difference between...",
    "reasoning": "User showed weakness in concurrency, probing deeper",
    "expected_depth": "detailed"
}
```

### Evaluator Agent (Enhanced)

**Multi-Dimensional Evaluation**:
```python
{
    "technical_accuracy": 85,  # 0-100
    "depth_of_understanding": 70,
    "communication_clarity": 90,
    "problem_solving_approach": 75,
    "overall_score": 80,
    "feedback": "Strong understanding of basics. Consider edge cases...",
    "identified_weak_areas": ["error handling"],
    "identified_strong_areas": ["core concepts"]
}
```

**Context-Aware Scoring**:
- Knows expected difficulty level
- Adjusts expectations based on stage
- Tracks improvement within session

### Question Agent (Enhanced)

**Question Selection Logic**:
```python
1. Filter by stage requirement
2. Filter by difficulty level (±1 from current)
3. Exclude recently asked to this user (last 30 days)
4. Prefer trending topics (if available from n8n)
5. RAG similarity search on weak areas
6. Fallback: LLM generation with template
```

**Follow-Up Generation**:
- Analyzes user's answer
- Identifies gaps or misunderstandings
- Generates targeted follow-up question
- Maintains conversational flow

### Planner Agent (Enhanced)

**Personalized Daily Plans**:
```python
Considers:
- User's weak areas across all sessions
- Recent industry trends (from n8n content)
- Time since last practice in each topic
- Upcoming interview stages user struggles with

Output:
- Prioritized topic list for today
- Recommended practice questions
- Estimated time for each topic
```

---

## 6. n8n Content Automation

### Integration Architecture

**n8n Workflow** (Cofounder manages):
```
Web Scraping → Content Extraction → LLM Question Gen → Quality Check → POST to Backend
```

**Backend API Endpoints**

**POST /api/content/ingest**
```python
Request Body:
{
    "question": "Explain Python's GIL and its implications",
    "expected_answer": "The Global Interpreter Lock...",
    "topic_tags": ["python", "concurrency"],
    "difficulty_level": 3,
    "stage_suitable": "technical",
    "source_url": "https://...",
    "metadata": {
        "source": "hacker_news",
        "date_scraped": "2026-03-27"
    }
}

Response:
{
    "content_id": "uuid",
    "status": "accepted",  # or "rejected" with reason
    "embedding_stored": true
}
```

**POST /api/content/batch-ingest**
```python
Request Body:
{
    "questions": [
        {...},  # up to 50 questions
        {...}
    ]
}

Response:
{
    "job_id": "uuid",
    "accepted_count": 45,
    "rejected_count": 5,
    "rejected_reasons": [...]
}
```

**GET /api/content/trending**
```python
Response:
{
    "trending_topics": ["python", "kubernetes", "LLMs"],
    "recent_questions": [
        {
            "question_id": "uuid",
            "topic": "python",
            "added_date": "2026-03-27"
        }
    ]
}
```

### Content Validation

**Automatic Checks**:
- Non-empty question and answer
- Valid difficulty level (1-5)
- Valid stage assignment
- Topic tags present
- Source URL format valid

**Deduplication**:
- Embed new question
- Check ChromaDB for similar embeddings (cosine similarity > 0.9)
- If duplicate found → reject with reference to existing question

**Quality Scoring** (Post-Usage):
- Track avg_user_score for each question
- Questions with avg_score < 30% flagged for review
- Admin can deactivate low-quality questions

### Content Lifecycle

**Ingestion** → **Active** → **Monitored** → **Archived/Deactivated**

- New questions start active
- Usage tracked (usage_count incremented)
- Quality monitored (avg_user_score)
- Old questions (6+ months, low usage) can be archived

---

## 7. Multi-User Support

### Authentication Flow

**Registration**:
```python
POST /api/auth/register
{
    "email": "user@example.com",
    "password": "secure_password",
    "full_name": "John Doe"
}

Response:
{
    "user_id": "uuid",
    "email": "user@example.com",
    "token": "jwt_token"
}
```

**Login**:
```python
POST /api/auth/login
{
    "email": "user@example.com",
    "password": "secure_password"
}

Response:
{
    "user_id": "uuid",
    "email": "user@example.com",
    "role": "user",
    "token": "jwt_token",
    "expires_in": 604800  # 7 days
}
```

**Token Validation**:
- All protected endpoints require: `Authorization: Bearer <token>`
- Middleware validates JWT and injects user_id into request context
- Invalid/expired tokens → 401 Unauthorized

### User Data Isolation

**Per-User Resources**:
- Interview sessions (user_id foreign key)
- Question responses (via session)
- Daily plans (user_id scoped)
- Progress tracking (user_id scoped)

**Shared Resources**:
- Question bank (all users)
- ChromaDB embeddings (all users)

**Data Access Rules**:
- Users can only access their own sessions and history
- Admins can view aggregate stats (not individual answers unless shared)

### Admin Features

**Team Dashboard** (Admin-only):
```python
GET /api/admin/team-stats

Response:
{
    "total_users": 8,
    "active_users_7d": 6,
    "total_sessions": 45,
    "avg_team_score": 72.5,
    "most_challenging_topics": ["system design", "concurrency"],
    "recent_activity": [...]
}
```

**User Management**:
```python
GET /api/admin/users  # List all users
POST /api/admin/users/{user_id}/deactivate
POST /api/admin/users/{user_id}/make-admin
```

**Content Management**:
```python
GET /api/admin/content/pending  # Review flagged questions
POST /api/admin/content/{question_id}/approve
POST /api/admin/content/{question_id}/deactivate
```

### Streamlit UI Updates

**Login/Registration Page**:
- Email + password form
- "Remember me" checkbox
- Link to registration page
- Password validation

**User Profile Page**:
- Personal stats (sessions completed, avg score, improvement trend)
- Change password
- Export personal data (JSON/CSV)

**Admin Dashboard**:
- Team overview cards
- User list with stats
- Content management interface
- System health metrics

---

## 8. Error Handling & Reliability

### LLM Failure Handling

**Timeouts**:
- Question generation: 30 seconds
- Answer evaluation: 60 seconds
- If exceeded: return cached/fallback response

**Retry Logic**:
```python
@retry(max_attempts=3, backoff=exponential)
def call_ollama(prompt, timeout=30):
    try:
        response = ollama.generate(prompt, timeout=timeout)
        return response
    except TimeoutError:
        logger.warning("Ollama timeout, retrying...")
        raise
    except ConnectionError:
        logger.error("Ollama unavailable")
        raise
```

**Fallback Strategies**:
- Question generation fails → use emergency question pool (100+ curated)
- Evaluation fails → save answer, mark "pending evaluation", retry later
- User sees: "Generating question... taking longer than expected"

### State Recovery

**Auto-Save**:
- Session state saved every 30 seconds
- Conversation history persisted to DB
- Current stage and progress saved

**Resume Capability**:
```python
# On login, check for incomplete sessions
GET /api/sessions/incomplete

# User sees "Resume Interview" button
POST /api/sessions/{session_id}/resume
```

**Session Expiry**:
- Sessions inactive for 2 hours marked "abandoned"
- Can still review in history, but can't resume
- User must start new session

### RAG Retrieval Failures

**No Relevant Questions Found**:
```python
1. Expand search (lower similarity threshold)
2. Broaden topic tags (parent categories)
3. Fall back to LLM generation with template
4. Log missing content area for n8n team
```

**Emergency Question Pool**:
- 100+ curated high-quality questions
- Cover all stages and difficulties
- Manually reviewed and maintained
- Used when RAG and LLM both fail

### n8n Pipeline Issues

**Content Ingestion Failures**:
- Failed ingestions queued for retry (max 3 attempts)
- After 3 failures → email notification to admin
- System continues with existing question bank

**Webhook Downtime**:
- Backend continues operating normally
- Manual upload available via admin UI
- Cofounder notified of webhook failures

### User Experience

**Loading States**:
- "Generating your next question..."
- "Evaluating your answer..."
- Progress bars for long operations

**Error Messages** (User-Friendly):
- ❌ "LLM timeout" → ✅ "Taking longer than expected, please wait..."
- ❌ "DB connection failed" → ✅ "Having trouble saving, retrying..."
- ❌ "RAG retrieval empty" → ✅ "Preparing a question for you..."

**Graceful Degradation**:
- n8n down → use existing questions
- Ollama slow → show waiting message, don't crash
- ChromaDB issues → fall back to SQL query + LLM

---

## 9. Testing Strategy

### Unit Tests (70%+ Coverage Target)

**Agent Logic**:
```python
test_interview_agent.py:
- test_stage_transition_logic()
- test_adaptive_difficulty_adjustment()
- test_question_selection_with_context()
- test_hint_generation()

test_evaluator_agent.py:
- test_multi_dimensional_scoring()
- test_weak_area_identification()
- test_context_aware_evaluation()

test_question_agent.py:
- test_question_filtering_by_stage()
- test_deduplication_logic()
- test_follow_up_generation()
```

**API Endpoints**:
```python
test_auth.py:
- test_user_registration()
- test_login_success_and_failure()
- test_jwt_token_validation()
- test_role_based_access()

test_sessions.py:
- test_session_creation()
- test_session_resume()
- test_session_state_persistence()

test_content.py:
- test_content_ingestion()
- test_duplicate_rejection()
- test_batch_ingestion()
```

### Integration Tests

**End-to-End Interview Flow**:
```python
test_e2e_interview.py:
def test_complete_interview_flow():
    # 1. User logs in
    # 2. Starts new interview
    # 3. Completes all 5 stages
    # 4. Receives evaluation
    # 5. Views history
```

**Multi-User Isolation**:
```python
def test_user_data_isolation():
    user1 = create_user("user1@test.com")
    user2 = create_user("user2@test.com")
    
    session1 = start_interview(user1)
    
    # User2 should not see user1's session
    assert get_sessions(user2) == []
```

**n8n Integration**:
```python
def test_content_ingestion_pipeline():
    payload = create_sample_n8n_payload()
    response = post("/api/content/ingest", payload)
    
    # Verify question stored in DB
    # Verify embedding in ChromaDB
    # Verify question available in RAG
```

### Manual Testing Checklist

**Pre-Deployment**:
- [ ] Complete one full interview as different users
- [ ] Test session resume after disconnect
- [ ] Verify adaptive difficulty changes
- [ ] Test admin dashboard shows correct stats
- [ ] Verify user cannot see other users' data
- [ ] Test n8n webhook with sample payload
- [ ] Verify error handling (disconnect Ollama, test graceful failure)
- [ ] Test on mobile browser (responsive design)

### Testing Tools

- **pytest**: Backend unit and integration tests
- **httpx**: API endpoint testing
- **pytest-mock**: Mocking Ollama responses
- **Selenium/Playwright**: Critical UI flows (optional for time constraints)

### Continuous Testing

- Run tests on every commit (GitHub Actions)
- Block merges if tests fail
- Coverage report generated automatically

---

## 10. Deployment

### Docker Compose (Enhanced)

```yaml
version: "3.9"

networks:
  app_net:

services:
  ollama:
    image: ollama/ollama:latest
    container_name: ollama
    volumes:
      - ollama_data:/root/.ollama
    healthcheck:
      test: ["CMD", "ollama", "list"]
      interval: 30s
      timeout: 10s
      retries: 5
    restart: unless-stopped
    networks:
      - app_net
    deploy:
      resources:
        limits:
          memory: 6g
          cpus: "2"

  backend:
    build: ./backend
    container_name: interview-backend
    volumes:
      - backend_sqlite:/data
      - chroma_data:/app/rag/chroma_db
    environment:
      OLLAMA_HOST: http://ollama:11434
      OLLAMA_MODEL: mistral
      JWT_SECRET: ${JWT_SECRET}  # Set in .env
      DATABASE_PATH: /data/interview_ai.db
    depends_on:
      ollama:
        condition: service_healthy
    healthcheck:
      test: ["CMD", "wget", "-qO-", "http://localhost:8000/health"]
      interval: 30s
      retries: 5
    restart: unless-stopped
    networks:
      - app_net
    ports:
      - "8000:8000"

  ui:
    build: ./frontend
    container_name: interview-ui
    ports:
      - "8501:8501"
    environment:
      API_URL: http://backend:8000
    depends_on:
      backend:
        condition: service_healthy
    restart: unless-stopped
    networks:
      - app_net

  n8n:
    image: n8nio/n8n:latest
    container_name: n8n
    volumes:
      - n8n_data:/home/node/.n8n
    ports:
      - "5678:5678"
    restart: unless-stopped
    networks:
      - app_net

volumes:
  backend_sqlite:
  chroma_data:
  ollama_data:
  n8n_data:
```

### Environment Configuration

**Development** (.env.dev):
```bash
JWT_SECRET=dev_secret_key_change_in_production
OLLAMA_HOST=http://localhost:11434
OLLAMA_MODEL=mistral
DATABASE_PATH=./interview_ai.db
LOG_LEVEL=DEBUG
```

**Production** (.env.prod):
```bash
JWT_SECRET=<strong_random_key>
OLLAMA_HOST=http://ollama:11434
OLLAMA_MODEL=mistral
DATABASE_PATH=/data/interview_ai.db
LOG_LEVEL=INFO
ENABLE_HTTPS=true
```

### Monitoring

**Health Endpoints**:
```python
GET /health → {"status": "ok", "timestamp": "..."}
GET /health/ollama → {"status": "ok", "model": "mistral"}
GET /health/db → {"status": "ok", "connection": "active"}
GET /health/chromadb → {"status": "ok", "collections": 2}
```

**Logging**:
```python
# Structured logging with context
logger.info("Interview started", extra={
    "user_id": "uuid",
    "session_id": "uuid",
    "timestamp": "..."
})

# Error logging with stack traces
logger.error("Ollama timeout", exc_info=True)
```

**Basic Metrics** (Optional):
- Requests per minute
- Average response time per endpoint
- Session completion rate
- Average session duration

**Alerting**:
- Email admin on critical errors
- Slack notification for system health issues (optional)

### Backup Strategy

**Database Backups**:
```bash
# Daily automated backup (cron job)
0 2 * * * /backup-scripts/backup-db.sh

# Keep last 7 daily backups
# Keep last 4 weekly backups
```

**ChromaDB Backups**:
```bash
# Weekly ChromaDB snapshot
0 3 * * 0 /backup-scripts/backup-chromadb.sh
```

**Backup Storage**:
- Local: `/backups/` directory
- External: AWS S3 or equivalent (optional for production)

### Deployment Timeline (2 Weeks)

**Week 1: Development**
- Days 1-2: Backend architecture (orchestrator, session manager, auth)
- Days 3-4: Enhanced agents + state machine
- Days 5-6: n8n integration + content management
- Day 7: Multi-user support + UI updates

**Week 2: Testing & Deployment**
- Days 8-9: Unit tests + integration tests
- Day 10: End-to-end testing
- Day 11: Deploy to staging, team testing
- Day 12: Bug fixes from team feedback
- Day 13: Production deployment
- Day 14: Monitoring + documentation

### Production Checklist

**Before Deployment**:
- [ ] Generate strong JWT_SECRET
- [ ] Set up SSL/TLS (nginx reverse proxy)
- [ ] Configure automatic backups
- [ ] Set up monitoring/alerting
- [ ] Test all health endpoints
- [ ] Verify n8n webhook connectivity
- [ ] Load test with 10 concurrent users

**Post-Deployment**:
- [ ] Monitor logs for errors
- [ ] Verify backups running
- [ ] Test with real team members
- [ ] Document any issues
- [ ] Set up weekly check-ins for first month

---

## 11. Success Metrics

### Technical Metrics
- **System Uptime**: >99% availability
- **Response Time**: <2s for question generation, <5s for evaluation
- **Session Completion Rate**: >70% (users who start complete the interview)
- **Error Rate**: <1% of requests

### User Experience Metrics
- **User Satisfaction**: Collect feedback after each interview
- **Engagement**: Average sessions per user per week
- **Improvement Tracking**: Average score trend over time
- **Content Quality**: Average user rating of questions

### Content Pipeline Metrics
- **Questions Added**: Track weekly n8n ingestion count
- **Question Quality**: Average score per question (>60% target)
- **Content Freshness**: % of questions used from last 30 days

---

## 12. Future Enhancements (Post-2 Weeks)

**Short-Term (1 month)**:
- Voice input/output support
- Mobile app (React Native)
- Advanced analytics dashboard

**Medium-Term (3 months)**:
- Team collaboration features (share sessions, peer review)
- Custom interview templates (per role: SWE, ML Engineer, etc.)
- Integration with calendar for scheduled practice

**Long-Term (6+ months)**:
- Multi-LLM support (OpenAI, Anthropic fallbacks)
- Kubernetes deployment for scaling
- Public API for third-party integrations
- Marketplace for community-contributed questions

---

## 13. Risks & Mitigations

| Risk | Impact | Mitigation |
|------|--------|------------|
| n8n webhook delays content | Medium | Emergency question pool, manual upload |
| Ollama slow/crashes | High | Retry logic, fallback questions, health monitoring |
| 2-week timeline too aggressive | High | Prioritize core features, defer nice-to-haves |
| User adoption low | Medium | User onboarding, feedback sessions, iterative improvements |
| SQLite concurrency issues (10+ users) | Low | Monitor performance, migrate to PostgreSQL if needed |

---

## 14. Open Questions

1. **LLM Model Choice**: Continue with Mistral or test Llama3.1 for better quality?
2. **Admin Approval**: Should new n8n questions require admin approval before going live?
3. **Scoring Algorithm**: Linear scoring or weighted by stage importance?
4. **Session Length**: Should there be a maximum interview duration (e.g., 60 minutes)?

---

## Conclusion

This design transforms the NVIDIA Interview AI Agent from a simple Q&A system into an intelligent, multi-stage interview simulator. Key innovations:

1. **Stateful interview flow** with realistic stage progression
2. **Adaptive intelligence** that adjusts to user performance
3. **n8n integration** for automated, fresh content
4. **Multi-user support** for team deployment
5. **Robust error handling** for production reliability

The design balances ambition with the 2-week timeline by focusing on core features and deferring nice-to-haves. All components are designed for maintainability and future extensibility.

**Next Step**: Implementation planning with detailed task breakdown.
