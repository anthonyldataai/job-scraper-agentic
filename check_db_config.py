import sqlite3
import json

conn = sqlite3.connect('job_portal.db')
cursor = conn.cursor()

print("--- Current Config ---")
cursor.execute("SELECT key, value FROM config")
rows = cursor.fetchall()
for row in rows:
    print(f"{row[0]}: {row[1]}")

conn.close()
