# 华为云部署指南

## 服务器信息
- 公网IP: 119.3.155.21
- 操作系统: 假设为 Ubuntu/CentOS Linux

## 部署步骤

### 1. 准备工作
在本地需要确保：
- 有服务器的SSH访问权限（需要密码或SSH密钥）
- 已将代码提交到Git仓库

### 2. 服务器环境准备

SSH连接到服务器后执行：

```bash
# 更新系统包
sudo apt update && sudo apt upgrade -y  # Ubuntu/Debian
# 或
sudo yum update -y  # CentOS

# 安装必要软件
sudo apt install -y python3 python3-pip python3-venv nginx git  # Ubuntu
# 或
sudo yum install -y python3 python3-pip nginx git  # CentOS

# 安装Node.js（用于前端构建）
curl -fsSL https://deb.nodesource.com/setup_18.x | sudo -E bash -
sudo apt install -y nodejs  # Ubuntu
# 或使用nvm安装Node.js
```

### 3. 克隆项目到服务器

```bash
cd /var/www
sudo git clone https://gitlab.com/tj-cs-swe/CS10102302-2025/group4/SH-Drug-Mgmt.git
sudo chown -R $USER:$USER SH-Drug-Mgmt
cd SH-Drug-Mgmt
```

### 4. 部署后端

```bash
cd /var/www/SH-Drug-Mgmt/backend

# 创建Python虚拟环境
python3 -m venv venv
source venv/bin/activate

# 安装依赖
pip install -r requirements.txt

# 创建生产环境配置
cp .env.template .env.production
nano .env.production  # 编辑配置文件，设置密钥等

# 初始化数据库
python tools/init_db.py

# 使用gunicorn运行（生产环境）
pip install gunicorn
gunicorn -w 4 -b 127.0.0.1:5000 'app:create_app()' --daemon
```

### 5. 部署前端

```bash
cd /var/www/SH-Drug-Mgmt/frontend

# 安装依赖
npm install

# 修改API地址为生产环境
# 编辑 .env.production 文件
echo "VITE_API_BASE_URL=http://119.3.155.21/api" > .env.production

# 构建生产版本
npm run build

# 构建后的文件在 dist/ 目录
```

### 6. 配置Nginx

创建Nginx配置文件：

```bash
sudo nano /etc/nginx/sites-available/sh-drug-mgmt
```

配置内容见下方 `nginx.conf` 文件

```bash
# 启用配置
sudo ln -s /etc/nginx/sites-available/sh-drug-mgmt /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx
```

### 7. 配置系统服务（可选，确保重启后自动运行）

创建systemd服务文件：

```bash
sudo nano /etc/systemd/system/sh-drug-backend.service
```

内容见下方 `sh-drug-backend.service` 文件

```bash
sudo systemctl daemon-reload
sudo systemctl enable sh-drug-backend
sudo systemctl start sh-drug-backend
```

### 8. 配置防火墙

```bash
# 开放HTTP端口
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp  # 如果使用HTTPS
sudo ufw enable
```

## 访问应用

部署完成后：
- 前端访问: http://119.3.155.21
- 后端API: http://119.3.155.21/api

## 更新部署

```bash
cd /var/www/SH-Drug-Mgmt
git pull origin main

# 更新后端
cd backend
source venv/bin/activate
pip install -r requirements.txt
sudo systemctl restart sh-drug-backend

# 更新前端
cd ../frontend
npm install
npm run build
```
