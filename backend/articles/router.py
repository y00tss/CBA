from fastapi import APIRouter, Depends, Form, UploadFile, File, BackgroundTasks
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import insert, select, update, delete

from auth.models import User
from articles.models import Articles
from articles.schemas import ArticleCreateRequest, ArticleUpdateRequest
from articles.article_service.document_init import DocumentInit
from auth.base_config import current_user
from settings.database import get_async_session
from articles.tasks import document_process

from services.logger.logger import Logger
import logging

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
        articles = await session.execute(select(Articles).order_by(Articles.c.id))

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
        document_path = await document.save_document(user_name=user.username, session=session)
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
            "description": f"Article was created successfully. "
                           f"I need 1 minute to check your document. Check the status later"
        }
    except Exception as e:
        await session.rollback()
        logger.error(f"Error creating magazine: {e}")
        return {"status": 500, "description": f"{e}"}


# @router.post("/test", status_code=201)
# async def test(
#         background_tasks: BackgroundTasks,
#         user: User = Depends(current_user),
#         session: AsyncSession = Depends(get_async_session),
# ):
#     path = 'articles/documents/test/original_document_2024-11-14_b4eec6ed-65d4-4a3a-983d-a2d7d78af449.docx'
#     background_tasks.add_task(
#         document_process,
#         path,
#         article_id=31,
#         user_name=user.username,
#         session=session
#     )


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
        result = await session.execute(select(Articles).where(Articles.c.id == article_id))
        article = result.scalar_one_or_none()
        if not article:
            return {"status": 404, "description": "Article not found"}

        old_original_path = article.original_file
        old_updated_path = article.updated_file

        document = DocumentInit(file=file, magazine_id=magazine_id)
        document_path = await document.save_document(user_name=user.username, session=session)
        if old_original_path:
            await DocumentInit.delete_document(old_original_path)
        if old_updated_path:
            await DocumentInit.delete_document(old_updated_path)

        article.title = title
        article.magazine_id = magazine_id
        article.original_file = document_path
        article.updated_file = None
        article.checked = False
        article.user_id = user.id

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
            "description": "Article changed successfully"
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
        result = await session.execute(select(Articles).where(Articles.c.id == article_id))
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
