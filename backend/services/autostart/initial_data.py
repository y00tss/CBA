import os
from auth.models import User
from magazines.models import Magazine
from passlib.context import CryptContext
from sqlalchemy import select, insert

from services.logger.logger import Logger
import logging

logger = Logger(__name__, level=logging.INFO, log_to_file=True,
                filename='start_app.log').get_logger()


class InitializationData:
    """For starting the project with initial"""

    def __init__(self, session):
        self.session = session

    async def start_app(self):
        await self._create_superuser()
        await self._create_magazines()

    async def _create_superuser(self):
        """Creating a superuser if it does not exist yet."""

        pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
        username = os.getenv("SUPERUSER_USERNAME", "admin")
        email = os.getenv("SUPERUSER_EMAIL", "admin@admin.com")
        password = os.getenv("SUPERUSER_PASSWORD", "admin")

        try:
            result = await self.session.execute(select(User).where(User.username == username))  # noqa
            user = result.scalars().first()

            if not user:
                hashed_password = pwd_context.hash(password)
                new_user = User(
                    username=username,
                    email=email,
                    hashed_password=hashed_password,
                    is_superuser=True
                )
                self.session.add(new_user)
                await self.session.commit()
                logger.info("Superuser created")

        except Exception as e:
            logger.error(f"Error creating superuser: {e}")
            return {"status": 500, "description": f"{e}"}

    async def _create_magazines(self):
        """Creating magazines if they do not exist yet."""

        try:
            result = await self.session.execute(select(Magazine))
            magazines = result.scalars().all()

            if not magazines:
                stmt = insert(Magazine).values(title="Magazine 1", maximum_articles=5)
                await self.session.execute(stmt)
                await self.session.commit()
                logger.info("Magazines created")

        except Exception as e:
            logger.error(f"Error creating magazines: {e}")
            return {"status": 500, "description": f"{e}"}
