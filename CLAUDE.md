# CLAUDE.md

This file provides guidance to Claude Code when working with code in this repository.

## Project Overview

Ameba Barcelona backend — a Django REST API serving [ameba-site](../ameba-site) (React SPA) for a cultural association. Handles events, e-commerce (shop items/carts), memberships & subscriptions, member profiles with QR cards, interviews/articles, and Stripe payments.

The frontend developer maintaining this repo does not have a Django/backend background — the original backend developer is no longer on the project. Favor explicit, well-explained changes over clever ones, and call out anything risky (migrations, Stripe, email delivery, prod config) before doing it.

## Stack

Django 3.2 · Django REST Framework 3.13 · PostgreSQL · Redis (cache, via `django-redis`) · djangorestframework-simplejwt (auth) · Stripe SDK 2.65 · django-anymail + Mailgun (transactional email) · django-background-tasks (async jobs, DB-backed, no Celery) · django-modeltranslation (ca/es content) · drf-yasg (Swagger docs) · Pillow/qrcode/weasyprint/pdfkit (images, QR, PDF generation) · gunicorn (prod server)

## Commands

Run locally via the venv in `env/`, or via docker-compose (`ameba-backend` container).

```bash
python manage.py runserver              # dev server on :8000
python manage.py test                   # full test suite
python manage.py test api.tests.event   # single test module
python manage.py makemigrations         # after model changes
python manage.py migrate                # apply migrations
python manage.py compilemessages        # after editing .po translation files
python manage.py collectstatic
python manage.py createsuperuser
python manage.py loadlocal              # load real-ish local dataset
python manage.py dumpdata --indent 2 > demo.json   # snapshot current data
python manage.py loaddata demo.json                # restore a snapshot
```

Docker (full stack incl. Postgres + Redis):
```bash
docker-compose up                                          # backend on :8000
docker-compose run --rm ameba-backend python manage.py <cmd>
```

Custom management commands (`api/management/commands/`): `loadlocal`, `dumpremote`, `regenerate_qr_codes`, `resize_images`, `send_email`, `generate_all_emails`.

## Architecture

Single Django app, `api`, organized **by resource, not by layer** — when working on a domain (e.g. "events"), the same filename recurs across each concern:

- `api/models/event.py`, `api/serializers/event.py`, `api/views/event.py`, `api/admin/event.py`, `api/tests/event.py`

Domains include: article, artist, cart, collaborators, covers, discount, event, genres, images, interview, item, legal, mailing_list, manifest, member, membership, orders, payment, subscriber, subscription, user, member_project.

Cross-cutting pieces (not per-resource):
- `api/urls.py` — all routes
- `api/permissions.py`, `api/authentication.py` — DRF permission classes, JWT auth
- `api/signals/` — side effects on model events, split by concern: `payments.py`, `mailgun.py`, `mailing_lists.py`, `memberships.py`, `subscriber.py`, `user.py`, `events.py`, `items.py`, `emails.py`
- `api/tasks/` — background jobs via `django-background-tasks` (no Celery/broker): `events.py`, `memberships.py`, `notifications.py`
- `api/stripe.py` — Stripe client wrapper; `api/mocks/stripe.py` — test mocks (no real Stripe calls in tests)
- `api/mailgun.py`, `api/email_factories.py` — transactional email building/sending via Anymail+Mailgun
- `api/qr_generator.py`, `api/qr_factories.py` — member card QR generation
- `api/images.py` — uploaded images are normalized to `.jpeg`, resized to 1920×1080
- `api/cache_utils.py` — Redis-backed response caching helpers
- `api/middleware/language.py` — per-request language handling (`ca`/`es`/`en`, no browser-based i18n — client sends explicit preference)
- `api/helpers/anonymization.py` — GDPR-style data anonymization

### Tests (`api/tests/`)

Mirrors the resource-per-file convention, plus subfolders:
- `api/tests/signals/` — signal-triggered side effects (subscriber, mailgun)
- `api/tests/integrations/stripe.py` — Stripe integration tests (against `api/mocks/stripe.py`)
- `api/tests/flows/events.py` — end-to-end flow tests
- `api/tests/helpers/` — shared test fixtures/utilities (user, payments, subscriptions)
- `api/tests/_helpers.py` — shared base test utilities
- `api/fixtures/` — `auth.json`, `local.json`, `media.tgz`

Run the full suite before considering any change to models/serializers/views/signals done — signal side effects in particular are easy to break silently.

### Authentication

JWT via `djangorestframework-simplejwt`. Obtain tokens at `POST /api/token/`, refresh at `POST /api/token/refresh/`. Frontend stores `access`/`refresh` in localStorage and sends `Authorization: Bearer <access>`. See `README.md` for the full curl walkthrough.

### Recurring pain points (from git history — be careful here)

- **Missing/conflicting migrations** are the single most common source of hotfixes in this repo (`hotfix/missing-migration*`, `hotfix/manifest-migrations`, `fix/conciliate-migrations`). Always run `makemigrations` after model changes and check the migration is actually generated and committed — don't rely on it being implicit.
- **Stripe edge cases** — free payments, webhook secret handling, payment-method defaults have all had bugs before. Changes touching `api/stripe.py`, `api/views/payment.py`, or webhook handling need test coverage via `api/mocks/stripe.py`, not live Stripe calls.
- **django-background-tasks** is DB-polled, not a real broker — there's no Celery worker. `BGTASK_SLEEP_TIME` env var controls polling interval. Don't assume tasks run instantly.
- Content is bilingual (ca/es) via `django-modeltranslation` — translatable model fields get `_ca`/`_es` suffixed DB columns automatically; don't hand-roll translation fields.

## Environment Variables

Defined in `.env` (gitignored, loaded via `envs` package in `backend/settings.py`). Key ones: `DEBUG`, `DJANGO_SECRET`, `ALLOWED_HOSTS`, `CORS_ALLOWED_ORIGINS`, `POSTGRES_*`, `EMAIL_*` / `DEFAULT_FROM_EMAIL` (Mailgun via Anymail), `STRIPE_SECRET`/`STRIPE_PUBLIC`/`STRIPE_WH_SECRET`, `REDIS_LOC`, `BGTASK_SLEEP_TIME`, `HOST_NAME`, `FE_MEMBERSHIP_CARD_PATH` (link back to the frontend), `SUBSCRIPTION_RECURRENCES`, `ACCESS_TOKEN_LIFETIME`, `DEVELOPERS`.

Per-environment config for dev/local/prod lives one level up in `devops/.environments/`. Treat `devops/.environments/prod/` as read-only unless the user explicitly asks to change production config.

## Git Workflow

- Remotes: `origin` = personal fork, `upstream` = `ameba-bcn/ameba-backend` (the real org repo).
- Integration branch is `dev`; `main` tracks releases. Release branches are tagged `release/X.Y`.
- Branch naming mirrors Jira-style tickets: `feature/AW-<n>-<slug>`, `bugfix/AW-<n>-<slug>`, `hotfix/<slug>`.
- CI (`.drone.yml`) just builds and pushes Docker images — there's no automated test gate, so running `python manage.py test` locally before pushing matters more than usual.

## Working Agreement

- This project is paired with a Claude Code subagent (`backend-developer`, defined globally) meant to act as the backend developer replacement. Follow the autonomy rules in that agent definition: free to edit code, run tests, and run local migrations; ask before `git push`, touching `devops/.environments/prod`, resetting/dropping data, or anything Stripe/email that could hit real external services.
- Explain backend concepts in plain terms when they affect a decision (e.g. "this needs a migration because...") — the user is a frontend developer and wants to learn enough to sanity-check the work, not just receive a diff.
