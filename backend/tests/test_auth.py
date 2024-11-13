from sqlalchemy import insert, select

from auth.models import role
from tests.conftest import client, async_session_maker


async def test_add_role():
    """Adding a role should return a 201 status"""
    async with async_session_maker() as session:
        stmt = insert(role).values(id=1, name="admin", permissions=None)
        await session.execute(stmt)
        await session.commit()

        query = select(role)
        result = await session.execute(query)
        assert result.all() == [(1, 'admin', None)], "Adding role"


def test_register_new_user():
    """Registering a new user should return a 201 status code."""
    response = client.post("/auth/register", json={
        "email": "test@testc.com",
        "username": "test@testc.com",
        "password": "sdgs6531we#$adra!",
        "is_active": True,
        "is_superuser": False,
        "is_verified": False,
        "role_id": 1
    })
    assert response.status_code == 201
    result = response.json()
    assert result['email'] == "test@testc.com"
    assert result['username'] == "test@testc.com"
    assert result['is_active']
    assert ~result['is_superuser']


def test_register_existing_user():
    """Registering an existing user should return a 400 status code."""
    response = client.post("/auth/register", json={
        "email": "test@testc.com",
        "username": "test@testc.com",
        "password": "sdgs6531we#$adra!",
        "is_active": True,
        "is_superuser": False,
        "is_verified": False,
        "role_id": 1
    })
    assert response.status_code == 400


def test_login_user():
    """Logging in a user should return a 200 status code."""
    response = client.post("/auth/login", data={
        "username": "test@testc.com",
        "password": "sdgs6531we#$adra!",
    })
    assert response.status_code == 200
    assert response.json()['access_token']

    client.headers.update(
        {"Authorization": f"Bearer {response.json()['access_token']}"}
    )
