# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

**驿联站 (WaylinkHub)** - Smart bus station project providing intelligent storage cabinets, cross-station transfer, fast charging, and public WiFi services.

## Technology Stack

| Layer | Technology |
|-------|------------|
| Backend | Python + Django + Django REST Framework |
| Database | SQLite (unified for dev and production) |
| Authentication | JWT (djangorestframework-simplejwt) |
| Device Communication | ESP32 HTTP polling |
| Deployment | VPS (Linux + Gunicorn + Nginx) |

## Project Structure

```
backend/
├── manage.py
├── requirements.txt
├── gunicorn.conf.py              # Gunicorn WSGI config
├── nginx.conf                    # Nginx reverse proxy config
├── waylink/                      # Django project settings
│   ├── settings.py               # Main settings (DEBUG=True by default)
│   ├── settings_production.py   # Production settings
│   ├── urls.py                   # URL routing
│   └── wsgi.py / asgi.py
└── apps/
    ├── users/                    # User auth: register, login, JWT
    ├── cabinets/                 # Cabinet CRUD, status tracking
    ├── orders/                   # Order lifecycle: create→pay→use→complete
    ├── devices/                  # ESP32 heartbeat, status reporting, open commands
    └── operations/               # Admin: stats, health, alerts
```

## Documentation Files

| File | Description |
|------|-------------|
| `docs/WayLinkHub.md` | Project overview, hardware dev guide (ESP32) |
| `docs/DevPlan.md` | Development plan & progress |
| `docs/API.md` | Complete API documentation |
| `docs/DeployGuidance.md` | VPS deployment guide (detailed) |
| `docs/TODO.md` | Current optimization tasks |

## Architecture Patterns

### ESP32 Device Communication (Polling Model)
The system uses HTTP polling instead of WebSockets:
1. **Heartbeat**: ESP32 calls `POST /api/devices/heartbeat/` with `X-API-Key` header
2. **Status Query**: ESP32 polls `GET /api/devices/{id}/open/` to get pending open commands
3. **Status Report**: ESP32 calls `POST /api/devices/status/` to report sensor data (door, lock_angle, has_item)
4. **Server Query**: Admin can trigger `GET /api/devices/query/{id}/` which ESP32 polls to get query commands

### Order State Machine
```
pending → paid → in_use → completed
              ↘→ cancelled
              ↘→ overdue (automatic when end_time passes)
```

### Device-Order Binding
- One Device controls multiple Cabinets (ManyToMany via `bound_cabinets`)
- One Order binds to one Cabinet
- Pickup code (6-digit) validates open requests

## Common Commands

```bash
cd backend

# Setup development environment
python -m venv venv
source venv/bin/activate  # or venv\Scripts\activate on Windows
pip install -r requirements.txt

# Run development server
python manage.py runserver

# Create migrations (after model changes)
python manage.py makemigrations
python manage.py migrate

# Verify no errors
python manage.py check

# Create admin user
python manage.py createsuperuser
```

## API Endpoints

| Module | Base URL | Auth | Purpose |
|--------|----------|------|---------|
| Auth | `/api/auth/register/` | None | User registration |
| Auth | `/api/auth/login/` | None | Get JWT tokens |
| Auth | `/api/auth/token/refresh/` | JWT | Refresh access token |
| Cabinets | `/api/cabinets/` | None | List all cabinets |
| Cabinets | `/api/cabinets/available/` | None | Filter available cabinets |
| Cabinets | `/api/cabinets/{id}/status/` | None | Real-time cabinet state |
| Orders | `/api/orders/create/` | JWT | Reserve cabinet |
| Orders | `/api/orders/{id}/pay/` | JWT | Process payment |
| Orders | `/api/orders/{id}/extend/` | JWT | Add time to order |
| Orders | `/api/orders/my/` | JWT | User's order list |
| Devices | `/api/devices/heartbeat/` | API Key | ESP32 heartbeat |
| Devices | `/api/devices/status/` | API Key | Sensor data upload |
| Devices | `/api/devices/{id}/open/` | API Key | ESP32 polls for commands |
| Devices | `/api/devices/open/by-code/` | JWT | User scans to open |
| Admin | `/api/admin/health/` | None | Service health check |
| Admin | `/api/admin/stats/` | Admin | Dashboard statistics |
| Admin | `/api/admin/revenue/` | Admin | Revenue by date/station |

See `docs/API.md` for complete endpoint documentation.

## Key Implementation Details

- **Custom User Model**: Uses `users.User` (extends AbstractUser with phone, balance fields)
- **JWT Config**: Access token: 1 day, Refresh token: 7 days with rotation
- **Device API Key**: Stored in `Device.api_key`, passed via `X-API-Key` header
- **Cabinet Status**: Tracks `lock_angle`, `lock_locked`, `has_item` from ESP32 sensors
- **Pickup Code**: 6-digit random numeric, generated on payment

## Configuration

Environment variables (in `.env`):
- `SECRET_KEY`: Django secret key
- `DEBUG`: Set to 'False' in production
- `ALLOWED_HOSTS`: Comma-separated hostnames

## Development Notes

- All cabinet/order endpoints except create/pay use `AllowAny` permission (intentional for public kiosk access)
- Device endpoints use `X-API-Key` header authentication, not JWT
- No formal test suite exists - verify APIs with curl after changes
- SQLite database file: `backend/db.sqlite3`
- **docs/ folder is NOT tracked in git** (development early stage, documentation kept locally)

## Current Optimization Work

See `docs/TODO.md` for the current list of technical improvements being made.

**Key constraint**: All fixes must be implemented without changing API documentation to avoid impacting frontend and hardware teams.
