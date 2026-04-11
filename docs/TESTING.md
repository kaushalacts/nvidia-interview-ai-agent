# Testing Guide

Overview of testing practices and how to run tests for NVIDIA Interview AI Agent.

---

## Test Overview

The project uses **pytest** as the testing framework with comprehensive coverage across:
- **Unit Tests** - Individual functions and classes
- **Integration Tests** - Component interactions
- **End-to-End Tests** - Complete interview workflows

---

## Quick Start

### Run All Tests

```bash
cd backend
pytest tests/ -v
```

### Run with Coverage

```bash
pytest tests/ --cov=. --cov-report=html
```

This generates an HTML coverage report in `htmlcov/index.html`

### Run Specific Test File

```bash
pytest tests/test_auth.py -v
```

### Run Specific Test

```bash
pytest tests/test_auth.py::test_register_user -v
```

---

## Test Structure

```
backend/tests/
├── conftest.py                  # Shared fixtures and setup
├── test_api_auth.py             # API authentication tests
├── test_auth.py                 # Auth utility tests
├── test_content_manager.py      # Content ingestion tests
├── test_e2e_interview.py        # End-to-end interview flow
├── test_enhanced_evaluator.py   # Evaluation logic tests
├── test_middleware.py           # Middleware tests
├── test_models.py               # Database model tests
├── test_orchestrator.py         # Orchestrator tests
├── test_session_manager.py      # Session management tests
├── test_state_machine.py        # State machine tests
└── __init__.py
```

---

## Test Categories

### Unit Tests

Test individual functions and components in isolation.

**Examples:**
- `test_auth.py` - Password hashing, token creation
- `test_state_machine.py` - Stage transitions, difficulty adjustment
- `test_session_manager.py` - Session CRUD operations

**Run:**
```bash
pytest tests/test_auth.py tests/test_state_machine.py -v
```

### Integration Tests

Test how components work together.

**Examples:**
- `test_orchestrator.py` - Orchestrator with session manager
- `test_enhanced_evaluator.py` - Evaluation with scoring
- `test_content_manager.py` - Content ingestion flow

**Run:**
```bash
pytest tests/test_orchestrator.py tests/test_enhanced_evaluator.py -v
```

### End-to-End Tests

Test complete user workflows.

**Examples:**
- `test_e2e_interview.py` - Full interview session from start to finish

**Run:**
```bash
pytest tests/test_e2e_interview.py -v
```

---

## Key Test Files

### conftest.py

Shared test configuration and fixtures.

**Fixtures:**
- `db_session` - SQLite test database
- `test_client` - FastAPI test client
- `sample_user` - Test user account
- `auth_token` - Valid JWT token

**Usage:**
```python
def test_something(db_session, test_client, auth_token):
    # Test implementation
    pass
```

### test_auth.py

Tests authentication utilities.

**Tests:**
- `test_hash_password` - Password hashing
- `test_verify_password` - Password verification
- `test_create_access_token` - JWT token creation
- `test_verify_token` - Token verification
- `test_verify_token_invalid` - Invalid token handling

### test_api_auth.py

Tests authentication API endpoints.

**Tests:**
- `test_register_user` - User registration
- `test_register_duplicate_email` - Duplicate email handling
- `test_login_user` - User login
- `test_login_invalid_password` - Invalid password handling
- `test_login_nonexistent_user` - Non-existent user handling

### test_state_machine.py

Tests interview state machine.

**Tests:**
- `test_get_next_stage` - Stage progression
- `test_can_transition` - Transition conditions
- `test_adjust_difficulty_score_high` - Difficulty increase
- `test_adjust_difficulty_score_low` - Difficulty decrease
- `test_stage_requirements` - Stage validation

**Key Validations:**
- Stage order: WARMUP → TECHNICAL_DEEP_DIVE → PROBLEM_SOLVING → BEHAVIORAL → WRAP_UP
- Transition requirements: time, questions, score
- Difficulty adjustment: 1-5 scale

### test_orchestrator.py

Tests interview orchestration.

**Tests:**
- `test_start_interview` - Session creation
- `test_get_next_action_ask_question` - Question asking
- `test_should_transition_stage` - Stage readiness
- `test_transition_to_next_stage` - Stage transitions
- `test_record_response` - Answer recording
- `test_complete_interview` - Interview completion

### test_e2e_interview.py

Complete end-to-end interview test.

**Flow:**
1. Register user
2. Login and get token
3. Start interview
4. Get question
5. Submit answer and get evaluation
6. Complete interview
7. Verify final scores

**Run:**
```bash
pytest tests/test_e2e_interview.py -v -s
```

---

## Running Tests with Options

### Verbose Output

```bash
pytest tests/ -v
```

### Show Print Statements

```bash
pytest tests/ -v -s
```

### Stop on First Failure

```bash
pytest tests/ -x
```

### Run Tests Matching Pattern

```bash
pytest tests/ -k "auth" -v
```

### Run Tests with Specific Marker

```bash
pytest tests/ -m "integration" -v
```

### Generate Coverage Report

```bash
pytest tests/ --cov=. --cov-report=html --cov-report=term-missing
```

---

## Test Coverage

Current coverage targets:

| Module | Target |
|--------|--------|
| `api/` | 80%+ |
| `core/` | 90%+ |
| `agents/` | 70%+ |
| `rag/` | 75%+ |

**View Coverage:**
```bash
pytest tests/ --cov=. --cov-report=html
open htmlcov/index.html
```

---

## Writing New Tests

### Test Template

```python
import pytest
from api.models import User
from api.auth import hash_password

def test_new_feature(db_session, test_client):
    """Descriptive test name"""
    # Arrange - Setup test data
    user = User(email="test@example.com")
    db_session.add(user)
    db_session.commit()
    
    # Act - Execute the feature
    result = do_something(user)
    
    # Assert - Verify results
    assert result is not None
    assert result.status == "success"
```

### Using Fixtures

```python
def test_with_auth_token(test_client, auth_token):
    """Test requiring authentication"""
    response = test_client.get(
        "/api/interview/session",
        headers={"Authorization": f"Bearer {auth_token}"}
    )
    assert response.status_code == 200
```

### Database Tests

```python
def test_database_transaction(db_session):
    """Test database operations"""
    # Changes are rolled back after test
    user = User(email="new@example.com")
    db_session.add(user)
    db_session.commit()
    
    assert db_session.query(User).count() >= 1
```

### Parametrized Tests

```python
@pytest.mark.parametrize("difficulty,expected", [
    (1, 1),
    (3, 3),
    (5, 5),
])
def test_difficulty_levels(difficulty, expected):
    """Test multiple difficulty levels"""
    assert validate_difficulty(difficulty) == expected
```

---

## Common Test Patterns

### Testing API Endpoints

```python
def test_api_endpoint(test_client, auth_token):
    response = test_client.post(
        "/api/interview/plan",
        headers={"Authorization": f"Bearer {auth_token}"},
        json={"difficulty_level": 3}
    )
    assert response.status_code == 201
    data = response.json()
    assert "session_id" in data
```

### Testing Error Handling

```python
def test_error_handling(test_client):
    response = test_client.post(
        "/api/auth/register",
        json={
            "email": "invalid-email",  # Invalid email
            "password": "pass"
        }
    )
    assert response.status_code == 422
    assert "email" in response.json()["detail"][0]["loc"]
```

### Testing State Transitions

```python
def test_state_transition(db_session):
    # Create initial state
    session = create_session(db_session, "warmup")
    
    # Transition to next state
    session.current_stage = "technical_deep_dive"
    db_session.commit()
    
    # Verify new state
    assert session.current_stage == "technical_deep_dive"
```

---

## Continuous Integration

The project uses GitHub Actions for CI/CD.

**Test Runs On:**
- Pull requests
- Commits to main/develop
- Manual trigger

**Pipeline:**
1. Checkout code
2. Setup Python environment
3. Install dependencies
4. Run linting (if configured)
5. Run tests with coverage
6. Report results

---

## Performance Testing

### Test Execution Time

```bash
pytest tests/ --durations=10
```

This shows the 10 slowest tests.

### Load Testing (Future)

Consider adding:
- Locust for load testing
- Performance benchmarks
- Memory profiling

---

## Mock and Patch Examples

### Mocking External Services

```python
from unittest.mock import patch, MagicMock

@patch('agents.llm.generate_question')
def test_question_generation(mock_generate):
    mock_generate.return_value = "Sample question?"
    
    question = get_next_question()
    assert question == "Sample question?"
    mock_generate.assert_called_once()
```

### Mocking Database

```python
@patch('api.database.SessionLocal')
def test_with_mock_db(mock_session):
    mock_db = MagicMock()
    mock_session.return_value = mock_db
    
    # Test code using mock database
    pass
```

---

## Debugging Tests

### Verbose Output with Stacktrace

```bash
pytest tests/ -vv --tb=long
```

### Interactive Debugging

```bash
pytest tests/test_auth.py --pdb
```

This drops into debugger on failure.

### Capture Print Statements

```bash
pytest tests/test_auth.py -v -s --capture=no
```

---

## Troubleshooting

### Import Errors

**Problem:** `ModuleNotFoundError: No module named 'api'`

**Solution:**
```bash
cd backend
export PYTHONPATH=$PYTHONPATH:$(pwd)
pytest tests/
```

### Database Lock

**Problem:** Tests fail with "database locked"

**Solution:**
- Ensure test isolation with fixtures
- Check for uncommitted transactions
- Use in-memory SQLite for tests

### Flaky Tests

**Problem:** Tests pass/fail intermittently

**Solution:**
- Check for timing dependencies
- Avoid hardcoded waits
- Use proper test fixtures

### Fixture Errors

**Problem:** `fixture 'auth_token' not found`

**Solution:**
- Ensure conftest.py is in tests directory
- Check fixture naming matches parameter names
- Verify conftest.py is being loaded

---

## Best Practices

1. **Test One Thing**: Each test should verify one behavior
2. **Use Descriptive Names**: Test name should describe what it tests
3. **Isolate Tests**: Tests should not depend on other tests
4. **Clean Up**: Use fixtures for setup/teardown
5. **Mock External Calls**: Don't make real network calls
6. **Test Both Success and Failure**: Include error cases
7. **Keep Tests Fast**: Aim for < 1s per test
8. **Use Parametrization**: For testing multiple inputs
9. **Document Complex Tests**: Add comments for tricky logic
10. **Maintain High Coverage**: Aim for 80%+ code coverage

---

## Additional Resources

- **Pytest Documentation**: https://docs.pytest.org/
- **Testing Best Practices**: https://docs.python-guide.org/writing/tests/
- **Fixtures Guide**: https://docs.pytest.org/en/latest/how-to/fixtures.html
- **Mocking Guide**: https://docs.python.org/3/library/unittest.mock.html

---

## Running Tests in CI/CD

See `.github/workflows/` for CI configuration.

To run locally like CI:

```bash
# Install test dependencies
pip install -r requirements.txt

# Run full test suite with coverage
pytest tests/ --cov=. --cov-report=xml --cov-report=term-missing

# Check for lint issues (if configured)
flake8 . --count --statistics
```
