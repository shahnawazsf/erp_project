"""Inspect columns of finance-related Oracle tables."""
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

tables = ['INVOICE_MASTER', 'INVOICE_DETAIL', 'VAT_SETUP_MASTER', 'VAT_SETUP_DETAIL',
          'CUSTOMERS', 'CUSTOMER_BASIC', 'ZATCA_EINVOICE_DETAIL']

for table in tables:
    cur.execute("""
        SELECT column_name, data_type, data_length, nullable
          FROM user_tab_columns
         WHERE table_name = :t
         ORDER BY column_id
    """, t=table)
    rows = cur.fetchall()
    if rows:
        print(f"\n{'='*60}")
        print(f"  TABLE: {table}")
        print(f"{'='*60}")
        for r in rows:
            print(f"  {r[0]:<35} {r[1]:<15} {r[2]}")
    else:
        print(f"\n  TABLE {table}: not found or no columns")

conn.close()
