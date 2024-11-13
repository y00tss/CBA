import asyncio
from typing import AsyncGenerator

import pytest
from fastapi.testclient import TestClient
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import NullPool

from settings.database import get_async_session, metadata
from settings.config import TEST_DATABASE_URL
from settings.main import app

# DATABASE
DATABASE_URL_TEST = TEST_DATABASE_URL

engine_test = create_async_engine(DATABASE_URL_TEST, poolclass=NullPool)
async_session_maker = sessionmaker(
    engine_test, class_=AsyncSession, expire_on_commit=False
)
metadata.bind = engine_test


async def override_get_async_session() -> AsyncGenerator[AsyncSession, None]:
    async with async_session_maker() as session:
        yield session


app.dependency_overrides[get_async_session] = override_get_async_session


@pytest.fixture(autouse=True, scope='session')
async def prepare_database():
    async with engine_test.begin() as conn:
        await conn.run_sync(metadata.create_all)
    yield
    async with engine_test.begin() as conn:
        pass
        await conn.run_sync(metadata.drop_all)


# SETUP
@pytest.fixture(scope='session')
def event_loop(request):
    """Create an instance of the default event loop for each test case."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


client = TestClient(app)


@pytest.fixture(scope="session")
async def ac() -> AsyncGenerator[AsyncClient, None]:
    async with AsyncClient(app=app, base_url="http://test") as ac:
        ac.headers = {
            'Content-Type': 'application/json',
            'Accept': 'application/json'
        }
        token = client.post("/auth/login", data={
            "username": "test@testc.com",
            "password": "sdgs6531we#$adra!",
        })
        ac.headers.update({"Authorization": f"Bearer {token.json()['access_token']}"})
        yield ac


@pytest.fixture(scope="session")
async def ac_fake() -> AsyncGenerator[AsyncClient, None]:
    async with AsyncClient(app=app, base_url="http://test") as ac:
        yield ac
