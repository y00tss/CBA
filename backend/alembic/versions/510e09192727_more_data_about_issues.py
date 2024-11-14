"""More data about issues

Revision ID: 510e09192727
Revises: ff5699d83f0e
Create Date: 2024-11-13 17:49:42.263249

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '510e09192727'
down_revision: Union[str, None] = 'ff5699d83f0e'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('articles', sa.Column('checked', sa.Boolean(), nullable=False))
    op.add_column('articles', sa.Column('list_issues', sa.JSON(), nullable=True))
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('articles', 'list_issues')
    op.drop_column('articles', 'checked')
    # ### end Alembic commands ###
