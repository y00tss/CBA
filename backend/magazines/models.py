from datetime import datetime

from sqlalchemy import (
    Table, Column,
    Integer, String,
    TIMESTAMP, MetaData,
)

metadata = MetaData()

Magazine = Table(
    'magazines',
    metadata,
    Column('id', Integer, primary_key=True),
    Column('title', String, nullable=False),
    Column('publish_date', TIMESTAMP, default=datetime.utcnow),
    Column('maximum_articles', Integer, nullable=False),
)
