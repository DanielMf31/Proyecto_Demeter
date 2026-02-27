import pytest
from fastapi.testclient import TestClient
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
import asyncio

# Fix sys path to allow absolute imports
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app import app
from Core.database import Base, get_db
from Core.auth import get_password_hash, create_access_token
from BD.models import User

# --- Override Database Dependency for Testing ---
# (Using SQLite in-memory for fast testing)
TEST_DATABASE_URL = "sqlite+aiosqlite:///:memory:"

engine = create_async_engine(TEST_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine, class_=AsyncSession)

async def override_get_db():
    async with TestingSessionLocal() as session:
        yield session

app.dependency_overrides[get_db] = override_get_db

# --- Fixtures ---

@pytest.fixture(scope="session")
def event_loop():
    """Create an instance of the default event loop for each test case."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()

import pytest_asyncio

@pytest_asyncio.fixture(scope="module", autouse=True)
async def setup_database():
    """Create tables and prepopulate users before tests run."""
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    
    # Pre-populate Test Users
    async with TestingSessionLocal() as session:
        admin_user = User(username="admin_test", password_hash=get_password_hash("pass123"), role="admin", is_active=True)
        normal_user = User(username="operator_test", password_hash=get_password_hash("pass123"), role="operator", is_active=True)
        guest_user = User(username="guest_test", password_hash=get_password_hash("pass123"), role="user", is_active=True)
        inactive_user = User(username="inactive_test", password_hash=get_password_hash("pass123"), role="user", is_active=False)
        
        session.add_all([admin_user, normal_user, guest_user, inactive_user])
        await session.commit()
        
    yield
    
    # Teardown
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)

@pytest.fixture
def client():
    """Returns the FastAPI Test Client."""
    return TestClient(app)

@pytest.fixture
def admin_token() -> str:
    """Returns a valid JWT token for an admin user."""
    return create_access_token(data={"sub": "admin_test", "role": "admin"})

@pytest.fixture
def operator_token() -> str:
    """Returns a valid JWT token for an operator user."""
    return create_access_token(data={"sub": "operator_test", "role": "operator"})

@pytest.fixture
def user_token() -> str:
    """Returns a valid JWT token for a regular user."""
    return create_access_token(data={"sub": "guest_test", "role": "user"})

@pytest.fixture
def inactive_token() -> str:
    """Returns a valid JWT token for an inactive user."""
    return create_access_token(data={"sub": "inactive_test", "role": "user"})
