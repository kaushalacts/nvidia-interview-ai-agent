# Setup Guide

Complete step-by-step setup instructions for NVIDIA Interview AI Agent.

---

## Prerequisites

Choose one of the following:

### Option 1: Docker Compose (Recommended)
- Docker (version 20.10+)
- Docker Compose (version 1.29+)
- 6GB RAM available
- 2+ CPU cores

### Option 2: Local Development
- Python 3.9 or higher
- Ollama (for local LLM)
- Node.js 18+ (for frontend)
- SQLite (included with Python)
- 8GB RAM available
- 4+ CPU cores

---

## Option 1: Docker Compose Setup (Recommended)

### Step 1: Clone Repository

```bash
git clone https://github.com/kaushalacts/nvidia-interview-ai-agent.git
cd nvidia-interview-ai-agent
```

### Step 2: Configure Environment

```bash
cp backend/.env.example backend/.env
```

Edit `backend/.env` and update if needed:

```env
JWT_SECRET=your-secret-key-change-in-production-min-32-chars
OLLAMA_HOST=http://ollama:11434
OLLAMA_MODEL=mistral
DATABASE_PATH=./interview_ai.db
LOG_LEVEL=INFO
```

**Security Note:** Change `JWT_SECRET` to a unique value (minimum 32 characters) for production.

### Step 3: Start Services

```bash
docker-compose up -d
```

This starts:
- **Ollama** (LLM) on internal network
- **Backend** (FastAPI) on internal network
- **Frontend** (Streamlit) on `http://localhost:8501`
- **n8n** (content automation) on `http://localhost:5678`

### Step 4: Wait for Services

Check service health:

```bash
docker-compose ps
```

Wait 30-60 seconds for Ollama to download the model. Monitor:

```bash
docker-compose logs ollama
```

### Step 5: Access Services

- **Frontend UI:** http://localhost:8501
- **Backend API:** http://localhost:8000
- **API Docs:** http://localhost:8000/docs
- **n8n UI:** http://localhost:5678 (optional)

### Step 6: Register First User

In Streamlit UI:
1. Click "Register"
2. Enter email and password
3. Enter full name
4. Submit

Or via API:

```bash
curl -X POST http://localhost:8000/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "email": "user@example.com",
    "password": "securepass123",
    "full_name": "John Doe"
  }'
```

---

## Option 2: Local Development Setup

### Step 1: Clone Repository

```bash
git clone https://github.com/kaushalacts/nvidia-interview-ai-agent.git
cd nvidia-interview-ai-agent
```

### Step 2: Start Ollama

**Install Ollama:** https://ollama.ai

```bash
# In a new terminal
ollama pull mistral
ollama serve
```

Keep this terminal open. Ollama runs on `http://localhost:11434`

### Step 3: Setup Backend

```bash
cd backend

# Create virtual environment
python3 -m venv venv

# Activate virtual environment
# On Windows:
venv\Scripts\activate
# On macOS/Linux:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Create .env file
cp .env.example .env

# Initialize database
python3 -c "from api.database import engine; from api import models; models.Base.metadata.create_all(bind=engine)"

# Start backend
uvicorn api.main:app --reload --host 0.0.0.0 --port 8000
```

Backend runs on `http://localhost:8000`

### Step 4: Setup Frontend

In a new terminal:

```bash
cd frontend

# Create virtual environment
python3 -m venv venv

# Activate virtual environment
# On Windows:
venv\Scripts\activate
# On macOS/Linux:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Start frontend
streamlit run ui/app.py
```

Frontend runs on `http://localhost:8501`

### Step 5: Configure API Connection

Edit `frontend/ui/app.py` and set:

```python
API_URL = "http://localhost:8000"
```

### Step 6: Access Application

Open browser to `http://localhost:8501`

---

## Configuration

### Environment Variables

**Backend (.env)**

| Variable | Description | Default |
|----------|-------------|---------|
| `JWT_SECRET` | Secret key for JWT tokens (min 32 chars) | dev-secret |
| `OLLAMA_HOST` | Ollama API URL | http://localhost:11434 |
| `OLLAMA_MODEL` | Model to use | mistral |
| `DATABASE_PATH` | SQLite database path | ./interview_ai.db |
| `LOG_LEVEL` | Logging level | INFO |
| `CONTENT_WEBHOOK_TOKEN` | Token for n8n webhook | (optional) |

### Database

Database is automatically initialized on first run. To reset:

```bash
# Docker
docker-compose down -v

# Or locally
rm interview_ai.db
```

### Ollama Models

Available models (alternatives to mistral):
- `mistral` - Fast, good balance (default)
- `llama2` - Larger, more capable
- `neural-chat` - Optimized for dialogue

Pull alternative:

```bash
ollama pull llama2
```

Update `.env`:

```env
OLLAMA_MODEL=llama2
```

---

## Verification

### 1. Health Check

```bash
curl http://localhost:8000/health
```

Expected response:
```json
{"status": "ok"}
```

### 2. Register Test User

```bash
curl -X POST http://localhost:8000/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "password": "testpass123",
    "full_name": "Test User"
  }'
```

Expected response:
```json
{
  "user_id": "...",
  "email": "test@example.com",
  "token": "..."
}
```

### 3. Login Test

```bash
curl -X POST http://localhost:8000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "password": "testpass123"
  }'
```

### 4. Start Interview

```bash
curl -X POST http://localhost:8000/api/interview/plan \
  -H "Authorization: Bearer <token-from-login>" \
  -H "Content-Type: application/json" \
  -d '{"difficulty_level": 3}'
```

---

## Troubleshooting

### Ollama Connection Fails

**Problem:** Backend cannot reach Ollama

**Solution:**
- Docker: Ensure `OLLAMA_HOST=http://ollama:11434`
- Local: Ensure Ollama is running (`ollama serve`)
- Check: `curl http://localhost:11434/api/tags` (local) or `curl http://ollama:11434/api/tags` (Docker)

### Database Locked

**Problem:** "Database is locked"

**Solution:**
```bash
# Docker
docker-compose restart backend

# Local
Kill the backend process and restart
```

### Token Errors

**Problem:** "Invalid token" or 401 errors

**Solution:**
- Ensure JWT_SECRET is same on startup
- Tokens expire after 7 days, re-login
- Include "Bearer " prefix: `Authorization: Bearer <token>`

### Port Already in Use

**Problem:** Port 8000, 8501, or 11434 in use

**Solution:**
```bash
# Docker: Change docker-compose.yml ports
# Local: Change uvicorn/streamlit port

# Find process on port (macOS/Linux)
lsof -i :8000

# Kill process
kill -9 <PID>
```

### Out of Memory

**Problem:** Services crash with memory errors

**Solution:**
- Docker: Increase memory in docker-compose.yml
- Local: Ensure 8GB+ available RAM
- Restart services to free memory

---

## Advanced Configuration

### Custom LLM Prompts

Edit `backend/agents/` files to customize:
- Question generation
- Answer evaluation
- Interview analysis

### Database Backup

```bash
# Local
cp interview_ai.db interview_ai.db.backup

# Docker
docker-compose exec backend cp /data/interview_ai.db /data/interview_ai.db.backup
```

### Enable Debug Logging

Update `.env`:

```env
LOG_LEVEL=DEBUG
```

### SSL/HTTPS for Production

Use reverse proxy (nginx, Caddy) to:
- Terminate SSL
- Forward to backend on http://backend:8000
- Forward to frontend on http://frontend:8501

---

## Next Steps

1. **Start Interview:** See [API.md](API.md) for endpoints
2. **Run Tests:** See [TESTING.md](TESTING.md)
3. **Customize:** Edit agents and prompts in `backend/agents/`
4. **Deploy:** Use Docker Compose in production environment

---

## Support

- **Documentation:** See [docs/](../) directory
- **API Reference:** See [API.md](API.md)
- **Testing:** See [TESTING.md](TESTING.md)
- **Issues:** File GitHub issues with reproduction steps
