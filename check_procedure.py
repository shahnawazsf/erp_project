"""Inspect GET_USER_DETAIL procedure signature on the Oracle server."""
import os

env_path = os.path.join(os.path.dirname(__file__), '.env')
if os.path.exists(env_path):
    with open(env_path) as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith('#') and '=' in line:
                k, v = line.split('=', 1)
                os.environ.setdefault(k.strip(), v.strip())

import oracledb

CLIENT = os.environ.get('ORACLE_CLIENT_DIR', '')
if CLIENT:
    oracledb.init_oracle_client(lib_dir=CLIENT)

conn = oracledb.connect(
    user=os.environ['ORACLE_DB_USER'],
    password=os.environ['ORACLE_DB_PASSWORD'],
    dsn=f"{os.environ['ORACLE_DB_HOST']}:{os.environ['ORACLE_DB_PORT']}/{os.environ['ORACLE_DB_NAME']}",
)

cur = conn.cursor()

# Get all parameters of the procedure
cur.execute("""
    SELECT argument_name, position, in_out, data_type, data_length
      FROM user_arguments
     WHERE object_name = 'GET_USER_DETAIL'
     ORDER BY position
""")
rows = cur.fetchall()

if not rows:
    print("Procedure GET_USER_DETAIL not found in user_arguments.")
else:
    print(f"{'POS':<5} {'NAME':<20} {'IN/OUT':<10} {'TYPE':<15} {'LEN'}")
    print("-" * 60)
    for row in rows:
        print(f"{str(row[1]):<5} {str(row[0] or '(return)'):<20} {row[2]:<10} {row[3]:<15} {row[4]}")

cur.close()
conn.close()
