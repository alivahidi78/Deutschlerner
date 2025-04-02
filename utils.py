import os
import shutil
from dotenv import load_dotenv
import numpy as np
import ebooklib
from ebooklib import epub
from bs4 import BeautifulSoup
import re
from db import DB

class DATA:
    window = None
    text = None
    title = None
    display_data = None
    book_data = None
    chapter = -1
    chapter_count = -1
    book_id = -1
    last_index = 0

def read_txt(path):
    try:
        with open(path, 'r', encoding="utf-8") as file:
            # Read the contents of the file
            content = file.read()
            return content
    except FileNotFoundError:
        print(f"The file at {path} was not found.")
    except IOError:
        print("An error occurred while reading the file.")

def get_test_text():
    load_dotenv()
    DATA.title = os.getenv("TEST_TITLE")
    DATA.text = read_txt(os.getenv("TEST_FILE_PATH"))
    DATA.display_data = list(pre_process(DATA.text))
    DATA.chapter = 1
    return DATA.title, DATA.display_data, 1, 1

def get_chapter():
    load_dotenv()
    if not DATA.book_data:
        return get_test_text()
    DATA.book_id = DATA.book_data[0]
    DATA.title = DATA.book_data[1]
    DATA.chapter_count = DATA.book_data[2]
    if DATA.chapter == -1:
        DATA.chapter = DATA.book_data[3]
    txt_path = os.getenv("TXT_OUTPUT_FOLDER")
    file_path = os.path.join(txt_path, str(DATA.book_id), f"{DATA.chapter}.txt")
    DATA.text = read_txt(file_path)
    DATA.display_data = list(pre_process(DATA.text))
    return DATA.title, DATA.display_data, DATA.chapter_count, DATA.chapter

def next_chapter():
    if DATA.chapter < DATA.chapter_count:
        DATA.chapter+=1
    else:
        pass

def prev_chapter():
    if DATA.chapter > 1:
        DATA.chapter-=1
    else:
        pass
    
def pre_process(text):
    paragraphs = [p.strip() for p in text.split("\n") if p.strip()]
    word_list = np.empty(0)
    index = np.empty(0)
    word_count = 0

    for pa in paragraphs:
        words = [w.strip() for w in pa.split(" ") if w.strip()]
        index = np.append(index, np.arange(word_count, word_count + len(words)))
        word_count = word_count + len(words)
        words.append("\n")
        index = np.append(index, -1)
        word_list = np.append(word_list, words)
        
    #TODO check actual words. these contain random bits of punctuation, etc
    #TODO do not highlight words that are not words (numbers etc)
    highlight = (DB.check_word_list(word_list))
    highlight = [not elem for elem in highlight]
    
    return word_list.tolist(), index.tolist(), highlight

def epub2txt(epub_object, target_folder):
    # Load EPUB file
    # Extract text from the EPUB
    text = ""
    chapter_counter = 1
    for item in epub_object.get_items():
        if item.get_type() == ebooklib.ITEM_DOCUMENT:
            content = item.get_body_content().decode('utf-8')
            chapter_filename = os.path.join(target_folder, f"{chapter_counter}.txt")
            soup = BeautifulSoup(content, 'html.parser')
            paragraphs = [re.sub(r'\s+', ' ', p.get_text(strip=True)) for p in soup.find_all('p')]
            text = '\n\n'.join(paragraphs).strip()
            if not text:
                continue
            with open(chapter_filename, 'w', encoding='utf-8') as f:
                chapter_text = text
                f.write(chapter_text)
                # Increment chapter counter
            chapter_counter += 1
    return chapter_counter - 1


def import_epub(path):
    load_dotenv()
    target_path = os.getenv("TXT_OUTPUT_FOLDER")
    epub_book = epub.read_epub(path)
    title = epub_book.title
    file_name = os.path.basename(path)
    id = DB.add_book(title, 1)
    try:
        folder = str(id)
        folder_path = os.path.join(target_path ,folder)
        if not os.path.exists(folder_path):
            os.makedirs(folder_path)
        chapter_cnt = epub2txt(epub_book, folder_path)
        DB.update_book(title, "chapter_cnt", chapter_cnt)
    except Exception as e:
        DB.delete_book(title)
        raise e
    

def import_txt(path):
    load_dotenv()
    target_path = os.getenv("TXT_OUTPUT_FOLDER")
    file_name = os.path.basename(path)
    id = DB.add_book(file_name, 1)
    try:
        folder = str(id)
        # Create the folder if it doesn't exist
        folder_path = os.path.join(target_path ,folder)
        if not os.path.exists(folder_path):
            os.makedirs(folder_path)
        file_path = os.path.join(folder_path, "1.txt")
        shutil.copy(path, file_path)
    except Exception as e:
        DB.delete_book(file_name)
        raise e
    
def get_book_list():
    return DB.list_books()
    