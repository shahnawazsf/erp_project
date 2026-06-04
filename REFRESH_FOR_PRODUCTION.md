# Refresh for Production - Complete Steps

**This guide walks through refreshing the entire application for production deployment.**

---

## 📋 Complete Refresh Checklist

- [ ] Stop development server
- [ ] Clear cache & temporary files
- [ ] Verify all code changes committed
- [ ] Update dependencies
- [ ] Collect static files
- [ ] Test database connection
- [ ] Run production readiness check
- [ ] Create/verify .env file
- [ ] Update Django settings
- [ ] Start production server
- [ ] Verify all pages load
- [ ] Check logs for errors
- [ ] Monitor performance

---

## 🔄 Step-by-Step Refresh Process

### **STEP 1: Stop Development Server**

Stop any running development servers:

```bash
# If using runserver, press Ctrl+C
# If using Waitress in background, kill the process

# Check for running Python processes
ps aux | grep python

# Kill the process (replace PID with actual process ID)
kill -9 <PID>

# Or on Windows with Taskkill
taskkill /F /IM python.exe
```

---

### **STEP 2: Clean Up Development Artifacts**

Remove cache and temporary files:

```bash
# Remove Python cache files
find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null
find . -type f -name "*.pyc" -delete

# Remove .pytest cache
rm -rf .pytest_cache

# Remove Django cache
python manage.py clear_cache 2>/dev/null || true

# Clean old staticfiles (optional)
rm -rf staticfiles/
```

**On Windows:**
```bash
# Remove __pycache__ folders
Get-ChildItem -Directory -Filter __pycache__ -Recurse | Remove-Item -Recurse -Force

# Remove .pyc files
Get-ChildItem -Filter "*.pyc" -Recurse | Remove-Item -Force

# Clear Django cache
python manage.py clear_cache 2>$null
```

---

### **STEP 3: Verify Code Committed**

Ensure all changes are committed to git:

```bash
# Check git status
git status

# Expected output: "On branch master, nothing to commit"

# If there are changes, commit them
git add .
git commit -m "Pre-production refresh: all changes committed"

# View recent commits
git log --oneline -5
```

---

### **STEP 4: Update Dependencies**

Install/update all required packages:

```bash
# Upgrade pip, setuptools, wheel
pip install --upgrade pip setuptools wheel

# Install all dependencies
pip install django==6.0.5 \
    djangorestframework \
    pillow \
    django-crispy-forms \
    crispy-bootstrap5 \
    django-widget-tweaks \
    oracledb \
    whitenoise \
    waitress \
    python-dotenv

# Verify installations
pip list | grep -i "django\|waitress\|oracle"
```

**On Windows:**
```powershell
pip install --upgrade pip setuptools wheel

pip install `
    django==6.0.5 `
    djangorestframework `
    pillow `
    django-crispy-forms `
    crispy-bootstrap5 `
    django-widget-tweaks `
    oracledb `
    whitenoise `
    waitress `
    python-dotenv
```

---

### **STEP 5: Collect Static Files**

Gather all CSS, JavaScript, and image files:

```bash
# Remove old staticfiles (if exists)
rm -rf staticfiles/

# Collect fresh static files
python manage.py collectstatic --noinput --clear

# Verify collection
ls -la staticfiles/ | head -20
ls staticfiles/staticfiles.json
```

**Expected output:**
```
0 static files copied to 'staticfiles'
158 unmodified
408 post-processed
```

---

### **STEP 6: Test Database Connection**

Verify Oracle database is accessible:

```bash
# Test database connection
python manage.py dbshell

# Expected: Should open SQL> prompt
# Type 'exit' to quit

# Or test with Django
python manage.py shell
>>> from django.db import connection
>>> connection.ensure_connection()
>>> print("Database connected successfully!")
>>> exit()
```

---

### **STEP 7: Create/Update .env File**

Create environment configuration file:

```bash
# Create .env file
cat > .env << 'EOF'
# Database Configuration
ORACLE_DB_NAME=SDESDB
ORACLE_DB_USER=erp_user
ORACLE_DB_PASSWORD=YourSecurePassword123!
ORACLE_DB_HOST=172.16.1.12
ORACLE_DB_PORT=1521

# Oracle Client (optional, for thick mode)
ORACLE_CLIENT_DIR=C:\oracle\instantclient_12_2

# Django Configuration
SECRET_KEY=django-insecure-change-this-to-a-secure-random-key
DEBUG=False
ALLOWED_HOSTS=localhost,127.0.0.1,172.16.2.3,your-domain.com
EOF

# Verify .env file created
cat .env

# Add to .gitignore (NEVER COMMIT THIS)
echo ".env" >> .gitignore
git add .gitignore
git commit -m "Ensure .env is never committed"
```

**On Windows PowerShell:**
```powershell
$envContent = @"
# Database Configuration
ORACLE_DB_NAME=SDESDB
ORACLE_DB_USER=erp_user
ORACLE_DB_PASSWORD=YourSecurePassword123!
ORACLE_DB_HOST=172.16.1.12
ORACLE_DB_PORT=1521

# Django Configuration
SECRET_KEY=django-insecure-change-this-to-a-secure-random-key
DEBUG=False
ALLOWED_HOSTS=localhost,127.0.0.1,172.16.2.3,your-domain.com
"@

$envContent | Out-File -FilePath .env -Encoding UTF8

# Verify creation
Get-Content .env
```

---

### **STEP 8: Update Django Settings**

Modify `erp_project/settings.py` for production:

```python
# At the top of settings.py, add:
import os
from pathlib import Path
from dotenv import load_dotenv

# Load .env file
load_dotenv()

BASE_DIR = Path(__file__).resolve().parent.parent

# ── PRODUCTION SETTINGS ──
SECRET_KEY = os.environ.get('SECRET_KEY', 'CHANGE-ME-IN-PRODUCTION')
DEBUG = os.environ.get('DEBUG', 'False') == 'True'
ALLOWED_HOSTS = os.environ.get('ALLOWED_HOSTS', 'localhost').split(',')

# Security settings for production
if not DEBUG:
    SECURE_SSL_REDIRECT = False  # Set True if using HTTPS
    SESSION_COOKIE_SECURE = False  # Set True if using HTTPS
    CSRF_COOKIE_SECURE = False  # Set True if using HTTPS
    SECURE_BROWSER_XSS_FILTER = True
    SECURE_CONTENT_SECURITY_POLICY = {
        'default-src': ("'self'",),
    }
```

---

### **STEP 9: Run Production Readiness Check**

Verify everything is ready:

```bash
# Run automated checker
bash verify_production_ready.sh

# Expected output:
# ✓ Environment file (.env) exists
# ✓ Static files collected
# ✓ settings.py exists
# ... [more checks]
# ✅ READY FOR PRODUCTION
```

---

### **STEP 10: Create Production Logs Directory**

Set up logging:

```bash
# Create logs directory
mkdir -p logs

# Verify creation
ls -la logs/

# On Windows PowerShell
New-Item -ItemType Directory -Force -Path logs
```

---

### **STEP 11: Start Production Server**

Launch the application:

**Option A: Waitress (Windows/Linux)**
```bash
echo "Starting production server..."
python -m waitress --port=9001 --host=0.0.0.0 erp_project.wsgi:application
```

**Option B: Gunicorn (Linux)**
```bash
echo "Starting production server..."
gunicorn --workers=4 --bind=0.0.0.0:9001 erp_project.wsgi:application
```

**Expected output:**
```
Starting server in PID 12345.
Listening on http://0.0.0.0:9001
```

---

### **STEP 12: Verify Application Loads**

Test all key pages:

**Test 1: Login Page**
```bash
curl -I http://localhost:9001/accounts/login/
# Should return: HTTP/1.1 200 OK
```

**Test 2: Static Files**
```bash
curl -I http://localhost:9001/static/css/bootstrap.min.css
# Should return: HTTP/1.1 200 OK (not 404)
```

**Test 3: Dashboard (requires login)**
```bash
# Open in browser: http://localhost:9001/
# Login with your credentials
# Check sidebar loads
# Check footer appears at bottom
```

**Test 4: Container Notification Page**
```bash
# Navigate to: Finance > Container Notification
# Verify page loads
# Click "Add Record"
# Verify form shows "CNT-" prefix
```

**Test 5: All Navigation**
- [ ] Dashboard loads
- [ ] Finance menu works
- [ ] Reports pages load
- [ ] Container Notification page loads
- [ ] Search bar appears in header
- [ ] Settings dropdown appears
- [ ] Footer is visible
- [ ] No console errors (F12)

---

### **STEP 13: Monitor Server & Logs**

Keep watch for any issues:

**In a separate terminal, monitor logs:**
```bash
# Watch logs in real-time
tail -f logs/django.log

# On Windows PowerShell
Get-Content logs/django.log -Wait
```

**Check for errors:**
```bash
# Count errors
grep ERROR logs/django.log | wc -l

# Show last 20 lines
tail -20 logs/django.log

# Show only errors
grep ERROR logs/django.log
```

---

## ⚡ Quick Refresh Command (Copy & Paste)

**For Linux/Mac:**
```bash
#!/bin/bash

echo "🔄 Refreshing for Production..."
echo ""

echo "1️⃣  Cleaning up..."
find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null
find . -type f -name "*.pyc" -delete
rm -rf .pytest_cache staticfiles/

echo "2️⃣  Updating dependencies..."
pip install --upgrade pip setuptools wheel
pip install django==6.0.5 djangorestframework pillow django-crispy-forms crispy-bootstrap5 django-widget-tweaks oracledb whitenoise waitress python-dotenv

echo "3️⃣  Collecting static files..."
python manage.py collectstatic --noinput --clear

echo "4️⃣  Creating logs directory..."
mkdir -p logs

echo "5️⃣  Testing database..."
python manage.py dbshell << EOF
SELECT 1 FROM DUAL;
EXIT
EOF

echo "6️⃣  Running readiness check..."
bash verify_production_ready.sh

echo ""
echo "✅ Refresh Complete!"
echo ""
echo "To start production server:"
echo "  python -m waitress --port=9001 --host=0.0.0.0 erp_project.wsgi:application"
```

**For Windows PowerShell:**
```powershell
# Copy this into PowerShell and run

Write-Host "🔄 Refreshing for Production..." -ForegroundColor Green
Write-Host ""

Write-Host "1️⃣  Cleaning up..." -ForegroundColor Yellow
Get-ChildItem -Directory -Filter __pycache__ -Recurse | Remove-Item -Recurse -Force -ErrorAction SilentlyContinue
Get-ChildItem -Filter "*.pyc" -Recurse | Remove-Item -Force -ErrorAction SilentlyContinue
Remove-Item -Recurse -Force staticfiles -ErrorAction SilentlyContinue

Write-Host "2️⃣  Updating dependencies..." -ForegroundColor Yellow
pip install --upgrade pip setuptools wheel
pip install django djangorestframework pillow django-crispy-forms crispy-bootstrap5 django-widget-tweaks oracledb whitenoise waitress python-dotenv

Write-Host "3️⃣  Collecting static files..." -ForegroundColor Yellow
python manage.py collectstatic --noinput --clear

Write-Host "4️⃣  Creating logs directory..." -ForegroundColor Yellow
New-Item -ItemType Directory -Force -Path logs | Out-Null

Write-Host "5️⃣  Testing database..." -ForegroundColor Yellow
python manage.py dbshell

Write-Host "6️⃣  Running readiness check..." -ForegroundColor Yellow
bash verify_production_ready.sh

Write-Host ""
Write-Host "✅ Refresh Complete!" -ForegroundColor Green
Write-Host ""
Write-Host "To start production server:" -ForegroundColor Cyan
Write-Host "  python -m waitress --port=9001 --host=0.0.0.0 erp_project.wsgi:application" -ForegroundColor White
```

---

## 🎯 Verification Checklist

After refresh, verify everything:

```bash
# 1. Check application responds
curl http://localhost:9001/accounts/login/

# 2. Check static files loaded
curl -I http://localhost:9001/static/css/bootstrap.min.css

# 3. Check logs exist
ls -la logs/

# 4. Check git status
git status

# 5. Check .env not committed
git log --name-status | grep .env

# 6. Check database connection
python manage.py dbshell

# 7. Check Python packages
pip list | grep -E "Django|Waitress|oracledb"

# 8. Check server running on port 9001
netstat -tuln | grep 9001
```

---

## 🚀 Final Production Readiness

Once all steps complete:

```
✅ Code cleaned and committed
✅ Dependencies updated
✅ Static files collected
✅ Database tested
✅ .env configured
✅ Settings updated for production
✅ Logs directory created
✅ Server started successfully
✅ All pages loading
✅ No errors in logs
✅ Ready for users!
```

---

## 📞 If Something Goes Wrong

| Issue | Solution |
|-------|----------|
| Static files not loading | Run: `python manage.py collectstatic --clear --noinput` |
| Database connection error | Check `.env` file, test: `python manage.py dbshell` |
| Port 9001 in use | Use different port: `--port=9002` |
| Permission denied | Create directory: `mkdir -p logs && chmod 755 logs` |
| Module not found | Update deps: `pip install -r requirements.txt` |
| CSS/JS broken | Clear browser cache, `Ctrl+Shift+Delete` |

---

## 📊 Pre vs Post Refresh

**Before Refresh:**
```
- __pycache__ folders present
- .pyc files cached
- old staticfiles
- unverified dependencies
- DEBUG = True
```

**After Refresh:**
```
✅ Clean codebase
✅ Fresh dependencies
✅ Collected static files
✅ Verified production readiness
✅ DEBUG = False
✅ Configured for production
✅ Server running
✅ All tests passing
```

---

## ⏱️ Time Estimates

| Step | Time |
|------|------|
| Stop server & cleanup | 2 min |
| Commit code | 1 min |
| Update dependencies | 3 min |
| Collect static files | 1 min |
| Test database | 1 min |
| Create .env | 2 min |
| Run readiness check | 1 min |
| Start server | 1 min |
| Verify pages load | 2 min |
| **Total** | **~15 minutes** |

---

**Status**: ✅ Ready to Refresh  
**Updated**: June 4, 2026  
**Next**: Run the refresh steps above
