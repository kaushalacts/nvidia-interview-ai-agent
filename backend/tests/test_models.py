import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from api.models import User
from api.database import Base


@pytest.fixture(scope="function")
def test_db():
    # Use in-memory SQLite for testing
    engine = create_engine("sqlite:///:memory:", connect_args={"check_same_thread": False})
    Base.metadata.create_all(bind=engine)
    SessionLocal = sessionmaker(bind=engine, autoflush=False)
    yield SessionLocal
    Base.metadata.drop_all(bind=engine)


def test_user_model_creation(test_db):
    db = test_db()
    
    user = User(
        user_id="test-uuid",
        email="test@example.com",
        password_hash="hashed_pw",
        full_name="Test User",
        role="user"
    )
    db.add(user)
    db.commit()
    
    retrieved = db.query(User).filter_by(email="test@example.com").first()
    assert retrieved is not None
    assert retrieved.full_name == "Test User"
    assert retrieved.role == "user"
    db.close()
