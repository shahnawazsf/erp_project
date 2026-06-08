# Complete Refresh for Production - Full Documentation

**Version**: 1.0  
**Date**: June 4, 2026  
**Status**: Production Ready  
**Audience**: System Administrators & Developers

---

## 📋 TABLE OF CONTENTS

1. [Overview](#overview)
2. [Prerequisites](#prerequisites)
3. [Directory Structure](#directory-structure)
4. [Step-by-Step Execution](#step-by-step-execution)
5. [Verification Procedures](#verification-procedures)
6. [Troubleshooting](#troubleshooting)
7. [FAQs](#faqs)
8. [Monitoring & Maintenance](#monitoring--maintenance)
9. [Rollback Procedures](#rollback-procedures)

---

## OVERVIEW

### What is Production Refresh?

**Production Refresh** is the process of cleaning, updating, and preparing the ERP application for production deployment.

**Key Activities:**
- Clear development cache files
- Update dependencies
- Collect static files (CSS, JS, images)
- Verify database connectivity
- Configure production environment
- Start production server
- Verify all systems working

**Time Required**: ~15 minutes

**Prerequisites**: Python 3.8+, pip, Oracle database access

---

### Why Refresh for Production?

| Reason | Impact |
|--------|--------|
| Clean cache | Removes old .pyc files that cause errors |
| Update dependencies | Ensures all packages are latest secure versions |
| Collect static | Optimizes CSS/JS delivery |
| Verify database | Confirms connectivity before deployment |
| Production config | Sets proper security settings |

---

## PREREQUISITES

### System Requirements

**Windows:**
- Windows 10 or Server 2016+
- Administrator privileges (for taskkill)
- Command Prompt or PowerShell

**Linux/Mac:**
- Python 3.8+
- bash shell
- sudo access (optional)

### Software Requirements

| Software | Min Version | Purpose |
|----------|-------------|---------|
| Python | 3.8 | Runtime |
| pip | 20.0 | Package manager |
| Django | 6.0 | Web framework |
| Oracle Client | 12.2 | Database driver |
| Waitress | 1.4 | WSGI server |

### Database Requirements

- Oracle 12.2 or higher
- Database connectivity available
- User credentials: `erp_user` / `password`
- Tables: `CNT_RECVD_NOTIFICATION`, `LOGIN_USER`, etc.

### Network Requirements

- Port 9001 available
- No firewall blocking port 9001
- Oracle database accessible at `172.16.1.12:1521`

---

## DIRECTORY STRUCTURE

### Project Root

```
E:\Testing\projects\erp_project\
├── manage.py                      ← Django management script
├── COMPLETE_REFRESH_DOCUMENTATION.md  ← This file
├── EXECUTE_REFRESH_GUIDE.md       ← Execution guide
├── REFRESH_FOR_PRODUCTION.md      ← Detailed steps
├── PRODUCTION_QUICK_START.md      ← Quick reference
├── verify_production_ready.sh      ← Checker script
│
├── erp_project/                   ← Django project settings
│   ├── settings.py                ← Configuration (modify for production)
│   ├── wsgi.py                    ← Production entry point
│   ├── urls.py                    ← URL routing
│   └── __pycache__/               ← Cache (delete during refresh)
│
├── templates/                     ← HTML templates
│   ├── base.html                  ← Main layout
│   ├── accounts/
│   ├── finance/
│   └── core/
│
├── staticfiles/                   ← Collected static files (generated)
│   ├── css/
│   ├── js/
│   ├── images/
│   └── staticfiles.json
│
├── logs/                          ← Application logs (generated)
│   └── django.log
│
├── .env                           ← Production secrets (create manually)
│   └── Not committed to git!
│
├── .gitignore                     ← Tells git what to ignore
│   └── Includes: .env, __pycache__/, *.pyc
│
├── accounts/                      ← Django app
├── finance/                       ← Django app
├── core/                          ← Django app
├── inventory/                     ← Django app
├── sales/                         ← Django app
├── purchasing/                    ← Django app
│
└── .git/                          ← Version control
```

### Key Files to Know

| File | Purpose | Action |
|------|---------|--------|
| `manage.py` | Django control script | Run commands with this |
| `erp_project/settings.py` | Configuration | Modify for production |
| `erp_project/wsgi.py` | Entry point | Used by production server |
| `.env` | Secrets & config | Create before starting |
| `staticfiles/` | CSS/JS/images | Generate with collectstatic |
| `logs/` | Error logs | Monitor during operation |

---

## STEP-BY-STEP EXECUTION

### PREPARATION PHASE (5 minutes)

#### Step 1: Open Terminal at Project Root

**Windows - Method A (File Explorer):**
```
1. Open File Explorer
2. Navigate to: E:\Testing\projects\erp_project\
3. Click address bar (shows path)
4. Type: cmd
5. Press Enter
```

**Windows - Method B (Command Prompt):**
```
1. Press: Win + R
2. Type: cmd
3. Press Enter
4. Type: cd E:\Testing\projects\erp_project
5. Press Enter
```

**Windows - Method C (VS Code - EASIEST):**
```
1. Open VS Code
2. File → Open Folder
3. Select: E:\Testing\projects\erp_project\
4. Press: Ctrl + J (opens terminal)
5. Already at correct location!
```

**Linux/Mac:**
```bash
cd E:\Testing\projects\erp_project
```

**Expected Result:**
```
E:\Testing\projects\erp_project> _
```

---

#### Step 2: Verify Correct Location

Type:
```bash
dir
```

**Expected Output (Windows):**
```
Directory of E:\Testing\projects\erp_project

2026-06-04  14:32    <DIR>          .git
2026-06-04  14:32    <DIR>          accounts
2026-06-04  14:32    <DIR>          core
2026-06-04  14:32    <DIR>          finance
2026-06-04  14:32    <DIR>          templates
                  123  manage.py
                  456  REFRESH_FOR_PRODUCTION.md
```

**If you see these files:** ✅ You're in correct location

**If you don't:** ❌ Navigate to correct directory first

---

#### Step 3: Stop Running Servers

If a server is already running, stop it:

**Windows (Command Prompt):**
```bash
taskkill /F /IM python.exe
```

**Windows (PowerShell):**
```powershell
Stop-Process -Name python -Force
```

**Linux/Mac:**
```bash
pkill -f "python.*waitress"
```

**Expected:** Process termination message or "success"

---

### CLEANUP PHASE (5 minutes)

#### Step 4: Remove Cache Files

**Windows (Command Prompt):**
```bash
for /r . %d in (__pycache__) do @if exist "%d" rd /s /q "%d"
del /s *.pyc
```

**Windows (PowerShell):**
```powershell
Get-ChildItem -Directory -Filter __pycache__ -Recurse | Remove-Item -Recurse -Force -ErrorAction SilentlyContinue
Get-ChildItem -Filter "*.pyc" -Recurse | Remove-Item -Force -ErrorAction SilentlyContinue
Remove-Item -Recurse -Force staticfiles -ErrorAction SilentlyContinue
```

**Linux/Mac:**
```bash
find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null
find . -type f -name "*.pyc" -delete
rm -rf staticfiles/
```

**Expected:** Command completes silently (no output means success)

---

### INSTALLATION PHASE (5 minutes)

#### Step 5: Update Python Package Manager

```bash
pip install --upgrade pip setuptools wheel
```

**Expected Output:**
```
Collecting pip
Downloading pip-24.0-py3-none-any.whl (2.1 MB)
Installing collected packages: pip, setuptools, wheel
Successfully installed pip-24.0 setuptools-69.0 wheel-0.42.0
```

---

#### Step 6: Install All Dependencies

```bash
pip install django==6.0.5 djangorestframework pillow django-crispy-forms crispy-bootstrap5 django-widget-tweaks oracledb whitenoise waitress python-dotenv
```

**Expected Output:**
```
Collecting django==6.0.5
  Downloading Django-6.0.5-py3-none-any.whl (8.1 MB)
Collecting djangorestframework
  Downloading djangorestframework-3.14.0-py3-none-any.whl (1.1 MB)
...
Successfully installed django-6.0.5 djangorestframework-3.14.0 ... [more packages]
```

**Time:** 2-3 minutes depending on internet speed

---

### BUILD PHASE (3 minutes)

#### Step 7: Collect Static Files

```bash
python manage.py collectstatic --noinput --clear
```

**Expected Output:**
```
0 static files copied to 'E:\Testing\projects\erp_project\staticfiles'
158 unmodified
408 post-processed
```

**What This Does:**
- Gathers all CSS files from `templates/`
- Gathers all JavaScript files
- Optimizes and minifies them
- Places in `staticfiles/` directory
- Creates `staticfiles.json` for reference

**Verification:**
```bash
dir staticfiles
```

Should show: CSS, JS, images, and `staticfiles.json`

---

### CONFIGURATION PHASE (3 minutes)

#### Step 8: Create .env Configuration File

**Windows (PowerShell):**
```powershell
@"
# Database Configuration
ORACLE_DB_NAME=SDESDB
ORACLE_DB_USER=erp_user
ORACLE_DB_PASSWORD=YourSecurePassword123
ORACLE_DB_HOST=172.16.1.12
ORACLE_DB_PORT=1521

# Oracle Client Path (optional)
ORACLE_CLIENT_DIR=C:\oracle\instantclient_12_2

# Django Configuration
SECRET_KEY=django-insecure-your-secret-key-here-change-me
DEBUG=False
ALLOWED_HOSTS=localhost,127.0.0.1,172.16.2.3,your-domain.com
"@ | Out-File -FilePath .env -Encoding UTF8
```

**Windows (Command Prompt):**
```bash
(
echo # Database Configuration
echo ORACLE_DB_NAME=SDESDB
echo ORACLE_DB_USER=erp_user
echo ORACLE_DB_PASSWORD=YourSecurePassword123
echo ORACLE_DB_HOST=172.16.1.12
echo ORACLE_DB_PORT=1521
echo.
echo # Django Configuration
echo SECRET_KEY=django-insecure-your-secret-key-here
echo DEBUG=False
echo ALLOWED_HOSTS=localhost,127.0.0.1,172.16.2.3
) > .env
```

**Verify Creation:**
```bash
type .env
```

**Expected:** Shows the file contents

**⚠️ IMPORTANT:**
- ❌ DO NOT commit `.env` to git
- ✅ Keep `.env` in `.gitignore`
- ✅ Change `ORACLE_DB_PASSWORD` to your actual password
- ✅ Change `SECRET_KEY` to a random secure key

---

#### Step 9: Create Logs Directory

```bash
mkdir logs
```

**Verify:**
```bash
dir logs
```

**Expected:** Directory `logs` exists (shown in listing)

---

### VERIFICATION PHASE (3 minutes)

#### Step 10: Test Database Connection

```bash
python manage.py dbshell
```

**Expected:** SQL prompt opens

```
SQL> 
```

Type:
```bash
SELECT 1 FROM DUAL;
```

**Expected Output:**
```
         1
----------
         1
```

Then exit:
```bash
EXIT
```

**Expected:** Returns to command prompt

```
E:\Testing\projects\erp_project>
```

---

#### Step 11: Run Production Readiness Check

```bash
bash verify_production_ready.sh
```

**Expected Output:**
```
═══════════════════════════════════════════════════════════
  ERP Production Readiness Checker
═══════════════════════════════════════════════════════════

📋 Checking Django Configuration...
✓ Environment file (.env) exists
✓ Static files collected
✓ settings.py exists
✓ wsgi.py exists

📦 Checking Python Packages...
✓ Django installed
✓ Waitress installed
✓ oracledb installed
✓ WhiteNoise installed

🗄️ Checking Database...
✓ Can connect to Oracle

📁 Checking Directory Structure...
✓ templates/ directory exists
✓ staticfiles/ directory exists
✓ logs/ directory exists

🔐 Checking Security Settings...
✓ DEBUG set to False
✓ SECRET_KEY is not default
✓ ALLOWED_HOSTS configured

═══════════════════════════════════════════════════════════
  Summary
═══════════════════════════════════════════════════════════

Passed: 12
Warnings: 0
Failed: 0

✅ READY FOR PRODUCTION
```

**If you see:** `✅ READY FOR PRODUCTION` → Continue to Step 12

**If you see:** `❌ NOT READY FOR PRODUCTION` → Fix failed checks before proceeding

---

### DEPLOYMENT PHASE (1 minute)

#### Step 12: Start Production Server

```bash
python -m waitress --port=9001 --host=0.0.0.0 erp_project.wsgi:application
```

**Expected Output:**
```
INFO:waitress:Serving on http://0.0.0.0:9001
```

**Server is now RUNNING!** ✅

**⚠️ IMPORTANT:** Keep this terminal window OPEN. The server runs in this window.

```
┌─────────────────────────────────────────┐
│ Terminal 1 - Server Running             │
│                                         │
│ E:\Testing\projects\erp_project>        │
│ $ python -m waitress --port=9001 ...    │
│ INFO:waitress:Serving on 0.0.0.0:9001  │
│                                         │
│ ✅ DO NOT CLOSE THIS WINDOW!            │
└─────────────────────────────────────────┘
```

---

## VERIFICATION PROCEDURES

### Verification Phase (5 minutes)

After server starts, verify everything works:

#### Test 1: Local Connectivity

**Open NEW terminal window** (keep server running in first window)

```bash
curl http://localhost:9001/accounts/login/
```

**Expected Output:** HTML content of login page

```html
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Sign In — Reporting Tool</title>
    ...
```

**If you see HTML:** ✅ Server is working

**If you see error:** 
```
curl: (7) Failed to connect to localhost port 9001: Connection refused
```
❌ Server not running - check first terminal

---

#### Test 2: Static Files

```bash
curl -I http://localhost:9001/static/css/bootstrap.min.css
```

**Expected Output:**
```
HTTP/1.1 200 OK
Content-Type: text/css; charset=utf-8
Content-Length: 123456
```

**If you see:** `HTTP/1.1 200 OK` → ✅ Static files working

**If you see:** `HTTP/1.1 404 Not Found` → ❌ Static files not collected (run Step 7 again)

---

#### Test 3: Browser Access

**Open Web Browser** and go to:
```
http://localhost:9001
```

**Expected:**
- Login page loads
- See "Reporting Tool" title
- See login form (Username & Password fields)
- CSS styling visible (proper colors, fonts, spacing)
- No broken images or console errors

**If you see all of above:** ✅ Application fully working

**If CSS is broken:** 
- Clear browser cache: `Ctrl + Shift + Delete`
- Refresh page: `Ctrl + R`

---

#### Test 4: Test Container Notification Feature

**In browser:**
1. Login with your credentials
2. Click: **Finance** → **Container Notification**
3. Click: **Add Record** button
4. Notice: Form field shows "CNT-" prefix pre-filled

**Expected:**
```
Container No *
┌────────────────────┐
│ CNT-               │  ← Prefilled
└────────────────────┘
```

**If you see** "CNT-" prefilled → ✅ Container feature working

---

#### Test 5: Verify All Pages Load

**Test these pages:**
- [ ] Dashboard: http://localhost:9001/core/dashboard/
- [ ] Finance Reports: http://localhost:9001/finance/reports/
- [ ] Container Notification: http://localhost:9001/finance/container-notification/
- [ ] VAT Report: http://localhost:9001/finance/reports/vat/

**Expected:** All pages load without 404 errors

---

### Verification Checklist

```
✅ Terminal 1: Server shows "Serving on 0.0.0.0:9001"
✅ Terminal 2: curl shows HTML content (not connection refused)
✅ Browser: Login page loads with CSS styling
✅ Browser: Can login with credentials
✅ Browser: Dashboard shows without errors
✅ Browser: Container Notification shows "CNT-" prefix
✅ Browser: No red error messages in console (F12)
✅ Logs: No ERROR lines in logs/django.log
```

If all checked: **✅ PRODUCTION REFRESH COMPLETE**

---

## TROUBLESHOOTING

### Common Issues & Solutions

#### Issue 1: "Connection refused" on port 9001

**Symptom:**
```
curl: (7) Failed to connect to localhost port 9001: Connection refused
```

**Cause:** Server not running or crashed

**Solution:**
1. Check Terminal 1 - does it show "Serving on..."?
2. If not, go to Terminal 1 and run Step 12 again
3. If server crashes, check error message
4. See: [Server Crashes](#server-crashes) section below

---

#### Issue 2: Static Files Return 404

**Symptom:**
```
HTTP/1.1 404 Not Found
```

When accessing: `http://localhost:9001/static/css/...`

**Cause:** Static files not collected

**Solution:**
1. Go to Terminal 1
2. Press: `Ctrl + C` (stop server)
3. Run: `python manage.py collectstatic --clear --noinput`
4. Run Step 12 again: Start server

---

#### Issue 3: Database Connection Error

**Symptom:**
```
ORA-12154: TNS:could not resolve the connect identifier specified
```

**Cause:** Database unreachable or credentials wrong

**Solution:**
1. Check `.env` file: `type .env`
2. Verify credentials:
   - `ORACLE_DB_HOST=172.16.1.12` (correct IP?)
   - `ORACLE_DB_USER=erp_user` (correct user?)
   - `ORACLE_DB_PASSWORD=...` (correct password?)
3. Test connection manually:
   ```bash
   python manage.py dbshell
   ```
4. If fails, contact DBA with error message

---

#### Issue 4: Port 9001 Already in Use

**Symptom:**
```
OSError: [Errno 48] Address already in use
```

**Cause:** Another application using port 9001

**Solution:**
1. Check what's using port: `netstat -ano | findstr :9001` (Windows)
2. Option A: Kill the process: `taskkill /PID <PID> /F`
3. Option B: Use different port: `--port=9002`

---

#### Issue 5: ModuleNotFoundError: No module named 'django'

**Symptom:**
```
ModuleNotFoundError: No module named 'django'
```

**Cause:** Django not installed

**Solution:**
1. Run Step 6 again:
   ```bash
   pip install django==6.0.5
   ```
2. Verify installation: `pip list | grep django`

---

#### Issue 6: Server Crashes

**Symptom:** Server starts then immediately stops

**Cause:** Application error

**Solution:**
1. Check logs: `type logs/django.log`
2. Look for ERROR lines
3. Fix the issue based on error message
4. Restart server (Step 12)

---

#### Issue 7: CSS/JS Not Loaded in Browser

**Symptom:** 
- Login page visible but no colors/styling
- Broken layout

**Cause:** Browser cache or static files issue

**Solution:**
1. Hard refresh browser: `Ctrl + Shift + R` (or `Cmd + Shift + R` on Mac)
2. Clear browser cache: `Ctrl + Shift + Delete`
3. Or re-collect static files:
   ```bash
   python manage.py collectstatic --clear --noinput
   ```

---

### Emergency Rollback

If everything is broken and you need to rollback:

```bash
# Stop server
Ctrl + C

# Revert code changes
git checkout -- .

# Remove generated files
rm -rf staticfiles/ logs/*

# Go back to last commit
git reset --hard HEAD

# Start over from Step 1
```

---

## FAQs

### Q: Can I close the terminal with the running server?

**A:** ❌ NO! The server runs in that terminal. If you close it, the server stops.

**Solution:** Open a NEW terminal for testing/commands, keep server terminal open.

---

### Q: How do I stop the server?

**A:** In the terminal running the server, press: `Ctrl + C`

**Expected:** Server stops, prompt returns

```
^C
Keyboard interrupt: shutting down WSGIServer

E:\Testing\projects\erp_project>
```

---

### Q: Can I restart the server without refreshing everything?

**A:** Yes! Just run Step 12 again (no need to repeat Steps 1-11)

```bash
python -m waitress --port=9001 --host=0.0.0.0 erp_project.wsgi:application
```

---

### Q: Do I need to update .env every time?

**A:** No. Create `.env` once (Step 8), then it persists.

Only update if:
- Database credentials change
- Adding new domains to ALLOWED_HOSTS
- Changing SECRET_KEY

---

### Q: What if I accidentally committed .env to git?

**A:** ⚠️ SECURITY ISSUE! Your credentials are exposed!

**Solution:**
```bash
git rm --cached .env
git commit -m "Remove .env from repository"
git push

# Immediately change database password!
```

---

### Q: Can I run multiple servers on different ports?

**A:** Yes! Run in separate terminals with different ports:

```bash
# Terminal 1
python -m waitress --port=9001 --host=0.0.0.0 erp_project.wsgi:application

# Terminal 2
python -m waitress --port=9002 --host=0.0.0.0 erp_project.wsgi:application
```

---

### Q: How do I access the application from another computer?

**A:** Use the server's IP address instead of localhost:

```
http://172.16.2.3:9001
```

(Replace `172.16.2.3` with your server's IP)

---

### Q: What's the difference between DEBUG=True and DEBUG=False?

**A:**

| Setting | DEBUG=True | DEBUG=False |
|---------|-----------|-----------|
| Error Details | Shows full traceback | Shows generic error page |
| Performance | Slower (reloads code) | Faster (cached) |
| Security | Less secure (exposes paths) | Secure for production |
| Ideal For | Development | Production |

**For production:** Always use `DEBUG=False`

---

## MONITORING & MAINTENANCE

### Monitor Server During Operation

**In a separate terminal, watch logs in real-time:**

```bash
tail -f logs/django.log
```

**Expected:** Shows any errors/warnings

**Look for:**
- ❌ `ERROR` - Major problems
- ⚠️ `WARNING` - Issues to investigate
- ✅ Nothing - Server running smoothly

---

### Daily Checklist

Every day, check:

```
Morning:
- [ ] Server started without errors
- [ ] Can access http://localhost:9001
- [ ] No ERROR lines in logs/django.log

During day:
- [ ] Monitor logs for errors
- [ ] Check disk space: df -h
- [ ] Monitor memory: top

Evening:
- [ ] Review error logs for patterns
- [ ] Backup database
- [ ] Verify backups completed
```

---

### Weekly Maintenance

```
Every week:
- [ ] Review security logs
- [ ] Check for available updates: pip list --outdated
- [ ] Test disaster recovery (restore from backup)
- [ ] Review application performance
- [ ] Check disk space trending
```

---

## SUMMARY

### Refresh Process Timeline

| Phase | Steps | Duration | Terminal |
|-------|-------|----------|----------|
| Preparation | 1-3 | 5 min | Main |
| Cleanup | 4 | 2 min | Main |
| Installation | 5-6 | 5 min | Main |
| Build | 7 | 3 min | Main |
| Configuration | 8-9 | 3 min | Main |
| Verification | 10-11 | 3 min | Main |
| Deployment | 12 | 1 min | Main |
| Testing | 1-5 | 5 min | New |
| **TOTAL** | - | **~15 min** | - |

---

### Success Indicators

When complete, you should have:

```
✅ Clean codebase (no cache files)
✅ Updated dependencies (latest secure versions)
✅ Collected static files (CSS/JS optimized)
✅ Verified database connection
✅ Created .env with credentials
✅ Set DEBUG=False for security
✅ Server running on port 9001
✅ All pages loading without errors
✅ Logs directory created
✅ Ready for production use
```

---

### File Locations (Post-Refresh)

```
E:\Testing\projects\erp_project\
├── .env                    ← Your production config (KEEP SECURE!)
├── logs/
│   └── django.log         ← Error logs (monitor regularly)
├── staticfiles/           ← Optimized CSS/JS (generated)
│   ├── css/
│   ├── js/
│   └── staticfiles.json
├── manage.py              ← Control script
└── [app folders]          ← Django apps
```

---

## NEXT STEPS

After successful refresh:

1. **Monitor Server**
   ```bash
   tail -f logs/django.log
   ```

2. **Test All Features**
   - Login
   - View reports
   - Add containers
   - Test search
   - Test settings

3. **Set Up Monitoring**
   - Check logs daily
   - Monitor disk space
   - Backup regularly

4. **Document Your Setup**
   - Save IP address
   - Document any custom configuration
   - Keep backups

---

## SUPPORT & REFERENCES

### Documentation Files

- `EXECUTE_REFRESH_GUIDE.md` - Where to type commands
- `REFRESH_FOR_PRODUCTION.md` - Detailed step explanations
- `PRODUCTION_QUICK_START.md` - Quick 5-minute setup
- `PRODUCTION_DEPLOYMENT.md` - Complete deployment guide

### Quick Commands Reference

```bash
# Stop server
Ctrl + C

# Start server
python -m waitress --port=9001 --host=0.0.0.0 erp_project.wsgi:application

# Test connectivity
curl http://localhost:9001/accounts/login/

# View logs
tail -f logs/django.log

# Collect static files
python manage.py collectstatic --noinput

# Test database
python manage.py dbshell
```

---

## CONCLUSION

**You now have:**
- ✅ Complete documentation
- ✅ Step-by-step refresh process
- ✅ Verification procedures
- ✅ Troubleshooting guide
- ✅ Everything needed for production

**Ready to refresh?** Start with Step 1: Open Terminal at Project Root!

---

**Document Version**: 1.0  
**Last Updated**: June 4, 2026  
**Status**: Complete & Ready for Production  
**Maintainer**: DevOps Team
