"""
Test ERP login end-to-end via HTTP.
Usage: python test_login.py <username> <password>
"""
import sys
import urllib.request
import urllib.parse
import urllib.error
import http.cookiejar
import re

if len(sys.argv) != 3:
    print("Usage: python test_login.py <username> <password>")
    sys.exit(1)

username, password = sys.argv[1], sys.argv[2]
BASE = "http://127.0.0.1:9000"

# Cookie jar so the session cookie persists between requests
jar = http.cookiejar.CookieJar()
opener = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(jar))
opener.addheaders = [('User-Agent', 'erp-login-test/1.0')]

print(f"\n  Target : {BASE}/accounts/login/")
print(f"  User   : {username}\n")

# ── 1. GET login page — grab CSRF token ─────────────────────────────
print("[1/3] Fetching login page...")
try:
    resp = opener.open(f"{BASE}/accounts/login/")
    html = resp.read().decode()
    print(f"      Status : {resp.status}")
except urllib.error.URLError as e:
    print(f"[FAIL] Cannot reach server: {e}")
    sys.exit(1)

match = re.search(r'csrfmiddlewaretoken["\s]+value=["\']([^"\']+)', html)
if not match:
    match = re.search(r'name="csrfmiddlewaretoken"\s+value="([^"]+)"', html)
if not match:
    print("[FAIL] Could not find CSRF token in login page.")
    sys.exit(1)

csrf = match.group(1)
print(f"      CSRF   : {csrf[:12]}…")

# ── 2. POST credentials ───────────────────────────────────────────────
print("[2/3] Posting credentials...")
payload = urllib.parse.urlencode({
    'username': username,
    'password': password,
    'csrfmiddlewaretoken': csrf,
}).encode()

req = urllib.request.Request(
    f"{BASE}/accounts/login/",
    data=payload,
    headers={
        'Referer': f"{BASE}/accounts/login/",
        'X-CSRFToken': csrf,
        'Content-Type': 'application/x-www-form-urlencoded',
    },
)

try:
    resp = opener.open(req)
    final_url = resp.url
    status = resp.status
except urllib.error.HTTPError as e:
    final_url = e.url
    status = e.code

print(f"      Status : {status}")
print(f"      Landed : {final_url}")

# ── 3. Evaluate result ────────────────────────────────────────────────
print("[3/3] Evaluating result...")
session_cookie = next(
    (c.value for c in jar if c.name == 'sessionid'), None
)

if session_cookie:
    print(f"\n[OK]  Login SUCCESSFUL")
    print(f"      Session ID : {session_cookie[:16]}…")
    print(f"      Redirected to: {final_url}")
else:
    print(f"\n[FAIL] Login FAILED — no session cookie set.")
    print(f"       Check the server console for auth backend log output.")
