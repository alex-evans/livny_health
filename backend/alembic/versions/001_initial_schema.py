"""Initial schema

Revision ID: 001
Revises:
Create Date: 2024-01-01 00:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = '001'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Create patients table
    op.create_table(
        'patients',
        sa.Column('id', sa.String(64), primary_key=True),
        sa.Column('name_family', sa.String(255), nullable=False, index=True),
        sa.Column('name_given', postgresql.JSONB(), nullable=False, server_default='[]'),
        sa.Column('name_prefix', postgresql.JSONB(), nullable=False, server_default='[]'),
        sa.Column('name_suffix', postgresql.JSONB(), nullable=False, server_default='[]'),
        sa.Column('birth_date', sa.Date(), nullable=True),
        sa.Column('gender', sa.String(20), nullable=False, server_default='unknown'),
        sa.Column('active', sa.Boolean(), nullable=False, server_default='true'),
        sa.Column('identifiers', postgresql.JSONB(), nullable=False, server_default='[]'),
        sa.Column('telecom', postgresql.JSONB(), nullable=False, server_default='[]'),
        sa.Column('address', postgresql.JSONB(), nullable=False, server_default='[]'),
        sa.Column('problem_list', postgresql.JSONB(), nullable=False, server_default='[]'),
        sa.Column('recent_vitals', postgresql.JSONB(), nullable=True),
        sa.Column('insurance', postgresql.JSONB(), nullable=True),
        sa.Column('allergy_review_status', postgresql.JSONB(), nullable=True),
        sa.Column('meta_version_id', sa.String(10), nullable=False, server_default='1'),
        sa.Column('meta_last_updated', sa.DateTime(), nullable=False, server_default=sa.text('now()')),
    )

    # Create practitioners table
    op.create_table(
        'practitioners',
        sa.Column('id', sa.String(64), primary_key=True),
        sa.Column('name_family', sa.String(255), nullable=False, index=True),
        sa.Column('name_given', postgresql.JSONB(), nullable=False, server_default='[]'),
        sa.Column('name_prefix', postgresql.JSONB(), nullable=False, server_default='[]'),
        sa.Column('name_suffix', postgresql.JSONB(), nullable=False, server_default='[]'),
        sa.Column('gender', sa.String(20), nullable=False, server_default='unknown'),
        sa.Column('active', sa.Boolean(), nullable=False, server_default='true'),
        sa.Column('identifiers', postgresql.JSONB(), nullable=False, server_default='[]'),
        sa.Column('telecom', postgresql.JSONB(), nullable=False, server_default='[]'),
        sa.Column('qualifications', postgresql.JSONB(), nullable=False, server_default='[]'),
        sa.Column('meta_version_id', sa.String(10), nullable=False, server_default='1'),
        sa.Column('meta_last_updated', sa.DateTime(), nullable=False, server_default=sa.text('now()')),
    )

    # Create medications table
    op.create_table(
        'medications',
        sa.Column('id', sa.String(64), primary_key=True),
        sa.Column('code', postgresql.JSONB(), nullable=False, server_default='{}'),
        sa.Column('form', sa.String(100), nullable=True),
        sa.Column('strength', sa.String(100), nullable=True),
        sa.Column('is_controlled', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('common_dosing', postgresql.JSONB(), nullable=False, server_default='[]'),
        sa.Column('status', sa.String(50), nullable=False, server_default='active'),
        sa.Column('meta_version_id', sa.String(10), nullable=False, server_default='1'),
        sa.Column('meta_last_updated', sa.DateTime(), nullable=False, server_default=sa.text('now()')),
    )

    # Create medication_requests table
    op.create_table(
        'medication_requests',
        sa.Column('id', sa.String(64), primary_key=True),
        sa.Column('status', sa.String(50), nullable=False, server_default='active', index=True),
        sa.Column('intent', sa.String(50), nullable=False, server_default='order'),
        sa.Column('medication', postgresql.JSONB(), nullable=False, server_default='{}'),
        sa.Column('brand_name', sa.String(255), nullable=True),
        sa.Column('strength', sa.String(100), nullable=True),
        sa.Column('form', sa.String(50), nullable=True),
        sa.Column('is_controlled', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('subject_id', sa.String(64), sa.ForeignKey('patients.id'), nullable=False, index=True),
        sa.Column('encounter_id', sa.String(64), nullable=True),
        sa.Column('requester', postgresql.JSONB(), nullable=True),
        sa.Column('authored_on', sa.DateTime(), nullable=False, server_default=sa.text('now()')),
        sa.Column('dosage_instruction', postgresql.JSONB(), nullable=False, server_default='[]'),
        sa.Column('dispense_quantity', postgresql.JSONB(), nullable=True),
        sa.Column('dispense_refills', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('status_reason', sa.String(255), nullable=True),
        sa.Column('pharmacy', sa.String(255), nullable=True),
        sa.Column('indication', sa.String(500), nullable=True),
        sa.Column('prescriber_notes', sa.String(1000), nullable=True),
        sa.Column('drug_class', sa.String(100), nullable=True),
        sa.Column('meta_version_id', sa.String(10), nullable=False, server_default='1'),
        sa.Column('meta_last_updated', sa.DateTime(), nullable=False, server_default=sa.text('now()')),
    )

    # Create allergy_intolerances table
    op.create_table(
        'allergy_intolerances',
        sa.Column('id', sa.String(64), primary_key=True),
        sa.Column('patient_id', sa.String(64), sa.ForeignKey('patients.id'), nullable=False, index=True),
        sa.Column('code', postgresql.JSONB(), nullable=False, server_default='{}'),
        sa.Column('category', sa.String(50), nullable=False, server_default='medication'),
        sa.Column('criticality', sa.String(50), nullable=False, server_default='high'),
        sa.Column('clinical_status', sa.String(50), nullable=False, server_default='active'),
        sa.Column('verification_status', sa.String(50), nullable=False, server_default='confirmed'),
        sa.Column('reactions', postgresql.JSONB(), nullable=False, server_default='[]'),
        sa.Column('recorded_date', sa.DateTime(), nullable=True),
        sa.Column('recorder', postgresql.JSONB(), nullable=True),
        sa.Column('last_updated', sa.DateTime(), nullable=True),
        sa.Column('notes', sa.String(1000), nullable=True),
        sa.Column('meta_version_id', sa.String(10), nullable=False, server_default='1'),
        sa.Column('meta_last_updated', sa.DateTime(), nullable=False, server_default=sa.text('now()')),
    )

    # Create encounters table
    op.create_table(
        'encounters',
        sa.Column('id', sa.String(64), primary_key=True),
        sa.Column('status', sa.String(50), nullable=False, server_default='planned', index=True),
        sa.Column('encounter_class', sa.String(20), nullable=False, server_default='AMB'),
        sa.Column('type', postgresql.JSONB(), nullable=True),
        sa.Column('subject_id', sa.String(64), sa.ForeignKey('patients.id'), nullable=False, index=True),
        sa.Column('participants', postgresql.JSONB(), nullable=False, server_default='[]'),
        sa.Column('period', postgresql.JSONB(), nullable=True),
        sa.Column('reason', postgresql.JSONB(), nullable=False, server_default='[]'),
        sa.Column('chief_complaint', sa.String(500), nullable=True),
        sa.Column('appointment_id', sa.String(64), nullable=True),
        sa.Column('meta_version_id', sa.String(10), nullable=False, server_default='1'),
        sa.Column('meta_last_updated', sa.DateTime(), nullable=False, server_default=sa.text('now()')),
    )

    # Create appointments table
    op.create_table(
        'appointments',
        sa.Column('id', sa.String(64), primary_key=True),
        sa.Column('status', sa.String(50), nullable=False, server_default='booked', index=True),
        sa.Column('appointment_type', postgresql.JSONB(), nullable=True),
        sa.Column('start', sa.DateTime(), nullable=False, index=True),
        sa.Column('end', sa.DateTime(), nullable=True),
        sa.Column('duration_minutes', sa.Integer(), nullable=False, server_default='30'),
        sa.Column('reason', sa.String(500), nullable=True),
        sa.Column('participants', postgresql.JSONB(), nullable=False, server_default='[]'),
        sa.Column('flags', postgresql.JSONB(), nullable=False, server_default='[]'),
        sa.Column('is_double_booked', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('meta_version_id', sa.String(10), nullable=False, server_default='1'),
        sa.Column('meta_last_updated', sa.DateTime(), nullable=False, server_default=sa.text('now()')),
    )

    # Create lab_results table
    op.create_table(
        'lab_results',
        sa.Column('id', sa.String(64), primary_key=True),
        sa.Column('test_name', sa.String(255), nullable=False, index=True),
        sa.Column('test_code', sa.String(50), nullable=True),
        sa.Column('value', sa.String(100), nullable=False),
        sa.Column('unit', sa.String(50), nullable=False),
        sa.Column('reference_range', sa.String(100), nullable=False),
        sa.Column('status', sa.String(50), nullable=False, server_default='normal', index=True),
        sa.Column('subject_id', sa.String(64), sa.ForeignKey('patients.id'), nullable=False, index=True),
        sa.Column('collection_date', sa.DateTime(), nullable=False, index=True),
        sa.Column('performing_lab', sa.String(255), nullable=True),
        sa.Column('panel_id', sa.String(64), nullable=True),
        sa.Column('last_updated', sa.DateTime(), nullable=True),
        sa.Column('acknowledged', sa.Boolean(), nullable=False, server_default='true'),
        sa.Column('acknowledged_by', sa.String(64), nullable=True),
        sa.Column('acknowledged_at', sa.DateTime(), nullable=True),
        sa.Column('meta_version_id', sa.String(10), nullable=False, server_default='1'),
        sa.Column('meta_last_updated', sa.DateTime(), nullable=False, server_default=sa.text('now()')),
    )

    # Create vital_signs table
    op.create_table(
        'vital_signs',
        sa.Column('id', sa.String(64), primary_key=True),
        sa.Column('vital_type', sa.String(50), nullable=False, index=True),
        sa.Column('value', sa.Float(), nullable=False),
        sa.Column('unit', sa.String(50), nullable=False),
        sa.Column('status', sa.String(50), nullable=False, server_default='normal', index=True),
        sa.Column('subject_id', sa.String(64), sa.ForeignKey('patients.id'), nullable=False, index=True),
        sa.Column('recorded_at', sa.DateTime(), nullable=False, index=True),
        sa.Column('recorded_by', sa.String(255), nullable=True),
        sa.Column('location', sa.String(255), nullable=True),
        sa.Column('meta_version_id', sa.String(10), nullable=False, server_default='1'),
        sa.Column('meta_last_updated', sa.DateTime(), nullable=False, server_default=sa.text('now()')),
    )

    # Create visit_notes table
    op.create_table(
        'visit_notes',
        sa.Column('id', sa.String(64), primary_key=True),
        sa.Column('encounter_id', sa.String(64), nullable=False, index=True),
        sa.Column('subject_id', sa.String(64), sa.ForeignKey('patients.id'), nullable=False, index=True),
        sa.Column('visit_type', sa.String(50), nullable=False, server_default='office_visit'),
        sa.Column('status', sa.String(50), nullable=False, server_default='completed'),
        sa.Column('date', sa.DateTime(), nullable=False, index=True),
        sa.Column('chief_complaint', sa.String(500), nullable=False, server_default=''),
        sa.Column('location', sa.String(255), nullable=True),
        sa.Column('duration', sa.Integer(), nullable=True),
        sa.Column('provider', postgresql.JSONB(), nullable=True),
        sa.Column('diagnoses', postgresql.JSONB(), nullable=False, server_default='[]'),
        sa.Column('soap_note', postgresql.JSONB(), nullable=True),
        sa.Column('vitals', postgresql.JSONB(), nullable=True),
        sa.Column('medications', postgresql.JSONB(), nullable=False, server_default='[]'),
        sa.Column('orders', postgresql.JSONB(), nullable=False, server_default='[]'),
        sa.Column('notes', sa.String(2000), nullable=True),
        sa.Column('has_critical_findings', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('critical_findings_summary', sa.String(500), nullable=True),
        sa.Column('has_follow_up_required', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('follow_up_summary', sa.String(500), nullable=True),
        sa.Column('meta_version_id', sa.String(10), nullable=False, server_default='1'),
        sa.Column('meta_last_updated', sa.DateTime(), nullable=False, server_default=sa.text('now()')),
    )

    # Create imaging_studies table
    op.create_table(
        'imaging_studies',
        sa.Column('id', sa.String(64), primary_key=True),
        sa.Column('patient_id', sa.String(64), sa.ForeignKey('patients.id'), nullable=False, index=True),
        sa.Column('accession_number', sa.String(64), nullable=True),
        sa.Column('modality', sa.String(20), nullable=False, server_default='XR', index=True),
        sa.Column('modality_name', sa.String(100), nullable=False, server_default=''),
        sa.Column('body_part', sa.String(100), nullable=False, server_default=''),
        sa.Column('study_date', sa.DateTime(), nullable=False, index=True),
        sa.Column('facility', sa.String(255), nullable=False, server_default=''),
        sa.Column('ordering_provider', sa.String(255), nullable=False, server_default=''),
        sa.Column('reading_radiologist', sa.String(255), nullable=True),
        sa.Column('indication', sa.String(500), nullable=False, server_default=''),
        sa.Column('series_count', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('image_count', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('has_images', sa.Boolean(), nullable=False, server_default='true'),
        sa.Column('report_status', sa.String(50), nullable=False, server_default='pending'),
        sa.Column('report', postgresql.JSONB(), nullable=True),
        sa.Column('meta_version_id', sa.String(10), nullable=False, server_default='1'),
        sa.Column('meta_last_updated', sa.DateTime(), nullable=False, server_default=sa.text('now()')),
    )

    # Create social_family_histories table
    op.create_table(
        'social_family_histories',
        sa.Column('id', sa.String(64), primary_key=True),
        sa.Column('subject_id', sa.String(64), sa.ForeignKey('patients.id'), nullable=False, index=True, unique=True),
        sa.Column('social_history', postgresql.JSONB(), nullable=False, server_default='{}'),
        sa.Column('family_history', postgresql.JSONB(), nullable=False, server_default='{}'),
        sa.Column('risk_assessments', postgresql.JSONB(), nullable=False, server_default='[]'),
        sa.Column('meta_version_id', sa.String(10), nullable=False, server_default='1'),
        sa.Column('meta_last_updated', sa.DateTime(), nullable=False, server_default=sa.text('now()')),
    )

    # Create clinical_alerts table
    op.create_table(
        'clinical_alerts',
        sa.Column('id', sa.String(64), primary_key=True),
        sa.Column('patient_id', sa.String(64), sa.ForeignKey('patients.id'), nullable=False, index=True),
        sa.Column('alert_type', sa.String(50), nullable=False, server_default='critical_lab'),
        sa.Column('severity', sa.String(50), nullable=False, server_default='medium', index=True),
        sa.Column('status', sa.String(50), nullable=False, server_default='active', index=True),
        sa.Column('title', sa.String(255), nullable=False, server_default=''),
        sa.Column('description', sa.String(1000), nullable=False, server_default=''),
        sa.Column('generated_at', sa.DateTime(), nullable=False, server_default=sa.text('now()')),
        sa.Column('source', sa.String(100), nullable=False, server_default=''),
        sa.Column('source_id', sa.String(64), nullable=False, server_default=''),
        sa.Column('source_link', sa.String(500), nullable=True),
        sa.Column('context', postgresql.JSONB(), nullable=False, server_default='{}'),
        sa.Column('recommended_actions', postgresql.JSONB(), nullable=False, server_default='[]'),
        sa.Column('acknowledgment', postgresql.JSONB(), nullable=True),
        sa.Column('dismissed_at', sa.DateTime(), nullable=True),
        sa.Column('dismissed_by', sa.String(64), nullable=True),
        sa.Column('dismissed_reason', sa.String(500), nullable=True),
        sa.Column('meta_version_id', sa.String(10), nullable=False, server_default='1'),
        sa.Column('meta_last_updated', sa.DateTime(), nullable=False, server_default=sa.text('now()')),
    )


def downgrade() -> None:
    op.drop_table('clinical_alerts')
    op.drop_table('social_family_histories')
    op.drop_table('imaging_studies')
    op.drop_table('visit_notes')
    op.drop_table('vital_signs')
    op.drop_table('lab_results')
    op.drop_table('appointments')
    op.drop_table('encounters')
    op.drop_table('allergy_intolerances')
    op.drop_table('medication_requests')
    op.drop_table('medications')
    op.drop_table('practitioners')
    op.drop_table('patients')
