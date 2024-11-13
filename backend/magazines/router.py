from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import insert, select, update, delete

from auth.models import User
from magazines.models import Magazine
from magazines.schemas import MagazineCreateRequest, MagazineUpdateRequest
from auth.base_config import current_user
from settings.database import get_async_session

from services.logger.logger import Logger
import logging

logger = Logger(__name__, level=logging.INFO, log_to_file=True,
                filename='magazine.log').get_logger()

router = APIRouter()


@router.get("/all", status_code=200)
async def get_all_magazines(
        user: User = Depends(current_user),
        session: AsyncSession = Depends(get_async_session),
):
    """
    Get all magazines
    """
    try:
        magazines = await session.execute(select(Magazine).order_by(Magazine.c.id))

        return magazines.mappings().all()
    except IndexError:
        return {"status": 404, "description": "Magazines not found"}
    except Exception as e:
        logger.error(f"Error getting all magazines: {e}")
        return {"status": 500, "description": f"{e}"}


@router.get("/{magazine_id}", status_code=200)
async def get_magazine_by_id(
        magazine_id: int,
        user: User = Depends(current_user),
        session: AsyncSession = Depends(get_async_session),
):
    """
    Get magazine by id
    """
    try:
        magazine = await session.execute(select(Magazine).where(
            Magazine.c.id == magazine_id
        ).order_by(Magazine.c.id))
        return magazine.mappings().all()[0]
    except IndexError:
        return {"status": 404, "description": "Magazine not found"}
    except Exception as e:
        logger.error(f"Error getting magazine by id: {e}")
        return {"status": 500, "description": f"{e}"}


@router.post("/", status_code=201)
async def create_magazine(
        post_request: MagazineCreateRequest,
        user: User = Depends(current_user),
        session: AsyncSession = Depends(get_async_session),
):
    """
    Create magazine
    """
    try:
        if not user.is_superuser:
            logger.error(f"User: {user.username} is not a superuser")
            return {"status": 403, "description": "Forbidden. Only superusers can create magazines"}

        await session.execute(insert(Magazine).values(
            title=post_request.title,
            maximum_articles=post_request.maximum_articles,
        ))
        await session.commit()
        await session.close()

        logger.info(f"Magazine: {post_request.title} created by superuser: {user.username}")
        return {
            "status": 201,
            "description": "Magazine created successfully"
        }
    except Exception as e:
        await session.rollback()
        logger.error(f"Error creating magazine: {e}")
        return {"status": 500, "description": f"{e}"}


@router.patch("/{magazine_id}", status_code=200)
async def update_magazine(
        magazine_id: int,
        post_update: MagazineUpdateRequest,
        user: User = Depends(current_user),
        session: AsyncSession = Depends(get_async_session),
):
    """
    Update magazine
    """
    try:
        if not user.is_superuser:
            logger.error(f"User: {user.username} is not a superuser")
            return {"status": 403, "description": "Forbidden. Only superusers can update magazines"}

        await session.execute(update(Magazine).where(Magazine.c.id == magazine_id).values(
            title=post_update.title,
            maximum_articles=post_update.maximum_articles,
        ))
        await session.commit()
        logger.info(f"Magazine: {magazine_id} was updated by superuser: {user.username}")
        return {
            "status": 200,
            "description": "Magazine changed successfully"
        }
    except IndexError:
        return {"status": 404, "description": "Magazine not found"}
    except Exception as e:
        await session.rollback()
        logger.error(f"Error updating magazine: {e}")
        return {"status": 500, "description": f"{e}"}


@router.delete("/{magazine_id}", status_code=200)
async def delete_magazine(
        magazine_id: int,
        user: User = Depends(current_user),
        session: AsyncSession = Depends(get_async_session),
):
    """
    Delete magazine
    """
    try:
        await session.execute(delete(Magazine).where(Magazine.c.id == magazine_id))
        await session.commit()

        logger.info(f"Magazine: {magazine_id} was deleted by user: {user.username}")

        return {"status": 200, "description": "Magazine deleted successfully"}
    except IndexError:
        return {"status": 404, "description": "Magazine not found"}
    except Exception as e:
        await session.rollback()
        logger.error(f"Error deleting magazine: {e}")
        return {"status": 500, "description": f"{e}"}
