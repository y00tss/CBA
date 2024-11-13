from fastapi import BackgroundTasks
import asyncio
from articles.article_service.document_work import DocumentWorkFlow
from fastapi import APIRouter, Depends
from settings.database import get_async_session
from articles.models import Articles
from sqlalchemy import select, update
from articles.article_service.document_init import DocumentInit

import logging
from services.logger.logger import Logger

logger = Logger(__name__, level=logging.INFO, log_to_file=True,
                filename='tasks.log').get_logger()


async def document_process(path: str, article_id: int, magazine_id: int, user_name: str):
    """Function to process the document"""
    await asyncio.sleep(3)
    session = Depends(get_async_session)

    logger.info(f"Start checking the document: {path} for article: {article_id}")
    try:
        doc = DocumentWorkFlow(path)
        document = await doc.start_flow()

        report = await doc.create_report()

        article = session.execute(
            update(Articles).where(Articles.c.id == article_id).values(document=document,
                                                                       checked=True,
                                                                       list_issues=report)
        )
        session.commit()

        update_document = DocumentInit(file=document, magazine_id=magazine_id)
        updated_document_path = await update_document.save_document(user_name=user_name, session=session)

        logger.info(f"Document processed successfully: {path}")

    except Exception as e:
        logger.error(f"Error processing document: {e}")
        return {"status": 500, "description": f"{e}"}
