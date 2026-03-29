"""Pytest configuration and fixtures for tests."""
import sys
from pathlib import Path

# Add the backend directory to sys.path so we can import api modules
backend_dir = Path(__file__).parent.parent
sys.path.insert(0, str(backend_dir))

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

# Import Base and models from the api package
from api.models import Base
from api.database import SessionLocal


@pytest.fixture(scope="session")
def test_engine():
    """Create a test database engine (in-memory SQLite)"""
    engine = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    # Create all tables using the test engine
    Base.metadata.create_all(bind=engine)
    return engine


@pytest.fixture(scope="function")
def test_db_session(test_engine):
    """Create a fresh database session for each test"""
    TestingSessionLocal = sessionmaker(bind=test_engine, autocommit=False, autoflush=False)
    session = TestingSessionLocal()
    
    # Clear all tables before each test
    for table in reversed(Base.metadata.sorted_tables):
        session.execute(table.delete())
    session.commit()
    
    yield session
    
    # Clean up after test
    session.close()
    for table in reversed(Base.metadata.sorted_tables):
        session.execute(table.delete())
    session.commit()
