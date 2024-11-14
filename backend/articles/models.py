from datetime import datetime
from sqlalchemy import Enum
from enum import Enum as PyEnum

from sqlalchemy import (
    Table, Column,
    Integer, String,
    TIMESTAMP, ForeignKey,
    Boolean, MetaData,
    JSON,
)

from auth.models import User
from magazines.models import Magazine

metadata = MetaData()


class RefactorType(PyEnum):
    APA = "APA"
    Custom = "Custom"


Articles = Table(
    'articles',
    metadata,
    Column('id', Integer, primary_key=True),
    Column('title', String, nullable=False),
    Column('updated_file', String, nullable=True),
    Column('original_file', String, nullable=True),
    Column('user_id', ForeignKey(User.id)),
    Column('magazine_id', ForeignKey(Magazine.c.id)),
    Column('publish_date', TIMESTAMP, default=datetime.utcnow),
    Column('checked', Boolean, default=False, nullable=False),
    Column('list_issues', JSON, nullable=True),
    Column('refactor_type', Enum(RefactorType), nullable=False)
)
