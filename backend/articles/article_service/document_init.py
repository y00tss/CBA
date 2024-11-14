"""
Document interface for the Article Service
"""

from sqlalchemy.ext.asyncio import AsyncSession
import aiofiles
from articles.models import Articles
from magazines.models import Magazine
from sqlalchemy import select, func
from datetime import datetime
import os
from fastapi import UploadFile
import uuid
from abc import ABC, abstractmethod


class BaseDocument(ABC):
    """Base document class"""

    @abstractmethod
    async def save_document(self, user_name, session: AsyncSession) -> str:
        pass

    @staticmethod
    async def delete_document(path: str) -> bool:
        """Static method to delete a document from the file system"""
        if path and os.path.exists(path):
            print(f"Deleting document: {path}")
            os.remove(path)
            return True
        return False


class DocumentInit(BaseDocument):
    """Document initialization class for files with the .docx extension"""

    def __init__(self, file: UploadFile, magazine_id: int, update: bool = False):
        self.file = file
        self.magazine_id = magazine_id
        self.update = update

    async def save_document(self, user_name, session: AsyncSession) -> str:
        """Save document to database"""
        if all([await self._check_extension(), await self._magazine_exists(self.magazine_id, session),
                await self._check_max_articles(session)]):
            file_path = await self._create_document(user_name)
            return file_path
        raise ValueError("Unexpected error occurred while saving the document.")

    async def _check_extension(self) -> bool:
        """Check extension for docx files"""
        if self.file.filename.lower().endswith('.docx'):
            return True
        raise ValueError("Invalid file extension. Only .docx files are allowed")

    async def _magazine_exists(self, magazine_id: int, session: AsyncSession) -> bool:
        """Check if magazine exists"""
        magazine = await session.execute(select(Magazine).where(Magazine.c.id == magazine_id))
        if not magazine.fetchone():
            raise ValueError("Magazine not found.")
        return True

    async def _check_max_articles(self, session: AsyncSession) -> bool:
        """Check if the user has reached the maximum number of articles"""
        magazine_limit_query = select(Magazine.c.maximum_articles).where(Magazine.c.id == self.magazine_id)
        magazine_limit_result = await session.execute(magazine_limit_query)
        magazine_limit = magazine_limit_result.scalar()

        article_count_query = select(func.count(Articles.c.id)).where(Articles.c.magazine_id == self.magazine_id)
        article_count_result = await session.execute(article_count_query)
        current_article_count = article_count_result.scalar()

        if current_article_count >= magazine_limit:
            raise ValueError("You have reached the maximum number of articles for this magazine.")
        return True

    async def _create_document(self, user_name) -> str:
        """Save document to disk"""
        if self.update:
            file_name = f"updated_document_{datetime.now().date()}_{uuid.uuid4()}.docx"
        else:
            file_name = f"original_document_{datetime.now().date()}_{uuid.uuid4()}.docx"
        file_path = f"articles/documents/{user_name}/{file_name}"

        os.makedirs(f"articles/documents/{user_name}", exist_ok=True)

        async with aiofiles.open(file_path, "wb") as f:
            content = await self.file.read()
            await f.write(content)

        return file_path
