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

def migrate():
    try:
        conn = mysql.connector.connect(**db_config)
        cursor = conn.cursor()
        
        print("Running migration for collections...")
        
        # 1. Create collections table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS collections (
                id INT AUTO_INCREMENT PRIMARY KEY,
                user_id INT,
                name VARCHAR(100) NOT NULL,
                cover_color VARCHAR(20) DEFAULT '#C8D898',
                art_style VARCHAR(50) DEFAULT 'linen',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
            )
        """)
        print("- Created 'collections' table (or it already exists).")
        
        # 2. Add collection_id to journal_entries if it doesn't exist
        cursor.execute("DESCRIBE journal_entries")
        cols = [c[0] for c in cursor.fetchall()]
        
        if 'collection_id' not in cols:
            cursor.execute("ALTER TABLE journal_entries ADD COLUMN collection_id INT")
            cursor.execute("ALTER TABLE journal_entries ADD CONSTRAINT fk_collection FOREIGN KEY (collection_id) REFERENCES collections(id) ON DELETE SET NULL")
            print("- Added 'collection_id' to 'journal_entries'.")
        else:
            print("- 'collection_id' already exists in 'journal_entries'.")
            
        conn.commit()
        conn.close()
        print("\nMigration successful!")
        
    except Exception as e:
        print(f"\nMigration failed: {e}")

if __name__ == "__main__":
    migrate()
