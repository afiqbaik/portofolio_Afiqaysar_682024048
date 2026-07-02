import os
import sys
import time
from dotenv import load_dotenv
import mysql.connector

load_dotenv()

DB_HOST = os.getenv('DB_HOST')
DB_PORT = int(os.getenv('DB_PORT', '4000'))
DB_USER = os.getenv('DB_USER')
DB_PASSWORD = os.getenv('DB_PASSWORD')
DB_NAME = os.getenv('DB_NAME')

print('Testing DB connection to', DB_HOST, 'port', DB_PORT, 'database', DB_NAME)

try:
    start = time.time()
    conn = mysql.connector.connect(
        host=DB_HOST,
        port=DB_PORT,
        user=DB_USER,
        password=DB_PASSWORD,
        database=DB_NAME,
        connection_timeout=10
    )
    elapsed = time.time() - start
    print('CONNECTED (in {:.2f}s)'.format(elapsed))
    conn.close()
    sys.exit(0)
except Exception as e:
    print('CONNECTION_FAILED')
    print(str(e))
    sys.exit(2)
