"""repair token_blacklist

Revision ID: fa9a350483f1
Revises: 308b18df3b50
Create Date: 2026-02-11 16:38:49.486271

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'fa9a350483f1'
down_revision: Union[str, Sequence[str], None] = '308b18df3b50'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass
