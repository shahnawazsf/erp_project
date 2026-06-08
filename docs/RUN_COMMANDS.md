# ERP Application - Quick Run Commands

## 🖥️ Localhost Only (Default)

**Single command to start:**
```bash
python manage.py runserver 9001
```

**Access:**
```
http://localhost:9001
http://127.0.0.1:9001
```

**Use case:** Solo development, isolated testing

---

## 🌐 LAN Access (Network-Wide)

### Step 1: Find Your IP
```powershell
ipconfig | Select-String -Pattern 'IPv4 Address'
```

Example output: `172.16.2.3`

### Step 2: Update settings.py
Add to `CSRF_TRUSTED_ORIGINS`:
```python
CSRF_TRUSTED_ORIGINS = [
    'http://localhost:9001',
    'http://127.0.0.1:9001',
    'http://172.16.2.3:9001'  # ← Replace with your IP
]
```

### Step 3: Start Server
```bash
python manage.py runserver 0.0.0.0:9001
```

**Access from any machine on your network:**
```
http://172.16.2.3:9001
```

Replace `172.16.2.3` with your actual IP from Step 1.

---

## 📋 Other Useful Commands

### Run Migrations
```bash
python manage.py makemigrations
python manage.py migrate
```

### Collect Static Files
```bash
python manage.py collectstatic
```

### Create Django Admin User
```bash
python manage.py shell

# Inside the shell:
from accounts.models import User
User.objects.create_superuser(
    username='admin',
    email='admin@example.com',
    password='admin123'
)
exit()
```

### Access Django Admin
```
http://localhost:9001/admin/
```

---

## ✅ Checklist for LAN Access

- [ ] Found your IP: ___________
- [ ] Updated `CSRF_TRUSTED_ORIGINS` in settings.py
- [ ] Started server with `0.0.0.0:9001`
- [ ] Can ping the server from another machine
- [ ] Firewall allows port 9001 (Windows Defender)
- [ ] Can access from other machine's browser

---

## 🔧 Troubleshooting

| Issue | Solution |
|-------|----------|
| **"Connection refused"** | Server not started or wrong IP address |
| **"CSRF token missing"** | IP not added to `CSRF_TRUSTED_ORIGINS` |
| **"Can't access from other machine"** | Firewall blocking port 9001 |
| **"Wrong IP in CSRF_TRUSTED_ORIGINS"** | Check with `ipconfig` again, not 127.0.0.1 |

---

## 📝 Notes

- Port `9001` is used (not 8000/8080) to avoid Hyper-V conflicts on this machine
- `ALLOWED_HOSTS = ['*']` is already configured for any host
- Sessions are stored in Oracle `DJANGO_SESSION` table
- Both localhost and LAN access work simultaneously
