# API Documentation

Complete reference for all NVIDIA Interview AI Agent endpoints.

---

## Base URL

```
http://localhost:8000
```

For Docker deployment:
```
http://backend:8000
```

---

## Authentication

All protected endpoints require JWT token in the `Authorization` header:

```
Authorization: Bearer <jwt-token>
```

Tokens are valid for **7 days** from issue.

---

## Health Check

### GET /health

Check if backend is running.

**Response:**
```json
{
  "status": "ok"
}
```

**Status Code:** `200`

---

## Authentication Endpoints

### POST /api/auth/register

Register a new user account.

**Request:**
```json
{
  "email": "user@example.com",
  "password": "securepassword123",
  "full_name": "John Doe"
}
```

**Response (201 Created):**
```json
{
  "user_id": "550e8400-e29b-41d4-a716-446655440000",
  "email": "user@example.com",
  "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
}
```

**Error (400):**
```json
{
  "detail": "Email already registered"
}
```

**Constraints:**
- Email must be valid and unique
- Password minimum 8 characters recommended
- Full name required

---

### POST /api/auth/login

Authenticate and get JWT token.

**Request:**
```json
{
  "email": "user@example.com",
  "password": "securepassword123"
}
```

**Response (200 OK):**
```json
{
  "user_id": "550e8400-e29b-41d4-a716-446655440000",
  "email": "user@example.com",
  "role": "user",
  "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "expires_in": 604800
}
```

**Error (401):**
```json
{
  "detail": "Invalid email or password"
}
```

**Notes:**
- `expires_in` is in seconds (604800 = 7 days)
- Token must be included in `Authorization` header for protected endpoints
- Last login timestamp is updated on successful authentication

---

## Interview Endpoints

### POST /api/interview/plan

Start a new interview session and create an interview plan.

**Headers:**
```
Authorization: Bearer <jwt-token>
Content-Type: application/json
```

**Request:**
```json
{
  "difficulty_level": 3,
  "focus_area": "System Design"
}
```

**Response (201 Created):**
```json
{
  "session_id": "session-550e8400-e29b-41d4-a716-446655440000",
  "user_id": "550e8400-e29b-41d4-a716-446655440000",
  "current_stage": "WARMUP",
  "difficulty_level": 3,
  "status": "active",
  "plan": {
    "focus_area": "System Design",
    "topic": "Distributed Systems Fundamentals",
    "estimated_duration": "45 minutes",
    "objectives": [
      "Understand CAP theorem",
      "Learn consistency models",
      "Practice load balancing concepts"
    ]
  }
}
```

**Interview Stages:**
1. **WARMUP** - Introduction and baseline (2+ questions, 5 min minimum)
2. **TECHNICAL_DEEP_DIVE** - Core technical assessment (3+ questions, 15 min minimum)
3. **PROBLEM_SOLVING** - Algorithm and system design (2+ questions, 10 min minimum)
4. **BEHAVIORAL** - Communication and experience (2+ questions, 5 min minimum)
5. **WRAP_UP** - Final evaluation and feedback

**Difficulty Levels:** 1-5 (1=Easy, 5=Expert)

---

### GET /api/interview/question

Get the next interview question for current stage.

**Headers:**
```
Authorization: Bearer <jwt-token>
```

**Query Parameters:**
- `session_id` (required): Interview session ID

**Response (200 OK):**
```json
{
  "question_id": "q-550e8400-e29b-41d4-a716-446655440000",
  "question_text": "Explain how load balancing works in distributed systems. What are the key challenges?",
  "stage": "TECHNICAL_DEEP_DIVE",
  "difficulty": 3,
  "time_limit": 300,
  "hints": [
    "Consider consistency requirements",
    "Think about failure scenarios"
  ]
}
```

**Notes:**
- Questions are generated based on current stage and difficulty
- `time_limit` is in seconds
- Hints are optional suggestions for the candidate

---

### POST /api/interview/evaluate

Submit answer and receive evaluation.

**Headers:**
```
Authorization: Bearer <jwt-token>
Content-Type: application/json
```

**Request:**
```json
{
  "session_id": "session-550e8400-e29b-41d4-a716-446655440000",
  "question_id": "q-550e8400-e29b-41d4-a716-446655440000",
  "answer": "Load balancing distributes incoming requests across multiple servers to improve performance. Key challenges include handling server failures, maintaining session consistency, and choosing appropriate load distribution algorithms like round-robin or least connections.",
  "time_taken": 120
}
```

**Response (200 OK):**
```json
{
  "response_id": "r-550e8400-e29b-41d4-a716-446655440000",
  "question_id": "q-550e8400-e29b-41d4-a716-446655440000",
  "stage": "TECHNICAL_DEEP_DIVE",
  "evaluation": {
    "overall_score": 75,
    "technical_accuracy": 80,
    "depth_of_understanding": 70,
    "communication_clarity": 75,
    "problem_solving_approach": 75,
    "feedback": "Good understanding of the basics. Consider discussing specific algorithms and fault tolerance strategies in more detail.",
    "identified_weak_areas": [
      "Consistency models",
      "Failure detection"
    ],
    "identified_strong_areas": [
      "Load distribution concepts",
      "High-level architecture thinking"
    ]
  },
  "next_action": "ask_question",
  "stage_progress": {
    "questions_in_stage": 1,
    "average_score": 75,
    "time_in_stage": 120
  }
}
```

**Scoring Metrics:**
- **Overall Score** (0-100): Composite evaluation
- **Technical Accuracy** (0-100): Correctness of content
- **Depth of Understanding** (0-100): Conceptual mastery
- **Communication Clarity** (0-100): Articulation quality
- **Problem-Solving Approach** (0-100): Methodology and logic

**Next Actions:**
- `"ask_question"` - Continue with another question in current stage
- `"transition_stage"` - Move to next interview stage
- `"complete_interview"` - Interview is complete

---

### GET /api/interview/session

Get current session context and progress.

**Headers:**
```
Authorization: Bearer <jwt-token>
```

**Query Parameters:**
- `session_id` (required): Interview session ID

**Response (200 OK):**
```json
{
  "session_id": "session-550e8400-e29b-41d4-a716-446655440000",
  "user_id": "550e8400-e29b-41d4-a716-446655440000",
  "current_stage": "TECHNICAL_DEEP_DIVE",
  "difficulty_level": 3,
  "status": "active",
  "overall_progress": {
    "total_questions_answered": 5,
    "overall_score": 72,
    "time_elapsed": 480
  },
  "stage_progress": {
    "stage": "TECHNICAL_DEEP_DIVE",
    "questions_in_stage": 2,
    "average_score": 75,
    "time_in_stage": 240,
    "can_transition": false,
    "transition_reason": "Minimum questions requirement not met"
  },
  "weak_areas": [
    "Consistency models",
    "Failure detection",
    "Network protocols"
  ],
  "strong_areas": [
    "Architecture thinking",
    "Load balancing concepts",
    "High-level design"
  ],
  "conversation_history": [
    {
      "question": "Explain how load balancing works...",
      "answer": "Load balancing distributes...",
      "score": 75
    }
  ]
}
```

**Status Values:**
- `"active"` - Interview in progress
- `"completed"` - Interview finished
- `"paused"` - Interview temporarily paused

---

### POST /api/interview/complete

Complete current interview session and get final evaluation.

**Headers:**
```
Authorization: Bearer <jwt-token>
```

**Request:**
```json
{
  "session_id": "session-550e8400-e29b-41d4-a716-446655440000"
}
```

**Response (200 OK):**
```json
{
  "session_id": "session-550e8400-e29b-41d4-a716-446655440000",
  "overall_score": 72,
  "total_questions": 8,
  "stage_scores": {
    "WARMUP": 85,
    "TECHNICAL_DEEP_DIVE": 75,
    "PROBLEM_SOLVING": 68,
    "BEHAVIORAL": 70,
    "WRAP_UP": 72
  },
  "weak_areas": [
    "Consistency models",
    "Failure detection",
    "Network protocols"
  ],
  "strong_areas": [
    "Architecture thinking",
    "Load balancing concepts",
    "Communication"
  ],
  "recommendations": [
    "Study consistency models (CAP, PACELC)",
    "Practice system design with fault tolerance",
    "Review distributed consensus algorithms"
  ],
  "duration": 1440,
  "timestamp": "2024-01-15T14:30:00Z"
}
```

---

## Content Endpoints

### POST /api/content/ingest

Ingest question content from n8n webhook.

**Headers:**
```
Content-Type: application/json
```

**Request:**
```json
{
  "webhook_token": "secure-webhook-token",
  "content": {
    "question_text": "Explain the difference between Process and Thread",
    "topic": "Operating Systems",
    "difficulty": 2,
    "category": "fundamentals",
    "tags": ["concurrency", "systems"]
  }
}
```

**Response (201 Created):**
```json
{
  "content_id": "content-550e8400-e29b-41d4-a716-446655440000",
  "status": "ingested",
  "message": "Content successfully added to knowledge base"
}
```

**Error (401):**
```json
{
  "detail": "Invalid webhook token"
}
```

**Notes:**
- Webhook token must match configured `CONTENT_WEBHOOK_TOKEN`
- Content is embedded and stored in ChromaDB
- Automatically available for future interviews

---

## Error Handling

### Standard Error Response

```json
{
  "detail": "Error message describing what went wrong"
}
```

### Common HTTP Status Codes

| Code | Meaning |
|------|---------|
| 200 | Success |
| 201 | Resource created |
| 400 | Bad request (validation error) |
| 401 | Unauthorized (invalid/missing token) |
| 403 | Forbidden (insufficient permissions) |
| 404 | Not found |
| 422 | Unprocessable entity (invalid data) |
| 500 | Server error |

---

## Rate Limiting

No rate limiting currently implemented in MVP.

---

## Pagination

List endpoints support pagination:

**Query Parameters:**
- `skip` (default: 0): Number of records to skip
- `limit` (default: 10): Number of records to return

**Response:**
```json
{
  "items": [...],
  "total": 150,
  "skip": 0,
  "limit": 10
}
```

---

## Examples

### Complete Interview Flow

```bash
# 1. Register
curl -X POST http://localhost:8000/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "email": "user@example.com",
    "password": "securepass123",
    "full_name": "John Doe"
  }'

# Response: { "token": "...", "user_id": "..." }

# 2. Start interview
curl -X POST http://localhost:8000/api/interview/plan \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{"difficulty_level": 3}'

# Response: { "session_id": "...", "current_stage": "WARMUP" }

# 3. Get question
curl -X GET "http://localhost:8000/api/interview/question?session_id=<session_id>" \
  -H "Authorization: Bearer <token>"

# Response: { "question_id": "...", "question_text": "..." }

# 4. Submit answer
curl -X POST http://localhost:8000/api/interview/evaluate \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{
    "session_id": "<session_id>",
    "question_id": "<question_id>",
    "answer": "Your answer here...",
    "time_taken": 120
  }'

# Response: { "evaluation": {...}, "next_action": "..." }

# 5. Complete interview
curl -X POST http://localhost:8000/api/interview/complete \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{"session_id": "<session_id>"}'

# Response: { "overall_score": 72, "recommendations": [...] }
```

---

## Webhook Configuration

To enable n8n content ingestion:

1. Generate a secure webhook token
2. Set `CONTENT_WEBHOOK_TOKEN` environment variable
3. Configure n8n webhook to POST to `/api/content/ingest`
4. Include token in request body

---

## Future Enhancements

- [ ] OpenAPI/Swagger documentation endpoint
- [ ] GraphQL API layer
- [ ] WebSocket real-time updates
- [ ] Advanced filtering and search
- [ ] Batch operations
- [ ] Import/export history
- [ ] Admin endpoints for analytics
