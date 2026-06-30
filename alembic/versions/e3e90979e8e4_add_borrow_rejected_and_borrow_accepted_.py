"""add borrow rejected and borrow accepted notification types

Revision ID: e3e90979e8e4
Revises: 675f5ef2d7cb
Create Date: 2026-06-30 15:23:40.449744

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "e3e90979e8e4"
down_revision: Union[str, Sequence[str], None] = "675f5ef2d7cb"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.execute("ALTER TYPE notification_type ADD VALUE 'BOOK_BORROW_ACCEPTED';")
    op.execute("ALTER TYPE notification_type ADD VALUE 'BOOK_BORROW_REJECTED';")


def downgrade() -> None:
    """Downgrade schema."""
    pass
