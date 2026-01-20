# 驿联站 API 文档

> 版本：1.1.0
> 更新日期：2026-01-19

## 目录

- [快速开始](#快速开始)
- [认证说明](#认证说明)
- [用户模块](#用户模块-auth)
- [储物柜模块](#储物柜模块-cabinets)
- [订单模块](#订单模块-orders)
- [设备通信模块](#设备通信模块-devices)
- [运维管理模块](#运维管理模块-admin)
- [错误码说明](#错误码说明)

---

## 快速开始

### 基础信息

| 项目 | 值 |
|-----|------|
| 基础URL | `http://localhost:8000/api/` |
| 数据格式 | JSON |
| 编码 | UTF-8 |

### 统一响应格式

```json
{
    "code": 0,
    "message": "success",
    "data": { }
}
```

| 字段 | 类型 | 说明 |
|-----|------|------|
| code | int | 状态码，0表示成功 |
| message | string | 状态消息 |
| data | object | 响应数据 |

---

## 认证说明

系统使用两种认证方式：

### 1. 用户认证（JWT Token）

用于用户相关操作，Header 格式：

```
Authorization: Bearer <access_token>
```

Token 获取方式：
- 注册用户：`POST /api/auth/register/`
- 登录用户：`POST /api/auth/login/`

Token 有效期：24小时

### 2. 设备认证（API Key）

用于 ESP32 设备通信，Header 格式：

```
X-API-Key: <device_api_key>
```

---

## 用户模块 (Auth)

### 接口概览

| 方法 | 路径 | 说明 | 认证 |
|------|------|------|------|
| POST | `/api/auth/register/` | 注册用户 | 无 |
| POST | `/api/auth/login/` | 用户登录 | 无 |
| POST | `/api/auth/token/` | 获取Token (DRF) | 无 |
| POST | `/api/auth/token/refresh/` | 刷新Token | 无 |
| GET | `/api/auth/me/` | 获取当前用户信息 | JWT |
| GET | `/api/auth/<id>/` | 获取指定用户详情 | JWT |

---

### 注册用户

**POST** `/api/auth/register/`

#### 请求参数

| 参数 | 类型 | 必填 | 说明 |
|-----|------|------|------|
| username | string | 是 | 用户名 |
| phone | string | 是 | 手机号（11位） |
| password | string | 是 | 密码（至少6位） |
| password2 | string | 是 | 确认密码 |
| email | string | 否 | 邮箱 |

#### 请求示例

```json
{
    "username": "testuser",
    "phone": "13900139000",
    "password": "test123456",
    "password2": "test123456",
    "email": "test@example.com"
}
```

#### 响应示例

```json
{
    "code": 0,
    "message": "注册成功",
    "data": {
        "user": {
            "id": 2,
            "username": "testuser",
            "phone": "13900139000",
            "email": "test@example.com",
            "balance": "0.00",
            "created_at": "2026-01-19T20:16:49.211115+08:00"
        },
        "access": "eyJhbGciOiJIUzI1NiIs...",
        "refresh": "eyJhbGciOiJIUzI1NiIs..."
    }
}
```

---

### 用户登录

**POST** `/api/auth/login/`

#### 请求参数

| 参数 | 类型 | 必填 | 说明 |
|-----|------|------|------|
| phone | string | 是 | 手机号 |
| password | string | 是 | 密码 |

#### 请求示例

```json
{
    "phone": "13900139000",
    "password": "test123456"
}
```

#### 响应示例

```json
{
    "code": 0,
    "message": "登录成功",
    "data": {
        "user": {
            "id": 2,
            "username": "testuser",
            "phone": "13900139000",
            "balance": "100.00",
            "created_at": "2026-01-19T20:16:49.211115+08:00"
        },
        "access": "eyJhbGciOiJIUzI1NiIs...",
        "refresh": "eyJhbGciOiJIUzI1NiIs..."
    }
}
```

---

### 获取Token（DRF标准接口）

**POST** `/api/auth/token/`

返回 JWT Token 对（access + refresh）

#### 请求参数

| 参数 | 类型 | 必填 | 说明 |
|-----|------|------|------|
| username | string | 是 | 用户名 |
| password | string | 是 | 密码 |

#### 请求示例

```json
{
    "username": "testuser",
    "password": "test123456"
}
```

#### 响应示例

```json
{
    "access": "eyJhbGciOiJIUzI1NiIs...",
    "refresh": "eyJhbGciOiJIUzI1NiIs..."
}
```

---

### 刷新Token

**POST** `/api/auth/token/refresh/`

#### 请求参数

| 参数 | 类型 | 必填 | 说明 |
|-----|------|------|------|
| refresh | string | 是 | 刷新令牌 |

#### 请求示例

```json
{
    "refresh": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
}
```

#### 响应示例

```json
{
    "access": "eyJhbGciOiJIUzI1NiIs...",
    "refresh": "eyJhbGciOiJIUzI1NiIs..."
}
```

---

### 获取当前用户信息

**GET** `/api/auth/me/`

#### 需要认证

```
Authorization: Bearer <access_token>
```

#### 响应示例

```json
{
    "code": 0,
    "message": "success",
    "data": {
        "id": 2,
        "username": "testuser",
        "phone": "13900139000",
        "email": "test@example.com",
        "balance": "88.00",
        "created_at": "2026-01-19T20:16:49.211115+08:00"
    }
}
```

---

### 获取指定用户详情

**GET** `/api/auth/<id>/`

#### 需要认证

```
Authorization: Bearer <access_token>
```

#### 响应示例

```json
{
    "code": 0,
    "message": "success",
    "data": {
        "id": 2,
        "username": "testuser",
        "phone": "13900139000",
        "balance": "88.00",
        "created_at": "2026-01-19T20:16:49.211115+08:00"
    }
}
```

---

## 储物柜模块 (Cabinets)

### 接口概览

| 方法 | 路径 | 说明 | 认证 |
|------|------|------|------|
| GET | `/api/cabinets/` | 柜子列表 | 无 |
| GET | `/api/cabinets/available/` | 可用柜子列表 | 无 |
| POST | `/api/cabinets/create/` | 创建柜子 | JWT (Admin) |
| GET | `/api/cabinets/<cabinet_id>/` | 柜子详情 | 无 |
| GET | `/api/cabinets/<cabinet_id>/status/` | 柜子状态（实时） | 无 |

---

### 柜子列表

**GET** `/api/cabinets/`

#### 查询参数

| 参数 | 类型 | 说明 |
|-----|------|------|
| station | string | 站点筛选 |
| size | string | 尺寸筛选 (small/medium/large) |
| status | string | 状态筛选 |
| available | string | 仅显示可用柜子 (true/false) |

#### 响应示例

```json
{
    "code": 0,
    "message": "success",
    "data": [
        {
            "id": 1,
            "cabinet_id": "A001",
            "size": "small",
            "size_display": "小柜（放背包）",
            "location": "站厅东侧",
            "station": "火车站",
            "status": "available",
            "status_display": "空闲",
            "price_per_hour": "2.00"
        }
    ]
}
```

---

### 可用柜子列表

**GET** `/api/cabinets/available/`

快速筛选当前可用的柜子

#### 查询参数

| 参数 | 类型 | 说明 |
|-----|------|------|
| station | string | 站点筛选 |
| size | string | 尺寸筛选 |

#### 响应示例

```json
{
    "code": 0,
    "message": "success",
    "data": [
        {
            "id": 1,
            "cabinet_id": "A001",
            "size": "small",
            "size_display": "小柜（放背包）",
            "location": "站厅东侧",
            "station": "火车站",
            "status": "available",
            "status_display": "空闲",
            "price_per_hour": "2.00"
        }
    ]
}
```

---

### 创建柜子

**POST** `/api/cabinets/create/`

#### 需要认证（管理员）

```
Authorization: Bearer <admin_token>
```

#### 请求参数

| 参数 | 类型 | 必填 | 说明 |
|-----|------|------|------|
| cabinet_id | string | 是 | 柜子编号 (如 A001) |
| size | string | 是 | 尺寸 (small/medium/large) |
| location | string | 是 | 位置描述 |
| station | string | 是 | 所属站点 |
| price_per_hour | decimal | 是 | 单价（元/小时） |

#### 请求示例

```json
{
    "cabinet_id": "D001",
    "size": "large",
    "location": "南广场入口",
    "station": "汽车站",
    "price_per_hour": "5.00"
}
```

#### 响应示例

```json
{
    "code": 0,
    "message": "创建成功",
    "data": {
        "id": 6,
        "cabinet_id": "D001",
        "size": "large",
        "location": "南广场入口",
        "station": "汽车站",
        "status": "available",
        "price_per_hour": "5.00"
    }
}
```

---

### 柜子详情

**GET** `/api/cabinets/<cabinet_id>/`

#### 响应示例

```json
{
    "code": 0,
    "message": "success",
    "data": {
        "id": 1,
        "cabinet_id": "A001",
        "size": "small",
        "size_display": "小柜（放背包）",
        "location": "站厅东侧",
        "station": "火车站",
        "status": "available",
        "status_display": "空闲",
        "price_per_hour": "2.00",
        "device_id": null,
        "is_locked": true
    }
}
```

---

### 柜子状态（实时）

**GET** `/api/cabinets/<cabinet_id>/status/`

获取柜子的实时状态

#### 响应示例

```json
{
    "code": 0,
    "message": "success",
    "data": {
        "id": 1,
        "cabinet_id": "A001",
        "size": "small",
        "status": "available",
        "status_display": "空闲",
        "price_per_hour": "2.00",
        "is_locked": true
    }
}
```

---

## 订单模块 (Orders)

### 接口概览

| 方法 | 路径 | 说明 | 认证 |
|------|------|------|------|
| POST | `/api/orders/create/` | 创建订单 | JWT |
| GET | `/api/orders/my/` | 我的订单列表 | JWT |
| GET | `/api/orders/<order_id>/` | 订单详情 | JWT |
| POST | `/api/orders/<order_id>/pay/` | 订单支付 | JWT |
| POST | `/api/orders/<order_id>/extend/` | 订单续费 | JWT |
| POST | `/api/orders/<order_id>/cancel/` | 取消订单 | JWT |

### 订单状态说明

| 状态 | 说明 |
|------|------|
| pending | 待支付 |
| paid | 已预约 |
| in_use | 使用中 |
| completed | 已完成 |
| cancelled | 已取消 |

---

### 创建订单

**POST** `/api/orders/create/`

#### 需要认证

```
Authorization: Bearer <access_token>
```

#### 请求参数

| 参数 | 类型 | 必填 | 说明 |
|-----|------|------|------|
| cabinet_id | string | 是 | 柜子编号 |
| duration_hours | decimal | 是 | 使用时长（小时，最小0.5） |

#### 请求示例

```json
{
    "cabinet_id": "A001",
    "duration_hours": 2
}
```

#### 响应示例

```json
{
    "code": 0,
    "message": "订单创建成功",
    "data": {
        "id": 1,
        "order_no": "O20260119122609198Z",
        "cabinet_id": "A001",
        "cabinet_size": "small",
        "status": "pending",
        "status_display": "待支付",
        "duration_hours": "2.00",
        "price_per_hour": "2.00",
        "total_amount": "4.00"
    }
}
```

---

### 我的订单列表

**GET** `/api/orders/my/`

#### 需要认证

```
Authorization: Bearer <access_token>
```

#### 查询参数

| 参数 | 类型 | 说明 |
|-----|------|------|
| status | string | 状态筛选 |

#### 响应示例

```json
{
    "code": 0,
    "message": "success",
    "data": [
        {
            "id": 1,
            "order_no": "O20260119122609198Z",
            "cabinet_id": "A001",
            "status": "pending",
            "status_display": "待支付",
            "duration_hours": "2.00",
            "total_amount": "4.00",
            "created_at": "2026-01-19T20:26:09",
            "end_time": null
        }
    ]
}
```

---

### 订单详情

**GET** `/api/orders/<order_id>/`

#### 需要认证

```
Authorization: Bearer <access_token>
```

#### 响应示例

```json
{
    "code": 0,
    "message": "success",
    "data": {
        "id": 2,
        "order_no": "O20260119122632B6BZ",
        "user_phone": "13900139000",
        "cabinet_id": "B001",
        "cabinet_size": "medium",
        "status": "paid",
        "status_display": "已预约",
        "duration_hours": "4.00",
        "price_per_hour": "3.00",
        "total_amount": "12.00",
        "pickup_code": "578674",
        "end_time": "2026-01-20T00:26:33"
    }
}
```

---

### 订单支付

**POST** `/api/orders/<order_id>/pay/`

#### 需要认证

```
Authorization: Bearer <access_token>
```

#### 请求参数

| 参数 | 类型 | 必填 | 说明 |
|-----|------|------|------|
| payment_method | string | 是 | 支付方式 (wechat/alipay/balance) |

#### 请求示例

```json
{
    "payment_method": "balance"
}
```

#### 响应示例

```json
{
    "code": 0,
    "message": "支付成功",
    "data": {
        "id": 2,
        "order_no": "O20260119122632B6BZ",
        "status": "paid",
        "status_display": "已预约",
        "pickup_code": "578674"
    }
}
```

---

### 订单续费

**POST** `/api/orders/<order_id>/extend/`

#### 需要认证

```
Authorization: Bearer <access_token>
```

#### 请求参数

| 参数 | 类型 | 必填 | 说明 |
|-----|------|------|------|
| additional_hours | decimal | 是 | 增加时长（小时，最小0.5） |

#### 请求示例

```json
{
    "additional_hours": 1
}
```

#### 响应示例

```json
{
    "code": 0,
    "message": "续费成功",
    "data": {
        "id": 2,
        "duration_hours": "5.00",
        "total_amount": "15.00",
        "end_time": "2026-01-20T01:26:33"
    }
}
```

---

### 取消订单

**POST** `/api/orders/<order_id>/cancel/`

> 仅待支付状态的订单可以取消

#### 需要认证

```
Authorization: Bearer <access_token>
```

#### 响应示例

```json
{
    "code": 0,
    "message": "订单已取消",
    "data": {
        "id": 1,
        "status": "cancelled",
        "status_display": "已取消"
    }
}
```

---

## 设备通信模块 (Devices)

### 接口概览

| 方法 | 路径 | 说明 | 认证 |
|------|------|------|------|
| POST | `/api/devices/heartbeat/` | 心跳上报 | API Key |
| POST | `/api/devices/status/` | 状态上报 | API Key |
| POST | `/api/devices/open/by-code/` | 扫码开柜（用户） | JWT |
| GET | `/api/devices/<device_id>/open/` | 获取开柜指令（轮询） | API Key |
| GET | `/api/devices/<device_id>/logs/` | 设备日志查询 | JWT (Admin) |

> ESP32 设备应每 30 秒发送一次心跳，超过 10 分钟无心跳则标记为离线

---

### 心跳上报（ESP32）

**POST** `/api/devices/heartbeat/`

#### 认证方式

```
X-API-Key: <device_api_key>
```

#### 请求参数

| 参数 | 类型 | 说明 |
|-----|------|------|
| battery_level | int | 电量百分比（0-100） |

#### 请求示例

```json
{
    "battery_level": 85
}
```

#### 响应示例

```json
{
    "code": 0,
    "message": "心跳接收成功",
    "data": {
        "device_id": "ESP32_001",
        "status": "online"
    }
}
```

---

### 状态上报（ESP32）

**POST** `/api/devices/status/`

上报柜门状态和电量

#### 认证方式

```
X-API-Key: <device_api_key>
```

#### 请求参数

| 参数 | 类型 | 说明 |
|-----|------|------|
| cabinet_status | object | 柜子状态，格式: {"柜子ID": true/false} |
| battery_level | int | 电量百分比 |

#### 请求示例

```json
{
    "cabinet_status": {
        "A001": true,
        "A002": false
    },
    "battery_level": 80
}
```

- `true` 表示柜门关闭，`false` 表示柜门打开

#### 响应示例

```json
{
    "code": 0,
    "message": "状态更新成功"
}
```

---

### 获取开柜指令（ESP32轮询）

**GET** `/api/devices/<device_id>/open/`

设备应每 5 秒轮询一次，检查是否有待执行的开柜指令

#### 认证方式

```
X-API-Key: <device_api_key>
```

#### 响应示例（有指令）

```json
{
    "code": 0,
    "message": "有待执行指令",
    "data": {
        "command": "open_cabinet",
        "cabinet_id": "B001",
        "timestamp": "2026-01-19T20:30:23.874651+00:00"
    }
}
```

#### 响应示例（无指令）

```json
{
    "code": 0,
    "message": "无待执行指令",
    "data": {
        "command": "none"
    }
}
```

---

### 扫码开柜（用户）

**POST** `/api/devices/open/by-code/`

用户扫描柜子二维码，输入取件码开柜

#### 需要认证

```
Authorization: Bearer <access_token>
```

#### 请求参数

| 参数 | 类型 | 必填 | 说明 |
|-----|------|------|------|
| cabinet_id | string | 是 | 柜子编号 |
| pickup_code | string | 是 | 6位取件码 |

#### 请求示例

```json
{
    "cabinet_id": "B001",
    "pickup_code": "578674"
}
```

#### 响应示例

```json
{
    "code": 0,
    "message": "开柜成功",
    "data": {
        "cabinet_id": "B001",
        "action": "open",
        "order_id": 2
    }
}
```

---

### 设备日志查询（管理员）

**GET** `/api/devices/<device_id>/logs/`

#### 需要认证（管理员）

```
Authorization: Bearer <admin_token>
```

#### 响应示例

```json
{
    "code": 0,
    "message": "success",
    "data": [
        {
            "id": 3,
            "device_id": "ESP32_001",
            "log_type": "status",
            "message": "状态上报",
            "data": {"cabinet_status": {"B001": false}},
            "created_at": "2026-01-19T20:30:34.859454+08:00"
        }
    ]
}
```

---

## 运维管理模块 (Admin)

所有接口需要管理员认证。

```
Authorization: Bearer <admin_token>
```

### 接口概览

| 方法 | 路径 | 说明 |
|------|------|------|
| GET | `/api/admin/stats/` | 仪表盘统计 |
| GET | `/api/admin/revenue/` | 收入统计 |
| GET | `/api/admin/orders/` | 所有订单（分页） |
| GET/PUT | `/api/admin/cabinets/` | 柜子管理 |
| GET/PUT | `/api/admin/devices/` | 设备管理 |
| GET | `/api/admin/alerts/` | 故障预警 |

---

### 仪表盘统计

**GET** `/api/admin/stats/`

#### 查询参数

| 参数 | 类型 | 说明 |
|-----|------|------|
| days | int | 统计天数（默认7） |

#### 响应示例

```json
{
    "code": 0,
    "message": "success",
    "data": {
        "overview": {
            "total_users": 2,
            "total_orders": 2,
            "total_cabinets": 5,
            "total_devices": 1
        },
        "orders": {
            "total": 2,
            "completed": 0,
            "cancelled": 0,
            "total_amount": 16.0
        },
        "cabinets": {
            "total": 5,
            "available": 4,
            "in_use": 1,
            "maintenance": 0
        },
        "devices": {
            "total": 1,
            "online": 1,
            "offline": 0
        },
        "daily_orders": [
            {"date": "2026-01-19", "count": 2}
        ],
        "peak_hours": [
            {"hour": 12, "count": 2}
        ]
    }
}
```

---

### 收入统计

**GET** `/api/admin/revenue/`

#### 查询参数

| 参数 | 类型 | 说明 |
|-----|------|------|
| days | int | 统计天数（默认30） |

#### 响应示例

```json
{
    "code": 0,
    "message": "success",
    "data": {
        "total_revenue": 12.0,
        "total_orders": 1,
        "average_order": 12.0,
        "daily_revenue": [
            {"date": "2026-01-19", "revenue": 12.0, "orders": 1}
        ],
        "station_revenue": [
            {"station": "火车站", "revenue": 12.0, "orders": 1}
        ]
    }
}
```

---

### 所有订单（管理员）

**GET** `/api/admin/orders/`

#### 查询参数

| 参数 | 类型 | 说明 |
|-----|------|------|
| status | string | 状态筛选 |
| station | string | 站点筛选 |
| from | date | 开始日期 |
| to | date | 结束日期 |
| page | int | 页码（默认1） |
| page_size | int | 每页数量（默认20） |

---

### 柜子管理

**GET** `/api/admin/cabinets/` - 获取所有柜子

查询参数同 `/api/cabinets/`

**PUT** `/api/admin/cabinets/` - 更新柜子

#### 请求参数

| 参数 | 类型 | 说明 |
|-----|------|------|
| cabinet_id | string | 柜子编号（必填） |
| status | string | 状态 (available/in_use/maintenance) |
| price_per_hour | decimal | 单价 |
| location | string | 位置 |

#### 请求示例

```json
{
    "cabinet_id": "C001",
    "price_per_hour": 6,
    "status": "available"
}
```

#### 响应示例

```json
{
    "code": 0,
    "message": "更新成功",
    "data": {
        "cabinet_id": "C001",
        "price_per_hour": "6.00",
        "status": "available"
    }
}
```

---

### 设备管理

**GET** `/api/admin/devices/` - 获取所有设备

**PUT** `/api/admin/devices/` - 更新设备

#### 请求参数

| 参数 | 类型 | 说明 |
|-----|------|------|
| device_id | string | 设备ID（必填） |
| name | string | 设备名称 |
| station | string | 所属站点 |
| location | string | 位置 |
| is_active | bool | 是否启用 |

#### 请求示例

```json
{
    "device_id": "ESP32_001",
    "name": "火车站主柜控制器",
    "is_active": true
}
```

---

### 故障预警

**GET** `/api/admin/alerts/`

#### 响应示例

```json
{
    "code": 0,
    "message": "success",
    "data": {
        "total": 2,
        "alerts": [
            {
                "type": "device_offline",
                "level": "warning",
                "title": "设备离线",
                "message": "设备 ESP32_001 (火车站) 已离线",
                "device_id": "ESP32_001",
                "station": "火车站",
                "created_at": "2026-01-19T20:30:00+08:00"
            }
        ]
    }
}
```

#### 告警类型

| type | level | 说明 |
|-----|-------|------|
| device_offline | warning | 设备离线（超过10分钟无心跳） |
| low_battery | warning | 电量低（低于20%） |
| order_overdue | warning | 订单逾期（超过结束时间未取件） |
| cabinet_maintenance | info | 柜子维护中 |

---

## 错误码说明

### 业务错误码

| code | message | 说明 |
|-----|---------|------|
| 0 | success | 成功 |
| 400 | 参数错误 | 请求参数不合法 |
| 400 | 注册失败 | 用户名或手机号已存在 |
| 400 | 登录失败 | 手机号或密码错误 |
| 400 | 柜子不可用 | 柜子已被占用 |
| 400 | 订单已支付或已取消 | 订单状态不允许此操作 |
| 400 | 只有待支付的订单可以取消 | 状态不允许取消 |
| 400 | 无效的取件码或订单已过期 | 取件码验证失败 |
| 400 | 余额不足 | 余额支付时余额不足 |
| 401 | 无效的API密钥 | 设备认证失败 |
| 401 | 认证凭据未提供 | 未提供Token或API Key |
| 403 | 无权限访问 | 无管理员权限 |
| 404 | 用户不存在 | 用户ID不存在 |
| 404 | 柜子不存在 | 柜子ID不存在 |
| 404 | 订单不存在 | 订单ID不存在 |
| 404 | 设备不存在 | 设备ID不存在 |

### HTTP 状态码

| 状态码 | 说明 |
|-------|------|
| 200 | 成功 |
| 201 | 创建成功 |
| 400 | 请求参数错误 |
| 401 | 未认证或Token无效 |
| 403 | 无权限访问 |
| 404 | 资源不存在 |
| 500 | 服务器内部错误 |

---

## 附录

### 柜子尺寸说明

| size | size_display | 适用场景 |
|------|--------------|----------|
| small | 小柜（放背包） | 背包、小件物品 |
| medium | 中柜（放行李箱） | 20寸行李箱 |
| large | 大柜（放多个行李） | 24寸行李箱、多件物品 |

### 柜子状态说明

| status | status_display | 说明 |
|--------|----------------|------|
| available | 空闲 | 可预约 |
| in_use | 使用中 | 已有人使用 |
| maintenance | 维护中 | 不可用 |

### 订单状态说明

| status | status_display | 说明 |
|--------|----------------|------|
| pending | 待支付 | 已创建，待付款 |
| paid | 已预约 | 已付款，等待取件 |
| in_use | 使用中 | 已开柜使用中 |
| completed | 已完成 | 正常使用完毕 |
| cancelled | 已取消 | 已取消的订单 |
