# Production Deployment - Quick Start

**Ready to deploy to production?** Follow these 5 steps.

---

## ⚡ 5-Minute Production Setup

### **Step 1: Verify Production Readiness**

```bash
bash verify_production_ready.sh
```

Expected output:
```
✓ Environment file (.env) exists
✓ Static files collected
✓ settings.py exists
✓ wsgi.py exists
... [more checks]
✅ READY FOR PRODUCTION
```

---

### **Step 2: Collect Static Files** (One-time)

```bash
python manage.py collectstatic --noinput
```

Expected output:
```
0 static files copied to 'staticfiles'
158 unmodified
408 post-processed
```

---

### **Step 3: Create Production .env**

Create `.env` file in project root:

```ini
# Database Configuration
ORACLE_DB_NAME=SDESDB
ORACLE_DB_USER=erp_user
ORACLE_DB_PASSWORD=your_secure_password
ORACLE_DB_HOST=172.16.1.12
ORACLE_DB_PORT=1521

# Oracle Client Path (optional)
ORACLE_CLIENT_DIR=C:\oracle\instantclient_12_2

# Django Configuration
SECRET_KEY=your-super-secret-key-change-me
DEBUG=False
ALLOWED_HOSTS=localhost,127.0.0.1,172.16.2.3,your-domain.com
```

---

### **Step 4: Update Settings for Production**

Open `erp_project/settings.py` and change:

```python
# Change from:
DEBUG = True
ALLOWED_HOSTS = ['*']

# To:
DEBUG = False
ALLOWED_HOSTS = ['localhost', '127.0.0.1', '172.16.2.3', 'your-domain.com']
```

Or load from environment:
```python
import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

BASE_DIR = Path(__file__).resolve().parent.parent
SECRET_KEY = os.environ.get('SECRET_KEY')
DEBUG = os.environ.get('DEBUG', 'False') == 'True'
ALLOWED_HOSTS = os.environ.get('ALLOWED_HOSTS', 'localhost').split(',')
```

---

### **Step 5: Start Production Server**

**Option A: Waitress (Windows/Linux)**
```bash
python -m waitress --port=9001 --host=0.0.0.0 erp_project.wsgi:application
```

**Option B: Gunicorn (Linux)**
```bash
pip install gunicorn
gunicorn --workers=4 --bind=0.0.0.0:9001 erp_project.wsgi:application
```

**Expected output:**
```
Starting server in PID 12345.
Listening on http://0.0.0.0:9001
```

---

## ✅ Verify Production Deployment

1. **Test Local Access**
   ```bash
   curl http://localhost:9001/accounts/login/
   ```

2. **Test Network Access**
   ```bash
   curl http://172.16.2.3:9001/accounts/login/
   ```

3. **Check Static Files**
   - Open: http://localhost:9001
   - Login page should load with CSS styling
   - No 404 errors in console

4. **Check Logs**
   ```bash
   tail -f logs/django.log
   ```

---

## 📦 What Gets Deployed

```
Production Directory:
├── staticfiles/              ← Collected CSS, JS, images
├── .env                      ← Secrets (don't commit!)
├── logs/                     ← Error logs
├── erp_project/
│   ├── settings.py           ← Updated for production
│   ├── wsgi.py               ← Production entry point
│   └── urls.py
├── templates/                ← HTML templates
├── finance/                  ← All Django apps
├── accounts/
├── core/
└── manage.py
```

---

## 🔒 Security Checklist

- [ ] DEBUG = False
- [ ] SECRET_KEY changed (not the default value)
- [ ] ALLOWED_HOSTS set to specific domains
- [ ] .env file created with secure passwords
- [ ] .env added to .gitignore (never commit!)
- [ ] Database password is strong
- [ ] HTTPS enabled (use Nginx + SSL)
- [ ] CSRF cookies are secure
- [ ] Session cookies are secure

---

## 🐛 Common Issues & Fixes

### **Static Files Not Loading**
```bash
# Clear and recollect
python manage.py collectstatic --clear --noinput
```

### **Database Connection Error**
```bash
# Verify .env file
cat .env

# Test connection
python manage.py dbshell
```

### **Port 9001 Already in Use**
```bash
# Use different port
python -m waitress --port=9002 --host=0.0.0.0 erp_project.wsgi:application
```

### **Permission Denied on Logs**
```bash
# Create logs directory
mkdir -p logs
chmod 755 logs
```

---

## 📊 Performance Monitoring

**Check Server Status:**
```bash
# CPU and Memory
top

# Disk Space
df -h

# Network Connections
netstat -tuln | grep 9001

# Open Files
lsof -i :9001
```

**Check Logs:**
```bash
# Real-time logs
tail -f logs/django.log

# Error count
grep ERROR logs/django.log | wc -l

# Recent errors
tail -50 logs/django.log | grep ERROR
```

---

## 🚀 Auto-Restart on Server Reboot (Linux)

Create `/etc/systemd/system/erp-project.service`:

```ini
[Unit]
Description=ERP Project Django Application
After=network.target

[Service]
Type=notify
User=www-data
WorkingDirectory=/path/to/erp_project
ExecStart=/usr/bin/python -m waitress --port=9001 --host=0.0.0.0 erp_project.wsgi:application
Restart=on-failure
RestartSec=5s

[Install]
WantedBy=multi-user.target
```

Enable and start:
```bash
sudo systemctl daemon-reload
sudo systemctl enable erp-project
sudo systemctl start erp-project
sudo systemctl status erp-project
```

---

## 📈 Load Balancing (Multiple Servers)

If running on multiple servers, use Nginx to load balance:

```nginx
upstream erp_backend {
    server 172.16.2.3:9001 weight=1;
    server 172.16.2.4:9001 weight=1;
    server 172.16.2.5:9001 weight=1;
}

server {
    listen 80;
    server_name your-domain.com;

    location / {
        proxy_pass http://erp_backend;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    }
}
```

---

## 📞 Production Support

**For detailed guidance:**
- Read: `PRODUCTION_DEPLOYMENT.md` (comprehensive guide)
- Check: `COMPLETE_DEVELOPMENT_GUIDE.md` (architecture)
- Review: `DEVELOPMENT_CHANGELOG.md` (recent changes)

**For issues:**
1. Check logs: `tail -f logs/django.log`
2. Verify database: `python manage.py dbshell`
3. Test connectivity: `curl http://localhost:9001/`

---

## 🎯 Production Access

Once deployed:

- **Local**: http://localhost:9001
- **Network**: http://172.16.2.3:9001
- **Custom Domain**: https://your-domain.com (with Nginx)

Login with Oracle database credentials.

---

**Status**: ✅ Ready for Production  
**Last Updated**: June 4, 2026  
**Server**: Waitress / Gunicorn  
**Database**: Oracle 12.2
