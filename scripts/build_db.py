import sqlite3
import json

def create_kb_database(db_path):
    """
    Creates a new SQLite database with a 'knowledge' table.
    """
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS knowledge (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        unit_name TEXT NOT NULL,
        content TEXT NOT NULL,
        source_file TEXT,
        difficulty TEXT,
        learning_objectives TEXT,
        prerequisites TEXT
    )
    ''')
    conn.commit()
    conn.close()
    print(f"Database created at {db_path}")

def load_json_to_sqlite(json_path, db_path):
    """
    Loads tagged data from a JSON file into the SQLite database.
    """
    with open(json_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    for chunk in data:
        objectives = ",".join(chunk['metadata']['learning_objectives'])
        prerequisites = ",".join(chunk['metadata']['prerequisites'])
        cursor.execute('''
        INSERT INTO knowledge (unit_name, content, source_file, difficulty, learning_objectives, prerequisites)
        VALUES (?, ?, ?, ?, ?, ?)
        ''', (
            chunk['unit_name'],
            chunk['content'],
            chunk['source_file'],
            chunk['metadata']['difficulty'],
            objectives,
            prerequisites
        ))
    conn.commit()
    conn.close()
    print(f"Successfully loaded {len(data)} chunks into the database.")

if __name__ == "__main__":
    JSON_KB_PATH = 'tagged_knowledge_base.json'  # <-- UPDATE IF NEEDED
    SQLITE_DB_PATH = 'curriculum_kb.db'          # <-- UPDATE IF NEEDED
    create_kb_database(SQLITE_DB_PATH)
    load_json_to_sqlite(JSON_KB_PATH, SQLITE_DB_PATH)
