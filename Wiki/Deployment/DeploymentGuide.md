# 部署指南

## 🚀 部署概览

本指南详细说明如何在不同环境中部署上海药品信息管理与查询平台，包括开发环境、测试环境和生产环境的部署步骤。

## 📋 环境要求

### 最低硬件要求

| 环境 | CPU | 内存 | 存储 | 带宽 |
|------|-----|------|------|------|
| 开发 | 2核 | 4GB | 20GB | 10Mbps |
| 测试 | 4核 | 8GB | 50GB | 50Mbps |
| 生产 | 8核 | 16GB | 200GB | 100Mbps |

### 软件依赖

| 组件 | 版本要求 | 说明 |
|------|----------|------|
| 操作系统 | Ubuntu 20.04+ / CentOS 8+ / Windows Server 2019+ | 推荐Linux |
| Node.js | 18.0+ | 前端运行环境 |
| Python | 3.9+ | 后端运行环境 |
| Nginx | 1.20+ | Web服务器 |
| PostgreSQL | 14+ | 生产数据库 |
| Redis | 7.0+ | 缓存服务 |
| Docker | 20.10+ | 容器化部署（可选） |

## 🏗️ 架构部署

### 单机部署架构
```
┌─────────────────────────────────────────┐
│              服务器                      │
│  ┌─────────────┐  ┌─────────────┐       │
│  │   Nginx     │  │ PostgreSQL  │       │
│  │ (Web服务)   │  │  (数据库)   │       │
│  └─────────────┘  └─────────────┘       │
│         │               │               │
│  ┌─────────────┐  ┌─────────────┐       │
│  │  Flask App  │  │   Redis     │       │
│  │ (应用服务)   │  │  (缓存)     │       │
│  └─────────────┘  └─────────────┘       │
└─────────────────────────────────────────┘
```

### 集群部署架构
```
┌─────────────────────────────────────────────────────────┐
│                    负载均衡器                             │
│                   (Nginx/HAProxy)                        │
└─────────────────────────────────────────────────────────┘
                                │
                    ┌───────────┼───────────┐
                    ▼           ▼           ▼
┌─────────────┐ ┌─────────────┐ ┌─────────────┐
│  Web服务器1  │ │  Web服务器2  │ │  Web服务器N  │
│             │ │             │ │             │
│ Flask App   │ │ Flask App   │ │ Flask App   │
└─────────────┘ └─────────────┘ └─────────────┘
                    │           │           │
                    └───────────┼───────────┘
                                ▼
┌─────────────────────────────────────────────────────────┐
│                    数据库集群                             │
│         PostgreSQL主从复制 + Redis集群                  │
└─────────────────────────────────────────────────────────┘
```

## 🔧 开发环境部署

### 1. 系统准备
```bash
# Ubuntu/Debian
sudo apt update && sudo apt upgrade -y
sudo apt install -y git curl wget vim build-essential

# CentOS/RHEL
sudo yum update -y
sudo yum groupinstall -y "Development Tools"
sudo yum install -y git curl wget vim
```

### 2. 安装Node.js
```bash
# 使用NodeSource仓库
curl -fsSL https://deb.nodesource.com/setup_18.x | sudo -E bash -
sudo apt-get install -y nodejs

# 验证安装
node --version
npm --version
```

### 3. 安装Python
```bash
# Ubuntu/Debian
sudo apt install -y python3.9 python3.9-pip python3.9-venv

# CentOS/RHEL
sudo yum install -y python39 python39-pip

# 验证安装
python3.9 --version
pip3.9 --version
```

### 4. 安装PostgreSQL
```bash
# Ubuntu/Debian
sudo apt install -y postgresql postgresql-contrib

# 启动服务
sudo systemctl start postgresql
sudo systemctl enable postgresql

# 创建数据库和用户
sudo -u postgres psql
CREATE DATABASE shdrug_mgmt;
CREATE USER shdrug_user WITH PASSWORD 'your_password';
GRANT ALL PRIVILEGES ON DATABASE shdrug_mgmt TO shdrug_user;
\q
```

### 5. 安装Redis
```bash
# Ubuntu/Debian
sudo apt install -y redis-server

# 配置Redis
sudo vim /etc/redis/redis.conf
# 修改以下配置
# bind 127.0.0.1
# requirepass your_redis_password

# 启动服务
sudo systemctl start redis-server
sudo systemctl enable redis-server
```

### 6. 安装Nginx
```bash
# Ubuntu/Debian
sudo apt install -y nginx

# 启动服务
sudo systemctl start nginx
sudo systemctl enable nginx
```

### 7. 部署应用代码
```bash
# 创建应用目录
sudo mkdir -p /opt/shdrug-mgmt
sudo chown $USER:$USER /opt/shdrug-mgmt
cd /opt/shdrug-mgmt

# 克隆代码
git clone https://github.com/your-org/SH-Drug-Mgmt.git .

# 部署后端
cd backend
python3.9 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# 配置环境变量
cp .env.example .env
vim .env
# 配置数据库连接、JWT密钥等

# 初始化数据库
python manage.py db upgrade
python scripts/init_data.py

# 部署前端
cd ../frontend
npm install
npm run build
```

### 8. 配置Nginx
```bash
sudo vim /etc/nginx/sites-available/shdrug-mgmt
```

```nginx
server {
    listen 80;
    server_name your-domain.com;

    # 前端静态文件
    location / {
        root /opt/shdrug-mgmt/frontend/dist;
        try_files $uri $uri/ /index.html;
    }

    # API代理
    location /api/ {
        proxy_pass http://127.0.0.1:5000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    # WebSocket支持
    location /socket.io/ {
        proxy_pass http://127.0.0.1:5000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_set_header Host $host;
    }

    # 静态资源缓存
    location ~* \.(js|css|png|jpg|jpeg|gif|ico|svg)$ {
        expires 1y;
        add_header Cache-Control "public, immutable";
    }
}
```

```bash
# 启用站点
sudo ln -s /etc/nginx/sites-available/shdrug-mgmt /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl reload nginx
```

### 9. 配置系统服务
```bash
sudo vim /etc/systemd/system/shdrug-mgmt.service
```

```ini
[Unit]
Description=SH-Drug-Mgmt Application
After=network.target

[Service]
Type=simple
User=www-data
WorkingDirectory=/opt/shdrug-mgmt/backend
Environment=PATH=/opt/shdrug-mgmt/backend/venv/bin
ExecStart=/opt/shdrug-mgmt/backend/venv/bin/gunicorn --workers 4 --bind 127.0.0.1:5000 app:app
Restart=always

[Install]
WantedBy=multi-user.target
```

```bash
# 启动服务
sudo systemctl daemon-reload
sudo systemctl start shdrug-mgmt
sudo systemctl enable shdrug-mgmt
```

## 🐳 Docker部署

### 1. 创建Dockerfile

#### 后端Dockerfile
```dockerfile
# backend/Dockerfile
FROM python:3.9-slim

WORKDIR /app

# 安装系统依赖
RUN apt-get update && apt-get install -y \
    gcc \
    postgresql-client \
    && rm -rf /var/lib/apt/lists/*

# 安装Python依赖
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 复制应用代码
COPY . .

# 创建非root用户
RUN useradd --create-home --shell /bin/bash app \
    && chown -R app:app /app
USER app

# 暴露端口
EXPOSE 5000

# 启动命令
CMD ["gunicorn", "--workers", "4", "--bind", "0.0.0.0:5000", "app:app"]
```

#### 前端Dockerfile
```dockerfile
# frontend/Dockerfile
FROM node:18-alpine AS builder

WORKDIR /app
COPY package*.json ./
RUN npm ci --only=production

COPY . .
RUN npm run build

FROM nginx:alpine
COPY --from=builder /app/dist /usr/share/nginx/html
COPY nginx.conf /etc/nginx/nginx.conf

EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]
```

### 2. 创建docker-compose.yml
```yaml
version: '3.8'

services:
  db:
    image: postgres:14
    environment:
      POSTGRES_DB: shdrug_mgmt
      POSTGRES_USER: shdrug_user
      POSTGRES_PASSWORD: ${DB_PASSWORD}
    volumes:
      - postgres_data:/var/lib/postgresql/data
    ports:
      - "5432:5432"
    networks:
      - shdrug-network

  redis:
    image: redis:7-alpine
    command: redis-server --requirepass ${REDIS_PASSWORD}
    ports:
      - "6379:6379"
    networks:
      - shdrug-network

  backend:
    build: ./backend
    environment:
      DATABASE_URL: postgresql://shdrug_user:${DB_PASSWORD}@db:5432/shdrug_mgmt
      REDIS_URL: redis://:${REDIS_PASSWORD}@redis:6379/0
      JWT_SECRET_KEY: ${JWT_SECRET_KEY}
    depends_on:
      - db
      - redis
    ports:
      - "5000:5000"
    networks:
      - shdrug-network
    volumes:
      - ./logs:/app/logs

  frontend:
    build: ./frontend
    ports:
      - "80:80"
    depends_on:
      - backend
    networks:
      - shdrug-network

volumes:
  postgres_data:

networks:
  shdrug-network:
    driver: bridge
```

### 3. 环境变量配置
```bash
# .env
DB_PASSWORD=your_secure_password
REDIS_PASSWORD=your_redis_password
JWT_SECRET_KEY=your_jwt_secret_key
```

### 4. 部署命令
```bash
# 构建和启动服务
docker-compose up -d

# 查看服务状态
docker-compose ps

# 查看日志
docker-compose logs -f backend

# 停止服务
docker-compose down
```

## 🚀 生产环境部署

### 1. SSL证书配置
```bash
# 使用Let's Encrypt
sudo apt install certbot python3-certbot-nginx

# 获取证书
sudo certbot --nginx -d your-domain.com

# 自动续期
sudo crontab -e
# 添加以下行
0 12 * * * /usr/bin/certbot renew --quiet
```

### 2. 数据库优化
```sql
-- PostgreSQL配置优化
-- postgresql.conf
shared_buffers = 256MB
effective_cache_size = 1GB
maintenance_work_mem = 64MB
checkpoint_completion_target = 0.9
wal_buffers = 16MB
default_statistics_target = 100
random_page_cost = 1.1
effective_io_concurrency = 200
```

### 3. 性能监控
```bash
# 安装监控工具
sudo apt install -y htop iotop nethogs

# 配置日志轮转
sudo vim /etc/logrotate.d/shdrug-mgmt
```

```
/opt/shdrug-mgmt/logs/*.log {
    daily
    missingok
    rotate 52
    compress
    delaycompress
    notifempty
    create 644 www-data www-data
    postrotate
        systemctl reload shdrug-mgmt
    endscript
}
```

### 4. 备份策略
```bash
#!/bin/bash
# backup.sh

# 数据库备份
BACKUP_DIR="/opt/backups"
DATE=$(date +%Y%m%d_%H%M%S)
DB_NAME="shdrug_mgmt"

# 创建备份目录
mkdir -p $BACKUP_DIR

# 数据库备份
pg_dump -h localhost -U shdrug_user $DB_NAME > $BACKUP_DIR/db_backup_$DATE.sql

# 压缩备份
gzip $BACKUP_DIR/db_backup_$DATE.sql

# 删除7天前的备份
find $BACKUP_DIR -name "db_backup_*.sql.gz" -mtime +7 -delete

# 文件备份
tar -czf $BACKUP_DIR/files_backup_$DATE.tar.gz /opt/shdrug-mgmt

echo "备份完成: $DATE"
```

```bash
# 设置定时备份
sudo crontab -e
# 添加以下行
0 2 * * * /opt/scripts/backup.sh >> /var/log/backup.log 2>&1
```

## 🔍 监控和日志

### 1. 应用监控
```bash
# 健康检查脚本
#!/bin/bash
# health_check.sh

API_URL="http://localhost:5000/api/v1/health"
RESPONSE=$(curl -s -o /dev/null -w "%{http_code}" $API_URL)

if [ $RESPONSE -eq 200 ]; then
    echo "应用运行正常"
    exit 0
else
    echo "应用异常，HTTP状态码: $RESPONSE"
    # 发送告警
    curl -X POST "https://api.telegram.org/bot<TOKEN>/sendMessage" \
        -d "chat_id=<CHAT_ID>" \
        -d "text=SH-Drug-Mgmt应用异常: HTTP $RESPONSE"
    exit 1
fi
```

### 2. 日志配置
```python
# backend/app.py
import logging
from logging.handlers import RotatingFileHandler

# 配置日志
if not app.debug:
    file_handler = RotatingFileHandler('logs/app.log', maxBytes=10240000, backupCount=10)
    file_handler.setFormatter(logging.Formatter(
        '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'
    ))
    file_handler.setLevel(logging.INFO)
    app.logger.addHandler(file_handler)
    app.logger.setLevel(logging.INFO)
    app.logger.info('SH-Drug-Mgmt startup')
```

## 🚨 故障排除

### 常见问题和解决方案

#### 1. 数据库连接失败
```bash
# 检查数据库状态
sudo systemctl status postgresql

# 检查连接
psql -h localhost -U shdrug_user -d shdrug_mgmt

# 查看错误日志
sudo tail -f /var/log/postgresql/postgresql-14-main.log
```

#### 2. Nginx配置错误
```bash
# 检查配置
sudo nginx -t

# 重新加载配置
sudo systemctl reload nginx

# 查看访问日志
sudo tail -f /var/log/nginx/access.log
```

#### 3. 应用服务异常
```bash
# 检查服务状态
sudo systemctl status shdrug-mgmt

# 查看服务日志
sudo journalctl -u shdrug-mgmt -f

# 重启服务
sudo systemctl restart shdrug-mgmt
```

#### 4. 内存不足
```bash
# 检查内存使用
free -h

# 查看进程内存占用
ps aux --sort=-%mem | head

# 清理系统缓存
sudo sync && sudo sysctl vm.drop_caches=3
```

## 📈 性能优化

### 1. 数据库优化
```sql
-- 创建索引
CREATE INDEX idx_orders_tenant_status ON orders(tenant_id, status);
CREATE INDEX idx_inventory_items_drug_tenant ON inventory_items(drug_id, tenant_id);

-- 分析查询性能
EXPLAIN ANALYZE SELECT * FROM orders WHERE tenant_id = 1 AND status = 'PENDING';
```

### 2. 应用优化
```python
# 使用连接池
from sqlalchemy.pool import QueuePool

app.config['SQLALCHEMY_ENGINE_OPTIONS'] = {
    'pool_size': 10,
    'pool_recycle': 3600,
    'pool_pre_ping': True
}
```

### 3. 缓存策略
```python
# Redis缓存
import redis
import json

redis_client = redis.Redis(host='localhost', port=6379, db=0)

def get_drug_list():
    cache_key = 'drug_list'
    cached_data = redis_client.get(cache_key)

    if cached_data:
        return json.loads(cached_data)

    # 从数据库查询
    drugs = Drug.query.all()
    result = [drug.to_dict() for drug in drugs]

    # 缓存结果（1小时）
    redis_client.setex(cache_key, 3600, json.dumps(result))
    return result
```

---

**文档版本：** v1.0.0
**最后更新：** 2024-10-25
**维护团队：** 运维团队