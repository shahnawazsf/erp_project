# ERP System — Technical Overview
### Authentication Flow & Application Architecture

---

## 1. Technology Stack

| Layer | Technology |
|---|---|
| Web Framework | Django 6.0 (Python 3.14) |
| Database | Oracle 12.2.0.1.0 (`172.16.1.12:1521/SDESDB`) |
| Oracle Driver | `oracledb` (thick mode via Instant Client) |
| Frontend | Bootstrap 5.3.2 + Bootstrap Icons |
| Session Store | Oracle table `DJANGO_SESSION` |
| Auth Source | Oracle stored procedure `GET_USER_DETAIL` + table `LOGIN_USER` |
| Dev Server | `python manage.py runserver 9000` |

---

## 2. Application Entry Points

```
http://127.0.0.1:9000/                    →  Dashboard (login required)
http://127.0.0.1:9000/accounts/login/     →  Login page
http://127.0.0.1:9000/accounts/logout/    →  Logout
http://127.0.0.1:9000/accounts/profile/  →  User profile (login required)
http://127.0.0.1:9000/hr/                →  HR module
http://127.0.0.1:9000/inventory/          →  Inventory module
http://127.0.0.1:9000/sales/              →  Sales module
http://127.0.0.1:9000/purchasing/         →  Purchasing module
http://127.0.0.1:9000/finance/            →  Finance module
http://127.0.0.1:9000/admin/              →  Django admin
```

---

## 3. Login Flow — Step by Step

### 3.1 User opens the login page (GET request)

```
Browser  ──GET /accounts/login/──►  Django URL Router
                                         │
                              accounts/urls.py
                              path('login/', views.login_view)
                                         │
                              accounts/views.py → login_view()
                                         │
                              Check: session['oracle_user'] exists?
                              ├── YES → redirect to dashboard (already logged in)
                              └── NO  → render accounts/login.html
                                         │
Browser  ◄── 200 OK + HTML page ─────────┘
```

**Template rendered:** `templates/accounts/login.html`
- Left panel: Brand panel (static, gradient dark blue)
- Right panel: Login form with CSRF token, username field, password field, Sign In button

---

### 3.2 User clicks "Sign In" (POST request)

#### Step 1 — Browser (JavaScript, before form submits)
```
loginForm  'submit' event fires
    │
    ├─ submitBtn.disabled = true          (prevents double-click)
    ├─ spinner.style.display = 'inline-block'   (shows loading spinner)
    └─ btnText.textContent = 'Signing in…'
    │
Form POSTs to POST /accounts/login/
```

Fields sent in the POST body:
```
csrfmiddlewaretoken = <token from hidden input>
username            = e.g. "sfaridi"
password            = e.g. "Jan@2022"
```

---

#### Step 2 — Django Middleware Chain (every request passes through this)

```
Incoming POST /accounts/login/
    │
    ▼
[1] SecurityMiddleware          — HTTPS redirect, security headers
[2] SessionMiddleware           — reads session cookie, loads session dict
                                  from DJANGO_SESSION table in Oracle
[3] CommonMiddleware            — URL normalization, content-type checks
[4] CsrfViewMiddleware          — validates csrfmiddlewaretoken
                                  (rejects with 403 if token is wrong/missing)
[5] AuthenticationMiddleware    — sets request.user = AnonymousUser
                                  (no Django user table, so always Anonymous)
[6] OracleAuthMiddleware        — checks session['oracle_user']
                                  ├─ EXISTS → request.user = OracleUser(data)
                                  └─ MISSING → request.user stays AnonymousUser
[7] MessageMiddleware           — loads flash messages
[8] XFrameOptionsMiddleware     — adds X-Frame-Options header
    │
    ▼
accounts/views.py → login_view(request)
```

---

#### Step 3 — login_view() processes the POST

File: `accounts/views.py`

```python
def login_view(request):
    # Already logged in? Skip to dashboard.
    if request.session.get('oracle_user'):
        return redirect('dashboard')

    if request.method == 'POST':
        username = request.POST.get('username', '').strip()
        password = request.POST.get('password', '')

        # Call Oracle stored procedure
        info = call_get_user_detail(username, password)

        if info:
            # Store user data in session
            request.session['oracle_user'] = info
            # Redirect to dashboard (or ?next= URL)
            return redirect(request.GET.get('next', 'dashboard'))

        # Failed — show error message, re-render form
        messages.error(request, 'Invalid username or password.')

    return render(request, 'accounts/login.html')
```

---

#### Step 4 — Oracle Procedure Call

File: `accounts/oracle_auth.py` → `call_get_user_detail(username, password)`

```
Django DB connection (oracle_compat backend)
    │
    ▼
connection.cursor()                  ← Django CursorWrapper
    │
django_cur.cursor                    ← Django FormatStylePlaceholderCursor
    │
django_cur.cursor.cursor             ← Raw oracledb cursor (required for .var())
    │
Bind OUT variables:
    p_user_name     = oracledb.STRING var
    p_user_grp_id   = oracledb.STRING var
    p_user_emp_code = oracledb.STRING var
    p_user_desc     = oracledb.STRING var
    p_status        = oracledb.STRING var
    │
    ▼
EXEC GET_USER_DETAIL(
    P_USER_ID       IN  = 'sfaridi',
    P_PASSWORD      IN  = 'Jan@2022',
    P_USER_NAME     OUT → e.g. 'Shahnawaz Faridi',
    P_USER_GRP_ID   OUT → e.g. 'admingrp',
    P_USER_EMP_CODE OUT → e.g. 'EMP-001',
    P_USER_DESC     OUT → e.g. 'System Administrator',
    P_STATUS        OUT → 'TRUE'  (success) | other (failure)
)
    │
    ▼
p_status.getvalue() == 'TRUE'?
    ├─ YES → return dict:
    │         { username, user_name, user_grp_id, user_emp_code, user_desc }
    └─ NO  → log WARNING, return None
```

The procedure queries the Oracle table `LOGIN_USER` internally.

---

#### Step 5 — Session Storage

On successful authentication:

```python
request.session['oracle_user'] = {
    'username':      'sfaridi',
    'user_name':     'Shahnawaz Faridi',
    'user_grp_id':   'admingrp',
    'user_emp_code': 'EMP-001',
    'user_desc':     'System Administrator',
}
```

Django serializes this dict and stores it in Oracle:
```sql
INSERT INTO DJANGO_SESSION (session_key, session_data, expire_date)
VALUES ('<random 32-char key>', '<base64-encoded data>', <2 weeks from now>)
```

A `sessionid` cookie is set in the browser response.

---

#### Step 6 — Redirect to Dashboard

```
HTTP 302 Found
Location: /
    │
Browser follows redirect → GET /
    │
SessionMiddleware loads session from DJANGO_SESSION using cookie
OracleAuthMiddleware reads session['oracle_user']
    │ → request.user = OracleUser(data)   ← is_authenticated = True
    │
core/views.py → dashboard(request)
    │
@login_required checks request.user.is_authenticated → True → allowed
    │
Queries ERP module counts (safely — returns 0 if table missing)
    │
Renders templates/core/dashboard.html
    │
Browser ◄── 200 OK + Dashboard HTML
```

---

### 3.3 Failed Login

```
GET_USER_DETAIL returns P_STATUS != 'TRUE'
    │
call_get_user_detail() returns None
    │
login_view:  messages.error(request, 'Invalid username or password.')
    │
render(request, 'accounts/login.html')   ← stays on login page
    │
Template renders error alert box (red banner):
    {% if messages %}
        <div class="alert-error">Invalid username or password.</div>
    {% endif %}
    │
Input fields get CSS class 'is-invalid' → red border styling
```

---

## 4. How Sessions Keep You Logged In

```
Browser                    Django                     Oracle DB
  │                          │                            │
  │──GET /hr/ (with cookie)──►│                            │
  │                          │──SELECT session_data───────►│
  │                          │◄── { oracle_user: {...} } ──│
  │                          │                            │
  │               OracleAuthMiddleware                     │
  │               request.user = OracleUser(data)          │
  │               is_authenticated = True                  │
  │                          │                            │
  │◄──── 200 OK + HR page ───│                            │
```

Session expires after **2 weeks** (Django default).

---

## 5. Logout Flow

```
GET /accounts/logout/
    │
logout_view(request):
    request.session.flush()    ← deletes session from DJANGO_SESSION table
                                  clears session cookie from browser
    │
redirect('login')
    │
Browser → GET /accounts/login/
```

---

## 6. OracleUser — Why No Database Model

Django normally expects `request.user` to be a model instance stored in `AUTH_USER` or a custom table. This project skips that because:

- The canonical user store is Oracle's `LOGIN_USER` table (managed outside Django)
- No Django migrations have been run for ERP-specific tables
- Authentication is fully handled by `GET_USER_DETAIL` procedure

`OracleUser` is a plain Python class that satisfies Django's user interface:

```python
class OracleUser:
    is_anonymous     = False
    is_authenticated = True   # ← makes @login_required pass
    username         = 'sfaridi'
    user_name        = 'Shahnawaz Faridi'
    user_grp_id      = 'admingrp'
    user_emp_code    = 'EMP-001'
    user_desc        = 'System Administrator'
```

It is never written to any database table.

---

## 7. File Map

```
erp_project/
│
├── accounts/
│   ├── oracle_auth.py      ← call_get_user_detail() + OracleUser class
│   ├── middleware.py        ← OracleAuthMiddleware (sets request.user)
│   ├── views.py             ← login_view, logout_view, profile_view
│   ├── urls.py              ← /accounts/login|logout|profile/
│   └── backends.py         ← (legacy, no longer used for main login)
│
├── core/
│   ├── views.py             ← dashboard() with _safe() guards
│   └── urls.py              ← / → dashboard
│
├── erp_project/
│   ├── settings.py          ← MIDDLEWARE list, DATABASES, LOGGING
│   ├── urls.py              ← root URL dispatcher
│   └── oracle_compat/       ← custom Oracle 12.2 DB backend
│       └── base.py
│
└── templates/
    └── accounts/
        └── login.html       ← split-panel login UI (Bootstrap 5)
```

---

## 8. Middleware Execution Order

```
settings.py MIDDLEWARE (top = first executed):

1. SecurityMiddleware
2. SessionMiddleware          ← loads DJANGO_SESSION from Oracle
3. CommonMiddleware
4. CsrfViewMiddleware         ← blocks invalid CSRF tokens (403)
5. AuthenticationMiddleware   ← sets request.user = AnonymousUser
6. OracleAuthMiddleware       ← overrides to OracleUser if session exists  ★
7. MessageMiddleware
8. XFrameOptionsMiddleware
```

---

## 9. Logging

All authentication events log to the `accounts.backends` logger (console output).

| Event | Level | Message |
|---|---|---|
| Wrong password / unknown user | WARNING | `GET_USER_DETAIL: status='FALSE' for username='x'` |
| Oracle procedure error | ERROR | Full traceback printed to console |
| Oracle connection failure | ERROR | Full traceback printed to console |

Enable debug logging in `erp_project/settings.py`:
```python
'accounts.backends': { 'level': 'DEBUG', ... }
```

---

## 10. Oracle Stored Procedure Signature

```sql
GET_USER_DETAIL (
    P_USER_ID       IN  VARCHAR2,   -- login username (from LOGIN_USER table)
    P_PASSWORD      IN  VARCHAR2,   -- plain-text password (validated in Oracle)
    P_USER_NAME     OUT VARCHAR2,   -- full display name
    P_USER_GRP_ID   OUT VARCHAR2,   -- group/role (e.g. 'admingrp')
    P_USER_EMP_CODE OUT VARCHAR2,   -- employee code
    P_USER_DESC     OUT VARCHAR2,   -- user description
    P_STATUS        OUT VARCHAR2    -- 'TRUE' = success, anything else = failure
)
```

The procedure is owned by schema `sdeserp` on `172.16.1.12:1521/SDESDB`.

---

*Generated: 2026-05-11 | ERP System v1.0 | Django 6.0 | Oracle 12.2*
