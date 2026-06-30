"""image_url for books

Revision ID: 17ec917fbd97
Revises: 141077ee5325
Create Date: 2026-06-30 11:09:20.136514

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '17ec917fbd97'
down_revision: Union[str, Sequence[str], None] = '141077ee5325'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""

    # Remove old column
    op.drop_column("books", "links")

    # Add new column
    op.add_column(
        "books",
        sa.Column(
            "image_url",
            sa.String(length=255),
            nullable=True,
        ),
    )


def downgrade() -> None:
    """Downgrade schema."""

    # Remove new column
    op.drop_column("books", "image_url")

    # Restore old column
    op.add_column(
        "books",
        sa.Column(
            "links",
            sa.String(length=255),
            nullable=True,
        ),
    )
