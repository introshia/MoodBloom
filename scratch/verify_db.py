import mysql.connector

db_config = {
    'host': 'localhost',
    'user': 'root',
    'password': 'password',
    'database': 'moodbloom_db'
}

try:
    conn = mysql.connector.connect(**db_config)
    cursor = conn.cursor()
    cursor.execute("DESCRIBE journal_entries")
    for row in cursor.fetchall():
        print(row)
    conn.close()
except Exception as e:
    print(f"Error: {e}")
