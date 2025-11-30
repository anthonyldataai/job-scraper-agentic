import sqlite3
import json

conn = sqlite3.connect('job_portal.db')
cursor = conn.cursor()

# Manually set enabled_sources to just linkedin to fix the immediate state
key = "enabled_sources"
value = json.dumps(["linkedin"])

# Check if exists
cursor.execute("SELECT 1 FROM config WHERE key = ?", (key,))
if cursor.fetchone():
    cursor.execute("UPDATE config SET value = ? WHERE key = ?", (value, key))
else:
    cursor.execute("INSERT INTO config (key, value) VALUES (?, ?)", (key, value))

conn.commit()
print("Updated enabled_sources to ['linkedin']")
conn.close()
