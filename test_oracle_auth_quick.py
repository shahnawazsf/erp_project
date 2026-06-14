"""
Non-interactive Oracle GET_USER_DETAIL test.
Usage: python test_oracle_auth_quick.py <username> <password>
"""
import os, sys

env_path = os.path.join(os.path.dirname(__file__), '.env')
if os.path.exists(env_path):
    with open(env_path) as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith('#') and '=' in line:
                k, v = line.split('=', 1)
                os.environ.setdefault(k.strip(), v.strip())

if len(sys.argv) != 3:
    print("Usage: python test_oracle_auth_quick.py <username> <password>")
    sys.exit(1)

test_username, test_password = sys.argv[1], sys.argv[2]

HOST    = os.environ.get('ORACLE_DB_HOST', 'localhost')
PORT    = os.environ.get('ORACLE_DB_PORT', '1521')
SERVICE = os.environ.get('ORACLE_DB_NAME', 'ORCL')
USER    = os.environ.get('ORACLE_DB_USER', '')
PASSWORD= os.environ.get('ORACLE_DB_PASSWORD', '')
CLIENT  = os.environ.get('ORACLE_CLIENT_DIR', '')
DSN     = f"{HOST}:{PORT}/{SERVICE}"

import oracledb
if CLIENT:
    oracledb.init_oracle_client(lib_dir=CLIENT)

conn = oracledb.connect(user=USER, password=PASSWORD, dsn=DSN)
print(f"Connected to Oracle {conn.version}")

cur = conn.cursor()
p_user_id    = cur.var(oracledb.NUMBER)
p_first_name = cur.var(oracledb.STRING)
p_last_name  = cur.var(oracledb.STRING)
p_email      = cur.var(oracledb.STRING)
p_role       = cur.var(oracledb.STRING)
p_phone      = cur.var(oracledb.STRING)
p_is_active  = cur.var(oracledb.NUMBER)
p_status     = cur.var(oracledb.STRING)

cur.callproc('SDESERP.GET_USER_DETAIL', [
    test_username, test_password,
    p_user_id, p_first_name, p_last_name,
    p_email, p_role, p_phone, p_is_active, p_status,
])

status = p_status.getvalue()
print(f"\nStatus    : {status}")
if status == 'SUCCESS':
    print(f"User ID   : {p_user_id.getvalue()}")
    print(f"Name      : {p_first_name.getvalue()} {p_last_name.getvalue()}")
    print(f"Email     : {p_email.getvalue()}")
    print(f"Role      : {p_role.getvalue()}")
    print(f"Phone     : {p_phone.getvalue()}")
    print(f"Is Active : {p_is_active.getvalue()}")
    print("\n[OK] Authentication working correctly.")
else:
    print("\n[FAIL] Invalid credentials or inactive account.")

conn.close()
