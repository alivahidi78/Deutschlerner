import sqlite3
from dotenv import load_dotenv
import os

class DB:
    
    path = None
    
    def create_db():
        
        load_dotenv()
        DB.path = os.path.join(os.getenv("DB_FOLDER"), "database.db")
        DB.txt_path = os.getenv("TXT_OUTPUT_FOLDER")
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
            chapter_cnt INTEGER DEFAULT 1,
            last_chapter_read INTEGER DEFAULT 1,
            last_index_read INTEGER DEFAULT 0
        );
        """)
        
        DB.refresh_books()

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
        
    def add_book(name, chapter_cnt, last_chapter_read=1, last_index_read=0):
        conn = sqlite3.connect(DB.path)
        cursor = conn.cursor()
        
        # Insert a new book into the books table
        cursor.execute("""
            INSERT INTO books (name, chapter_cnt, last_chapter_read, last_index_read)
            VALUES (?, ?, ?, ?);
        """, (name, chapter_cnt, last_chapter_read, last_index_read))
        
        conn.commit()
        print(f"Book '{name}' added successfully.")
        id = cursor.lastrowid
        conn.close()
        
        return id
    
    def update_book(name, field, new_value):
        conn = sqlite3.connect(DB.path)
        cursor = conn.cursor()
        
        # Validate that the field is a valid column
        valid_fields = ['last_chapter_read', 'last_index_read', 'chapter_cnt']
        if field not in valid_fields:
            raise ValueError(f"Error: Invalid field '{field}'.")
        
        # Update the specific field of the book with the given name
        cursor.execute(f"""
            UPDATE books
            SET {field} = ?
            WHERE name = ?;
        """, (new_value, name))
        
        conn.commit()
        
        if cursor.rowcount > 0:
            print(f"Book '{name}' updated successfully. {field} set to {new_value}.")
        else:
            print(f"Book '{name}' not found.")
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

    def list_books():
        conn = sqlite3.connect(DB.path)
        cursor = conn.cursor()
        
        # Query to fetch all books
        cursor.execute("SELECT * FROM books;")
        books = cursor.fetchall()  # Fetch all rows
        
        conn.close()
        
        # If there are no books, display a message
        if not books:
            print("No books found in the database.")
            return None
        else:
            # Print out the details of each book
            return books
        
    def refresh_books():
        books = DB.list_books()
        if not books:
            return
        for book in books:
            folder = str(book[0])
            folder_path = os.path.join(DB.txt_path ,folder)
            if not os.path.exists(folder_path):
                DB.delete_book(book[1])
            
    
        
        




        
    
    