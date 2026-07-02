"""empty message

Revision ID: df45ffafe6fe
Revises: 2ed989d3cd46, e909e00e9479
Create Date: 2026-07-01 19:10:10.727657

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'df45ffafe6fe'
down_revision: Union[str, Sequence[str], None] = ('2ed989d3cd46', 'e909e00e9479')
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass
