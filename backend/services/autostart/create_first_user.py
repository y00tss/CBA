"""
User creation before the first start of the application
"""
#
import os
from auth.models import User
from passlib.context import CryptContext
from sqlalchemy import select
from services.logger.logger import Logger

logger = Logger(__name__).get_logger()

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

async def create_superuser(session): # noqa
    """
    Создание суперпользователя, если он еще не существует.
    """
    username = os.getenv("SUPERUSER_USERNAME", "admin")
    email = os.getenv("SUPERUSER_EMAIL", "admin@admin.com")
    password = os.getenv("SUPERUSER_PASSWORD", "admin")

    try:
        result = await session.execute(select(User).where(User.username == username)) # noqa
        user = result.scalars().first()

        if not user:
            hashed_password = pwd_context.hash(password)
            new_user = User(
                username=username,
                email=email,
                hashed_password=hashed_password,
                is_superuser=True
            )
            session.add(new_user)
            await session.commit()
            logger.info("Superuser created")
        else:
            logger.info("Superuser already exists")
    except Exception as e:
        logger.error(f"Error creating superuser: {e}")
        return {"status": 500, "description": f"{e}"}
