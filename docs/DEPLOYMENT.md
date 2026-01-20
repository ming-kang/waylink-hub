# 驿联站部署指南

> 版本：1.1.0
> 更新日期：2026-01-20

## 目录

- [环境要求](#环境要求)
- [服务器初始化](#服务器初始化)
- [部署步骤](#部署步骤)
- [进程管理](#进程管理)
- [SSL配置](#ssl配置)
- [常见问题](#常见问题)

---

## 环境要求

### 最低配置

| 配置 | 要求 |
|-----|------|
| CPU | 1核 |
| 内存 | 1GB |
| 磁盘 | 10GB |
| 带宽 | 1Mbps |

### 软件环境

| 软件 | 版本要求 |
|-----|---------|
| Ubuntu | 20.04 LTS 或更高 |
| Python | 3.10+ |
| PostgreSQL | 13+ |
| Nginx | 1.18+ |
| Gunicorn | 20+ |

---

## 服务器初始化

### 1. 更新系统

```bash
sudo apt update && sudo apt upgrade -y
```

### 2. 安装 Python 和依赖

```bash
sudo apt install -y python3 python3-pip python3-venv git
sudo apt install -y build-essential libssl-dev libffi-dev python3-dev
```

### 3. 安装 PostgreSQL

```bash
sudo apt install -y postgresql postgresql-contrib

# 创建数据库和用户
sudo -u postgres psql

CREATE DATABASE waylink;
CREATE USER waylink_user WITH PASSWORD 'your_secure_password';
ALTER ROLE waylink_user SET client_encoding TO 'utf8';
ALTER ROLE waylink_user SET default_transaction_isolation TO 'read committed';
ALTER ROLE waylink_user SET timezone TO 'Asia/Shanghai';
GRANT ALL PRIVILEGES ON DATABASE waylink TO waylink_user;
GRANT ALL ON SCHEMA public TO waylink_user;
\q
```

### 4. 安装 Nginx

```bash
sudo apt install -y nginx
```

---

## 部署步骤

### 1. 创建部署目录

```bash
sudo mkdir -p /var/www/waylink
sudo mkdir -p /var/www/waylink/backend/logs
sudo chown -R $USER:$USER /var/www/waylink
```

### 2. 上传代码

```bash
cd /var/www/waylink
git clone https://your-repo-url/waylink-hub.git backend
cd backend
```

### 3. 创建虚拟环境

```bash
python3 -m venv venv
source venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
```

### 4. 配置环境变量

```bash
cp .env.example .env
nano .env
```

编辑 `.env` 文件：

```env
DEBUG=False
SECRET_KEY=your-very-long-random-secret-key-here
ALLOWED_HOSTS=your-domain.com,www.your-domain.com

# Database
DB_NAME=waylink
DB_USER=waylink_user
DB_PASSWORD=your_secure_password
DB_HOST=localhost
DB_PORT=5432

# Gunicorn
GUNICORN_BIND=127.0.0.1:8000
```

### 5. 初始化数据库

```bash
export DJANGO_SETTINGS_MODULE=waylink.settings_production
python manage.py migrate
python manage.py createsuperuser
python manage.py collectstatic --noinput
```

> **SSL 重定向注意**：`settings_production.py` 中配置了 `SECURE_SSL_REDIRECT = True`。如果使用 Let's Encrypt 证书，请先配置好 Nginx SSL，然后注释掉 nginx.conf 中的 80 端口重定向部分。如仅在测试环境，请将 `SECURE_SSL_REDIRECT` 改为 `False`。

### 6. 创建日志目录

```bash
mkdir -p logs
touch logs/django.log
touch logs/gunicorn-error.log
touch logs/gunicorn-access.log
```

### 7. 配置 Nginx

```bash
sudo cp nginx.conf /etc/nginx/sites-available/waylink
sudo ln -s /etc/nginx/sites-available/waylink /etc/nginx/sites-enabled/
sudo nginx -t  # 测试配置
sudo systemctl reload nginx
```

### 8. 启动 Gunicorn

> **注意**：首次启动前请先确保 `logs/` 目录已创建，否则 Gunicorn 无法写入日志。

```bash
# 测试启动
source venv/bin/activate
gunicorn -c gunicorn.conf.py waylink.wsgi:application

# 后台运行（使用 systemd）
```

---

## 进程管理

### 创建 Systemd 服务

```bash
sudo nano /etc/systemd/system/waylink.service
```

写入以下内容：

```ini
[Unit]
Description=WaylinkHub Gunicorn Service
After=network.target

[Service]
User=www-data
Group=www-data
WorkingDirectory=/var/www/waylink/backend
Environment="PATH=/var/www/waylink/backend/venv/bin"
Environment="DJANGO_SETTINGS_MODULE=waylink.settings_production"
ExecStart=/var/www/waylink/backend/venv/bin/gunicorn \
    -c /var/www/waylink/backend/gunicorn.conf.py \
    --pid /var/www/waylink/backend/logs/gunicorn.pid \
    waylink.wsgi:application

Restart=on-failure
RestartSec=5

[Install]
WantedBy=multi-user.target
```

### 管理服务

```bash
# 启动服务
sudo systemctl start waylink

# 停止服务
sudo systemctl stop waylink

# 重启服务
sudo systemctl restart waylink

# 查看状态
sudo systemctl status waylink

# 查看日志
sudo journalctl -u waylink -f

# 开机自启
sudo systemctl enable waylink
```

---

## SSL配置

### 使用 Let's Encrypt（免费）

```bash
sudo apt install -y certbot python3-certbot-nginx

# 获取证书
sudo certbot --nginx -d your-domain.com -d www.your-domain.com

# 自动续期测试
sudo certbot renew --dry-run
```

### 添加自动续期任务

```bash
sudo crontab -e
```

添加：

```
0 2 * * * certbot renew --quiet
```

---

## 常见问题

### 1. 500 错误

查看日志：
```bash
sudo journalctl -u waylink -f
cat /var/www/waylink/backend/logs/django.log
```

常见原因：
- 数据库连接失败
- 静态文件路径错误
- 权限问题

### 2. 数据库迁移

```bash
# 开发环境更新迁移
python manage.py makemigrations

# 生成迁移文件后，在生产环境执行
python manage.py migrate
```

### 3. 更新代码

```bash
cd /var/www/waylink/backend
git pull
source venv/bin/activate
pip install -r requirements.txt
python manage.py migrate
sudo systemctl restart waylink
```

### 4. 静态文件不显示

```bash
# 重新收集静态文件
python manage.py collectstatic --noinput

# 检查 Nginx 配置
sudo nginx -t
sudo systemctl reload nginx
```

### 5. 性能优化

如需更高性能，可调整：

1. **Gunicorn workers**：`gunicorn.conf.py` 中的 `workers` 数量
2. **数据库连接池**：增加 `CONN_MAX_AGE`
3. **缓存**：使用 Redis 缓存

---

## 监控

### 健康检查端点

访问 `http://your-domain.com/health/` 应返回 `OK`

### 建议监控

- 服务器资源：`htop`、` glances`
- 应用日志：`tail -f /var/www/waylink/backend/logs/django.log`
- Nginx 访问：`tail -f /var/log/nginx/waylink-access.log`
- 系统服务：`sudo systemctl status waylink`

---

## 备份

### 数据库备份

```bash
# 手动备份
pg_dump -U waylink_user waylink > backup_$(date +%Y%m%d).sql

# 自动备份脚本
sudo nano /etc/cron.daily/backup-waylink
```

备份脚本内容：
```bash
#!/bin/bash
pg_dump -U waylink_user waylink | gzip > /var/backups/waylink_$(date +%Y%m%d).sql.gz
find /var/backups -name "waylink_*.sql.gz" -mtime +7 -delete
```

```bash
sudo chmod +x /etc/cron.daily/backup-waylink
```

---

## 更新日志

### v1.1.0 (2026-01-20)
- 新增健康检查端点 `GET /api/admin/health/`
- 新增服务器主动查询柜子状态接口 `GET /api/devices/query/<device_id>/`
- 新增 ESP32 状态查询轮询接口 `GET /api/devices/status/query/<device_id>/`
- 更新部署文档，添加 SSL 重定向注意事项
- 修复 operations app 缺少 migrations 目录问题

### v1.0.0 (2025-01-19)
- 初始版本
- 支持用户认证、储物柜管理、订单系统
- 支持 ESP32 设备通信
- 运维管理 API
- 部署配置
