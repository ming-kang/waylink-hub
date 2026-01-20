# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

**驿联站 (WaylinkHub)** - Smart bus station project providing intelligent storage cabinets, cross-station transfer, fast charging, and public WiFi services.

## Technology Stack

| Layer | Technology |
|-------|------------|
| Backend | Python + Django + Django REST Framework |
| Database | SQLite (unified for dev and production) |
| Authentication | JWT (账号密码登录) |
| API Documentation | Markdown docs in `docs/api/` |
| Deployment | VPS (Linux + Gunicorn + Nginx) |

## Project Structure (Backend)

```
backend/
├── manage.py
├── waylink/              # Django project settings
│   ├── settings.py
│   ├── urls.py
│   └── wsgi.py
├── apps/
│   ├── users/            # User authentication & profiles
│   ├── cabinets/         # Storage cabinet management
│   ├── orders/           # Order & reservation system
│   ├── devices/          # ESP32 device communication
│   └── operations/       # Admin/operations APIs
├── docs/
│   ├── api/              # API documentation (Markdown)
│   └── DEVELOPMENT_PLAN.md
└── requirements.txt
```

## Development Workflow

**IMPORTANT: Follow this workflow strictly for each development phase:**

1. **Read the development plan** in `docs/DEVELOPMENT_PLAN.md` before starting work
2. **Implement the phase** according to the plan requirements
3. **Test the implementation** before moving to the next phase:
   - Run `python manage.py check` to verify no errors
   - Run `python manage.py migrate` if models changed
   - Test APIs using the test scripts or curl commands
   - Verify all new endpoints work correctly
4. **Only proceed to the next phase** after all tests pass

## Common Commands

```bash
# Setup development environment
python -m venv venv
source venv/bin/activate  # or venv\Scripts\activate on Windows
pip install -r requirements.txt

# Run development server
python manage.py runserver

# Create migrations
python manage.py makemigrations

# Apply migrations
python manage.py migrate

# Check for errors
python manage.py check

# Create superuser (for admin access)
python manage.py createsuperuser
```

## API Endpoints

| Module | Base URL | Purpose |
|--------|----------|---------|
| Auth | `/api/auth/` | Register, login, JWT token |
| Cabinets | `/api/cabinets/` | Cabinet list, status, details |
| Orders | `/api/orders/` | Order creation, management |
| Devices | `/api/devices/` | ESP32 device control |
| Admin | `/api/admin/` | Statistics, device management |

See `docs/api/` for detailed endpoint documentation.

## Development Notes

- Use Django REST Framework serializers for API responses
- JWT authentication required for most endpoints (except auth)
- Device communication: ESP32 sends HTTP requests to backend APIs
- SQLite used for both development and production (simplified deployment)
- **Always update `docs/DEVELOPMENT_PLAN.md`** when a phase is completed

## Team

| Member | Role |
|--------|------|
| Fang Mingkang | Backend development |
| Chen Zhuo | Hardware integration (ESP32) |
| Chen Pengyu | Frontend design |
