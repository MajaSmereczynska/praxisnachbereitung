"""add damage_notes

Revision ID: a3aafca403d1
Revises: 
Create Date: 2025-11-23 09:51:29.360674

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'a3aafca403d1'
down_revision: Union[str, Sequence[str], None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Add the 'damage_notes' column to 'assignment' table
    # It is nullable=True because not every return has a damage.
    op.add_column('assignment', sa.Column('damage_notes', sa.Text(), nullable=True))


def downgrade() -> None:
    # Remove the column if we revert
    op.drop_column('assignment', 'damage_notes')