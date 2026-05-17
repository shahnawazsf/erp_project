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

print('--- DJANGO_MIGRATIONS ---')
cur.execute('SELECT app, name FROM DJANGO_MIGRATIONS ORDER BY id')
for r in cur.fetchall():
    print(r)

print()
print('--- DJANGO_CONTENT_TYPE columns ---')
cur.execute("SELECT column_name FROM user_tab_columns WHERE table_name='DJANGO_CONTENT_TYPE' ORDER BY column_id")
for r in cur.fetchall():
    print(r[0])

print()
print('--- ACCOUNTS_USER table exists? ---')
cur.execute("SELECT COUNT(*) FROM user_tables WHERE table_name='ACCOUNTS_USER'")
print(cur.fetchone()[0])

conn.close()
