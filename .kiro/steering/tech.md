# Tech Stack

## Core
- Python 3.10
- Django 3.2
- Django REST Framework 3.13
- PostgreSQL 12 (via psycopg2)
- Redis (django-redis, used for response caching)

## Key Libraries
- `djangorestframework-simplejwt` — JWT authentication (Bearer tokens)
- `drf-yasg` — Swagger/OpenAPI docs at `/api/docs/` (DEBUG only)
- `django-modeltranslation` — Model-level i18n (es/ca/en)
- `django-anymail[mailgun]` — Transactional email via Mailgun
- `stripe` — Payment processing and webhooks
- `Pillow` — Image handling and resizing
- `qrcode[pil]` — QR code generation for member cards and event tickets
- `weasyprint` / `pdfkit` — PDF generation
- `django-background-tasks` — Async background jobs
- `Faker` — Test data generation
- `gunicorn` — Production WSGI server

## Infrastructure
- Dockerized: all dev and prod workflows run via Docker Compose
- Dev container support (VSCode devcontainer)
- CI via Drone (`.drone.yml`)

## Common Commands

All commands run inside Docker:

```bash
# Start dev server
docker compose up

# Run tests
docker compose run --rm ameba-backend python manage.py test

# Apply migrations
docker compose run --rm ameba-backend python manage.py migrate

# Create new migrations
docker compose run --rm ameba-backend python manage.py makemigrations

# Compile i18n messages
docker compose run --rm ameba-backend python manage.py compilemessages

# Collect static files
docker compose run --rm ameba-backend python manage.py collectstatic

# Load local demo data
docker compose run --rm ameba-backend python manage.py loadlocal

# Create superuser
docker compose run --rm ameba-backend python manage.py createsuperuser
```

## Environment
Config is loaded from `.env` via the `envs` library. Key variables include `DJANGO_SECRET`, `POSTGRES_*`, `REDIS_LOC`, `STRIPE_*`, `MG_*` (Mailgun), and `EMAIL_*`.

Settings module: `config.settings`
