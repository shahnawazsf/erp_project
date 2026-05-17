"""
Production server entry point using Waitress.
Run:  python serve.py
Access on LAN:  http://172.16.2.3:9000
"""
import os
import sys

# Ensure the project root is on the path
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'erp_project.settings')

from waitress import serve
from erp_project.wsgi import application

HOST = '0.0.0.0'
PORT = 9000
THREADS = 8   # concurrent request threads

if __name__ == '__main__':
    print("=" * 52)
    print("  SDES ERP — Production Server (Waitress)")
    print("=" * 52)
    print(f"  Local :   http://127.0.0.1:{PORT}")
    print(f"  Network:  http://172.16.2.3:{PORT}")
    print(f"  Threads:  {THREADS}")
    print("  Press Ctrl+C to stop.")
    print("=" * 52)
    serve(application, host=HOST, port=PORT, threads=THREADS)
