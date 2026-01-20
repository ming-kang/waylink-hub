# 驿联站 (WaylinkHub) VPS 部署指南

> 基于 Debian 12，从零开始部署
> 版本：2.0.0
> 更新日期：2025-01-20

---

## 目录

1. [环境要求](#1-环境要求)
2. [服务器初始化](#2-服务器初始化)
3. [安装基础软件](#3-安装基础软件)
4. [配置 PostgreSQL 数据库](#4-配置-postgresql-数据库)
5. [部署项目代码](#5-部署项目代码)
6. [配置应用环境](#6-配置应用环境)
7. [配置 Gunicorn](#7-配置-gunicorn)
8. [配置 Nginx](#8-配置-nginx)
9. [配置 Systemd 服务](#9-配置-systemd-服务)
10. [配置 SSL 证书](#10-配置-ssl-证书)
11. [配置防火墙](#11-配置防火墙)
12. [配置备份](#12-配置备份)
13. [运维管理](#13-运维管理)
14. [常见问题](#14-常见问题)

---

## 1. 环境要求

### 1.1 服务器配置

| 配置 | 最低要求 | 推荐配置 |
|-----|---------|---------|
| CPU | 1 核 | 2 核 |
| 内存 | 1 GB | 2 GB |
| 磁盘 | 20 GB SSD | 40 GB SSD |
| 带宽 | 1 Mbps | 5 Mbps |

### 1.2 软件版本要求

| 软件 | 版本要求 |
|-----|---------|
| Debian | 12 (Bookworm) |
| Python | 3.10+ |
| PostgreSQL | 15+ |
| Nginx | 1.22+ |
| Gunicorn | 21+ |

### 1.3 域名要求

- 已解析到服务器 IP 的域名（用于 SSL 证书申请）
- 建议使用 `.com`、`.cn` 等常见域名后缀

---

## 2. 服务器初始化

### 2.1 连接服务器

```bash
# 使用 SSH 连接（替换为你的服务器 IP）
ssh root@your-server-ip

# 如果使用默认端口 22，直接连接
# 如果自定义端口，使用 -p 参数
ssh -p 2222 root@your-server-ip
```

### 2.2 创建部署用户

```bash
# 创建非 root 用户（用于运行应用）
adduser waylink

# 设置密码（输入强密码）
passwd waylink

# 添加到 sudo 组
usermod -aG sudo waylink
```

### 2.3 更新系统

```bash
# 切换到 root 用户
su -

# 更新软件包列表
apt update

# 升级已安装的软件包
apt upgrade -y

# 安装常用工具
apt install -y curl wget vim git unzip htop software-properties-common
```

### 2.4 设置时区

```bash
# 设置为上海时区
timedatectl set-timezone Asia/Shanghai

# 验证时区设置
date
```

---

## 3. 安装基础软件

### 3.1 安装 Python 3

```bash
# Debian 12 默认自带 Python 3.11，验证版本
python3 --version

# 安装 Python 开发环境和虚拟环境工具
apt install -y python3 python3-pip python3-venv python3-dev

# 安装 pip（如果未安装）
apt install -y python3-pip
```

### 3.2 安装 PostgreSQL

```bash
# 安装 PostgreSQL
apt install -y postgresql postgresql-contrib

# 启动 PostgreSQL 服务
systemctl start postgresql
systemctl enable postgresql

# 验证服务状态
systemctl status postgresql
```

### 3.3 安装 Nginx

```bash
# 安装 Nginx
apt install -y nginx

# 启动 Nginx 服务
systemctl start nginx
systemctl enable nginx

# 验证服务状态
systemctl status nginx

# 测试 Nginx 是否正常运行
curl -I http://localhost
```

### 3.4 安装其他依赖

```bash
# 安装编译工具和 SSL 库
apt install -y build-essential libssl-dev libffi-dev libpq-dev
```

---

## 4. 配置 PostgreSQL 数据库

### 4.1 创建数据库和用户

```bash
# 切换到 postgres 用户
su - postgres

# 进入 PostgreSQL 控制台
psql

# 在 psql 中执行以下命令：
```

```sql
-- 创建数据库
CREATE DATABASE waylink;

-- 创建数据库用户（替换为你的强密码）
CREATE USER waylink_user WITH PASSWORD 'Your-Strong-Password-Here';

-- 设置用户权限
ALTER ROLE waylink_user SET client_encoding TO 'utf8';
ALTER ROLE waylink_user SET default_transaction_isolation TO 'read committed';
ALTER ROLE waylink_user SET timezone TO 'Asia/Shanghai';

-- 授权
GRANT ALL PRIVILEGES ON DATABASE waylink TO waylink_user;

-- 退出 psql
\q
```

### 4.2 验证数据库连接

```bash
# 测试数据库连接（替换为你的密码）
psql -U waylink_user -d waylink -h localhost -W

# 输入密码后如果能进入数据库，说明配置成功
# 退出：\q
```

---

## 5. 部署项目代码

### 5.1 创建项目目录

```bash
# 切换到 waylink 用户
su - waylink

# 创建项目目录
mkdir -p /var/www/waylink
mkdir -p /var/www/waylink/backend/logs

# 设置目录所有者
sudo chown -R waylink:waylink /var/www/waylink
```

### 5.2 上传代码

**方式一：使用 Git（推荐）**

```bash
cd /var/www/waylink

# 如果使用私有仓库，需要配置 SSH 密钥或使用 HTTPS
# HTTPS 方式（需要输入用户名和密码）
git clone https://your-repository-url/waylink-hub.git backend

# 或者先在本地打包，上传到服务器
# scp waylink-hub.tar.gz waylink@your-server-ip:/var/www/waylink/
# 然后解压
```

**方式二：使用 SCP 上传**

```bash
# 在本地执行（替换为你的服务器信息）
scp -r /path/to/waylink-hub waylink@your-server-ip:/var/www/waylink/
```

### 5.3 创建虚拟环境

```bash
cd /var/www/waylink/backend

# 创建 Python 虚拟环境
python3 -m venv venv

# 激活虚拟环境
source venv/bin/activate

# 升级 pip
pip install --upgrade pip

# 安装依赖
pip install -r requirements.txt
```

### 5.4 验证安装

```bash
# 验证 Django 是否安装成功
python manage.py --version

# 验证所有依赖
pip list
```

---

## 6. 配置应用环境

### 6.1 创建环境变量文件

```bash
cd /var/www/waylink/backend

# 创建 .env 文件
nano .env
```

### 6.2 填写环境变量

```env
# ==================== Django 设置 ====================

# 关闭调试模式（生产环境必须为 False）
DEBUG=False

# 密钥（使用随机生成的长字符串）
SECRET_KEY=your-very-long-random-secret-key-generate-with-django-secret

# 允许的域名（替换为你的域名，用逗号分隔）
ALLOWED_HOSTS=your-domain.com,www.your-domain.com

# ==================== 数据库设置 ====================
DB_NAME=waylink
DB_USER=waylink_user
DB_PASSWORD=Your-Strong-Password-Here
DB_HOST=localhost
DB_PORT=5432

# ==================== Gunicorn 设置 ====================
GUNICORN_BIND=127.0.0.1:8000

# ==================== 管理员邮箱（可选）================
ADMIN_EMAIL=admin@your-domain.com
```

### 6.3 生成安全的密钥

```bash
# 使用 Django 生成安全的密钥
python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
```

### 6.4 初始化数据库

```bash
# 设置 Django 使用生产配置
export DJANGO_SETTINGS_MODULE=waylink.settings_production

# 运行数据库迁移
python manage.py migrate

# 创建超级管理员用户
python manage.py createsuperuser

# 收集静态文件
python manage.py collectstatic --noinput
```

### 6.5 创建日志目录

```bash
mkdir -p /var/www/waylink/backend/logs
touch /var/www/waylink/backend/logs/django.log
touch /var/www/waylink/backend/logs/gunicorn-error.log
touch /var/www/waylink/backend/logs/gunicorn-access.log
```

---

## 7. 配置 Gunicorn

### 7.1 编辑 Gunicorn 配置

项目已包含 `gunicorn.conf.py`，确保配置正确：

```bash
cd /var/www/waylink/backend

# 编辑配置文件（检查配置）
cat gunicorn.conf.py
```

确保 `gunicorn.conf.py` 中的以下配置正确：

```python
import os
import multiprocessing

base_dir = os.path.dirname(os.path.abspath(__file__))
os.chdir(base_dir)

# Worker 数量（根据 CPU 核心数自动计算）
workers = multiprocessing.cpu_count() * 2 + 1

# 绑定地址
bind = os.environ.get('GUNICORN_BIND', '127.0.0.1:8000')

# 日志文件
errorlog = os.path.join(base_dir, 'logs/gunicorn-error.log')
accesslog = os.path.join(base_dir, 'logs/gunicorn-access.log')
loglevel = 'info'

# 进程名
proc_name = 'waylink'

# 预加载应用
preload_app = True
```

### 7.2 测试 Gunicorn 启动

```bash
cd /var/www/waylink/backend
source venv/bin/activate

# 测试启动
gunicorn -c gunicorn.conf.py waylink.wsgi:application

# 如果看到类似 "Booting worker with pid: xxx" 的输出，说明启动成功
# 使用 Ctrl+C 停止测试
```

---

## 8. 配置 Nginx

### 8.1 创建 Nginx 配置文件

```bash
sudo nano /etc/nginx/sites-available/waylink
```

### 8.2 填写配置内容

```nginx
# HTTP 配置
server {
    listen 80;
    server_name your-domain.com www.your-domain.com;

    # 重定向到 HTTPS（SSL 配置完成后启用）
    # return 301 https://$server_name$request_uri;

    # 根目录和索引
    root /var/www/waylink/backend;
    index index.html;

    # 访问日志
    access_log /var/log/nginx/waylink-access.log;
    error_log /var/log/nginx/waylink-error.log;

    # 静态文件
    location /static/ {
        alias /var/www/waylink/backend/staticfiles/;
        expires 30d;
        add_header Cache-Control "public, immutable";
    }

    # 媒体文件
    location /media/ {
        alias /var/www/waylink/backend/media/;
        expires 30d;
        add_header Cache-Control "public, immutable";
    }

    # API 请求代理
    location /api/ {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_connect_timeout 60s;
        proxy_send_timeout 60s;
        proxy_read_timeout 60s;
        proxy_buffering on;
        proxy_buffer_size 4k;
        proxy_buffers 8 32k;
    }

    # 健康检查端点
    location /health/ {
        access_log off;
        return 200 "OK";
        add_header Content-Type text/plain;
    }
}
```

### 8.3 启用站点配置

```bash
# 创建软链接
sudo ln -s /etc/nginx/sites-available/waylink /etc/nginx/sites-enabled/

# 检查默认配置（如果有）
# sudo rm /etc/nginx/sites-enabled/default

# 测试 Nginx 配置
sudo nginx -t

# 重载 Nginx
sudo systemctl reload nginx
```

### 8.4 验证 Nginx 配置

```bash
# 检查 Nginx 状态
sudo systemctl status nginx

# 测试 API 端点
curl http://localhost/api/cabinets/

# 应该返回 JSON 响应或 401（未认证）
```

---

## 9. 配置 Systemd 服务

### 9.1 创建服务文件

```bash
sudo nano /etc/systemd/system/waylink.service
```

### 9.2 填写服务配置

```ini
[Unit]
Description=WaylinkHub Django Application
After=network.target postgresql.service

[Service]
User=waylink
Group=waylink
WorkingDirectory=/var/www/waylink/backend
Environment="PATH=/var/www/waylink/backend/venv/bin"
Environment="DJANGO_SETTINGS_MODULE=waylink.settings_production"
Environment="PYTHONPATH=/var/www/waylink/backend"

# 绑定端口
ExecStart=/var/www/waylink/backend/venv/bin/gunicorn \
    -c /var/www/waylink/backend/gunicorn.conf.py \
    --pid /var/www/waylink/backend/logs/gunicorn.pid \
    waylink.wsgi:application

# 重启配置
Restart=on-failure
RestartSec=5

# 日志
StandardOutput=syslog
StandardError=syslog
SyslogIdentifier=waylink

[Install]
WantedBy=multi-user.target
```

### 9.3 重新加载 systemd

```bash
# 重新加载 systemd
sudo systemctl daemon-reload

# 启用开机自启
sudo systemctl enable waylink

# 启动服务
sudo systemctl start waylink

# 查看服务状态
sudo systemctl status waylink

# 查看实时日志
sudo journalctl -u waylink -f
```

### 9.4 验证服务运行

```bash
# 检查进程
ps aux | grep gunicorn

# 测试 API
curl http://localhost/api/cabinets/

# 检查日志
tail -f /var/www/waylink/backend/logs/django.log
```

---

## 10. 配置 SSL 证书

### 10.1 安装 Certbot

```bash
# 添加 Certbot 仓库
sudo apt install -y certbot python3-certbot-nginx

# 验证安装
certbot --version
```

### 10.2 申请 SSL 证书

```bash
# 申请证书（替换为你的域名）
sudo certbot --nginx -d your-domain.com -d www.your-domain.com

# 按提示输入：
# 1. 输入邮箱地址（用于证书到期提醒）
# 2. 同意服务条款
# 3. 选择是否接收邮件
# 4. 选择是否重定向 HTTP 到 HTTPS（建议选择 2）
```

### 10.3 验证自动续期

```bash
# 测试续期（dry-run）
sudo certbot renew --dry-run

# 设置自动续期任务
sudo crontab -e

# 添加以下行（每天凌晨 2 点检查续期）
0 2 * * * certbot renew --quiet
```

### 10.4 更新 Nginx 配置

Certbot 会自动修改 Nginx 配置，添加 SSL 相关配置。验证配置：

```bash
# 查看生成的配置
sudo nano /etc/nginx/sites-available/waylink
```

配置应包含 HTTPS 部分，类似于：

```nginx
server {
    listen 443 ssl http2;
    server_name your-domain.com www.your-domain.com;

    ssl_certificate /etc/letsencrypt/live/your-domain.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/your-domain.com/privkey.pem;

    # SSL 安全设置
    ssl_session_timeout 1d;
    ssl_session_cache shared:SSL:50m;
    ssl_session_tickets off;

    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers ECDHE-ECDSA-AES128-GCM-SHA256:ECDHE-RSA-AES128-GCM-SHA256:ECDHE-ECDSA-AES256-GCM-SHA384:ECDHE-RSA-AES256-GCM-SHA384;
    ssl_prefer_server_ciphers off;

    add_header Strict-Transport-Security "max-age=63072000" always;

    # ... 其余配置与 HTTP 相同
}
```

---

## 11. 配置防火墙

### 11.1 安装和配置 UFW

```bash
# 安装 UFW
sudo apt install -y ufw

# 设置默认策略
sudo ufw default deny incoming
sudo ufw default allow outgoing

# 允许 SSH 连接（修改端口号如果使用了非标准端口）
sudo ufw allow 22/tcp

# 允许 HTTP 和 HTTPS
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp

# 启用防火墙
sudo ufw enable

# 查看状态
sudo ufw status verbose
```

### 11.2 仅允许特定 IP 访问管理接口（可选）

```bash
# 如果需要限制管理后台访问 IP
sudo ufw allow from your-office-ip to any port 22
```

---

## 12. 配置备份

### 12.1 创建数据库备份脚本

```bash
sudo nano /etc/cron.daily/waylink-backup
```

### 12.2 填写备份脚本

```bash
#!/bin/bash

# 配置变量
BACKUP_DIR="/var/backups/waylink"
DB_NAME="waylink"
DB_USER="waylink_user"
DB_PASSWORD="Your-Strong-Password-Here"
RETENTION_DAYS=7

# 创建备份目录
mkdir -p $BACKUP_DIR

# 生成备份文件名
BACKUP_FILE="$BACKUP_DIR/waylink_$(date +%Y%m%d_%H%M%S).sql.gz"

# 执行备份
echo "Backing up database to $BACKUP_FILE"
PGPASSWORD=$DB_PASSWORD pg_dump -U $DB_USER -h localhost $DB_NAME | gzip > $BACKUP_FILE

# 删除旧备份
find $BACKUP_DIR -name "waylink_*.sql.gz" -mtime +$RETENTION_DAYS -delete

# 同步到远程存储（可选）
# rclone sync $BACKUP_DIR remote:waylink-backup

echo "Backup completed: $BACKUP_FILE"
```

### 12.3 设置备份脚本权限

```bash
sudo chmod +x /etc/cron.daily/waylink-backup

# 测试备份脚本
sudo /etc/cron.daily/waylink-backup

# 查看备份文件
ls -lh /var/backups/waylink/
```

### 12.4 备份代码仓库（可选）

```bash
# 创建代码备份脚本
sudo nano /etc/cron.weekly/waylink-code-backup

#!/bin/bash
BACKUP_DIR="/var/backups/waylink/code"
CODE_DIR="/var/www/waylink"

mkdir -p $BACKUP_DIR
cd $CODE_DIR
tar -czf "$BACKUP_DIR/waylink_code_$(date +%Y%m%d).tar.gz" --exclude='venv' --exclude='__pycache__' --exclude='.git' .

find $BACKUP_DIR -name "waylink_code_*.tar.gz" -mtime +14 -delete
```

```bash
sudo chmod +x /etc/cron.weekly/waylink-code-backup
```

---

## 13. 运维管理

### 13.1 常用命令

```bash
# 服务管理
sudo systemctl start waylink      # 启动
sudo systemctl stop waylink       # 停止
sudo systemctl restart waylink    # 重启
sudo systemctl status waylink     # 状态
sudo systemctl enable waylink     # 开机自启
sudo systemctl disable waylink    # 取消自启

# 查看日志
sudo journalctl -u waylink -f           # 实时日志
sudo journalctl -u waylink -n 100       # 最近 100 行
sudo journalctl -u waylink --since "1 hour ago"

# 查看应用日志
tail -f /var/www/waylink/backend/logs/django.log
tail -f /var/www/waylink/backend/logs/gunicorn-error.log

# 查看 Nginx 日志
tail -f /var/log/nginx/waylink-access.log
tail -f /var/log/nginx/waylink-error.log
```

### 13.2 更新部署

```bash
# 切换到项目目录
cd /var/www/waylink/backend

# 备份数据库（重要！）
sudo /etc/cron.daily/waylink-backup

# 拉取最新代码
git pull

# 激活虚拟环境
source venv/bin/activate

# 安装新依赖
pip install -r requirements.txt

# 运行数据库迁移
export DJANGO_SETTINGS_MODULE=waylink.settings_production
python manage.py migrate

# 收集静态文件
python manage.py collectstatic --noinput

# 重启服务
sudo systemctl restart waylink

# 验证服务状态
sudo systemctl status waylink
```

### 13.3 性能监控

```bash
# 查看系统资源
htop

# 查看磁盘使用
df -h

# 查看内存使用
free -h

# 查看网络连接
ss -tulnp

# 查看 Gunicorn 进程
ps aux | grep gunicorn
```

### 13.4 健康检查

```bash
# API 健康检查
curl https://your-domain.com/health/

# 数据库连接检查
python manage.py dbshell
# 在 dbshell 中：SELECT 1;

# Django 系统检查
python manage.py check --deploy
```

---

## 14. 常见问题

### 14.1 500 内部服务器错误

```bash
# 1. 检查 Gunicorn 日志
sudo journalctl -u waylink -n 50

# 2. 检查 Django 应用日志
cat /var/www/waylink/backend/logs/django.log

# 3. 常见原因：
#    - 数据库连接失败
#    - 环境变量未正确设置
#    - 权限问题
#    - 静态文件路径错误
```

### 14.2 数据库连接失败

```bash
# 1. 检查 PostgreSQL 服务状态
sudo systemctl status postgresql

# 2. 检查数据库用户权限
su - postgres
psql -c "\du"  # 查看用户列表

# 3. 测试数据库连接
psql -U waylink_user -d waylink -h localhost -W

# 4. 检查 pg_hba.conf 配置
sudo nano /etc/postgresql/15/main/pg_hba.conf
```

### 14.3 静态文件不显示

```bash
# 1. 检查静态文件目录
ls -la /var/www/waylink/backend/staticfiles/

# 2. 重新收集静态文件
cd /var/www/waylink/backend
source venv/bin/activate
python manage.py collectstatic --noinput

# 3. 检查 Nginx 配置
sudo nginx -t

# 4. 重载 Nginx
sudo systemctl reload nginx
```

### 14.4 SSL 证书过期

```bash
# 手动续期
sudo certbot renew

# 检查证书到期时间
sudo certbot certificates
```

### 14.5 内存不足

```bash
# 1. 检查内存使用
free -h

# 2. 减少 Gunicorn workers
# 编辑 gunicorn.conf.py
workers = 2  # 减少 worker 数量

# 3. 重启服务
sudo systemctl restart waylink
```

### 14.6 端口被占用

```bash
# 1. 查看端口占用
sudo lsof -i :8000

# 2. 终止占用端口的进程
sudo kill -9 <PID>

# 或者修改 Gunicorn 端口
# 编辑 .env 文件
GUNICORN_BIND=127.0.0.1:8001
```

### 14.7 域名解析问题

```bash
# 1. 检查域名解析
nslookup your-domain.com
dig your-domain.com

# 2. 检查 Nginx server_name 配置
sudo nano /etc/nginx/sites-available/waylink
```

---

## 快速部署清单

```
[ ] 1. 服务器 SSH 连接
[ ] 2. 创建部署用户 waylink
[ ] 3. 系统更新
[ ] 4. 安装 Python 3, PostgreSQL, Nginx
[ ] 5. 创建数据库 waylink 和用户 waylink_user
[ ] 6. 上传项目代码到 /var/www/waylink/backend
[ ] 7. 创建 Python 虚拟环境并安装依赖
[ ] 8. 创建 .env 文件并配置环境变量
[ ] 9. 运行数据库迁移
[ ] 10. 创建超级管理员用户
[ ] 11. 配置 Nginx
[ ] 12. 创建 Systemd 服务
[ ] 13. 启动并验证服务
[ ] 14. 配置 SSL 证书
[ ] 15. 配置防火墙
[ ] 16. 配置自动备份
[ ] 17. 测试所有功能
```

---

## 联系支持

如遇到问题，请提供以下信息：

1. 操作系统版本：`cat /etc/os-release`
2. 错误日志：`sudo journalctl -u waylink -n 100`
3. Nginx 错误日志：`cat /var/log/nginx/waylink-error.log`
4. Django 应用日志：`cat /var/www/waylink/backend/logs/django.log`

---

> 文档版本：2.0.0
> 最后更新：2025-01-20
> 项目地址：https://github.com/your-repo/waylink-hub
