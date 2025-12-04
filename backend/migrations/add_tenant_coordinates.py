"""
创建数据库迁移 - 为 Tenant 表添加地理坐标字段

运行方法:
1. 进入 backend 目录: cd backend
2. 初始化迁移（如果还没有）: flask db init
3. 生成迁移: flask db migrate -m "add latitude longitude to tenant"
4. 应用迁移: flask db upgrade

手动 SQL（如果不使用 Flask-Migrate）:
ALTER TABLE tenants ADD COLUMN latitude FLOAT;
ALTER TABLE tenants ADD COLUMN longitude FLOAT;
"""

# 如果使用 alembic 手动创建迁移，可以使用以下模板
migration_template = """
\"\"\"add latitude longitude to tenant

Revision ID: xxxxx
Revises: 
Create Date: 2025-12-02

\"\"\"
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'add_coords_to_tenant'
down_revision = None  # 改为上一个迁移的 revision
branch_labels = None
depends_on = None


def upgrade():
    # 添加经纬度字段
    op.add_column('tenants', sa.Column('latitude', sa.Float(), nullable=True))
    op.add_column('tenants', sa.Column('longitude', sa.Float(), nullable=True))


def downgrade():
    # 回滚时删除字段
    op.drop_column('tenants', 'longitude')
    op.drop_column('tenants', 'latitude')
"""

print(migration_template)
