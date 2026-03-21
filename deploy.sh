#!/bin/bash
# 等级保护评测过程记录系统 - 服务器部署脚本
set -e

APP_DIR="/opt/mlps-app"
REPO="git@github.com:Akiratsutsucn/mlps-app.git"

echo "=== 部署等级保护评测过程记录系统 ==="

# 克隆或更新代码
if [ -d "$APP_DIR" ]; then
    echo "更新代码..."
    cd "$APP_DIR"
    git pull
else
    echo "克隆代码..."
    git clone "$REPO" "$APP_DIR"
    cd "$APP_DIR"
fi

# 后端依赖
echo "安装后端依赖..."
cd "$APP_DIR/backend"
pip3 install -r requirements.txt -q

# 前端构建
echo "构建前端..."
cd "$APP_DIR/frontend"
npm install --silent
npm run build

# 创建systemd服务
echo "配置系统服务..."
cat > /etc/systemd/system/mlps-app.service << EOF
[Unit]
Description=MLPS App
After=network.target

[Service]
Type=simple
WorkingDirectory=$APP_DIR/backend
ExecStart=/usr/bin/python3 -m uvicorn app.main:app --host 0.0.0.0 --port 8900
Restart=always
RestartSec=5

[Install]
WantedBy=multi-user.target
EOF

systemctl daemon-reload
systemctl enable mlps-app
systemctl restart mlps-app

echo "=== 部署完成 ==="
echo "访问地址: http://$(hostname -I | awk '{print $1}'):8900"
