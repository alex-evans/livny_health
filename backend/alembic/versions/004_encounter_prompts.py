"""Add encounter_prompts table

Revision ID: 004
Revises: 003
Create Date: 2025-01-31 00:00:00.000000

This migration:
1. Creates encounter_prompts table for storing contextual prompts that guide physicians through encounters
2. Includes fields for prompt type, status, viewer section, alert level, and response tracking
3. Creates appropriate indexes for efficient querying
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


# revision identifiers, used by Alembic.
revision: str = '004'
down_revision: Union[str, None] = '003'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Create encounter_prompts table
    op.create_table(
        'encounter_prompts',
        sa.Column('id', sa.String(64), primary_key=True),
        sa.Column('encounter_id', sa.String(64), sa.ForeignKey('encounters.id'), nullable=False, index=True),

        # Prompt classification
        sa.Column('prompt_type', sa.String(50), nullable=False),  # chief_complaint, review, alert, follow_up, assessment, plan, free_text
        sa.Column('prompt_subtype', sa.String(50), nullable=True),  # vitals, medications, a1c_review, etc.

        # Prompt content
        sa.Column('prompt_text', sa.Text(), nullable=False),
        sa.Column('prompt_order', sa.Integer(), nullable=False),

        # Status tracking
        sa.Column('status', sa.String(50), nullable=False, server_default='pending'),  # pending, addressed, skipped, deferred
        sa.Column('response_data', postgresql.JSONB(), nullable=True),

        # Display configuration
        sa.Column('viewer_section', sa.String(50), nullable=True),  # subjective, objective, assessment, plan
        sa.Column('alert_level', sa.String(50), nullable=True),  # critical, high, medium, low
        sa.Column('is_skippable', sa.Boolean(), nullable=False, server_default='true'),

        # Source tracking
        sa.Column('source_reference', sa.String(255), nullable=True),  # Reference to source entity (e.g., condition ID)
        sa.Column('source_context', postgresql.JSONB(), nullable=True),  # Additional context about the source

        # Resolution tracking
        sa.Column('addressed_at', sa.DateTime(), nullable=True),
        sa.Column('addressed_by_id', sa.String(64), nullable=True),

        # Metadata
        sa.Column('meta_version_id', sa.String(10), nullable=False, server_default='1'),
        sa.Column('meta_last_updated', sa.DateTime(), nullable=False, server_default=sa.text('now()')),
    )

    # Create composite index for ordering within an encounter
    op.create_index(
        'ix_encounter_prompts_encounter_order',
        'encounter_prompts',
        ['encounter_id', 'prompt_order'],
    )

    # Create composite index for filtering by encounter and status
    op.create_index(
        'ix_encounter_prompts_encounter_status',
        'encounter_prompts',
        ['encounter_id', 'status'],
    )


def downgrade() -> None:
    # Drop indexes
    op.drop_index('ix_encounter_prompts_encounter_status', table_name='encounter_prompts')
    op.drop_index('ix_encounter_prompts_encounter_order', table_name='encounter_prompts')

    # Drop table
    op.drop_table('encounter_prompts')
