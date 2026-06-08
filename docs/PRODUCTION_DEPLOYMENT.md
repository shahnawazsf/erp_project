# Production Deployment Guide

**Version**: 1.0  
**Date**: June 4, 2026  
**Status**: Ready for Production

---

## 🎯 Production Checklist

- [ ] Collect static files
- [ ] Set DEBUG = False
- [ ] Configure ALLOWED_HOSTS
- [ ] Configure database credentials (.env)
- [ ] Set SECRET_KEY securely
- [ ] Configure CSRF settings
- [ ] Run migrations (if any)
- [ ] Create superuser for admin
- [ ] Start production server (Waitress/Gunicorn)
- [ ] Test all features
- [ ] Set up logging
- [ ] Configure backups

---

## 📋 Step-by-Step Production Setup

### **Step 1: Prepare Environment Variables**

Create or update `.env` file in project root:

```bash
# Database
ORACLE_DB_NAME=SDESDB
ORACLE_DB_USER=erp_user
ORACLE_DB_PASSWORD=your_secure_password
ORACLE_DB_HOST=172.16.1.12
ORACLE_DB_PORT=1521

# Oracle Client (for thick mode)
ORACLE_CLIENT_DIR=C:\oracle\instantclient_12_2

# Django Settings
SECRET_KEY=your-secure-secret-key-here
DEBUG=False
ALLOWED_HOSTS=localhost,127.0.0.1,172.16.2.3,your-domain.com
```

**Security Tips:**
- Use strong, random SECRET_KEY
- Never commit .env to git
- Use unique passwords for production
- Restrict ALLOWED_HOSTS to actual servers only

---

### **Step 2: Update Django Settings for Production**

**File: `erp_project/settings.py`**

```python
# ── PRODUCTION SETTINGS ──

import os
from pathlib import Path

# Load environment variables
from dotenv import load_dotenv
load_dotenv()

BASE_DIR = Path(__file__).resolve().parent.parent

# Security
SECRET_KEY = os.environ.get('SECRET_KEY', 'CHANGE-ME-IN-PRODUCTION')
DEBUG = os.environ.get('DEBUG', 'False') == 'True'
ALLOWED_HOSTS = os.environ.get('ALLOWED_HOSTS', 'localhost').split(',')

# ── HTTPS & Security Settings ──
if not DEBUG:
    SECURE_SSL_REDIRECT = True  # Force HTTPS
    SESSION_COOKIE_SECURE = True
    CSRF_COOKIE_SECURE = True
    SECURE_BROWSER_XSS_FILTER = True
    SECURE_CONTENT_SECURITY_POLICY = {
        'default-src': ("'self'",),
        'script-src': ("'self'", 'cdn.jsdelivr.net'),
        'style-src': ("'self'", 'cdn.jsdelivr.net'),
    }
```

---

### **Step 3: Collect Static Files**

Run this command to gather all static files:

```bash
python manage.py collectstatic --noinput
```

**Output:**
```
0 static files copied to 'E:\Testing\projects\erp_project\staticfiles'
158 unmodified
408 post-processed
```

This creates a `staticfiles/` directory with:
- CSS files
- JavaScript files
- Images
- Bootstrap/Bootstrap Icons

---

### **Step 4: Create Production Server Script**

Create `run_production.sh` (on Linux/Mac) or `run_production.bat` (on Windows):

**Windows (run_production.bat):**
```batch
@echo off
REM Production startup script for Windows

echo Collecting static files...
python manage.py collectstatic --noinput

echo Starting Waitress server on all interfaces...
python -m waitress --port=9001 --host=0.0.0.0 erp_project.wsgi:application

pause
```

**Linux/Mac (run_production.sh):**
```bash
#!/bin/bash

echo "Collecting static files..."
python manage.py collectstatic --noinput

echo "Starting Gunicorn server..."
gunicorn --workers=4 --bind=0.0.0.0:9001 erp_project.wsgi:application
```

---

### **Step 5: Choose Production WSGI Server**

#### **Option A: Waitress (Recommended for Windows)**

Install:
```bash
pip install waitress==3.0.2
```

Start:
```bash
python -m waitress --workers=4 --port=9001 --host=0.0.0.0 erp_project.wsgi:application
```

**Advantages:**
- Pure Python (no C extensions)
- Windows-friendly
- Production-ready
- Thread-safe

---

#### **Option B: Gunicorn (Recommended for Linux)**

Install:
```bash
pip install gunicorn
```

Start:
```bash
gunicorn \
  --workers=4 \
  --worker-class=sync \
  --bind=0.0.0.0:9001 \
  --timeout=120 \
  --access-logfile=- \
  erp_project.wsgi:application
```

**Advantages:**
- Battle-tested
- Excellent performance
- Linux-optimized
- Great documentation

---

### **Step 6: Configure Logging**

Add to `erp_project/settings.py`:

```python
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '{levelname} {asctime} {module} {process:d} {thread:d} {message}',
            'style': '{',
        },
        'simple': {
            'format': '{levelname} {message}',
            'style': '{',
        },
    },
    'handlers': {
        'file': {
            'level': 'INFO',
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': BASE_DIR / 'logs' / 'django.log',
            'maxBytes': 1024 * 1024 * 10,  # 10 MB
            'backupCount': 10,
            'formatter': 'verbose',
        },
        'console': {
            'level': 'DEBUG',
            'class': 'logging.StreamHandler',
            'formatter': 'simple',
        },
    },
    'loggers': {
        'django': {
            'handlers': ['file', 'console'],
            'level': 'INFO',
            'propagate': True,
        },
    },
}
```

---

### **Step 7: Database Backup Strategy**

**Daily Backup Script (backup_db.sh):**

```bash
#!/bin/bash

DATE=$(date +%Y%m%d_%H%M%S)
BACKUP_DIR="/backups/erp_db"
ORACLE_USER="erp_user"
ORACLE_DB="SDESDB"

mkdir -p $BACKUP_DIR

# Oracle export
expdp $ORACLE_USER@$ORACLE_DB \
  dumpfile=$BACKUP_DIR/backup_$DATE.dmp \
  logfile=$BACKUP_DIR/backup_$DATE.log

# Compress
gzip $BACKUP_DIR/backup_$DATE.dmp

echo "Backup completed: $BACKUP_DIR/backup_$DATE.dmp.gz"
```

Schedule with cron:
```bash
# Run daily at 2 AM
0 2 * * * /path/to/backup_db.sh
```

---

### **Step 8: Setup Nginx Reverse Proxy (Optional but Recommended)**

**File: `/etc/nginx/sites-available/erp-project`**

```nginx
upstream erp_app {
    server 127.0.0.1:9001;
}

server {
    listen 80;
    server_name your-domain.com;

    # Redirect HTTP to HTTPS
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl http2;
    server_name your-domain.com;

    # SSL certificates
    ssl_certificate /etc/letsencrypt/live/your-domain.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/your-domain.com/privkey.pem;

    # Security headers
    add_header Strict-Transport-Security "max-age=31536000" always;
    add_header X-Content-Type-Options "nosniff" always;
    add_header X-Frame-Options "SAMEORIGIN" always;

    # Serve static files directly
    location /static/ {
        alias /path/to/erp_project/staticfiles/;
        expires 30d;
    }

    # Serve media files
    location /media/ {
        alias /path/to/erp_project/media/;
    }

    # Proxy to Waitress/Gunicorn
    location / {
        proxy_pass http://erp_app;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_redirect off;
    }
}
```

Enable site:
```bash
sudo ln -s /etc/nginx/sites-available/erp-project /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx
```

---

## 🚀 Production Startup Commands

### **Complete Production Setup (One-Time)**

```bash
# 1. Install production dependencies
pip install waitress gunicorn python-dotenv

# 2. Collect static files
python manage.py collectstatic --noinput

# 3. Create logs directory
mkdir -p logs

# 4. Set correct permissions (Linux)
chmod 755 logs
```

### **Start Production Server**

**Option 1: Waitress (Windows/Linux)**
```bash
python -m waitress --port=9001 --host=0.0.0.0 erp_project.wsgi:application
```

**Option 2: Gunicorn (Linux)**
```bash
gunicorn --workers=4 --bind=0.0.0.0:9001 erp_project.wsgi:application
```

**Option 3: With Supervisor (Linux - Auto-restart)**

Create `/etc/supervisor/conf.d/erp_project.conf`:
```ini
[program:erp_project]
directory=/path/to/erp_project
command=/path/to/venv/bin/gunicorn \
    --workers=4 \
    --bind=0.0.0.0:9001 \
    erp_project.wsgi:application
autostart=true
autorestart=true
redirect_stderr=true
stdout_logfile=/var/log/erp_project.log
```

Start:
```bash
sudo supervisorctl reread
sudo supervisorctl update
sudo supervisorctl start erp_project
```

---

## 📊 Performance Optimization

### **Database Connection Pooling**

Add to `settings.py`:
```python
DATABASES = {
    'default': {
        # ... other settings ...
        'CONN_MAX_AGE': 600,  # 10 min connection reuse
        'OPTIONS': {
            'use_returning_into': False,  # Oracle-specific
        }
    }
}
```

### **Caching**

```python
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
        'LOCATION': 'unique-snowflake',
        'TIMEOUT': 300,  # 5 minutes
    }
}

# Cache session data
SESSION_ENGINE = 'django.contrib.sessions.backends.cache'
SESSION_CACHE_ALIAS = 'default'
```

### **Compression**

Static files are already compressed via WhiteNoiseMiddleware.

---

## 🔍 Testing Production Setup Locally

### **Test with DEBUG=False**

```bash
# Create .env.prod
cat > .env.prod << EOF
DEBUG=False
ALLOWED_HOSTS=localhost,127.0.0.1
SECRET_KEY=your-secret-key-here
EOF

# Load and test
export $(cat .env.prod)
python manage.py runserver
```

### **Test Static Files**

```bash
# Verify static files exist
ls -la staticfiles/

# Check if collectstatic works
python manage.py collectstatic --dry-run
```

### **Test Database Connection**

```bash
python manage.py dbshell
```

---

## ✅ Pre-Production Checklist

| Item | Check | Notes |
|------|-------|-------|
| Static files collected | [ ] | `python manage.py collectstatic` |
| DEBUG = False | [ ] | Set in settings.py or .env |
| SECRET_KEY set securely | [ ] | Use strong random value |
| ALLOWED_HOSTS configured | [ ] | List all production domains |
| Database credentials set | [ ] | Use .env file, never hardcode |
| HTTPS enabled | [ ] | Use Nginx + SSL certificate |
| Logging configured | [ ] | Check log files are writable |
| Database backups automated | [ ] | Test restore process |
| CSRF/Security headers set | [ ] | Verify in response headers |
| All migrations applied | [ ] | `python manage.py migrate` |
| Superuser created | [ ] | `python manage.py createsuperuser` |
| Error pages tested | [ ] | Test 404, 500 pages |
| Performance tested | [ ] | Check load time, memory usage |

---

## 🐛 Troubleshooting Production Issues

### **Static Files Not Loading**

```bash
# Recollect static files
python manage.py collectstatic --clear --noinput

# Verify with Nginx
curl -I http://localhost/static/css/bootstrap.min.css
```

### **Database Connection Refused**

```bash
# Test Oracle connection
python manage.py dbshell

# Check credentials in .env
cat .env

# Verify Oracle is running
sqlplus -L system/password@SDESDB
```

### **500 Errors in Production**

```bash
# Check logs
tail -f logs/django.log

# Check server logs (if using Supervisor)
tail -f /var/log/erp_project.log

# Test with DEBUG=True temporarily to see error details
```

### **High Memory Usage**

```bash
# Reduce worker processes
python -m waitress --workers=2 --port=9001 erp_project.wsgi:application

# Or with Gunicorn
gunicorn --workers=2 --bind=0.0.0.0:9001 erp_project.wsgi:application
```

---

## 📈 Monitoring & Maintenance

### **Daily Tasks**
- Check error logs: `tail -f logs/django.log`
- Monitor server resources: `top`, `df -h`
- Verify backups completed

### **Weekly Tasks**
- Review slow query logs
- Check disk space
- Test disaster recovery

### **Monthly Tasks**
- Review security headers
- Update dependencies: `pip list --outdated`
- Analyze performance metrics

---

## 🔐 Security Hardening

```python
# In settings.py for production

# HTTPS
SECURE_SSL_REDIRECT = True
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
SECURE_HSTS_SECONDS = 31536000  # 1 year

# Headers
SECURE_BROWSER_XSS_FILTER = True
SECURE_CONTENT_SECURITY_POLICY = {
    'default-src': ("'self'",),
}

# Session
SESSION_COOKIE_HTTPONLY = True
CSRF_COOKIE_HTTPONLY = True

# Admin
ADMIN_URL = 'secret-admin-path/'  # Change default /admin/
```

---

## 📝 Production Environment Example

**Final Production Setup:**

```
erp_project/
├── .env                    # Production secrets (never commit!)
├── staticfiles/            # Collected static files
├── logs/                   # Application logs
├── media/                  # User uploads
├── manage.py
├── erp_project/
│   ├── settings.py        # Production settings
│   ├── wsgi.py
│   └── urls.py
└── [other apps...]

Deployment:
- Server: Linux (CentOS/Ubuntu)
- Web Server: Nginx
- App Server: Gunicorn (4 workers)
- Database: Oracle 12.2
- Backup: Daily automated
- Monitoring: CloudWatch/Prometheus
- SSL: Let's Encrypt
```

---

## 🎯 Quick Production Deploy

```bash
#!/bin/bash
# Quick production deployment script

set -e

echo "📦 Collecting static files..."
python manage.py collectstatic --noinput

echo "🔧 Creating logs directory..."
mkdir -p logs

echo "✅ Production ready!"
echo ""
echo "Start server with:"
echo "  python -m waitress --port=9001 --host=0.0.0.0 erp_project.wsgi:application"
```

---

**Status**: ✅ Ready for Production  
**Last Updated**: June 4, 2026  
**Maintainer**: DevOps Team
