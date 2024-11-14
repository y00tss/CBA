from fastapi import (
    APIRouter, Depends,
    Form, UploadFile,
    File, BackgroundTasks
)
from fastapi.responses import FileResponse
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import (
    insert, select,
    update, delete,
)

from auth.models import User
from articles.models import Articles

from articles.article_service.document_init import DocumentInit
from auth.base_config import current_user
from settings.database import get_async_session
from articles.tasks import document_process

from services.logger.logger import Logger
import logging
import os

logger = Logger(__name__, level=logging.INFO, log_to_file=True,
                filename='article.log').get_logger()

router = APIRouter()


@router.get("/all", status_code=200)
async def get_all_articles(
        user: User = Depends(current_user),
        session: AsyncSession = Depends(get_async_session),
):
    """
    Get all articles from all magazines
    """
    try:
        articles = await session.execute(select(Articles
                                                ).order_by(Articles.c.id))

        return articles.mappings().all()
    except IndexError:
        return {"status": 404, "description": "Articles not found"}
    except Exception as e:
        logger.error(f"Error getting all magazines: {e}")
        return {"status": 500, "description": f"{e}"}


@router.get("/{articles_id}", status_code=200)
async def get_articles_by_id(
        articles_id: int,
        user: User = Depends(current_user),
        session: AsyncSession = Depends(get_async_session),
):
    """
    Get magazine by id
    """
    try:
        articles = await session.execute(select(Articles).where(
            Articles.c.id == articles_id
        ).order_by(Articles.c.id))
        return articles.mappings().all()[0]
    except IndexError:
        return {"status": 404, "description": "Article not found"}
    except Exception as e:
        logger.error(f"Error getting magazine by id: {e}")
        return {"status": 500, "description": f"{e}"}


@router.get("/{article_id}/download", status_code=200)
async def download_updated_file(
        article_id: int,
        user: User = Depends(current_user),
        session: AsyncSession = Depends(get_async_session)
):
    """
    Download the updated file for the given article ID
    """
    try:
        result = await session.execute(select(Articles
                                              ).where(Articles.c.id == article_id))
        article = result.fetchone()
        logger.info(f"Article: {article}")

        if not article:
            return {"status": 404, "description": "Article not found"}

        updated_file_path = article[2]
        if not updated_file_path or not os.path.exists(updated_file_path):
            return {"status": 404, "description": "Updated file not found"}

        # Возвращаем файл в ответе
        return FileResponse(
            path=updated_file_path,
            filename=os.path.basename(updated_file_path),
            media_type='application/vnd.openxmlformats-officedocument.wordprocessingml.document' # noqa
        )
    except Exception as e:
        logger.error(f"Error downloading updated file: {e}")
        return {"status": 500, "description": f"{e}"}


@router.post("/", status_code=201)
async def create_articles(
        background_tasks: BackgroundTasks,
        title: str = Form(...),
        magazine_id: int = Form(...),
        file: UploadFile = File(...),
        user: User = Depends(current_user),
        session: AsyncSession = Depends(get_async_session),
):
    """
    Create article
    """
    try:
        document = DocumentInit(file=file, magazine_id=magazine_id)
        document_path = await document.save_document(
            user_name=user.username, session=session
        )
        logger.info(f"Document saved: {document_path}")
        insert_stmt = insert(Articles).values(
            title=title,
            user_id=user.id,
            magazine_id=magazine_id,
            updated_file=None,
            original_file=document_path
        )
        result = await session.execute(insert_stmt)
        await session.commit()

        article_id = result.inserted_primary_key[0]

        logger.info(f"Article: {article_id} - {title} created by user: {user.username}")

        background_tasks.add_task(
            document_process,
            document_path,
            article_id=article_id,
            user_name=user.username,
            session=session
        )

        return {
            "status": 201,
            "description": "Article was created successfully. "
                           "I need 1 minute to check your document. "
                           "Check the status later"
        }
    except Exception as e:
        await session.rollback()
        logger.error(f"Error creating magazine: {e}")
        return {"status": 500, "description": f"{e}"}


@router.patch("/{article_id}", status_code=200)
async def update_article(
        background_tasks: BackgroundTasks,
        article_id: int,
        title: str = Form(...),
        magazine_id: int = Form(...),
        file: UploadFile = File(...),
        user: User = Depends(current_user),
        session: AsyncSession = Depends(get_async_session),
):
    """
    Update magazine
    """
    try:
        result = await session.execute(select(Articles
                                              ).where(Articles.c.id == article_id))
        article = result.fetchone()
        if not article:
            return {"status": 404, "description": "Article not found"}

        old_original_path = article[2]
        old_updated_path = article[3]

        document = DocumentInit(file=file, magazine_id=magazine_id)
        document_path = await document.save_document(
            user_name=user.username, session=session
        )
        if old_original_path:
            await DocumentInit.delete_document(old_original_path)
        if old_updated_path:
            await DocumentInit.delete_document(old_updated_path)

        await session.execute(
            update(Articles)
            .where(Articles.c.id == article_id)
            .values(
                title=title,
                magazine_id=magazine_id,
                original_file=document_path,
                updated_file=None,
                checked=False,
                user_id=user.id
            )
        )
        await session.commit()
        logger.info(f"Article was updated by user: {user.username}")

        background_tasks.add_task(
            document_process,
            document_path,
            article_id=article_id,
            user_name=user.username,
            session=session
        )

        return {
            "status": 200,
            "description": "Article changed successfully. "
                           "Wait 10 sec to check your document. Check the status later"
        }
    except Exception as e:
        await session.rollback()
        logger.error(f"Error updating article: {e}")
        return {"status": 500, "description": f"{e}"}


@router.delete("/{article_id}", status_code=200)
async def delete_article(
        article_id: int,
        user: User = Depends(current_user),
        session: AsyncSession = Depends(get_async_session),
):
    """
    Delete magazine
    """
    try:
        result = await session.execute(select(Articles
                                              ).where(Articles.c.id == article_id))
        article = result.fetchone()
        if not article:
            return {"status": 404, "description": "Article not found"}

        original_path = article.original_file
        update_path = article.updated_file

        if original_path:
            await DocumentInit.delete_document(original_path)
        if update_path:
            await DocumentInit.delete_document(update_path)

        await session.execute(delete(Articles).where(Articles.c.id == article_id))
        await session.commit()

        logger.info(f"Article deleted by user: {user.username}")

        return {"status": 200, "description": "Article deleted successfully"}
    except Exception as e:
        await session.rollback()
        logger.error(f"Error deleting article: {e}")
        return {"status": 500, "description": f"{e}"}
