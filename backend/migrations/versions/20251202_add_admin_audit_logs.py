"""Add admin audit log table

Revision ID: a6f9cb97f3a1
Revises: 673a4053aa3b
Create Date: 2025-12-02 10:25:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'a6f9cb97f3a1'
down_revision = '673a4053aa3b'
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        'admin_audit_logs',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('admin_id', sa.Integer(), nullable=False),
        sa.Column('action', sa.String(length=80), nullable=False),
        sa.Column('target_user_id', sa.Integer(), nullable=True),
        sa.Column('resource_type', sa.String(length=80), nullable=True),
        sa.Column('resource_id', sa.String(length=120), nullable=True),
        sa.Column('request_method', sa.String(length=10), nullable=True),
        sa.Column('request_path', sa.String(length=255), nullable=True),
        sa.Column('request_ip', sa.String(length=64), nullable=True),
        sa.Column('details', sa.JSON(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['admin_id'], ['users.id'], ),
        sa.ForeignKeyConstraint(['target_user_id'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    with op.batch_alter_table('admin_audit_logs', schema=None) as batch_op:
        batch_op.create_index(batch_op.f('ix_admin_audit_logs_admin_id'), ['admin_id'], unique=False)
        batch_op.create_index(batch_op.f('ix_admin_audit_logs_target_user_id'), ['target_user_id'], unique=False)


def downgrade():
    with op.batch_alter_table('admin_audit_logs', schema=None) as batch_op:
        batch_op.drop_index(batch_op.f('ix_admin_audit_logs_target_user_id'))
        batch_op.drop_index(batch_op.f('ix_admin_audit_logs_admin_id'))

    op.drop_table('admin_audit_logs')
