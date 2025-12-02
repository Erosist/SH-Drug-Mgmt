"""add latitude and longitude to tenants

Revision ID: add_tenant_coords
Revises: 673a4053aa3b
Create Date: 2025-12-02 10:00:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'add_tenant_coords'
down_revision = '673a4053aa3b'
branch_labels = None
depends_on = None


def upgrade():
    # 添加经纬度字段到 tenants 表
    with op.batch_alter_table('tenants', schema=None) as batch_op:
        batch_op.add_column(sa.Column('latitude', sa.Float(), nullable=True))
        batch_op.add_column(sa.Column('longitude', sa.Float(), nullable=True))


def downgrade():
    # 回滚时删除字段
    with op.batch_alter_table('tenants', schema=None) as batch_op:
        batch_op.drop_column('longitude')
        batch_op.drop_column('latitude')
