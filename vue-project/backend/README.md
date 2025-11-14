# Flask Auth Backend (示例)

一个最小的 Flask 后端示例，实现注册、登录并返回 JWT token，方便与前端（例如你的 Vue 项目）对接。

快速开始

1. 进入 backend 目录：

   ```bash
   cd backend
   ```

2. 创建虚拟环境并安装依赖（Windows cmd 示例）：

   ```cmd
   python -m venv .venv
   .venv\Scripts\activate
   pip install -r requirements.txt
   ```

3. 复制环境文件并修改（可选）：

   ```cmd
   copy .env.example .env
   ```

4. 初始化数据库并运行：

   ```cmd
   (这个可能不成功，建议直接python run.py)
   set FLASK_APP=run.py
   set FLASK_ENV=development
   flask run
   ```

或者运行：

   ```cmd
   python run.py
   ```

## 数据库升级提示

- 2025.11 起新增 `users.phone` 字段以及 `password_reset_codes` 表。
- 仍使用 SQLite 的情况，可重新运行 `python run.py`，脚本会自动执行缺失列/索引与表的创建。
- 如果你在生产环境中使用其他数据库，建议通过 `Flask-Migrate` 生成并执行迁移脚本（`flask db migrate && flask db upgrade`）。

API 示例（含角色 & 密码管理）

- 注册

   POST /api/auth/register
    Body (application/json): { "username": "alice", "email": "a@b.com", "phone": "13800138000", "password": "Secret123", "role": "pharmacy|supplier|logistics|regulator|unauth" }

- 登录

   POST /api/auth/login
   Body (application/json): { "username": "alice", "password": "Secret123" }
   Response: { "access_token": "...", "user": { "id":1, "username":"alice", "email":"a@b.com", "role":"pharmacy", ... } }

- 获取当前用户

  GET /api/auth/me
  Header: Authorization: Bearer <access_token>

- 修改密码

   POST /api/auth/change-password
   Header: Authorization: Bearer <access_token>
   Body: { "old_password": "旧密码", "new_password": "新密码" }
   说明：新密码需至少8位并包含大小写字母与数字；修改成功后客户端需重新登录。

- 找回密码（发送验证码）

   POST /api/auth/request-reset-code
   Body: { "identifier": "用户名/邮箱/手机号", "channel": "email|phone", "contact": "注册时绑定的邮箱或手机号" }
   返回：`expires_in=600` 表示验证码10分钟有效，开发模式额外返回 `debug_code` 便于调试。

- 找回密码（验证并重置）

   POST /api/auth/reset-password
   Body: { "identifier": "alice", "channel": "email", "contact": "a@b.com", "code": "123456", "new_password": "Secret123" }
   验证成功后立即更新密码并使验证码失效。

前端对接

- 在前端登录成功后，保存返回的 access_token（例如 localStorage），并在后续请求中通过 Authorization: Bearer <token> 发送。

后续改进建议

- 使用 Flask-Migrate 管理数据库迁移
- 对验证码发送增加节流 / 接入真实邮箱或短信网关
- 添加邮箱验证、重置密码
- 使用 refresh token 来延长登录会话
- 将 SECRET_KEY、JWT_SECRET_KEY 存放到更安全的机密管理中
