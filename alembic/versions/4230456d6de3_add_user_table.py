"""add user table

Revision ID: 4230456d6de3
Revises: 767c4f9ce48e
Create Date: 2026-10-10 06:11:07.910304

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '4230456d6de3'
down_revision: Union[str, Sequence[str], None] = '767c4f9ce48e'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.create_table("users", 
                    sa.Column("id", sa.Integer(), nullable=False, primary_key=True), 
                    sa.Column("email", sa.String(), nullable=False, unique=True), 
                    sa.Column("password", sa.String(), nullable=False), 
                    sa.Column("created_at", sa.TIMESTAMP(timezone=True), server_default=sa.text("now()"), nullable=False))
    pass


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_table("users")
    pass
