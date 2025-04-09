import sqlite3
from dotenv import load_dotenv
import os
import pandas as pd
import text_processing
import utils

class DB:
    
    path = None
    
    def initialize_db():
        """ Creates and/or loads user_data database files. Should be executed at program start.
        """
        
        load_dotenv("config.txt")
        load_dotenv(utils.resource_path(".env"))
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
        
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='book_x_x';")
        result = cursor.fetchone()

        if not result:
            sample_text_path = utils.resource_path(os.getenv("TEST_TXT_PATH"))
            sample_text = utils.read_txt(sample_text_path)
            sample_data = text_processing.preprocess(sample_text)
            DB.write_chapter_to_db(sample_data, "x", "x")
        
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
        """Adds a list of words to the user_data database.

        Args:
            word_list (list): list of the words to be saved.
            status (int, optional): status of the word. 1 means it is already known.
                0 means they are being learned. Defaults to 1.
            replace (bool, optional): what happens if any word already exists. True
                would replace and False would ignore the new word. Defaults to False.
        """
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
        """Adds a word to the user_data database.

        Args:
            word (str): word to be saved.
            status (int, optional): status of the word. 1 means it is already known.
                0 means it is being learned. Defaults to 1.
            replace (bool, optional): what happens if the word already exists. True
                would replace and False would ignore the new word. Defaults to False.
        """
        DB.add_word_list([word,], status=status, replace=replace)
        
    def word_exists(word):
        """Returns whether a word already exists in the database.
        """
        conn = sqlite3.connect(DB.path)
        cursor = conn.cursor()
        cursor.execute("SELECT 1 FROM words WHERE word = ?;", (word,))
        exists = cursor.fetchone() is not None
        conn.close()
        return exists
    
    def get_status_for_words(word_list):
        """Given a word list, returns the status of each, or None if a word does not
        exist in the database.
        """
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
        """Removes given word from database.
        """
        conn = sqlite3.connect(DB.path)
        cursor = conn.cursor()
        
        cursor.execute("DELETE FROM words WHERE word = ?;", (word,))
        conn.commit()
        
        if cursor.rowcount > 0:
            print(f"Word '{word}' deleted successfully.")
        else:
            print(f"Word '{word}' not found.")
        
        conn.close()
        
    def reset_words():
        """Removes all words from the database.
        """
        conn = sqlite3.connect(DB.path)
        cursor = conn.cursor()
        cursor.execute("DELETE FROM words")
        conn.commit()
        cursor.execute("VACUUM")
        conn.close()
        
    def add_book(name, chapter_cnt, last_chapter_read=1, last_index_read=0):
        """Adds a book description row to the database.

        Args:
            name (str): title of the book.
            chapter_cnt (int): number of the book's chapters.
            last_chapter_read (int, optional): current chapter. Defaults to 1.
            last_index_read (int, optional): current index. Defaults to 0.

        Returns:
            int: id of the book.
        """        
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
        """updates given field of the book description.
        """        
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
        
    def delete_book_desc(name):
        """Removes a book description from the database.
        """
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
        """Returns a book's description info by its name.
        """
        conn = sqlite3.connect(DB.path)
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM books WHERE name = ?", (name,))
        result = cursor.fetchone()
        conn.close()
        return result
        

    def list_books():
        """Lists all books.
        """
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
             
    def find_book_by_id(book_id):
        """Returns a book's description info by its id.
        """
        conn = sqlite3.connect(DB.path)
        cursor = conn.cursor()
        # Query to find the book by its ID
        cursor.execute("SELECT * FROM books WHERE id = ?;", (book_id,))
        book = cursor.fetchone()
        conn.close()
        return book
         
    def set_last_opened_book(book_id):
        """Set a book as the last opened one.
        """
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
        """Return the id of the last opened book.
        """
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
        """Writes a chapter to the database.

        Args:
            df (dataframe): chapter information in dataframe format.
            book_id (int): id of the book.
            chapter_id (int): id of the chapter.
            replace (bool): if already exists, replace or fail.
        """
        conn = sqlite3.connect(DB.path)
        df.to_sql(f"book_{book_id}_{chapter_id}", conn, if_exists="fail")
        conn.commit()
        conn.close()
        
    def read_chapter_from_db(book_id, chapter_id):
        """Reads a chapter from the database into a dataframe.
        """
        conn = sqlite3.connect(DB.path)
        df_from_sql = pd.read_sql(f'SELECT * FROM "book_{book_id}_{chapter_id}"', conn)
        conn.close()     
        return df_from_sql
    
    def delete_chapter_from_db(book_id, chapter_id):
        """Removes a chapter from the database.
        """
        conn = sqlite3.connect(DB.path)
        cursor = conn.cursor()
        cursor.execute(f"DROP TABLE IF EXISTS book_{book_id}_{chapter_id}")
        conn.commit()
        conn.close()
        
    def set_active_theme(id):
        """Sets the graphical theme.
        """
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
        """Returns the active graphical theme.
        """
        conn = sqlite3.connect(DB.path)
        cursor = conn.cursor()
        cursor.execute("SELECT theme_id FROM active_theme ORDER BY id DESC LIMIT 1")
        theme_id = cursor.fetchone()[0]
        conn.close()
        return theme_id
        
        
    
class Dictionary:
    
    dict_exists = False
    articles_exists = False
    dict_path = None
    articles_path = None
    
    def initialize_dictionary():
        """ Loads the dictionary files. Should be executed at program start.
        """
        load_dotenv("config.txt")
        Dictionary.dict_path = os.getenv("DICT_PATH")
        Dictionary.articles_path = os.getenv("ARTICLES_PATH")
        if(Dictionary.dict_path):
            if os.path.exists(Dictionary.dict_path):
                Dictionary.dict_exists = True
        if(Dictionary.articles_path):
            if os.path.exists(Dictionary.articles_path):
                Dictionary.articles_exists = True
    
    def get_translation(text):
        """Returns translation of given text based on db.

        Args:
            text (str): text to be translated.

        Returns:
            str: concatenation of all translations or `None` if no translation available.
        """
        if (not Dictionary.dict_exists):
            return None
        try:
            conn = sqlite3.connect(Dictionary.dict_path)
            cursor = conn.cursor()
            query = "SELECT translation FROM translation_table WHERE LOWER(text) = LOWER(?)"
            cursor.execute(query, (text,))
            result = cursor.fetchall()  # Fetch the first result
            conn.close()
            if result:
                translation = [row[0] for row in result if row[0]]
                return " | ".join(translation) if translation else None
            else:
                return None
        except Exception as e:
            return f"Error: {e}"
    
    def get_article(text):
        """Returns grammatical gender of given word based on db.

        Args:
            text (str): input word.

        Returns:
            str: letter representing the grammatical gender.
        """
        if (not Dictionary.articles_exists):
            return None
        try: 
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
        except Exception as e:
            return f"Error: {e}"
            

    
        
        




        
    
    