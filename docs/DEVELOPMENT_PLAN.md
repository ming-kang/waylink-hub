# 驿联站后端开发计划

> 最后更新：2025-01-19
> 状态：✅ **全部完成**

## 项目概述

**驿联站 (WaylinkHub)** - 智慧公交站项目后端开发计划

| 层级 | 技术选型 |
|-----|---------|
| Web框架 | Python + Django + Django REST Framework |
| 数据库 | SQLite（开发）/ PostgreSQL（生产） |
| 认证 | 账号密码 + JWT |
| 部署 | VPS (Linux + Gunicorn + Nginx) |

---

## 进度概览

| 阶段 | 状态 | 完成度 |
|-----|------|--------|
| 1. 项目初始化与基础配置 | ✅ 已完成 | 100% |
| 2. 用户认证模块 | ✅ 已完成 | 100% |
| 3. 储物柜管理模块 | ✅ 已完成 | 100% |
| 4. 订单模块 | ✅ 已完成 | 100% |
| 5. 设备通信模块 | ✅ 已完成 | 100% |
| 6. 运维管理API | ✅ 已完成 | 100% |
| 7. API文档编写 | ✅ 已完成 | 100% |
| 8. 部署配置与测试 | ✅ 已完成 | 100% |

**总体进度：8/8（100%）** 🎉

---

## 项目文件结构

```
WaylinkHub/
├── backend/
│   ├── manage.py
│   ├── requirements.txt
│   ├── gunicorn.conf.py              # Gunicorn配置
│   ├── waylink/
│   │   ├── settings.py               # 开发环境配置
│   │   ├── settings_production.py    # 生产环境配置
│   │   └── urls.py
│   └── apps/
│       ├── users/                    # 用户认证模块
│       ├── cabinets/                 # 储物柜模块
│       ├── orders/                   # 订单模块
│       ├── devices/                  # ESP32设备通信
│       └── operations/               # 运维管理模块
├── docs/
│   ├── DEVELOPMENT_PLAN.md           # 本开发计划
│   ├── DEPLOYMENT.md                 # 部署指南
│   └── api/
│       └── README.md                 # API接口文档
└── CLAUDE.md                         # AI开发规范
```

---

## 开发阶段

### 1. 项目初始化与基础配置 ✅
| 任务 | 说明 | 状态 |
|-----|------|------|
| 创建 Django 项目 | `backend/` 目录结构 | ✅ 已完成 |
| 安装依赖 | Django, DRF, djangorestframework-simplejwt, django-cors-headers | ✅ 已完成 |
| 配置 settings.py | 数据库、跨域、认证方式 | ✅ 已完成 |
| 创建 requirements.txt | 依赖清单 | ✅ 已完成 |
| 配置路由总览 | urls.py 路由分发 | ✅ 已完成 |

---

### 2. 用户认证模块 ✅
| 任务 | 说明 | 状态 |
|-----|------|------|
| 创建 users app | 用户模型扩展（UserProfile） | ✅ 已完成 |
| 用户注册接口 | `POST /api/auth/register/` | ✅ 已完成 |
| 用户登录接口 | `POST /api/auth/login/` 返回 JWT | ✅ 已完成 |
| JWT 刷新接口 | `POST /api/auth/token/refresh/` | ✅ 已完成（DRF内置） |
| 当前用户信息 | `GET /api/auth/me/` | ✅ 已完成 |
| 测试 | 注册、登录、认证流程 | ✅ 已通过 |

---

### 3. 储物柜管理模块 ✅
| 任务 | 说明 | 状态 |
|-----|------|------|
| 创建 cabinets app | - | ✅ 已完成 |
| 柜子模型 | 编号、位置、尺寸、状态、费率 | ✅ 已完成 |
| 柜子列表 | `GET /api/cabinets/` | ✅ 已完成 |
| 柜子详情 | `GET /api/cabinets/{id}/` | ✅ 已完成 |
| 柜子状态 | `GET /api/cabinets/{id}/status/` | ✅ 已完成 |
| 可用柜子筛选 | 按位置、尺寸过滤空闲柜子 | ✅ 已完成 |
| 测试 | 列表查询、状态更新 | ✅ 已通过 |

**测试数据**：
| 编号 | 尺寸 | 站点 | 价格 |
|-----|------|------|------|
| A001 | 小柜 | 火车站 | 2元/时 |
| A002 | 小柜 | 火车站 | 2元/时 |
| B001 | 中柜 | 火车站 | 3元/时 |
| C001 | 大柜 | 汽车站 | 5元/时 |

---

### 4. 订单模块 ✅
| 任务 | 说明 | 状态 |
|-----|------|------|
| 创建 orders app | - | ✅ 已完成 |
| 订单模型 | 用户、柜子、开始/结束时间、状态、金额 | ✅ 已完成 |
| 创建预约订单 | `POST /api/orders/create/` | ✅ 已完成 |
| 我的订单列表 | `GET /api/orders/my/` | ✅ 已完成 |
| 订单详情 | `GET /api/orders/{id}/` | ✅ 已完成 |
| 订单支付 | `POST /api/orders/{id}/pay/` | ✅ 已完成 |
| 续费接口 | `POST /api/orders/{id}/extend/` | ✅ 已完成 |
| 取消订单 | `POST /api/orders/{id}/cancel/` | ✅ 已完成 |
| 测试 | 订单CRUD、状态流转 | ✅ 已通过 |

**订单状态流转**：
```
待支付(pending) → 已预约(paid) → 使用中(in_use) → 已完成(completed)
                 → 已取消(cancelled)          → 逾期未取(overdue)
```

**测试数据**：
| 用户 | 余额 | 订单号 | 柜子 | 状态 | 金额 | 取件码 |
|-----|------|--------|------|------|------|--------|
| testuser | 88元 | O2026... | B001 | 已预约 | 12元 | 578674 |

---

### 5. 设备通信模块（ESP32对接）✅
| 任务 | 说明 | 状态 |
|-----|------|------|
| 创建 devices app | - | ✅ 已完成 |
| 设备模型 | 设备ID、站点、在线状态、柜子绑定 | ✅ 已完成 |
| 设备日志模型 | 心跳、开柜、状态变更记录 | ✅ 已完成 |
| 心跳上报接口 | `POST /api/devices/heartbeat/` | ✅ 已完成 |
| 状态上报接口 | `POST /api/devices/status/` | ✅ 已完成 |
| 开柜指令接口 | `POST /api/devices/{id}/open/` | ✅ 已完成 |
| 扫码开柜接口 | `POST /api/devices/open/by-code/` | ✅ 已完成 |
| 设备日志查询 | `GET /api/devices/{id}/logs/` | ✅ 已完成 |
| 设备管理接口 | `GET /api/devices/manage/` | ✅ 已完成 |
| 安全验证 | API密钥认证 | ✅ 已完成 |
| 测试 | 心跳、开柜、状态上报 | ✅ 已通过 |

**ESP32 对接流程**：
```
ESP32 → POST /api/devices/heartbeat/ (X-API-Key) → 后端
后端 ← 心跳响应 (status: online)

ESP32 → GET /api/devices/{id}/open/ (轮询) → 后端
后端 ← 开柜指令或 "none"

ESP32 → POST /api/devices/status/ → 后端
```

**测试数据**：
| 设备ID | 站点 | 绑定柜子 | API密钥 |
|--------|------|---------|---------|
| ESP32_001 | 火车站 | A001, A002, B001 | esp32_test_key_001 |

---

### 6. 运维管理API ✅
| 任务 | 说明 | 状态 |
|-----|------|------|
| 创建 operations app | - | ✅ 已完成 |
| 仪表盘统计 | `GET /api/admin/stats/` | ✅ 已完成 |
| 收入统计 | `GET /api/admin/revenue/` | ✅ 已完成 |
| 所有订单 | `GET /api/admin/orders/` | ✅ 已完成 |
| 柜子管理 | `GET/PUT /api/admin/cabinets/` | ✅ 已完成 |
| 设备管理 | `GET/PUT /api/admin/devices/` | ✅ 已完成 |
| 故障预警 | `GET /api/admin/alerts/` | ✅ 已完成 |
| 测试 | 统计接口、管理操作 | ✅ 已通过 |

**故障预警类型**：
| 类型 | 级别 | 说明 |
|-----|------|------|
| device_offline | warning | 设备离线 |
| low_battery | warning | 电量低（<20%） |
| order_overdue | warning | 订单逾期 |
| cabinet_maintenance | info | 柜子维护中 |

---

### 7. API文档编写 ✅
| 任务 | 说明 | 状态 |
|-----|------|------|
| API文档 | `docs/api/README.md` | ✅ 已完成 |
| 部署指南 | `docs/DEPLOYMENT.md` | ✅ 已完成 |

**API文档包含**：
- 概述与统一响应格式
- 认证模块（注册、登录、刷新Token）
- 储物柜模块（列表、详情、状态）
- 订单模块（创建、支付、续费、取消）
- 设备通信模块（心跳、状态上报、开柜）
- 运维管理模块（统计、收入、预警）
- 错误码说明

---

### 8. 部署配置与测试 ✅
| 任务 | 说明 | 状态 |
|-----|------|------|
| 生产配置 | `settings_production.py` | ✅ 已完成 |
| Gunicorn配置 | `gunicorn.conf.py` | ✅ 已完成 |
| Nginx配置 | `nginx.conf` | ✅ 已完成 |
| 部署指南 | `docs/DEPLOYMENT.md` | ✅ 已完成 |

**生产环境配置**：
- PostgreSQL 数据库连接
- 安全设置（SSL重定向、Cookie安全）
- Systemd 服务配置
- Let's Encrypt SSL 配置
- 数据库备份策略

---

## 启动开发服务器

```bash
cd backend
python manage.py runserver
```

访问 `http://localhost:8000/api/cabinets/` 测试 API。

---

## 团队分工

| 成员 | 负责方向 |
|-----|---------|
| 方明康 | 后端开发 |
| 陈卓 | 软硬件集成（ESP32） |
| 陈鹏宇 | 前端设计 + 用户研究 |

---

## 项目完成时间线

| 日期 | 完成内容 |
|-----|---------|
| 2025-01-19 | 项目初始化、用户认证、储物柜模块 |
| 2025-01-19 | 订单模块、设备通信模块 |
| 2025-01-19 | 运维管理API、API文档、部署配置 |

**总开发时间：约1天**
