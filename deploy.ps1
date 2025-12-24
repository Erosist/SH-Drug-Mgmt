# 华为云部署 - Windows PowerShell版本
# 使用方法: .\deploy.ps1

$SERVER_IP = "119.3.155.21"
$SERVER_USER = "root"  # 根据实际情况修改
$PROJECT_DIR = "/var/www/SH-Drug-Mgmt"

Write-Host "======================================" -ForegroundColor Cyan
Write-Host "  SH药品监管平台 - 华为云部署脚本" -ForegroundColor Cyan
Write-Host "======================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "服务器IP: $SERVER_IP"
Write-Host "项目目录: $PROJECT_DIR"
Write-Host ""

# 检查必要工具
if (-not (Get-Command ssh -ErrorAction SilentlyContinue)) {
    Write-Host "✗ 未找到SSH，请安装OpenSSH客户端" -ForegroundColor Red
    exit 1
}

# 1. 测试SSH连接
Write-Host "1. 测试服务器连接..." -ForegroundColor Yellow
try {
    ssh -o ConnectTimeout=5 "$SERVER_USER@$SERVER_IP" "echo '连接成功'"
    Write-Host "✓ 服务器连接正常" -ForegroundColor Green
} catch {
    Write-Host "✗ 无法连接到服务器" -ForegroundColor Red
    exit 1
}

# 2. 提交本地代码
Write-Host ""
Write-Host "2. 提交代码到Git仓库..." -ForegroundColor Yellow
git add .
git commit -m "Deploy to production $(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')" -ErrorAction SilentlyContinue
git push origin main
Write-Host "✓ 代码已推送到远程仓库" -ForegroundColor Green

# 3. 在服务器上执行部署
Write-Host ""
Write-Host "3. 在服务器上执行部署..." -ForegroundColor Yellow

$deployScript = @'
set -e

PROJECT_DIR="/var/www/SH-Drug-Mgmt"

echo ">>> 更新代码..."
if [ ! -d "$PROJECT_DIR" ]; then
    cd /var/www
    git clone https://gitlab.com/tj-cs-swe/CS10102302-2025/group4/SH-Drug-Mgmt.git
else
    cd $PROJECT_DIR
    git pull origin main
fi

cd $PROJECT_DIR

echo ">>> 安装系统依赖..."
apt update
apt install -y python3 python3-pip python3-venv nginx git curl

# 安装Node.js
if ! command -v node &> /dev/null; then
    echo ">>> 安装Node.js..."
    curl -fsSL https://deb.nodesource.com/setup_18.x | bash -
    apt install -y nodejs
fi

echo ">>> 部署后端..."
cd $PROJECT_DIR/backend

if [ ! -d "venv" ]; then
    python3 -m venv venv
fi
source venv/bin/activate

pip install --upgrade pip
pip install -r requirements.txt
pip install gunicorn

mkdir -p instance

# 创建生产配置
if [ ! -f ".env.production" ]; then
    cp .env.template .env.production
    SECRET_KEY=$(python3 -c "import secrets; print(secrets.token_hex(32))")
    JWT_SECRET=$(python3 -c "import secrets; print(secrets.token_hex(32))")
    sed -i "s/SECRET_KEY=.*/SECRET_KEY=$SECRET_KEY/" .env.production
    sed -i "s/JWT_SECRET_KEY=.*/JWT_SECRET_KEY=$JWT_SECRET/" .env.production
fi

# 初始化数据库
if [ ! -f "instance/data.db" ]; then
    echo ">>> 初始化数据库..."
    export FLASK_ENV=production
    python3 -c "from app import create_app; from extensions import db; app=create_app('production'); app.app_context().push(); db.create_all()"
    python3 tools/seed_users.py || true
    python3 tools/create_regulator_users.py || true
fi

echo ">>> 部署前端..."
cd $PROJECT_DIR/frontend
echo "VITE_API_BASE_URL=http://119.3.155.21/api" > .env.production
npm install
npm run build

echo ">>> 配置Nginx..."
cp $PROJECT_DIR/nginx.conf /etc/nginx/sites-available/sh-drug-mgmt
ln -sf /etc/nginx/sites-available/sh-drug-mgmt /etc/nginx/sites-enabled/
rm -f /etc/nginx/sites-enabled/default
nginx -t

echo ">>> 配置后端服务..."
mkdir -p /var/log/sh-drug-backend
chown -R www-data:www-data /var/log/sh-drug-backend $PROJECT_DIR

cp $PROJECT_DIR/sh-drug-backend.service /etc/systemd/system/
systemctl daemon-reload
systemctl enable sh-drug-backend
systemctl restart sh-drug-backend
systemctl restart nginx

if command -v ufw &> /dev/null; then
    ufw allow 80/tcp
    ufw allow 443/tcp
fi

echo ""
echo "======================================"
echo "  部署完成！"
echo "======================================"
systemctl status sh-drug-backend --no-pager -l | head -8
echo ""
echo "访问地址: http://119.3.155.21"
'@

ssh "$SERVER_USER@$SERVER_IP" $deployScript

Write-Host ""
Write-Host "======================================" -ForegroundColor Green
Write-Host "  部署完成！" -ForegroundColor Green
Write-Host "======================================" -ForegroundColor Green
Write-Host ""
Write-Host "访问信息:" -ForegroundColor Cyan
Write-Host "  前端地址: http://119.3.155.21"
Write-Host "  后端API: http://119.3.155.21/api"
Write-Host ""
Write-Host "默认账号:" -ForegroundColor Cyan
Write-Host "  管理员: admin / AdminPass123!"
Write-Host "  监管者: regulator01 / Regulator123!"
Write-Host ""
Write-Host "查看日志:" -ForegroundColor Cyan
Write-Host "  ssh $SERVER_USER@$SERVER_IP 'journalctl -u sh-drug-backend -f'"
