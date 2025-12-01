import sqlite3

def add_column():
    conn = sqlite3.connect('job_portal.db')
    cursor = conn.cursor()
    
    try:
        # Check if column exists
        cursor.execute("PRAGMA table_info(job_posts)")
        columns = [info[1] for info in cursor.fetchall()]
        
        if 'created_at' not in columns:
            print("Adding created_at column...")
            cursor.execute("ALTER TABLE job_posts ADD COLUMN created_at DATETIME")
            conn.commit()
            print("Column added successfully.")
        else:
            print("Column created_at already exists.")
            
    except Exception as e:
        print(f"Error: {e}")
    finally:
        conn.close()

if __name__ == "__main__":
    add_column()
