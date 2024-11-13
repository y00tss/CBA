from datetime import datetime

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

Articles = Table(
    'articles',
    metadata,
    Column('id', Integer, primary_key=True),
    Column('title', String, nullable=False),
    Column('file', String, nullable=False),
    Column('user_id', ForeignKey(User.id)),
    Column('magazine_id', ForeignKey(Magazine.c.id)),
    Column('publish_date', TIMESTAMP, default=datetime.utcnow),
    Column('checked', Boolean, default=False, nullable=False),
    Column('list_issues', JSON, nullable=True),
)
