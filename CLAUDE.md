# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Commands

```bash
# Start dev server (port 9001 — 8000/8080 reserved by Hyper-V, 9000 conflicts with another service)
python manage.py runserver 9001

# Production server (Waitress, binds 0.0.0.0:9001)
python serve.py
# or: python -m waitress --port=9001 --host=0.0.0.0 erp_project.wsgi:application

# Run migrations
python manage.py makemigrations
python manage.py migrate

# Collect static files
python manage.py collectstatic

# Install dependencies
pip install django djangorestframework pillow django-crispy-forms crispy-bootstrap5 django-widget-tweaks oracledb whitenoise waitress
```

There is no test suite configured. `manage.py createsuperuser` does not work — admin users must be inserted directly into the Oracle `erp_users` table (see SETUP_GUIDE.txt § 8).

## Architecture

**Stack:** Django 6.0 · Python 3.14 · Oracle 12.2 (`172.16.1.12:1521/SDESDB`) · Bootstrap 5 · `oracledb` in thick mode via Instant Client

**Custom Oracle DB backend** — `erp_project/oracle_compat/base.py` subclasses Django's Oracle backend solely to lower `minimum_database_version` to `(12, 2)`. All `DATABASES['default']['ENGINE']` references point here.

### Dual authentication paths

The project has two separate auth mechanisms that must not be confused:

1. **Main app login** (`/accounts/login/`) — `accounts/views.py` calls `accounts/oracle_auth.py:call_get_user_detail()` directly, stores a plain dict in `request.session['oracle_user']`, then `accounts/middleware.py:OracleAuthMiddleware` converts it to an `OracleUser` on every request. `OracleUser` is a plain Python class (never persisted), but it satisfies `is_authenticated = True` so `@login_required` passes. This path does **not** touch the `accounts_user` table.

2. **Django admin** (`/admin/`) — `accounts/backends.py:OracleProcedureBackend` calls the same Oracle procedure but uses `User.objects.get_or_create()` to create/sync a Django model row (`AUTH_USER_MODEL = 'accounts.User'`, which extends `AbstractUser`). This is the only path that writes to `accounts_user`. `is_staff`/`is_superuser` are refreshed on every login based on `role == 'admin'`.

Both paths call the procedure with its **schema-qualified name** `SDESERP.GET_USER_DETAIL` (not bare `GET_USER_DETAIL`) so connection-user / current-schema changes can't silently route to the wrong package. The same applies to `test_oracle_auth.py` and `test_oracle_auth_quick.py`. They use the same 7-param signature and both treat `P_STATUS = 'TRUE'` as success — keep them in sync if the procedure signature changes.

**Role mapping is single-source:** `oracle_auth.py` derives the app role
from `P_USER_GRP_ID` returned by the procedure (`A → admin`, `U → employee`,
anything else → `employee`). The `LOGIN_USER` table is **not** read at login
time anymore — don't reintroduce a second-trip query for the role.

### Raw Oracle cursor pattern

When calling Oracle stored procedures with OUT variables, you must unwrap two layers to reach the raw `oracledb` cursor:

```python
with connection.cursor() as django_cur:
    cur = django_cur.cursor.cursor  # raw oracledb cursor — needed for .var()
    p_out = cur.var(oracledb.STRING)
    cur.callproc('PROC_NAME', [in_val, p_out])
    result = p_out.getvalue()
```

Using `django_cur.var()` directly will fail because Django wraps it in a `VariableWrapper`.

### Dashboard `_safe()` guard

`core/views.py:dashboard()` wraps every ORM query in `_safe(default, fn)`, which catches all exceptions and returns the default. This allows the dashboard to render even when ERP tables haven't been migrated yet. New dashboard queries should follow the same pattern.

### Session storage

Sessions live in the Oracle table `DJANGO_SESSION` (managed by Django's session framework). The `oracle_user` key in the session holds the dict that `OracleAuthMiddleware` reads on every request. Flushing the session (logout) deletes the row.

### Module layout

Each ERP module (`hr`, `inventory`, `finance`, `sales`, `purchasing`, `operations`) is a standard Django app with its own `models.py`, `views.py`, `urls.py`, and `templates/<app>/` directory. The `accounts` app owns authentication; `core` owns the legacy dashboard and shared utilities. **`operations` is the post-login landing page** — its dashboard hosts the ApexCharts visualizations (daily containers, yearly bar chart, handling & demurrage).

### Operations dashboard caching

All chart and summary view functions in `operations/views.py` write through Django's cache with a 5-minute TTL. Cache keys: `container_chart_data`, `container_year_chart_data`, `handling_demurrage_chart_data`, `last_24hr_container_summary`, `last_24hr_hidem_summary`, `month_to_date_summary`. When changing the underlying Oracle queries or data shape, invalidate manually:

```python
from django.core.cache import cache
cache.clear()
```

### Environment config

All Oracle credentials come from `.env` (loaded manually in `settings.py` — no `python-dotenv` package). Copy `.env.example` → `.env`. `ORACLE_CLIENT_DIR` enables thick mode; leave blank for thin mode (some Oracle 12c features unavailable).

### Recent changes

See `docs/DEVELOPMENT_CHANGELOG.md` for dated entries. Most recent landmarks:
- **2026-06-14** — Schema-qualified `SDESERP.GET_USER_DETAIL`; role derived from `P_USER_GRP_ID` (no `LOGIN_USER` round-trip); server port standardized on **9001**; invoice Excel export forces date column to text; VAT report loader overlay.
- **2026-06-11** — Operations module + dashboard launch with ApexCharts, summary cards, 5-min caching, favicon set.
