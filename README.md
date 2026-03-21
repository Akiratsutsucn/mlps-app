# 等级保护评测过程记录系统 (MLPS 2.0)

等保2.0评测过程记录Web应用，帮助评测员管理评测项目、记录检查结果、导出Excel报告。

## 技术栈

- 后端：Python + FastAPI + SQLite
- 前端：Vue 3 + Vite + Element Plus + ECharts
- 题库：内置224条等保2.0二级+三级检查项（含云计算安全扩展）

## 功能

- 项目管理（创建/编辑/删除评测项目）
- 评测对象管理（13种评测对象类型，支持子类型）
- 检查记录填写（跳跃填写、自动保存、附件上传）
- 同类对象结果复制
- 问题发现记录（高危/中危/低危）
- 数据统计看板（ECharts图表）
- Excel导出（3个Sheet：系统信息/检查汇总/问题清单）
- 题库管理（可视化增删改查）

## 部署

### 服务器部署

```bash
# 克隆代码
git clone git@github.com:Akiratsutsucn/mlps-app.git /var/www/mlps-app
cd /var/www/mlps-app

# 后端
cd backend
pip install -r requirements.txt
# 启动（端口8900）
uvicorn app.main:app --host 0.0.0.0 --port 8900

# 前端构建
cd ../frontend
npm install
npm run build
```

前端构建后的静态文件会被后端自动serve，直接访问 `http://服务器IP:8900` 即可。

### 使用Nginx反向代理（可选）

```nginx
server {
    listen 8900;
    location / {
        root /var/www/mlps-app/frontend/dist;
        try_files $uri $uri/ /index.html;
    }
    location /api/ {
        proxy_pass http://127.0.0.1:8900;
    }
    location /uploads/ {
        proxy_pass http://127.0.0.1:8900;
    }
}
```
