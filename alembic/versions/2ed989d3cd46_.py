"""empty message

Revision ID: 2ed989d3cd46
Revises: 4bcda8008976, b6ef187a15fe
Create Date: 2026-07-01 09:54:11.782119

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '2ed989d3cd46'
down_revision: Union[str, Sequence[str], None] = ('4bcda8008976', 'b6ef187a15fe')
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass
