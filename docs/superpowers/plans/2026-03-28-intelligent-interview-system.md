# Intelligent Multi-Stage Interview System Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Transform the NVIDIA Interview AI Agent into an intelligent multi-stage interview simulator with adaptive difficulty, n8n content automation, and multi-user support

**Architecture:** State machine-based interview orchestrator manages 5 stages (warmup, technical, problem-solving, behavioral, wrap-up). Enhanced agents with session context, JWT authentication for multi-user, n8n webhook integration for automated content ingestion.

**Tech Stack:** FastAPI, SQLAlchemy, JWT (python-jose), ChromaDB, LangChain, Ollama, pytest

**Timeline:** 2 weeks (14 days)

---

## File Structure

### New Backend Files
- `backend/api/middleware.py` - Token validation middleware
- `backend/core/orchestrator.py` - Interview state machine orchestrator
- `backend/core/session_manager.py` - Session state management
- `backend/core/content_manager.py` - n8n integration, content ingestion
- `backend/agents/enhanced_evaluator_agent.py` - Multi-dimensional evaluator
- `backend/core/state_machine.py` - Interview stage definitions and transitions

### Modified Backend Files
- `backend/api/models.py` - Add User, InterviewSession, QuestionResponse, QuestionBank models
- `backend/api/schemas.py` - Add request/response schemas for new endpoints
- `backend/api/main.py` - Add new routes for auth, sessions, content
- `backend/api/auth.py` - Already exists, will be enhanced
- `backend/requirements.txt` - Add python-jose[cryptography], pytest, httpx

### New Test Files
- `backend/tests/__init__.py`
- `backend/tests/test_models.py`
- `backend/tests/test_auth.py`
- `backend/tests/test_middleware.py`
- `backend/tests/test_state_machine.py`
- `backend/tests/test_session_manager.py`
- `backend/tests/test_orchestrator.py`
- `backend/tests/test_content_manager.py`
- `backend/tests/test_enhanced_agents.py`
- `backend/tests/test_api_auth.py`
- `backend/tests/test_e2e_interview.py`

### Modified Frontend Files
- `frontend/ui/app.py` - Add login page, session management, multi-stage UI

### Configuration Files
- `backend/.env.example` - Environment variables template
- `backend/pytest.ini` - Pytest configuration
- `docker-compose.yml` - Update backend environment variables

---

## Implementation Plan

This plan contains 15 tasks broken into phases. Each task follows TDD principles with test-first development.

## Phase 1: Foundation & Authentication (Days 1-2)

**Task 1:** Database Models & Schema
**Task 2:** Interview Session Models  
**Task 3:** Question Models
**Task 4:** JWT Authentication Service
**Task 5:** Authentication Middleware

## Phase 2: Core Interview Engine (Days 3-5)

**Task 6:** Interview State Machine
**Task 7:** Session Manager
**Task 8:** Interview Orchestrator

## Phase 3: Enhanced Agents (Days 6-8)

**Task 9:** Enhanced Evaluator Agent

## Phase 4: n8n Integration & Content Management (Days 9-10)

**Task 10:** Content Manager

## Phase 5: API Endpoints (Days 11-12)

**Task 11:** Authentication Endpoints

## Phase 6: Frontend Updates & Integration (Days 13-14)

**Task 12:** Basic Frontend Auth Integration
**Task 13:** End-to-End Tests
**Task 14:** Update Documentation
**Task 15:** Final Integration & Deployment Prep

---

**Full detailed task steps available in the complete plan document.**

For implementation, I recommend using the **subagent-driven-development** approach for best results.
