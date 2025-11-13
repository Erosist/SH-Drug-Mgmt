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

API 示例（含角色）

- 注册

   POST /api/auth/register
   Body (application/json): { "username": "alice", "email": "a@b.com", "password": "secret", "role": "pharmacy|supplier|logistics|regulator|unauth" }

- 登录

  POST /api/auth/login
  Body (application/json): { "username": "alice", "password": "secret" }
   Response: { "access_token": "...", "user": { "id":1, "username":"alice", "email":"a@b.com", "role":"pharmacy", ... } }

- 获取当前用户

  GET /api/auth/me
  Header: Authorization: Bearer <access_token>

前端对接

- 在前端登录成功后，保存返回的 access_token（例如 localStorage），并在后续请求中通过 Authorization: Bearer <token> 发送。

后续改进建议

- 使用 Flask-Migrate 管理数据库迁移
- 添加邮箱验证、重置密码
- 使用 refresh token 来延长登录会话
- 将 SECRET_KEY、JWT_SECRET_KEY 存放到更安全的机密管理中
