"""Add encounter status workflow

Revision ID: 003
Revises: 002
Create Date: 2025-01-26 00:00:00.000000

This migration:
1. Adds workflow timestamp columns to encounters (opened_at, completed_at, signed_at, reopened_at)
2. Adds signature tracking columns (signed_by_id, signed_by_name)
3. Creates encounter_status_history table for audit trail
4. Migrates existing status values to new clinical workflow statuses
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '003'
down_revision: Union[str, None] = '002'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Add workflow timestamp columns to encounters table
    op.add_column(
        'encounters',
        sa.Column('opened_at', sa.DateTime(), nullable=True)
    )
    op.add_column(
        'encounters',
        sa.Column('completed_at', sa.DateTime(), nullable=True)
    )
    op.add_column(
        'encounters',
        sa.Column('signed_at', sa.DateTime(), nullable=True)
    )
    op.add_column(
        'encounters',
        sa.Column('reopened_at', sa.DateTime(), nullable=True)
    )

    # Add signature tracking columns
    op.add_column(
        'encounters',
        sa.Column('signed_by_id', sa.String(64), nullable=True)
    )
    op.add_column(
        'encounters',
        sa.Column('signed_by_name', sa.String(255), nullable=True)
    )

    # Create encounter_status_history table for audit trail
    op.create_table(
        'encounter_status_history',
        sa.Column('id', sa.String(64), primary_key=True),
        sa.Column('encounter_id', sa.String(64), sa.ForeignKey('encounters.id'), nullable=False, index=True),
        sa.Column('from_status', sa.String(50), nullable=True),  # null for initial creation
        sa.Column('to_status', sa.String(50), nullable=False),
        sa.Column('changed_by_id', sa.String(64), nullable=True),
        sa.Column('changed_by_name', sa.String(255), nullable=True),
        sa.Column('changed_at', sa.DateTime(), nullable=False, server_default=sa.text('now()')),
        sa.Column('reason', sa.Text(), nullable=True),
        sa.Column('ip_address', sa.String(45), nullable=True),  # IPv6 max length
        sa.Column('user_agent', sa.String(500), nullable=True),
        sa.Column('meta_version_id', sa.String(10), nullable=False, server_default='1'),
        sa.Column('meta_last_updated', sa.DateTime(), nullable=False, server_default=sa.text('now()')),
    )

    # Create index on encounter_id + changed_at for efficient lookups
    op.create_index(
        'ix_encounter_status_history_encounter_changed',
        'encounter_status_history',
        ['encounter_id', 'changed_at'],
    )

    # Migrate existing status values to new clinical workflow statuses
    # planned -> scheduled
    # in-progress -> in_progress
    # finished -> completed
    # Others -> scheduled
    op.execute("""
        UPDATE encounters
        SET status = CASE
            WHEN status = 'planned' THEN 'scheduled'
            WHEN status = 'in-progress' THEN 'in_progress'
            WHEN status = 'finished' THEN 'completed'
            WHEN status = 'cancelled' THEN 'scheduled'
            WHEN status = 'entered-in-error' THEN 'scheduled'
            ELSE 'scheduled'
        END
    """)


def downgrade() -> None:
    # Drop encounter_status_history table
    op.drop_index('ix_encounter_status_history_encounter_changed', table_name='encounter_status_history')
    op.drop_table('encounter_status_history')

    # Drop signature columns
    op.drop_column('encounters', 'signed_by_name')
    op.drop_column('encounters', 'signed_by_id')

    # Drop workflow timestamp columns
    op.drop_column('encounters', 'reopened_at')
    op.drop_column('encounters', 'signed_at')
    op.drop_column('encounters', 'completed_at')
    op.drop_column('encounters', 'opened_at')

    # Revert status values to FHIR statuses
    # This is a best-effort reversion
    op.execute("""
        UPDATE encounters
        SET status = CASE
            WHEN status = 'scheduled' THEN 'planned'
            WHEN status = 'in_progress' THEN 'in-progress'
            WHEN status = 'completed' THEN 'finished'
            WHEN status = 'signed' THEN 'finished'
            ELSE 'planned'
        END
    """)
