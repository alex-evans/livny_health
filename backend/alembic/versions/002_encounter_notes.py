"""Add encounter notes

Revision ID: 002
Revises: 001
Create Date: 2025-01-25 00:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = '002'
down_revision: Union[str, None] = '001'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Add note columns to encounters table
    op.add_column(
        'encounters',
        sa.Column('note_content', sa.Text(), nullable=True)
    )
    op.add_column(
        'encounters',
        sa.Column('note_version', sa.Integer(), nullable=False, server_default='1')
    )
    op.add_column(
        'encounters',
        sa.Column('note_word_count', sa.Integer(), nullable=False, server_default='0')
    )
    op.add_column(
        'encounters',
        sa.Column('note_updated_at', sa.DateTime(), nullable=True)
    )

    # Create encounter_note_versions table for version history
    op.create_table(
        'encounter_note_versions',
        sa.Column('id', sa.String(64), primary_key=True),
        sa.Column('encounter_id', sa.String(64), sa.ForeignKey('encounters.id'), nullable=False, index=True),
        sa.Column('version', sa.Integer(), nullable=False),
        sa.Column('content', sa.Text(), nullable=False, server_default=''),
        sa.Column('word_count', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('save_type', sa.String(20), nullable=False, server_default='auto'),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.text('now()')),
        sa.Column('meta_version_id', sa.String(10), nullable=False, server_default='1'),
        sa.Column('meta_last_updated', sa.DateTime(), nullable=False, server_default=sa.text('now()')),
    )

    # Create index on encounter_id + version for efficient lookups
    op.create_index(
        'ix_encounter_note_versions_encounter_version',
        'encounter_note_versions',
        ['encounter_id', 'version'],
        unique=True
    )


def downgrade() -> None:
    op.drop_index('ix_encounter_note_versions_encounter_version', table_name='encounter_note_versions')
    op.drop_table('encounter_note_versions')
    op.drop_column('encounters', 'note_updated_at')
    op.drop_column('encounters', 'note_word_count')
    op.drop_column('encounters', 'note_version')
    op.drop_column('encounters', 'note_content')
