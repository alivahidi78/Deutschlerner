import sqlite3
from dotenv import load_dotenv
import os

class DB:
    
    path = None
    
    def create_db():
        load_dotenv()
        DB.path = os.path.join(os.getenv("DB_FOLDER"), "database.db")
        conn = sqlite3.connect(DB.path)
        cursor = conn.cursor() 
        # Create words table
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS words (
            word TEXT PRIMARY KEY
        );
        """)
        
        # Create books table
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS books (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT UNIQUE NOT NULL,
            directory TEXT NOT NULL,
            chapter_cnt INTEGER DEFAULT 0,
            last_chapter_read INTEGER DEFAULT 0,
            last_index_read INTEGER DEFAULT 0
        );
        """)

        # Commit and close connection
        conn.commit()
        conn.close()
        
    def add_word(word):
        conn = sqlite3.connect(DB.path)
        cursor = conn.cursor()
        try:
            cursor.execute("INSERT INTO words (word) VALUES (?);", (word,))
            conn.commit()
            print(f"Word '{word}' added successfully.")
        except sqlite3.IntegrityError:
            print(f"Word '{word}' already exists.")
        conn.close()
        
    def word_exists(word):
        conn = sqlite3.connect(DB.path)
        cursor = conn.cursor()
        cursor.execute("SELECT 1 FROM words WHERE word = ?;", (word,))
        exists = cursor.fetchone() is not None
        conn.close()
        return exists
    
    def check_word_list(word_list):
        conn = sqlite3.connect(DB.path)
        cursor = conn.cursor()
        
        # Create a dictionary to store results
        word_existence = {word: False for word in word_list}  # Default all to 0

        # Query database for words that exist
        query = f"SELECT word FROM words WHERE word IN ({','.join(['?']*len(word_list))})"
        cursor.execute(query, word_list)
        
        # Mark words that exist as 1
        for (word,) in cursor.fetchall():
            word_existence[word] = True

        conn.close()
        
        # Return list of 1s and 0s in the same order as input
        return [word_existence[word] for word in word_list]
    
    def delete_word(word):
        conn = sqlite3.connect(DB.path)
        cursor = conn.cursor()
        
        cursor.execute("DELETE FROM words WHERE word = ?;", (word,))
        conn.commit()
        
        if cursor.rowcount > 0:
            print(f"Word '{word}' deleted successfully.")
        else:
            print(f"Word '{word}' not found.")
        
        conn.close()
        
    def delete_book(name):
        conn = sqlite3.connect(DB.path)
        cursor = conn.cursor()
        
        cursor.execute("DELETE FROM books WHERE name = ?;", (name,))
        conn.commit()
        
        if cursor.rowcount > 0:
            print(f"Book '{name}' deleted successfully.")
        else:
            print(f"Book '{name}' not found.")
        
        conn.close()



        
    
    