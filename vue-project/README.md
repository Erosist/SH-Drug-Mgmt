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

- 用户注册、登录，返回 JWT access_token（后端）。注册时可选填手机号，便于短信找回密码
- 获取当前登录用户信息 /api/auth/me（需 Authorization: Bearer <token>）
- 角色字段 role（pharmacy｜supplier｜logistics｜regulator｜unauth），用于前端跳转
- 前端路由守卫（meta.requiresAuth）：未登录访问受限页会被重定向至登录页
- 登录成功后根据角色跳转到对应页面（见 `src/utils/roleRoute.js`）
- 登录用户可在“修改密码”页面安全地更新口令（需旧密码验证，新密码须满足大小写+数字、至少8位），修改成功后自动退出重新登录
- “忘记密码”页面支持邮箱或手机号验证码找回，验证码有效期10分钟，并在开发模式下返回 `debug_code` 便于调试
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
{
	"username": "alice",
	"email": "a@b.com",
	"phone": "13800138000", // 可选
	"password": "Secret123",
	"role": "pharmacy"
}
```

- 成功（201）：

```json
{ "msg": "user created", "user": { "id":1, "username":"alice", "email":"a@b.com", "role":"pharmacy", "created_at":"..." } }
```

2）登录

- 路径：`POST /api/auth/login`
- Body（JSON）：

```json
{ "username": "alice", "password": "Secret123" }
```

- 成功：

```json
{ "access_token": "<JWT>", "user": { "id":1, "username":"alice", "email":"a@b.com", "role":"pharmacy", "created_at":"..." } }
```

3）当前用户

- 路径：`GET /api/auth/me`
- Header：`Authorization: Bearer <access_token>`
- 成功：`{ "user": { ... } }`

4）修改密码（需登录）

- 路径：`POST /api/auth/change-password`
- Header：`Authorization: Bearer <access_token>`
- Body：`{ "old_password": "旧密码", "new_password": "新密码" }`
- 说明：新密码需至少8位且同时包含大小写字母和数字，修改成功后前端会清除本地 token 并要求重新登录。

5）找回密码 - 发送验证码

- 路径：`POST /api/auth/request-reset-code`
- Body：

```json
{
	"identifier": "alice 或注册邮箱/手机号",
	"channel": "email 或 phone",
	"contact": "与账户绑定一致的邮箱或手机号"
}
```

- 响应：`{ "msg": "验证码已发送", "expires_in": 600, "debug_code": "123456" }`（debug_code 仅在 DEBUG 模式下返回）。

6）找回密码 - 验证并重置

- 路径：`POST /api/auth/reset-password`
- Body：

```json
{
	"identifier": "alice",
	"channel": "email",
	"contact": "a@b.com",
	"code": "123456",
	"new_password": "Secret123"
}
```

- 验证通过后即刻更新密码，并使验证码失效。

常见错误
- 400 参数缺失/非法（如缺少 username/password 或 role 无效）
- 401 未授权（token 缺失或失效、用户名或密码错误）
- 404 用户不存在

## 密码流程验证指引

以下示例基于默认后端地址 `http://127.0.0.1:5000`。若修改了端口或部署方式，请同步替换 URL。

1）申请验证码

```bash
curl -X POST http://127.0.0.1:5000/api/auth/request-reset-code \
	-H "Content-Type: application/json" \
	-d '{
		"identifier": "alice",
		"channel": "email",
		"contact": "a@b.com"
	}'
```

返回体包含 `expires_in`（秒）和 DEBUG 模式下的 `debug_code`，后者可直接作为下一步验证码。

2）使用验证码重置密码

```bash
curl -X POST http://127.0.0.1:5000/api/auth/reset-password \
	-H "Content-Type: application/json" \
	-d '{
		"identifier": "alice",
		"channel": "email",
		"contact": "a@b.com",
		"code": "123456",
		"new_password": "Secret123"
	}'
```

当返回 `{"msg": "password updated"}` 即表示重置成功，可立刻用新密码登录。

3）登录并获取 token

```bash
curl -X POST http://127.0.0.1:5000/api/auth/login \
	-H "Content-Type: application/json" \
	-d '{
		"username": "alice",
		"password": "Secret123"
	}'
```

响应中的 `access_token` 将在下一步作为 `Authorization: Bearer <token>` 头部。

4）登录用户修改密码

```bash
curl -X POST http://127.0.0.1:5000/api/auth/change-password \
	-H "Content-Type: application/json" \
	-H "Authorization: Bearer <token>" \
	-d '{
		"old_password": "Secret123",
		"new_password": "NewSecret123"
	}'
```

成功后前端会自动登出，需用新密码重新登录。若通过 UI 验证，可在导航栏的“修改密码”入口或登录页的“忘记密码”入口体验同样流程。

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

## 导入示例数据（drugs/inventory/tenants）

项目根目录已经包含 `drugs.json`、`inventory_items.json`、`tenants_pharmacy.json`，可用以下脚本一次性导入到 `backend/instance/data.db`：

```bash
cd backend
python tools/import_seed_data.py
```

脚本会按顺序清空并写入 3 张表。若 JSON 不在根目录，可通过 `--data-dir` 指定所在目录。导入成功后，可用 `python tools/dump_db.py --table drugs --limit 5` 验证。

### 查询 API + 前端展示

- `GET /api/catalog/drugs`：支持 `keyword`、`category`、`prescription_type` 查询药品资料。
- `GET /api/catalog/tenants`：支持 `keyword`、`type`、`is_active` 查询药店/机构信息。
- `GET /api/catalog/inventory`：支持 `keyword`、`tenant_id`、`drug_id` 查询库存批次信息（返回内容附带药品与药店名称）。

以上接口统一接受 `page`、`per_page` 分页参数，返回 `{ items, page, per_page, total }` 结构。前端 `库存管理` 页面新增“真实数据查询”板块，调用这些接口即可在 UI 中搜索药品、药店与库存记录。

- 库存查看方式调整：在“库存管理”页选择“药店/机构”查询，点击列表中的“查看库存”即可跳转到 `/tenants/:tenantId` 二级页面。页面会先展示该药店的基本信息与库存汇总，再分页展示其所有批次库存（同样来自上述 API）。

## 安全与可改进项

- 强化密码策略、登录失败重试限制、二次验证等
- 对验证码发送增加频率限制与真实短信/邮件通道
- 区分 Access Token / Refresh Token，完善续期策略
- 使用 Flask-Migrate 做结构化迁移；生产环境使用更可靠的数据库
- 使用 HTTPS；将 SECRET_KEY / JWT_SECRET_KEY 存入安全的配置中心
- 对接真实用户体系、完善权限（RBAC）到接口层

---

若需帮助或想扩展新页面/接口，在 `src/views` 新增页面并在 `src/router/index.js` 注册路由；  
后端可在 `backend` 新增蓝图并注册到 `create_app`。
