"""add content to posts table

Revision ID: 767c4f9ce48e
Revises: 4814d7369fcf
Create Date: 2026-10-10 06:03:28.928047

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '767c4f9ce48e'
down_revision: Union[str, Sequence[str], None] = '4814d7369fcf'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.add_column("posts", sa.Column("content", sa.String(), nullable=False))
    pass


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_column("posts", "content")
    pass
