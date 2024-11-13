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


async def document_process(path: str, article_id: int, user_name: str, session):
    """Function to process the document"""
    await asyncio.sleep(1)

    logger.info(f"Start checking the document: {path} for article: {article_id}")
    try:
        # check and replace issues in the document
        doc = DocumentWorkFlow(path)
        document = await doc.start_flow()
        report = await doc.create_report()

        logger.info(f"Report: {report}")

        # get back updated document "path and new document"
        new_path, new_document = await doc.get_updated_document(user_name=user_name)
        logger.info('1')

        logger.info('2')

        await session.execute(
            update(Articles).where(Articles.c.id == article_id).values(file=new_path,
                                                                       checked=True,
                                                                       list_issues=report)
        )
        await session.commit()
        logger.info('ГОТОВО')

        logger.info(f"Document processed successfully: {path}")

    except Exception as e:
        logger.error(f"Error processing document: {e}")
        return {"status": 500, "description": f"{e}"}
