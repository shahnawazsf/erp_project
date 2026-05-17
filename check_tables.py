import os, oracledb
with open('.env') as f:
    for line in f:
        line = line.strip()
        if line and not line.startswith('#') and '=' in line:
            k, v = line.split('=', 1)
            os.environ.setdefault(k.strip(), v.strip())
oracledb.init_oracle_client(lib_dir=os.environ['ORACLE_CLIENT_DIR'])
conn = oracledb.connect(
    user=os.environ['ORACLE_DB_USER'],
    password=os.environ['ORACLE_DB_PASSWORD'],
    dsn=f"{os.environ['ORACLE_DB_HOST']}:{os.environ['ORACLE_DB_PORT']}/{os.environ['ORACLE_DB_NAME']}"
)
cur = conn.cursor()
cur.execute("SELECT table_name FROM user_tables ORDER BY table_name")
for r in cur.fetchall():
    print(r[0])
conn.close()
