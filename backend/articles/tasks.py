import asyncio
from articles.article_service.document_work import DocumentWorkFlow
from articles.models import Articles
from sqlalchemy import update

import logging
from services.logger.logger import Logger

logger = Logger(__name__, level=logging.INFO, log_to_file=True,
                filename='tasks.log').get_logger()


async def document_process(path: str, article_id: int, user_name: str, session):
    """Function to process the document"""
    await asyncio.sleep(1)

    try:
        # check and replace issues in the document
        doc = DocumentWorkFlow(path)
        await doc.start_flow()
        report = await doc.create_report()

        # get back updated document: "path"
        new_path = await doc.get_updated_document(user_name=user_name)

        await session.execute(
            update(Articles).where(Articles.c.id == article_id).values(
                updated_file=new_path, checked=True, list_issues=report)
        )
        await session.commit()

        logger.info(f"Document with article id {article_id} was updated: {path}")

    except Exception as e:
        logger.error(f"Error processing document: {e}")
        return {"status": 500, "description": f"{e}"}
