import sqlite3

conn = sqlite3.connect('job_portal.db')
cursor = conn.cursor()

# Get recent error logs
    SELECT timestamp, agent_name, status, message 
    FROM agent_logs 
    ORDER BY timestamp DESC 
    LIMIT 20
""")

rows = cursor.fetchall()
print(f"{'TIMESTAMP':<20} | {'AGENT':<15} | {'STATUS':<10} | {'MESSAGE'}")
print("-" * 100)
for row in rows:
    print(f"{row[0]} | {row[1]:<15} | {row[2]:<10} | {row[3]}")

conn.close()
