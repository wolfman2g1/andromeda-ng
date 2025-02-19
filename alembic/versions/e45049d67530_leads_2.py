"""leads 2

Revision ID: e45049d67530
Revises: f88d015b7b28
Create Date: 2025-02-19 16:18:51.897661

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'e45049d67530'
down_revision: Union[str, None] = 'f88d015b7b28'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    pass


def downgrade() -> None:
    pass
