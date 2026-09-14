# Project Structure

```
ameba-backend/
├── config/               # Django project config (settings, root urls, wsgi/asgi)
├── api/                  # Single Django app containing all business logic
│   ├── models/           # One file per domain model (member, event, cart, etc.)
│   ├── views/            # One file per resource; ViewSets + function-based views
│   ├── serializers/      # One file per resource
│   ├── admin/            # Django admin registrations, one file per model
│   ├── docs/             # drf-yasg schema customizations and endpoint docs
│   ├── tests/            # Test files mirror view/model names; BaseTest in _helpers.py
│   ├── migrations/       # Django migrations (auto-generated)
│   ├── serializers/      # DRF serializers
│   ├── helpers/          # Utility modules (anonymization, signaling)
│   ├── middleware/        # Custom middleware (language detection)
│   ├── mocks/            # Test mocks (e.g. Stripe)
│   ├── signals/          # Django signals
│   ├── tasks/            # Background task definitions
│   ├── locale/           # Translation files (es, ca, en)
│   ├── management/commands/  # Custom manage.py commands
│   ├── fixtures/         # Initial data fixtures
│   ├── urls.py           # API URL routing (DRF router + manual paths)
│   ├── authentication.py # Custom JWT authentication logic
│   ├── permissions.py    # Custom DRF permission classes
│   ├── cache_utils.py    # Redis cache decorators for views
│   ├── email_factories.py# Email construction helpers
│   ├── stripe.py         # Stripe webhook and payment logic
│   ├── images.py         # Image processing utilities
│   ├── qr_factories.py / qr_generator.py  # QR code generation
│   └── responses.py      # Shared response helpers
├── templates/            # Django HTML templates (admin overrides, emails)
├── entrypoints/          # Docker entrypoint scripts (dev + prod)
├── static/               # Collected static files
├── media/                # User-uploaded media files
└── manage.py
```

## Conventions

- All API routes are prefixed with `/api/` and registered in `api/urls.py` using DRF's `DefaultRouter`.
- ViewSets inherit from base classes in `api/views/base.py`: `BaseReadOnlyViewSet`, `BaseUserEditableViewSet`, or `BaseCrudViewSet`. These support separate `list_serializer` and `detail_serializer` per action.
- Read-only public viewsets use `@cache_utils.cache_response` on `list` and `retrieve`.
- Models use `@cache_utils.invalidate_models_cache` on `save()` to bust cache on writes.
- Tests extend `BaseTest` (from `api/tests/_helpers.py`) which wraps `APITestCase` with helpers for authenticated requests (`_get`, `_create`, `_update`, `_partial_update`, `_list`, `_delete`).
- i18n strings use `gettext_lazy` (`_()`) throughout models and serializers. Translatable model fields are registered in `api/translation.py`.
- Custom `User` model is at `api/models/user.py`; always reference via `get_user_model()`.
- Environment-specific config is read via the `env()` helper in `config/settings.py`, never hardcoded.
