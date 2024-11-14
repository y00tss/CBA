from fastapi import APIRouter, Depends

from auth.models import User

from auth.base_config import (
    auth_backend,
    fastapi_users,
)
from auth.schemas import (
    UserRead,
    UserCreate,
)

from services.logger.logger import Logger
import logging

logger = Logger(__name__, level=logging.INFO, log_to_file=True,
                filename='auth.log').get_logger()

router = APIRouter()

router.include_router(
    fastapi_users.get_auth_router(auth_backend),
)
router.include_router(
    fastapi_users.get_register_router(UserRead, UserCreate),
)

current_user = fastapi_users.current_user()


@router.get("/users/me")
async def get_user(
        user: User = Depends(current_user)
):
    """
    Get user info

    :param user:

    :return: user data

    """
    return {
        "username": user.username,
        "email": user.email,
    }
