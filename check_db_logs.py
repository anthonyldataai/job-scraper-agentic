import sqlite3
from datetime import datetime

conn = sqlite3.connect('job_portal.db')
cursor = conn.cursor()

print("--- Recent Logs ---")
cursor.execute("SELECT timestamp, agent_name, message, status FROM agent_logs ORDER BY timestamp DESC LIMIT 5")
rows = cursor.fetchall()
for row in rows:
    print(row)

conn.close()
