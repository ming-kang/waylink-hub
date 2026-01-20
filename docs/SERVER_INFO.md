# 驿联站服务器配置记录

> 创建日期：2026-01-20
> 最后更新：2026-01-20

---

## 服务器信息

| 项目 | 值 |
|-----|------|
| 主机商 | KVM VPS |
| CPU | 1 vCPU |
| 内存 | 1 GB |
| 磁盘 | 25 GB SSD |
| 带宽 | 1 Gbps |
| IPv4 | xxx.xxx.xxx.xxx |
| 系统 | Debian 12 (Bookworm) |
| SSH端口 | 22 |

---

## 已安装软件

| 软件 | 版本 | 状态 |
|-----|------|------|
| Python | 3.11.2 | 已安装 |
| PostgreSQL | 15.x | 已安装、已启动 |
| Nginx | 1.22.x | 已安装、已启动 |
| Git | - | 已安装 |

---

## 数据库配置

### 连接信息

| 项目 | 值 |
|-----|------|
| 数据库名 | waylink |
| 用户名 | waylink_user |
| 密码 | Yk8xM2pL5n1 |
| 主机 | localhost |
| 端口 | 5432 |
| 编码 | UTF-8 |
| 时区 | Asia/Shanghai |

### 连接命令

```bash
# 方式1：直接连接
psql -U waylink_user -d waylink

# 方式2：使用postgres用户
sudo -u postgres psql -d waylink
```

---

## 部署目录

| 目录 | 路径 |
|-----|------|
| 项目根目录 | `/var/www/waylink` |
| 后端代码 | `/var/www/waylink/backend` |
| 日志目录 | `/var/www/waylink/backend/logs` |

---

## 待完成配置

- [ ] 上传代码（Git Clone）
- [ ] 创建Python虚拟环境
- [ ] 安装依赖
- [ ] 配置环境变量（.env）
- [ ] 初始化数据库（migrate）
- [ ] 创建管理员账户
- [ ] 配置Nginx站点
- [ ] 配置Gunicorn systemd服务
- [ ] 配置SSL证书
- [ ] 配置防火墙

---

## 常用命令

### 服务管理

```bash
# Nginx
sudo systemctl status nginx
sudo systemctl reload nginx

# PostgreSQL
sudo systemctl status postgresql

# 查看端口占用
sudo ss -tlnp | grep -E '(80|443|5432)'
```

### 系统资源

```bash
# 内存使用
free -h

# 磁盘使用
df -h

# CPU负载
uptime
```

---

## SSH登录信息

```bash
ssh root@xxx.xxx.xxx.xxx -p 22
```

---

## 后续步骤

1. 上传代码到服务器
2. 完成部署配置
3. 测试API接口
4. 配置域名和SSL

---

## 注意事项

- 数据库密码已记录：`Yk8xM2pL5n1`
- 建议配置SSH密钥登录
- 建议配置防火墙（ufw）
- 定期检查磁盘空间
