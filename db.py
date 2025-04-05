import sqlite3
from dotenv import load_dotenv
import os
import pandas as pd

class DB:
    
    path = None
    
    def create_db():
        
        load_dotenv()
        DB.path = os.getenv("DB_PATH")
        conn = sqlite3.connect(DB.path)
        cursor = conn.cursor() 
        # Create words table
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS words (
            word TEXT PRIMARY KEY,
            status INTEGER DEFAULT 1
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
        
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS last_opened_book (
            id INTEGER PRIMARY KEY,
            book_id INTEGER NOT NULL
        );
        """)
        
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS active_theme (
            id INTEGER PRIMARY KEY,
            theme_id INTEGER DEFAULT 0
        );
        """)
        
        cursor.execute("SELECT * FROM active_theme LIMIT 1;")
        result = cursor.fetchone()
        
        if not result:
            cursor.execute(f"""
                INSERT INTO active_theme (theme_id)
                VALUES (0);
            """)
        
        # Commit and close connection
        conn.commit()
        conn.close()
        
        
    def add_word_list(word_list, status=1, replace=False):
        conn = sqlite3.connect(DB.path)
        cursor = conn.cursor()
        if not replace:
            cursor.executemany("INSERT OR IGNORE INTO words (word, status) VALUES (?, ?);", [(word, status) for word in word_list])
        else:
            cursor.executemany("REPLACE INTO words (word, status) VALUES (?, ?);", [(word, status) for word in word_list])
        conn.commit()
        print(f"{len(word_list)} word(s) added successfully.")
        conn.close()
       
    def add_word(word, status=1, replace=False):
        DB.add_word_list([word,], status=status, replace=replace)
        
    def word_exists(word):
        conn = sqlite3.connect(DB.path)
        cursor = conn.cursor()
        cursor.execute("SELECT 1 FROM words WHERE word = ?;", (word,))
        exists = cursor.fetchone() is not None
        conn.close()
        return exists
    
    def get_status_for_words(word_list):
        conn = sqlite3.connect(DB.path)
        cursor = conn.cursor()

        # Build the query with the appropriate number of placeholders
        values = [None] * len(word_list) 
        
        placeholders = ','.join(['?'] * len(word_list))
        query = f"SELECT word, status FROM words WHERE word IN ({placeholders})"

        cursor.execute(query, word_list)
        results = dict(cursor.fetchall())
        conn.close()
        
        # status_list = [results.get(word, None) for word in word_list]
        status_list = ["empty" if word is None else results.get(word, None) for word in word_list]
        return status_list
        
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
            pass
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
        
    def get_book_info(name):
        conn = sqlite3.connect(DB.path)
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM books WHERE name = ?", (name,))
        result = cursor.fetchone()
        conn.close()
        return result
        

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
             
    def find_book_by_id(book_id):
        conn = sqlite3.connect(DB.path)
        cursor = conn.cursor()
        # Query to find the book by its ID
        cursor.execute("SELECT * FROM books WHERE id = ?;", (book_id,))
        book = cursor.fetchone()
        conn.close()
        return book
         
    def set_book_as_reading(book_id):
        conn = sqlite3.connect(DB.path)
        cursor = conn.cursor()
        
        # First, check if there is any existing last opened book
        cursor.execute("SELECT * FROM last_opened_book LIMIT 1;")
        result = cursor.fetchone()
        
        if result:
            # Update the existing record
            cursor.execute("""
                UPDATE last_opened_book
                SET book_id = ? WHERE id = 1;
            """, (book_id,))
        else:
            # Insert a new record as no book has been opened yet
            cursor.execute("""
                INSERT INTO last_opened_book (book_id)
                VALUES (?);
            """, (book_id,))
        
        conn.commit()
        conn.close()
        
    def get_last_opened_book():
        conn = sqlite3.connect(DB.path)
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM last_opened_book LIMIT 1;")
        result = cursor.fetchone()
        conn.close()
        
        if result:
            return result[1]
        else:
            print("No book has been opened yet.")
            return None
        
    def write_chapter_to_db(df, book_id, chapter_id):
        conn = sqlite3.connect(DB.path)
        df.to_sql(f"book_{book_id}_{chapter_id}", conn, if_exists="fail")
        conn.commit()
        conn.close()
        
    def read_chapter_from_db(book_id, chapter_id):
        conn = sqlite3.connect(DB.path)
        df_from_sql = pd.read_sql(f'SELECT * FROM "book_{book_id}_{chapter_id}"', conn)
        conn.close()     
        return df_from_sql
    
    def delete_chapter_from_db(book_id, chapter_id):
        conn = sqlite3.connect(DB.path)
        cursor = conn.cursor()
        cursor.execute(f"DROP TABLE IF EXISTS book_{book_id}_{chapter_id}")
        conn.commit()
        conn.close()
        
    def set_active_theme(id):
        conn = sqlite3.connect(DB.path)
        cursor = conn.cursor()
        
        cursor.execute("SELECT * FROM active_theme LIMIT 1;")
        result = cursor.fetchone()
        
        if result:
            # Update the existing record
            cursor.execute("""
                UPDATE active_theme
                SET theme_id = ? WHERE id = 1;
            """, (id,))
        else:
            cursor.execute("""
                INSERT INTO active_theme (theme_id)
                VALUES (?);
            """, (id,))
        
        conn.commit()
        conn.close()
    
    def get_active_theme():
        conn = sqlite3.connect(DB.path)
        cursor = conn.cursor()
        cursor.execute("SELECT theme_id FROM active_theme ORDER BY id DESC LIMIT 1")
        theme_id = cursor.fetchone()[0]
        conn.close()
        return theme_id
        
        
    
class Dictionary:
    
    dict_path = os.getenv("DICT_PATH")
    articles_path = os.getenv("ARTICLES_PATH")
    
    def get_translation(text):
        conn = sqlite3.connect(Dictionary.dict_path)
        cursor = conn.cursor()
        query = "SELECT trans_list FROM simple_translation WHERE written_rep = ?"
        cursor.execute(query, (text,))
        result = cursor.fetchone()  # Fetch the first result
        conn.close()
        if result:
            return result[0]
        else:
            return None
    
    def get_article(text):
        conn = sqlite3.connect(Dictionary.articles_path)
        cursor = conn.cursor()

        query = "SELECT genus FROM lemma_genus WHERE LOWER(lemma) = LOWER(?)"
        cursor.execute(query, (text,))
        result = cursor.fetchone()  # Fetch the first result
        if(result):
            return f"({",".join(result)})"
        else:
            return None
        conn.close()

    
        
        




        
    
    