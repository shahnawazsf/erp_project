"""
Quick Oracle connection + GET_USER_DETAIL procedure test.
Run: python test_oracle_auth.py
"""
import os
import sys

# Load .env
env_path = os.path.join(os.path.dirname(__file__), '.env')
if os.path.exists(env_path):
    with open(env_path) as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith('#') and '=' in line:
                k, v = line.split('=', 1)
                os.environ.setdefault(k.strip(), v.strip())

HOST     = os.environ.get('ORACLE_DB_HOST', 'localhost')
PORT     = os.environ.get('ORACLE_DB_PORT', '1521')
SERVICE  = os.environ.get('ORACLE_DB_NAME', 'ORCL')
USER     = os.environ.get('ORACLE_DB_USER', '')
PASSWORD = os.environ.get('ORACLE_DB_PASSWORD', '')
CLIENT   = os.environ.get('ORACLE_CLIENT_DIR', '')

DSN = f"{HOST}:{PORT}/{SERVICE}"

print("=" * 60)
print("  Oracle Auth Connection Test")
print("=" * 60)
print(f"  DSN  : {DSN}")
print(f"  User : {USER}")
print(f"  Mode : {'thick (Instant Client)' if CLIENT else 'thin'}")
print("=" * 60)

try:
    import oracledb
except ImportError:
    print("[FAIL] oracledb is not installed. Run: pip install oracledb")
    sys.exit(1)

# ── 1. Init thick mode if client dir is set ──────────────────────────
if CLIENT:
    try:
        oracledb.init_oracle_client(lib_dir=CLIENT)
        print(f"[OK]   Thick mode initialised ({CLIENT})")
    except Exception as e:
        print(f"[WARN] Thick mode init failed: {e}")
        print("       Falling back to thin mode.")
else:
    print("[INFO] No ORACLE_CLIENT_DIR set — using thin mode.")

# ── 2. Basic connection test ─────────────────────────────────────────
print("\n[1/3] Testing raw Oracle connection...")
try:
    conn = oracledb.connect(user=USER, password=PASSWORD, dsn=DSN)
    print(f"[OK]   Connected. Oracle server version: {conn.version}")
except Exception as e:
    print(f"[FAIL] Connection failed: {e}")
    sys.exit(1)

# ── 3. Check procedure exists ────────────────────────────────────────
print("\n[2/3] Checking GET_USER_DETAIL procedure...")
try:
    cur = conn.cursor()
    cur.execute(
        "SELECT object_name, status FROM user_objects "
        "WHERE object_name = 'GET_USER_DETAIL' AND object_type = 'PROCEDURE'"
    )
    row = cur.fetchone()
    if row:
        print(f"[OK]   Procedure found — status: {row[1]}")
        if row[1] != 'VALID':
            cur.execute(
                "SELECT line, text FROM user_errors WHERE name = 'GET_USER_DETAIL'"
            )
            for err in cur.fetchall():
                print(f"       Line {err[0]}: {err[1].strip()}")
    else:
        print("[WARN] GET_USER_DETAIL procedure does NOT exist in this schema.")
        print("       Create it using the DDL in SETUP_GUIDE.txt section 3.5.")
        conn.close()
        sys.exit(0)
except Exception as e:
    print(f"[FAIL] Could not query user_objects: {e}")
    conn.close()
    sys.exit(1)

# ── 4. Call the procedure with a test user ───────────────────────────
print("\n[3/3] Calling GET_USER_DETAIL with test credentials...")
test_username = input("       Enter username to test: ").strip()
test_password = input("       Enter password to test: ").strip()

try:
    cur = conn.cursor()
    p_user_id    = cur.var(oracledb.NUMBER)
    p_first_name = cur.var(oracledb.STRING)
    p_last_name  = cur.var(oracledb.STRING)
    p_email      = cur.var(oracledb.STRING)
    p_role       = cur.var(oracledb.STRING)
    p_phone      = cur.var(oracledb.STRING)
    p_is_active  = cur.var(oracledb.NUMBER)
    p_status     = cur.var(oracledb.STRING)

    cur.callproc('GET_USER_DETAIL', [
        test_username, test_password,
        p_user_id, p_first_name, p_last_name,
        p_email, p_role, p_phone, p_is_active, p_status,
    ])

    status = p_status.getvalue()
    print(f"\n  Status    : {status}")
    if status == 'SUCCESS':
        print(f"  User ID   : {p_user_id.getvalue()}")
        print(f"  Name      : {p_first_name.getvalue()} {p_last_name.getvalue()}")
        print(f"  Email     : {p_email.getvalue()}")
        print(f"  Role      : {p_role.getvalue()}")
        print(f"  Phone     : {p_phone.getvalue()}")
        print(f"  Is Active : {p_is_active.getvalue()}")
        print("\n[OK]   Authentication via GET_USER_DETAIL is working correctly.")
    else:
        print("\n[FAIL] Procedure returned FAILED — invalid credentials or inactive account.")

except Exception as e:
    print(f"[FAIL] Procedure call error: {e}")

conn.close()
print("\nDone.")
