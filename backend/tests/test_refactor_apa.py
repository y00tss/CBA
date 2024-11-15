import pytest
from unittest.mock import AsyncMock
from articles.article_service.mapper_type import DocumentWorkFlowFactory

TEMP_DIR = "articles/documents/test_user"


@pytest.mark.asyncio
async def test_document_process_success():
    # Mocking the session
    # mock_session = AsyncMock(AsyncSession)
    #
    # # Mocking the DocumentWorkFlowFactory
    # mock_doc = MagicMock()
    # mock_doc.start_flow = AsyncMock()
    # mock_doc.create_report = AsyncMock(return_value="No issues found.")
    # mock_doc.get_updated_document = AsyncMock(return_value=f"{TEMP_DIR}/document.docx") # noqa

    # Mocking the factory method to return our mocked document object
    # DocumentWorkFlowFactory.create_workflow = AsyncMock(return_value=mock_doc)
    pass


@pytest.mark.asyncio
async def test_document_process_failure():
    # Mocking the DocumentWorkFlowFactory to raise an exception
    DocumentWorkFlowFactory.create_workflow = AsyncMock(
        side_effect=Exception("Document processing failed")
    )
    pass
