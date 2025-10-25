# 快速开始指南

## 🚀 项目简介

上海药品信息管理与查询平台是一个基于Vue3 + Flask的B2B药品管理平台。本指南将帮助您快速搭建开发环境并运行项目。

## 📋 系统要求

### 开发环境
- **操作系统：** Windows 10+, macOS 10.15+, Ubuntu 18.04+
- **Node.js：** 18.0+
- **Python：** 3.9+
- **Git：** 2.30+

### 推荐工具
- **IDE：** Visual Studio Code
- **数据库工具：** DBeaver, SQLite Browser
- **API测试：** Postman, Insomnia
- **版本控制：** Git, GitHub Desktop

## 📦 环境准备

### 1. 安装Node.js
```bash
# 使用nvm安装Node.js（推荐）
curl -o- https://raw.githubusercontent.com/nvm-sh/nvm/v0.39.0/install.sh | bash
nvm install 18
nvm use 18

# 或直接从官网下载安装
# https://nodejs.org/
```

### 2. 安装Python
```bash
# Windows: 从官网下载安装包
# https://www.python.org/downloads/

# macOS (使用Homebrew)
brew install python@3.9

# Ubuntu/Debian
sudo apt update
sudo apt install python3.9 python3.9-pip python3.9-venv
```

### 3. 安装Git
```bash
# Windows: 从官网下载安装包
# https://git-scm.com/

# macOS
brew install git

# Ubuntu/Debian
sudo apt install git
```

## 🛠️ 项目搭建

### 1. 克隆项目
```bash
git clone https://github.com/your-org/SH-Drug-Mgmt.git
cd SH-Drug-Mgmt
```

### 2. 安装前端依赖
```bash
cd frontend
npm install
```

### 3. 安装后端依赖
```bash
cd ../backend

# 创建虚拟环境
python -m venv venv

# 激活虚拟环境
# Windows
venv\Scripts\activate
# macOS/Linux
source venv/bin/activate

# 安装依赖
pip install -r requirements.txt
```

### 4. 配置环境变量
```bash
# 后端配置
cd backend
cp .env.example .env

# 编辑配置文件
# 配置数据库连接、JWT密钥等
```

## 🗄️ 数据库设置

### 1. 初始化数据库
```bash
cd backend
python manage.py db init
python manage.py db migrate
python manage.py db upgrade
```

### 2. 导入初始数据
```bash
python scripts/init_data.py
```

### 3. 验证数据库
```bash
# 使用SQLite命令行工具
sqlite3 database/app.db
.tables
.quit
```

## ��‍♂️ 启动项目

### 方式一：分别启动（推荐开发）

#### 启动后端服务
```bash
cd backend
source venv/bin/activate  # Windows: venv\Scripts\activate
python app.py
```
后端服务将在 `http://localhost:5000` 启动

#### 启动前端服务
```bash
cd frontend
npm run dev
```
前端服务将在 `http://localhost:5173` 启动

### 方式二：同时启动
```bash
# 在项目根目录
npm run dev
```

## 🌐 访问应用

### 前端应用
- **地址：** http://localhost:5173
- **默认账户：** admin/admin123

### 后端API
- **API文档：** http://localhost:5000/docs
- **健康检查：** http://localhost:5000/health

### 开发工具
- **数据库管理：** http://localhost:5000/db-admin
- **日志查看：** logs/app.log

## 📱 功能测试

### 1. 用户注册测试
```bash
curl -X POST http://localhost:5000/api/v1/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "username": "testuser",
    "password": "Test123456",
    "email": "test@example.com"
  }'
```

### 2. 用户登录测试
```bash
curl -X POST http://localhost:5000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "username": "testuser",
    "password": "Test123456"
  }'
```

### 3. 药品信息查询
```bash
curl -X GET http://localhost:5000/api/v1/drugs \
  -H "Authorization: Bearer <YOUR_TOKEN>"
```

## 🛠️ 开发工具配置

### VS Code扩展推荐
```json
{
  "recommendations": [
    "vue.volar",
    "bradlc.vscode-tailwindcss",
    "ms-python.python",
    "ms-python.flake8",
    "ms-python.black-formatter",
    "ms-vscode.vscode-json",
    "redhat.vscode-yaml"
  ]
}
```

### VS Code设置
```json
{
  "editor.formatOnSave": true,
  "editor.codeActionsOnSave": {
    "source.fixAll.eslint": true
  },
  "python.defaultInterpreterPath": "./backend/venv/bin/python",
  "python.formatting.provider": "black",
  "python.linting.enabled": true,
  "python.linting.flake8Enabled": true
}
```

## 🐛 常见问题

### 1. Node.js版本问题
```bash
# 清除npm缓存
npm cache clean --force

# 重新安装依赖
rm -rf node_modules package-lock.json
npm install
```

### 2. Python虚拟环境问题
```bash
# 重新创建虚拟环境
rm -rf venv
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### 3. 数据库连接问题
```bash
# 检查数据库文件权限
ls -la database/app.db

# 重新初始化数据库
rm database/app.db
python manage.py db upgrade
```

### 4. 端口占用问题
```bash
# 查找占用端口的进程
# Windows
netstat -ano | findstr :5000
# macOS/Linux
lsof -i :5000

# 杀死进程
# Windows
taskkill /PID <PID> /F
# macOS/Linux
kill -9 <PID>
```

## 📚 开发规范

### Git提交规范
```bash
# 提交格式
<type>(<scope>): <subject>

# 示例
feat(auth): 添加用户注册功能
fix(inventory): 修复库存计算错误
docs(api): 更新API文档
style(frontend): 调整页面样式
refactor(backend): 重构用户服务逻辑
test: 添加单元测试
chore: 更新依赖版本
```

### 代码规范
- **前端：** 遵循Vue3官方风格指南
- **后端：** 遵循PEP8 Python编码规范
- **API：** 遵循RESTful设计原则

### 分支管理
```bash
# 主分支
main          # 生产环境代码
develop       # 开发环境代码

# 功能分支
feature/user-auth
feature/inventory-management

# 修复分支
hotfix/security-patch
bugfix/login-error
```

## 🧪 测试

### 运行前端测试
```bash
cd frontend
npm run test
npm run test:coverage
```

### 运行后端测试
```bash
cd backend
source venv/bin/activate
python -m pytest
python -m pytest --cov=app
```

### API测试
```bash
# 导入Postman集合
# 文件路径：docs/postman-collection.json
```

## 📖 学习资源

### 官方文档
- [Vue.js官方文档](https://vuejs.org/)
- [Flask官方文档](https://flask.palletsprojects.com/)
- [SQLAlchemy文档](https://docs.sqlalchemy.org/)

### 项目文档
- [项目Wiki](../Wiki/Home.md)
- [API文档](../Documentation/API/README.md)
- [数据库设计](../TechnicalArchitecture/Database.md)

### 在线课程
- Vue.js Mastery
- Flask Web Development
- Database Design Fundamentals

## 🤝 贡献指南

### 1. Fork项目
```bash
# 在GitHub上Fork项目到你的账户
git clone https://github.com/your-username/SH-Drug-Mgmt.git
```

### 2. 创建功能分支
```bash
git checkout -b feature/your-feature-name
```

### 3. 提交代码
```bash
git add .
git commit -m "feat: 添加新功能描述"
git push origin feature/your-feature-name
```

### 4. 创建Pull Request
在GitHub上创建Pull Request，等待代码审查

## 📞 获取帮助

### 技术支持
- **项目负责人：** [联系方式]
- **技术负责人：** [联系方式]
- **开发群组：** [群组链接]

### 问题反馈
- **GitHub Issues：** https://github.com/your-org/SH-Drug-Mgmt/issues
- **邮件支持：** dev@shdrug-mgmt.com

---

**文档版本：** v1.0.0
**最后更新：** 2024-10-25
**维护团队：** 开发团队