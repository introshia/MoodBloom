import os
import mysql.connector
from dotenv import load_dotenv

load_dotenv()

db_config = {
    'host': 'localhost',
    'user': 'root',
    'password': os.getenv('DB_PASSWORD'), 
    'database': 'moodbloom_db'
}

def check_db():
    try:
        conn = mysql.connector.connect(**db_config)
        cursor = conn.cursor()
        
        print("Checking tables in moodbloom_db...")
        cursor.execute("SHOW TABLES")
        tables = cursor.fetchall()
        for (table,) in tables:
            print(f"\nTable: {table}")
            cursor.execute(f"DESCRIBE {table}")
            columns = cursor.fetchall()
            for col in columns:
                print(f"  {col}")
        
        conn.close()
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    check_db()
