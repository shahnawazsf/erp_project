# Where & How to Execute Refresh Commands

**This guide shows EXACTLY where to type each command.**

---

## 📍 LOCATION TO WORK FROM

All commands must be executed from the **project root directory**:

```
E:\Testing\projects\erp_project\
```

**NOT from:**
- ❌ E:\Testing\projects\
- ❌ E:\Testing\
- ❌ C:\Users\...

---

## 🖥️ STEP 1: Open Terminal/Command Prompt

### **On Windows - Option A (Command Prompt)**

1. Open File Explorer
2. Navigate to: `E:\Testing\projects\erp_project\`
3. Click on address bar
4. Type: `cmd`
5. Press **Enter**

**Expected:** Command prompt opens in that directory

```
C:\Users\YourName> E:\Testing\projects\erp_project
E:\Testing\projects\erp_project>
```

### **On Windows - Option B (PowerShell)**

1. Open File Explorer
2. Navigate to: `E:\Testing\projects\erp_project\`
3. Right-click in empty area
4. Select: "Open PowerShell window here"

**Expected:** PowerShell opens in that directory

```
PS E:\Testing\projects\erp_project>
```

### **On Windows - Option C (VS Code Terminal)**

1. Open VS Code
2. Press: `Ctrl + J` (open terminal)
3. Terminal opens at project root
4. Or go to: Terminal → New Terminal

**Expected:**
```
PS E:\Testing\projects\erp_project>
```

---

## ✅ VERIFY YOU'RE IN CORRECT LOCATION

Type this command to verify:

**Windows Command Prompt:**
```bash
cd
```

**Windows PowerShell:**
```powershell
Get-Location
```

**Expected output:**
```
E:\Testing\projects\erp_project
```

If output is different, you're in wrong directory. Navigate to correct location first.

---

## 🔄 EXECUTE REFRESH - COMPLETE STEPS

### **STEP 1: Stop Running Server (if any)**

If a server is currently running, stop it:

**In terminal with running server:**
```
Press: Ctrl + C
```

Or kill the process:

```bash
# Windows Command Prompt
taskkill /F /IM python.exe

# Windows PowerShell
Stop-Process -Name python -Force
```

**Expected:** Server stops, terminal returns to prompt

```
E:\Testing\projects\erp_project>
```

---

### **STEP 2: Verify Current Directory**

Type:
```bash
dir
```

**Expected output (Windows):**
```
Directory of E:\Testing\projects\erp_project

2026-06-04  14:32    <DIR>          .git
2026-06-04  14:32    <DIR>          accounts
2026-06-04  14:32    <DIR>          core
2026-06-04  14:32    <DIR>          finance
2026-06-04  14:32    <DIR>          templates
2026-06-04  14:32    <DIR>          staticfiles
                  123  manage.py
                  456  REFRESH_FOR_PRODUCTION.md
```

If you don't see these files, you're in wrong directory!

---

### **STEP 3: Clean Up Cache Files**

**On Windows (Command Prompt):**
```bash
for /r . %d in (__pycache__) do @if exist "%d" rd /s /q "%d"
del /s *.pyc
```

**On Windows (PowerShell):**
```powershell
Get-ChildItem -Directory -Filter __pycache__ -Recurse | Remove-Item -Recurse -Force -ErrorAction SilentlyContinue
Get-ChildItem -Filter "*.pyc" -Recurse | Remove-Item -Force -ErrorAction SilentlyContinue
Remove-Item -Recurse -Force staticfiles -ErrorAction SilentlyContinue
```

**On Linux/Mac:**
```bash
find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null
find . -type f -name "*.pyc" -delete
rm -rf staticfiles/
```

**Expected:** Command completes silently (no output)

---

### **STEP 4: Update Python Packages**

**On Windows (Command Prompt or PowerShell):**
```bash
pip install --upgrade pip setuptools wheel
```

Then install packages:

```bash
pip install django==6.0.5 djangorestframework pillow django-crispy-forms crispy-bootstrap5 django-widget-tweaks oracledb whitenoise waitress python-dotenv
```

**Expected output:**
```
Collecting pip
Downloading pip-...whl (...)
...
Successfully installed pip-24.0 setuptools-69.0 wheel-0.42.0
```

---

### **STEP 5: Collect Static Files**

Type:
```bash
python manage.py collectstatic --noinput --clear
```

**Expected output:**
```
0 static files copied to 'E:\Testing\projects\erp_project\staticfiles'
158 unmodified
408 post-processed
```

---

### **STEP 6: Create .env File**

**On Windows (Command Prompt):**
```bash
(
echo # Database Configuration
echo ORACLE_DB_NAME=SDESDB
echo ORACLE_DB_USER=erp_user
echo ORACLE_DB_PASSWORD=YourPassword
echo ORACLE_DB_HOST=172.16.1.12
echo ORACLE_DB_PORT=1521
echo.
echo # Django
echo SECRET_KEY=django-insecure-change-me
echo DEBUG=False
echo ALLOWED_HOSTS=localhost,127.0.0.1,172.16.2.3
) > .env
```

**On Windows (PowerShell):**
```powershell
@"
# Database Configuration
ORACLE_DB_NAME=SDESDB
ORACLE_DB_USER=erp_user
ORACLE_DB_PASSWORD=YourPassword
ORACLE_DB_HOST=172.16.1.12
ORACLE_DB_PORT=1521

# Django
SECRET_KEY=django-insecure-change-me
DEBUG=False
ALLOWED_HOSTS=localhost,127.0.0.1,172.16.2.3
"@ | Out-File -FilePath .env -Encoding UTF8
```

**Verify file created:**
```bash
type .env
```

**Expected:** Shows the file contents

---

### **STEP 7: Create Logs Directory**

```bash
mkdir logs
```

**Verify:**
```bash
dir logs
```

**Expected:** Directory created (shown in output)

---

### **STEP 8: Test Database Connection**

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

Then:
```bash
EXIT
```

**Expected:** Returns to command prompt

```
E:\Testing\projects\erp_project>
```

---

### **STEP 9: Run Production Readiness Check**

```bash
bash verify_production_ready.sh
```

**Expected output:**
```
═══════════════════════════════════════════════════════════
  ERP Production Readiness Checker
═══════════════════════════════════════════════════════════

✓ Environment file (.env) exists
✓ Static files collected
✓ settings.py exists
✓ wsgi.py exists
... [more checks]

Passed: 12
Warnings: 0
Failed: 0

✅ READY FOR PRODUCTION
```

---

### **STEP 10: Create Logs Directory (again, to verify)**

```bash
ls logs
```

or on Windows:

```bash
dir logs
```

**Expected:** Directory exists

---

### **STEP 11: Start Production Server**

**Option A: Waitress (Recommended)**

```bash
python -m waitress --port=9001 --host=0.0.0.0 erp_project.wsgi:application
```

**Expected output:**
```
INFO:waitress:Serving on http://0.0.0.0:9001
```

**Server is now running!** ✅

Keep this terminal open and running.

---

### **STEP 12: Open NEW Terminal Window to Test**

**While server is running in first terminal:**

1. Open NEW terminal/command prompt
2. Navigate to same directory: `cd E:\Testing\projects\erp_project`
3. Type:

```bash
curl http://localhost:9001/accounts/login/
```

**Expected:** HTML content returns (login page)

```
<!DOCTYPE html>
<html lang="en">
...
```

If 404 error: server not running, go back to Step 11

---

### **STEP 13: Test in Browser**

Open browser and go to:

```
http://localhost:9001
```

**Expected:**
- Login page loads
- CSS styling appears (not broken)
- No "connection refused" error

---

## 📊 COMPLETE COMMAND SEQUENCE

**Copy & paste this entire sequence:**

```bash
REM Step 1: Stop any running servers
taskkill /F /IM python.exe

REM Step 2: Verify directory
cd E:\Testing\projects\erp_project
dir

REM Step 3: Clean cache
for /r . %d in (__pycache__) do @if exist "%d" rd /s /q "%d"
del /s *.pyc

REM Step 4: Update packages
pip install --upgrade pip setuptools wheel
pip install django==6.0.5 djangorestframework pillow django-crispy-forms crispy-bootstrap5 django-widget-tweaks oracledb whitenoise waitress python-dotenv

REM Step 5: Collect static files
python manage.py collectstatic --noinput --clear

REM Step 6: Create logs
mkdir logs

REM Step 7: Verify .env
type .env

REM Step 8: Test database
python manage.py dbshell
REM Type: SELECT 1 FROM DUAL;
REM Type: EXIT

REM Step 9: Run readiness check
bash verify_production_ready.sh

REM Step 10: Start server
python -m waitress --port=9001 --host=0.0.0.0 erp_project.wsgi:application
```

---

## 🎯 QUICK REFERENCE - WHERE TO TYPE EACH COMMAND

| Command | Type In | Window | Still Open? |
|---------|---------|--------|------------|
| Clean cache | Terminal | Main | YES |
| Update packages | Terminal | Main | YES |
| Collect static | Terminal | Main | YES |
| Create logs | Terminal | Main | YES |
| Test database | Terminal | Main | YES |
| Readiness check | Terminal | Main | YES |
| **Start server** | Terminal | Main | **KEEP OPEN** |
| Test pages | Terminal | **NEW** | YES (new) |
| Browser test | Browser | New tab | N/A |

---

## 🖼️ VISUAL LAYOUT

```
┌─────────────────────────────────────────────────────────┐
│ Main Terminal (Keep Running)                            │
├─────────────────────────────────────────────────────────┤
│ E:\Testing\projects\erp_project>                        │
│ $ python -m waitress --port=9001 ...                    │
│ INFO:waitress:Serving on http://0.0.0.0:9001           │
│ (Server running here - DO NOT CLOSE)                    │
└─────────────────────────────────────────────────────────┘

        ↓ Opens in same terminal during setup ↓

┌─────────────────────────────────────────────────────────┐
│ Test Terminal (NEW - Open after server starts)          │
├─────────────────────────────────────────────────────────┤
│ E:\Testing\projects\erp_project>                        │
│ $ curl http://localhost:9001/accounts/login/           │
│ (Shows login page HTML)                                 │
└─────────────────────────────────────────────────────────┘

        ↓ Opens browser during test ↓

┌─────────────────────────────────────────────────────────┐
│ Browser Window                                          │
├─────────────────────────────────────────────────────────┤
│ http://localhost:9001                                   │
│ (Shows login page with styling)                         │
└─────────────────────────────────────────────────────────┘
```

---

## ⚠️ COMMON MISTAKES

| Mistake | Fix |
|---------|-----|
| Running from wrong directory | `cd E:\Testing\projects\erp_project` first |
| Closing terminal with server | Keep it open! Server keeps running in that window |
| Not creating .env file | Create it before starting server |
| Typing command in browser | Type in terminal/command prompt, not browser address bar |
| Closing main terminal | Don't! Server stops when you close it |

---

## ✅ SUCCESS CHECKLIST

After executing all steps, verify:

- [ ] Terminal shows: `INFO:waitress:Serving on http://0.0.0.0:9001`
- [ ] No error messages in red
- [ ] Can access: http://localhost:9001
- [ ] Login page loads with styling
- [ ] No "connection refused" errors
- [ ] .env file created
- [ ] logs/ directory exists
- [ ] Static files collected

---

## 🚨 IF SOMETHING GOES WRONG

| Error | Solution |
|-------|----------|
| `ModuleNotFoundError: No module named 'django'` | Run: `pip install django` |
| `Port 9001 already in use` | Run server on different port: `--port=9002` |
| `Permission denied` | Open terminal as Administrator |
| `ORACLE_DB_PASSWORD not found` | Create .env file with correct credentials |
| Server crashes | Check logs: `type logs/django.log` |

---

## 📞 NEED HELP?

1. Make sure you're in: `E:\Testing\projects\erp_project`
2. Check current directory: `dir` or `Get-Location`
3. Verify file exists: `type manage.py` (should show file contents)
4. If stuck, type: `dir` and share output

---

**Ready to execute? Start with Step 1: Open Terminal!** 🚀
