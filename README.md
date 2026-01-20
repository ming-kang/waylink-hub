# 驿联站 (WaylinkHub)

智能公交站服务系统，提供储物柜、充电、Wifi 等便民服务。

## 功能特性

- **智能储物柜**：站点智能储物柜租用
- **跨站取件**：支持跨站点取件
- **快速充电**：USB/无线充电服务
- **公共WiFi**：站点免费上网

## 技术栈

| 层级 | 技术 |
|-----|------|
| 后端 | Python + Django + Django REST Framework |
| 数据库 | SQLite（开发/生产统一） |
| 认证 | JWT 账号密码登录 |
| 设备 | ESP32 硬件通信 |

## 项目结构

```
backend/
├── manage.py
├── requirements.txt
├── gunicorn.conf.py
├── waylink/           # Django 项目配置
│   ├── settings.py
│   ├── settings_production.py
│   └── urls.py
└── apps/              # 应用模块
    ├── users/         # 用户认证
    ├── cabinets/      # 储物柜管理
    ├── orders/        # 订单系统
    ├── devices/       # ESP32 设备通信
    └── operations/    # 运维管理
```

## 快速开始

```bash
# 创建虚拟环境
cd backend
python -m venv venv
source venv/bin/activate  # Linux/Mac
# venv\Scripts\activate   # Windows

# 安装依赖
pip install -r requirements.txt

# 配置环境变量
cp .env.example .env
# 编辑 .env 文件

# 运行开发服务器
python manage.py runserver
```

## API 文档

开发服务器运行后访问：`http://localhost:8000/api/`

主要接口：
- `POST /api/auth/register/` - 用户注册
- `POST /api/auth/login/` - 用户登录
- `GET /api/cabinets/` - 柜子列表
- `POST /api/orders/create/` - 创建订单
- `POST /api/devices/open/by-code/` - 扫码开柜

## 部署

```bash
# 安装生产依赖
pip install -r requirements.txt

# 配置生产环境
export DJANGO_SETTINGS_MODULE=waylink.settings_production

# 数据库迁移
python manage.py migrate

# 启动 Gunicorn
gunicorn -c gunicorn.conf.py waylink.wsgi:application
```

---

MIT License
