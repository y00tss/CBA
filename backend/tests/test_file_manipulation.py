import pytest
import uuid
import os
from unittest.mock import AsyncMock, patch, MagicMock
from fastapi import UploadFile
from articles.article_service.document_init import DocumentInit
from sqlalchemy.ext.asyncio import AsyncSession
from io import BytesIO

# Путь для временных файлов
TEMP_DIR = "articles/documents/test_user"


@pytest.fixture
def test_file():
    """Create test file"""
    file_content = b"Test content for .docx file"
    file = UploadFile(
        filename="test_document.docx",
        file=BytesIO(file_content)
    )
    return file


@pytest.fixture
def test_file_txt_extension():
    """Create test file with WRONG extension"""
    file_content = b"Test content for .txt file"
    file = UploadFile(
        filename="test_document_txt.txt",
        file=BytesIO(file_content)
    )
    return file


@pytest.fixture
def async_session():
    """Mock AsyncSession"""
    session = AsyncMock(spec=AsyncSession)
    return session


@pytest.fixture
def mock_document_init(test_file):
    """Mock DocumentInit with docx file"""
    return DocumentInit(file=test_file, magazine_id=1)


@pytest.fixture
def mock_document_with_wrong_ext_init(test_file_txt_extension):
    """Mock DocumentInit"""
    return DocumentInit(file=test_file_txt_extension, magazine_id=1)


@pytest.mark.asyncio
async def test_save_document(mock_document_init, async_session):
    """Test document saving"""
    with patch.object(mock_document_init, '_check_extension', return_value=True), \
            patch.object(mock_document_init, '_magazine_exists', return_value=True), \
            patch.object(mock_document_init, '_check_max_articles', return_value=True):
        file_path = await mock_document_init.save_document(user_name="test_user", session=async_session)

        assert file_path.endswith(".docx")

        os.remove(file_path)


@pytest.mark.asyncio
async def test_check_extension(mock_document_init):
    """Test extension check"""
    result = await mock_document_init._check_extension()
    assert result is True


@pytest.mark.asyncio
async def test_check__txt_extension(mock_document_with_wrong_ext_init):
    """Test extension check with wrong extension"""
    mock_document_with_wrong_ext_init.file.filename = "test_document_txt.txt"

    with pytest.raises(ValueError, match="Invalid file extension. Only .docx files are allowed"):
        await mock_document_with_wrong_ext_init._check_extension()


@pytest.mark.asyncio
async def test_magazine_exists(mock_document_init, async_session):
    """Test magazine exists check"""
    async_session.execute.return_value.fetchone = MagicMock(return_value=(1,))

    result = await mock_document_init._magazine_exists(1, async_session)
    assert result is True


@pytest.mark.asyncio
async def test_delete_document():
    """Test document deletion"""
    file_path = os.path.join(TEMP_DIR, f"test_document_{uuid.uuid4()}.docx")

    os.makedirs(TEMP_DIR, exist_ok=True)
    with open(file_path, "wb") as f:
        f.write(b"Test content")

    assert os.path.exists(file_path)

    with patch("os.remove") as mock_remove:
        result = await DocumentInit.delete_document(file_path)

        assert result is True
