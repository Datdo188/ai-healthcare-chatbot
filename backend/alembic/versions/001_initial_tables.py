"""initial tables

Revision ID: 001_initial_tables
Revises:
Create Date: 2026-05-23
"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "001_initial_tables"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "users",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("email", sa.String(length=255), nullable=False),
        sa.Column("full_name", sa.String(length=255), nullable=True),
        sa.Column("hashed_password", sa.String(length=255), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint("id"),
    )

    op.create_index(
        op.f("ix_users_id"),
        "users",
        ["id"],
        unique=False
    )

    op.create_index(
        op.f("ix_users_email"),
        "users",
        ["email"],
        unique=True
    )

    op.create_table(
        "chat_messages",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=True),
        sa.Column("question", sa.Text(), nullable=False),
        sa.Column("answer", sa.Text(), nullable=False),
        sa.Column("sources_json", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(
            ["user_id"],
            ["users.id"],
        ),
        sa.PrimaryKeyConstraint("id"),
    )

    op.create_index(
        op.f("ix_chat_messages_id"),
        "chat_messages",
        ["id"],
        unique=False
    )

    op.create_table(
        "uploaded_documents",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=True),
        sa.Column("original_filename", sa.String(length=500), nullable=False),
        sa.Column("saved_filename", sa.String(length=500), nullable=False),
        sa.Column("path", sa.String(length=1000), nullable=False),
        sa.Column("status", sa.String(length=50), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(
            ["user_id"],
            ["users.id"],
        ),
        sa.PrimaryKeyConstraint("id"),
    )

    op.create_index(
        op.f("ix_uploaded_documents_id"),
        "uploaded_documents",
        ["id"],
        unique=False
    )


def downgrade() -> None:
    op.drop_index(
        op.f("ix_uploaded_documents_id"),
        table_name="uploaded_documents"
    )
    op.drop_table("uploaded_documents")

    op.drop_index(
        op.f("ix_chat_messages_id"),
        table_name="chat_messages"
    )
    op.drop_table("chat_messages")

    op.drop_index(
        op.f("ix_users_email"),
        table_name="users"
    )
    op.drop_index(
        op.f("ix_users_id"),
        table_name="users"
    )
    op.drop_table("users")