from sqlalchemy import insert, select

from auth.models import role
from tests.conftest import client, async_session_maker


async def test_add_role():
    """Adding a role should return a 201 status"""
    async with async_session_maker() as session:
        pass


def test_register_new_user():
    """Registering a new user should return a 201 status code."""
    pass


def test_register_existing_user():
    """Registering an existing user should return a 400 status code."""
    pass


def test_login_user():
    """Logging in a user should return a 200 status code."""
    pass
