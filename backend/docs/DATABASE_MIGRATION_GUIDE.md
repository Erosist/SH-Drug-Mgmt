# 数据库迁移指南 - 添加经纬度字段

## 问题说明

测试时遇到错误：
```
sqlite3.OperationalError: no such column: tenants.latitude
```

这是因为数据库中的 `tenants` 表还没有 `latitude` 和 `longitude` 字段。

---

## 解决方案（3种方法，选择其一）

### 方法 1：使用快速迁移脚本（推荐，最简单）

```bash
cd e:\ShareCache\lyx\Thild\软件工程\小组\SH\backend
python apply_coordinates_migration.py
```

**优点：**
- ✅ 最简单，一键完成
- ✅ 不依赖 Flask-Migrate
- ✅ 直接修改 SQLite 数据库

**检查迁移状态：**
```bash
python apply_coordinates_migration.py --check
```

---

### 方法 2：使用 Flask-Migrate（标准方式）

```bash
cd e:\ShareCache\lyx\Thild\软件工程\小组\SH\backend

# 方式 A：使用 flask 命令
flask db upgrade

# 方式 B：使用 Python 脚本
python migrate_db.py
```

**优点：**
- ✅ 标准的 Flask 迁移流程
- ✅ 可以跟踪迁移历史
- ✅ 支持回滚

---

### 方法 3：手动 SQL（备用方案）

如果以上方法都不行，可以手动执行 SQL：

```bash
# 打开 SQLite 数据库
sqlite3 instance/data.db

# 执行 SQL
ALTER TABLE tenants ADD COLUMN latitude FLOAT;
ALTER TABLE tenants ADD COLUMN longitude FLOAT;

# 验证
PRAGMA table_info(tenants);

# 退出
.quit
```

---

## 执行步骤（推荐方法 1）

### 第 1 步：运行迁移脚本

```bash
cd e:\ShareCache\lyx\Thild\软件工程\小组\SH\backend
python apply_coordinates_migration.py
```

**预期输出：**
```
============================================================
数据库迁移工具 - 添加租户坐标字段
============================================================
连接到数据库: instance/data.db

当前 tenants 表的字段: id, name, type, unified_social_credit_code, ...

正在添加字段...
  添加 latitude 字段...
  ✓ latitude 字段添加成功
  添加 longitude 字段...
  ✓ longitude 字段添加成功

更新后的字段: id, name, type, ..., latitude, longitude

✓ 数据库迁移成功！

现在可以运行测试了:
  python scripts/test_nearby_api.py
```

### 第 2 步：验证迁移

```bash
python apply_coordinates_migration.py --check
```

**预期输出：**
```
tenants 表结构:
------------------------------------------------------------
列名                  类型            可空      
------------------------------------------------------------
id                   INTEGER         NO        
name                 VARCHAR(160)    NO        
...
latitude             FLOAT           YES       
longitude            FLOAT           YES       
------------------------------------------------------------

✓ 经纬度字段已存在
```

### 第 3 步：运行测试

```bash
python scripts/test_nearby_api.py
```

---

## 常见问题

### Q1: 运行迁移时提示 "数据库文件不存在"

**原因：** 数据库文件路径不对

**解决：**
```bash
# 检查数据库文件是否存在
dir instance\data.db

# 如果不存在，可能需要先初始化数据库
python
>>> from app import create_app
>>> from extensions import db
>>> app = create_app()
>>> with app.app_context():
...     db.create_all()
>>> exit()
```

### Q2: Flask-Migrate 报错

**错误信息：**
```
alembic.util.exc.CommandError: Can't locate revision identified by 'xxxxx'
```

**解决：**
```bash
# 重置迁移历史
flask db stamp head

# 或使用快速迁移脚本（方法1）
python apply_coordinates_migration.py
```

### Q3: 字段已存在但测试仍然报错

**解决：**
```bash
# 1. 检查是否连接到正确的数据库
python apply_coordinates_migration.py --check

# 2. 重启 Python 环境
# 3. 清除缓存
del __pycache__
del *.pyc

# 4. 重新运行测试
python scripts/test_nearby_api.py
```

---

## 迁移后的验证清单

- [ ] 运行迁移脚本成功
- [ ] 检查命令确认字段存在
- [ ] 测试脚本不再报错
- [ ] 可以成功创建带坐标的租户

---

## 快速命令总结

```bash
# 1. 应用迁移
python apply_coordinates_migration.py

# 2. 检查迁移状态
python apply_coordinates_migration.py --check

# 3. 运行测试
python scripts/test_nearby_api.py

# 4. 批量更新现有数据的坐标
python tools/batch_update_locations.py --stats
```

---

## 迁移文件说明

已创建的迁移相关文件：

1. **apply_coordinates_migration.py** - 快速迁移脚本（推荐）
   - 直接修改 SQLite 数据库
   - 不依赖 Flask-Migrate

2. **migrate_db.py** - Flask-Migrate 迁移脚本
   - 使用 Flask-Migrate 标准流程
   - 适合生产环境

3. **migrations/versions/add_tenant_coords_*.py** - Alembic 迁移文件
   - Flask-Migrate 使用的迁移定义
   - 包含 upgrade 和 downgrade 逻辑

---

## 下一步

迁移成功后：

1. ✅ 运行 API 测试确认功能正常
2. ✅ 使用批量工具为现有租户添加坐标
3. ✅ 开始前端集成

---

**现在请运行迁移脚本：**

```bash
python apply_coordinates_migration.py
```

然后告诉我结果！
