# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Commands

```bash
# Start dev server (must use port 9000 — ports 8000/8080 are reserved by Hyper-V on this machine)
python manage.py runserver 9001

# Run migrations
python manage.py makemigrations
python manage.py migrate

# Collect static files
python manage.py collectstatic

# Install dependencies
pip install django djangorestframework pillow django-crispy-forms crispy-bootstrap5 django-widget-tweaks oracledb whitenoise
```

There is no test suite configured. `manage.py createsuperuser` does not work — admin users must be inserted directly into the Oracle `erp_users` table (see SETUP_GUIDE.txt § 8).

## Architecture

**Stack:** Django 6.0 · Python 3.14 · Oracle 12.2 (`172.16.1.12:1521/SDESDB`) · Bootstrap 5 · `oracledb` in thick mode via Instant Client

**Custom Oracle DB backend** — `erp_project/oracle_compat/base.py` subclasses Django's Oracle backend solely to lower `minimum_database_version` to `(12, 2)`. All `DATABASES['default']['ENGINE']` references point here.

### Dual authentication paths

The project has two separate auth mechanisms that must not be confused:

1. **Main app login** (`/accounts/login/`) — `accounts/views.py` calls `accounts/oracle_auth.py:call_get_user_detail()` directly, stores a plain dict in `request.session['oracle_user']`, then `accounts/middleware.py:OracleAuthMiddleware` converts it to an `OracleUser` on every request. `OracleUser` is a plain Python class (never persisted), but it satisfies `is_authenticated = True` so `@login_required` passes. This path does **not** touch the `accounts_user` table.

2. **Django admin** (`/admin/`) — `accounts/backends.py:OracleProcedureBackend` calls the same Oracle procedure but uses `User.objects.get_or_create()` to create/sync a Django model row (`AUTH_USER_MODEL = 'accounts.User'`, which extends `AbstractUser`). This is the only path that writes to `accounts_user`. `is_staff`/`is_superuser` are refreshed on every login based on `role == 'admin'`.

`accounts/oracle_auth.py` and `accounts/backends.py` both call `GET_USER_DETAIL` but with **different procedure signatures** — the oracle_auth version uses 7 params (`P_STATUS` returns `'TRUE'`), while backends.py uses the same 7 params but expects `'TRUE'` as success status. Keep them in sync if the procedure signature changes.

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

Each ERP module (`hr`, `inventory`, `finance`, `sales`, `purchasing`) is a standard Django app with its own `models.py`, `views.py`, `urls.py`, and `templates/<app>/` directory. The `accounts` app owns authentication; `core` owns the dashboard and shared utilities.

### Environment config

All Oracle credentials come from `.env` (loaded manually in `settings.py` — no `python-dotenv` package). Copy `.env.example` → `.env`. `ORACLE_CLIENT_DIR` enables thick mode; leave blank for thin mode (some Oracle 12c features unavailable).
