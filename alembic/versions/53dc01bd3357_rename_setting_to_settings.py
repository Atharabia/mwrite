"""rename setting to settings

Revision ID: 53dc01bd3357
Revises: 446f4f176550
Create Date: 2026-07-11 00:00:00.000000

"""
from typing import Sequence
from typing import Union

from alembic import op

revision: str = '53dc01bd3357'
down_revision: Union[str, Sequence[str], None] = '446f4f176550'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.rename_table('setting', 'settings')


def downgrade() -> None:
    op.rename_table('settings', 'setting')
