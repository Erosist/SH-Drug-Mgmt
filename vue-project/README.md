# SH-Drug-Mgmt 前后端项目说明

本项目为“上海药品监管信息平台”的前后端分离示例：
- 前端基于 Vite + Vue 3 + Element Plus + Vue Router 构建，包含登录、注册、库存、流通、数据分析、B2B、智能调度以及基于角色的多端页面。
- 后端提供最小可用的用户认证能力（Flask + JWT + SQLAlchemy），实现注册、登录、获取当前用户信息等接口，并内置角色字段用于前端路由跳转。

> 适合用于课程作业/原型演示，便于快速跑通“登录 -> 进入对应角色界面”的完整链路。

## 技术栈

前端
- Vite 7 + Vue 3 + Vue Router 4
- Element Plus（UI 组件）
- Axios（通用 HTTP 客户端，项目中认证 API 使用 fetch 封装）
- ECharts（可视化，按需使用）

后端
- Flask 2 + Flask-SQLAlchemy 3 + Flask-Migrate 4
- Flask-JWT-Extended（JWT 鉴权）
- SQLite（默认，亦可通过环境变量切换）

## 目录结构（摘录）

```
vue-project/
├─ backend/                  # Flask 后端
│  ├─ app.py                 # 工厂函数 create_app
│  ├─ run.py                 # 开发启动入口（默认 127.0.0.1:5000）
│  ├─ auth.py                # 认证蓝图：/api/auth/*
│  ├─ models.py              # SQLAlchemy 模型（User 等）
│  ├─ extensions.py          # db/migrate/jwt 初始化
│  ├─ config.py              # 配置及环境变量加载
│  ├─ requirements.txt       # 后端依赖
│  └─ .env.example           # 环境变量示例
├─ src/                      # 前端源码
│  ├─ api/auth.js            # 认证 API（基于 fetch，base=/api/auth）
│  ├─ router/index.js        # 路由及守卫（requiresAuth）
│  ├─ utils/roleRoute.js     # 角色 -> 路由映射
│  ├─ views/                 # 业务页面
│  │  ├─ Login.vue           # 登录
│  │  ├─ Register.vue        # 注册
│  │  ├─ Home.vue / Inventory.vue / Circulation.vue / Analysis.vue / B2B.vue / SmartDispatch.vue
│  │  ├─ PharmacyUser.vue / SupplierUser.vue / LogisticsUser.vue / RegulatorUser.vue / UnauthenticatedUser.vue
│  └─ main.js                # Vue 入口（注册 Element Plus、全局 axios 等）
├─ vite.config.js            # Vite 代理：/api -> http://127.0.0.1:5000
├─ package.json              # 前端脚本与依赖
└─ README.md                 # 项目说明（本文件）
```

## 已实现功能

- 用户注册、登录，返回 JWT access_token（后端）
- 获取当前登录用户信息 /api/auth/me（需 Authorization: Bearer <token>）
- 角色字段 role（pharmacy｜supplier｜logistics｜regulator｜unauth），用于前端跳转
- 前端路由守卫（meta.requiresAuth）：未登录访问受限页会被重定向至登录页
- 登录成功后根据角色跳转到对应页面（见 `src/utils/roleRoute.js`）
- 开发环境下通过 Vite 代理将 `/api` 转发至 Flask（避免 CORS）

## 环境要求

- Node.js：遵循 package.json engines，建议 Node 20.19+ 或 22.12+
- npm（或 pnpm/yarn，本文以 npm 为例）
- Python：建议 3.10+（Windows / macOS / Linux 均可）

## 快速开始（Windows cmd）

### 1）启动后端（Flask）

```cmd
cd backend
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
copy .env.example .env
python run.py
```

默认监听 http://127.0.0.1:5000，首次启动会自动创建 SQLite 数据库（`data.db`）。

### 2）启动前端（Vite + Vue 3）

```cmd
npm install
npm run dev
```

默认开发地址 http://localhost:5173。

开发代理已在 `vite.config.js` 中配置：
- 以 `/api` 开头的请求会被转发到 `http://127.0.0.1:5000`
- 例如前端 `fetch('/api/auth/login')` 实际请求后端 `http://127.0.0.1:5000/api/auth/login`

> 注意：`src/main.js` 中有 `axios.defaults.baseURL = "http://localhost:8880"` 的演示配置；认证相关 API 实际通过 `src/api/auth.js` 的 fetch + 代理访问后端，无需依赖该 baseURL。

## API 接口说明（后端）

基地址：`/api/auth`

1）注册

- 路径：`POST /api/auth/register`
- Body（JSON）：

```json
{ "username": "alice", "email": "a@b.com", "password": "secret", "role": "pharmacy" }
```

- 成功（201）：

```json
{ "msg": "user created", "user": { "id":1, "username":"alice", "email":"a@b.com", "role":"pharmacy", "created_at":"..." } }
```

2）登录

- 路径：`POST /api/auth/login`
- Body（JSON）：

```json
{ "username": "alice", "password": "secret" }
```

- 成功：

```json
{ "access_token": "<JWT>", "user": { "id":1, "username":"alice", "email":"a@b.com", "role":"pharmacy", "created_at":"..." } }
```

3）当前用户

- 路径：`GET /api/auth/me`
- Header：`Authorization: Bearer <access_token>`
- 成功：`{ "user": { ... } }`

常见错误
- 400 参数缺失/非法（如缺少 username/password 或 role 无效）
- 401 未授权（token 缺失或失效、用户名或密码错误）
- 404 用户不存在

## 角色与路由

允许的角色（后端校验）：`pharmacy`、`supplier`、`logistics`、`regulator`、`unauth`

前端映射（见 `src/utils/roleRoute.js`）：
- pharmacy -> `/pharmacy`
- supplier -> `/supplier`
- logistics -> `/logistics`
- regulator -> `/regulator`
- unauth -> `/unauth`

路由守卫（见 `src/router/index.js`）：
- 当路由 `meta.requiresAuth = true` 时，若 `localStorage` 中没有 `current_user`（登录成功时写入），则重定向到登录页并附带 `redirect` 查询参数。

## 常见问题（FAQ）

1）接口报 CORS 错误？
- 请确保前端通过 `/api` 访问后端，并且 Vite 代理已生效（仅开发环境）。

2）访问 401 未授权？
- 登录成功后需在请求头携带 `Authorization: Bearer <access_token>`，或使用 `src/api/auth.js` 封装传入 `token`。

3）数据库文件在哪？
- 默认使用项目根目录下 `backend/data.db`（由 `DATABASE_URL=sqlite:///data.db` 控制）。

## 开发脚本

前端 package.json：
- `npm run dev` 开发启动
- `npm run build` 生产构建
- `npm run preview` 本地预览构建产物

后端（任选其一）：
- `python backend/run.py`
- 或在 backend 目录下：`set FLASK_APP=run.py && flask run`

## 安全与可改进项

- 强化密码策略、登录失败重试限制、二次验证等
- 区分 Access Token / Refresh Token，完善续期策略
- 使用 Flask-Migrate 做结构化迁移；生产环境使用更可靠的数据库
- 使用 HTTPS；将 SECRET_KEY / JWT_SECRET_KEY 存入安全的配置中心
- 对接真实用户体系、完善权限（RBAC）到接口层

---

若需帮助或想扩展新页面/接口，在 `src/views` 新增页面并在 `src/router/index.js` 注册路由；  
后端可在 `backend` 新增蓝图并注册到 `create_app`。
