"""merge branches

Revision ID: b6ef187a15fe
Revises: e3e90979e8e4, a5beae8f388a
Create Date: 2026-06-30 18:33:26.139431

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'b6ef187a15fe'
down_revision: Union[str, Sequence[str], None] = ('e3e90979e8e4', 'a5beae8f388a')
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass
