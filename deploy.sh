#!/bin/bash
# 华为云一键部署脚本
# 使用方法: chmod +x deploy.sh && ./deploy.sh

set -e

SERVER_IP="119.3.155.21"
SERVER_USER="root"  # 根据实际情况修改
PROJECT_DIR="/var/www/SH-Drug-Mgmt"
DOMAIN="$SERVER_IP"

echo "======================================"
echo "  SH药品监管平台 - 华为云部署脚本"
echo "======================================"
echo ""
echo "服务器IP: $SERVER_IP"
echo "项目目录: $PROJECT_DIR"
echo ""

# 颜色输出
GREEN='\033[0;32m'
RED='\033[0;31m'
NC='\033[0m' # No Color

success() {
    echo -e "${GREEN}✓ $1${NC}"
}

error() {
    echo -e "${RED}✗ $1${NC}"
    exit 1
}

# 1. 检查SSH连接
echo "1. 检查服务器连接..."
ssh -o ConnectTimeout=5 $SERVER_USER@$SERVER_IP "echo '连接成功'" || error "无法连接到服务器"
success "服务器连接正常"

# 2. 上传项目文件
echo ""
echo "2. 上传项目文件到服务器..."
rsync -avz --exclude 'node_modules' --exclude '.git' --exclude '__pycache__' \
    --exclude 'venv' --exclude 'instance/*.db' \
    ./ $SERVER_USER@$SERVER_IP:$PROJECT_DIR/ || error "文件上传失败"
success "项目文件上传完成"

# 3. 服务器端部署脚本
echo ""
echo "3. 在服务器上执行部署..."
ssh $SERVER_USER@$SERVER_IP << 'ENDSSH'
set -e

PROJECT_DIR="/var/www/SH-Drug-Mgmt"
cd $PROJECT_DIR

echo ">>> 安装系统依赖..."
apt update
apt install -y python3 python3-pip python3-venv nginx git curl

# 安装Node.js 18.x
if ! command -v node &> /dev/null; then
    echo ">>> 安装Node.js..."
    curl -fsSL https://deb.nodesource.com/setup_18.x | bash -
    apt install -y nodejs
fi

echo ">>> 部署后端..."
cd $PROJECT_DIR/backend

# 创建虚拟环境
if [ ! -d "venv" ]; then
    python3 -m venv venv
fi
source venv/bin/activate

# 安装Python依赖
pip install --upgrade pip
pip install -r requirements.txt
pip install gunicorn

# 创建数据库目录
mkdir -p instance

# 创建生产环境配置（如果不存在）
if [ ! -f ".env.production" ]; then
    cp .env.template .env.production
    # 生成随机密钥
    SECRET_KEY=$(python3 -c "import secrets; print(secrets.token_hex(32))")
    JWT_SECRET=$(python3 -c "import secrets; print(secrets.token_hex(32))")
    
    sed -i "s/SECRET_KEY=.*/SECRET_KEY=$SECRET_KEY/" .env.production
    sed -i "s/JWT_SECRET_KEY=.*/JWT_SECRET_KEY=$JWT_SECRET/" .env.production
fi

# 初始化数据库（如果需要）
if [ ! -f "instance/data.db" ]; then
    echo ">>> 初始化数据库..."
    python3 tools/init_db.py || true
fi

echo ">>> 部署前端..."
cd $PROJECT_DIR/frontend

# 创建生产环境配置
echo "VITE_API_BASE_URL=http://119.3.155.21/api" > .env.production

# 安装依赖并构建
npm install
npm run build

echo ">>> 配置Nginx..."
# 复制Nginx配置
cp $PROJECT_DIR/nginx.conf /etc/nginx/sites-available/sh-drug-mgmt

# 启用站点
ln -sf /etc/nginx/sites-available/sh-drug-mgmt /etc/nginx/sites-enabled/
rm -f /etc/nginx/sites-enabled/default

# 测试Nginx配置
nginx -t

echo ">>> 配置后端服务..."
# 创建日志目录
mkdir -p /var/log/sh-drug-backend
chown www-data:www-data /var/log/sh-drug-backend

# 复制systemd服务文件
cp $PROJECT_DIR/sh-drug-backend.service /etc/systemd/system/

# 重载systemd
systemctl daemon-reload

# 启动服务
systemctl enable sh-drug-backend
systemctl restart sh-drug-backend
systemctl restart nginx

echo ">>> 配置防火墙..."
# 开放端口（如果使用ufw）
if command -v ufw &> /dev/null; then
    ufw allow 80/tcp
    ufw allow 443/tcp
fi

echo ""
echo "======================================"
echo "  部署完成！"
echo "======================================"
echo ""
echo "服务状态:"
systemctl status sh-drug-backend --no-pager -l | head -10
echo ""
systemctl status nginx --no-pager -l | head -10
echo ""
echo "访问地址: http://119.3.155.21"
echo "后端API: http://119.3.155.21/api"
echo ""
echo "查看后端日志: journalctl -u sh-drug-backend -f"
echo "查看Nginx日志: tail -f /var/log/nginx/sh-drug-mgmt-error.log"

ENDSSH

success "部署完成！"
echo ""
echo "======================================"
echo "  访问信息"
echo "======================================"
echo "前端地址: http://119.3.155.21"
echo "后端API: http://119.3.155.21/api"
echo ""
echo "默认管理员账号:"
echo "  用户名: admin"
echo "  密码: AdminPass123!"
echo ""
echo "监管账号:"
echo "  用户名: regulator01"
echo "  密码: Regulator123!"
