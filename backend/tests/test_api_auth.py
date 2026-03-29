import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from api.main import app, get_db
from api.models import Base, User
from api.auth import verify_token
from datetime import datetime


# In-memory SQLite database for testing
SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"
engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def override_get_db():
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()


app.dependency_overrides[get_db] = override_get_db
client = TestClient(app)


@pytest.fixture(autouse=True)
def setup_database():
    """Create tables before each test and drop after"""
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)


def test_register_new_user():
    """Test successful user registration"""
    response = client.post(
        "/api/auth/register",
        json={
            "email": "newuser@example.com",
            "password": "secure_password123",
            "full_name": "John Doe"
        }
    )
    
    assert response.status_code == 201
    data = response.json()
    
    assert "user_id" in data
    assert data["email"] == "newuser@example.com"
    assert "token" in data
    assert len(data["user_id"]) == 36  # UUID format
    
    # Verify user was created in database
    db = TestingSessionLocal()
    user = db.query(User).filter(User.email == "newuser@example.com").first()
    assert user is not None
    assert user.full_name == "John Doe"
    assert user.role == "user"
    db.close()


def test_register_duplicate_email():
    """Test registration with duplicate email returns 400"""
    # Register first user
    client.post(
        "/api/auth/register",
        json={
            "email": "duplicate@example.com",
            "password": "password123",
            "full_name": "First User"
        }
    )
    
    # Try to register with same email
    response = client.post(
        "/api/auth/register",
        json={
            "email": "duplicate@example.com",
            "password": "different_password",
            "full_name": "Second User"
        }
    )
    
    assert response.status_code == 400
    assert response.json()["detail"] == "Email already registered"


def test_register_invalid_email():
    """Test registration with invalid email format returns 422"""
    response = client.post(
        "/api/auth/register",
        json={
            "email": "not-an-email",
            "password": "password123",
            "full_name": "John Doe"
        }
    )
    
    assert response.status_code == 422  # Pydantic validation error


def test_login_valid_credentials():
    """Test successful login with valid credentials"""
    # Register user first
    client.post(
        "/api/auth/register",
        json={
            "email": "loginuser@example.com",
            "password": "secure_password123",
            "full_name": "Login User"
        }
    )
    
    # Login
    response = client.post(
        "/api/auth/login",
        json={
            "email": "loginuser@example.com",
            "password": "secure_password123"
        }
    )
    
    assert response.status_code == 200
    data = response.json()
    
    assert "user_id" in data
    assert data["email"] == "loginuser@example.com"
    assert data["role"] == "user"
    assert "token" in data
    assert data["expires_in"] == 604800  # 7 days in seconds


def test_login_invalid_password():
    """Test login with wrong password returns 401"""
    # Register user first
    client.post(
        "/api/auth/register",
        json={
            "email": "wrongpass@example.com",
            "password": "correct_password",
            "full_name": "Test User"
        }
    )
    
    # Try login with wrong password
    response = client.post(
        "/api/auth/login",
        json={
            "email": "wrongpass@example.com",
            "password": "wrong_password"
        }
    )
    
    assert response.status_code == 401
    assert response.json()["detail"] == "Invalid email or password"


def test_login_nonexistent_user():
    """Test login with non-existent email returns 401"""
    response = client.post(
        "/api/auth/login",
        json={
            "email": "nonexistent@example.com",
            "password": "password123"
        }
    )
    
    assert response.status_code == 401
    assert response.json()["detail"] == "Invalid email or password"


def test_login_updates_last_login():
    """Test that login updates the last_login timestamp"""
    # Register user first
    client.post(
        "/api/auth/register",
        json={
            "email": "timestamp@example.com",
            "password": "password123",
            "full_name": "Timestamp User"
        }
    )
    
    # Get initial last_login (should be None)
    db = TestingSessionLocal()
    user = db.query(User).filter(User.email == "timestamp@example.com").first()
    initial_last_login = user.last_login
    db.close()
    
    # Login
    response = client.post(
        "/api/auth/login",
        json={
            "email": "timestamp@example.com",
            "password": "password123"
        }
    )
    
    assert response.status_code == 200
    
    # Check last_login was updated
    db = TestingSessionLocal()
    user = db.query(User).filter(User.email == "timestamp@example.com").first()
    assert user.last_login is not None
    assert user.last_login != initial_last_login
    db.close()


def test_register_returns_valid_token():
    """Test that registration returns a valid JWT token that can be decoded"""
    response = client.post(
        "/api/auth/register",
        json={
            "email": "tokentest@example.com",
            "password": "password123",
            "full_name": "Token Test"
        }
    )
    
    assert response.status_code == 201
    token = response.json()["token"]
    
    # Decode and verify token
    payload = verify_token(token)
    assert payload["user_id"] is not None
    assert payload["email"] == "tokentest@example.com"
    assert payload["role"] == "user"
    assert "exp" in payload  # Expiration timestamp
