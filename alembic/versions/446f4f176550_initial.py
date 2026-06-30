"""initial

Revision ID: 446f4f176550
Revises:
Create Date: 2026-07-01 00:13:33.746530

"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op


# revision identifiers, used by Alembic.
revision: str = '446f4f176550'
down_revision: Union[str, Sequence[str], None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        'setting',
        sa.Column('key', sa.String(), nullable=False),
        sa.Column('value', sa.String(), nullable=False),
        sa.PrimaryKeyConstraint('key'),
    )
    op.create_table(
        'writer',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('email', sa.String(), nullable=False),
        sa.Column('password', sa.String(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index('ix_writer_email', 'writer', ['email'], unique=True)
    op.create_table(
        'image',
        sa.Column('id', sa.String(), nullable=False),
        sa.Column('data', sa.LargeBinary(length=16_777_215), nullable=False),
        sa.Column('mime_type', sa.String(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_table(
        'blog',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('slug', sa.String(), nullable=True),
        sa.Column('title', sa.String(), nullable=False),
        sa.Column('content_delta', sa.Text(), nullable=False),
        sa.Column('content_html', sa.Text(), nullable=False),
        sa.Column('content_text', sa.Text(), nullable=False),
        sa.Column('status', sa.String(), nullable=False),
        sa.Column('views', sa.Integer(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index('ix_blog_slug', 'blog', ['slug'], unique=True)


def downgrade() -> None:
    op.drop_index('ix_blog_slug', table_name='blog')
    op.drop_table('blog')
    op.drop_table('image')
    op.drop_index('ix_writer_email', table_name='writer')
    op.drop_table('writer')
    op.drop_table('setting')
