"""add status to book_copies

Revision ID: 2da059bd1475
Revises: fc066a9a31db
Create Date: 2026-06-28 19:39:28.454983

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


# revision identifiers, used by Alembic.
revision: str = "2da059bd1475"
down_revision: Union[str, Sequence[str], None] = "fc066a9a31db"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


bookcopystatus = postgresql.ENUM(
    "AVAILABLE",
    "BORROWED",
    "LOST",
    "DAMAGED",
    name="bookcopystatus",
)


def upgrade() -> None:
    """Upgrade schema."""

    # Create the PostgreSQL enum type
    bookcopystatus.create(op.get_bind(), checkfirst=True)

    # Add the column
    op.add_column(
        "book_copies",
        sa.Column(
            "status",
            bookcopystatus,
            nullable=False,
            server_default="AVAILABLE",
        ),
    )


def downgrade() -> None:
    """Downgrade schema."""

    op.drop_column("book_copies", "status")

    # Drop the enum type
    bookcopystatus.drop(op.get_bind(), checkfirst=True)