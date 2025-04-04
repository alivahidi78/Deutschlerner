import os
import shutil
from dotenv import load_dotenv
import numpy as np
import ebooklib
from ebooklib import epub
from bs4 import BeautifulSoup
import re
import nlp
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
    chapter_df = None

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
    #TODO
    load_dotenv()
    DATA.title = os.getenv("TEST_TITLE")
    DATA.text = read_txt(os.getenv("TEST_FILE_PATH"))
    DATA.display_data = list(prepare_data(DATA.text))
    DATA.chapter = 1
    return DATA.title, DATA.display_data, 1, 1

def set_book_data(book_data):
    DATA.book_data = book_data
    DATA.book_id = DATA.book_data[0]
    DATA.title = DATA.book_data[1]
    DATA.chapter_count = DATA.book_data[2]
    DATA.chapter = DATA.book_data[3]
    DB.set_book_as_reading(DATA.book_id)
    
def get_chapter():
    if not DATA.book_data:
        try:
            last_id = DB.get_last_opened_book()
            last_book_data = DB.find_book_by_id(last_id)
            if last_book_data:
               set_book_data(last_book_data)
            else:
                return get_test_text()
        except:
            return get_test_text()
        
    df = DB.read_chapter_from_db(DATA.book_id, DATA.chapter)
    DATA.chapter_df = df
    DATA.display_data = prepare_data(df)
    json_data = DATA.display_data.reset_index().to_json(orient="records")
    return DATA.title, json_data, DATA.chapter_count, DATA.chapter

def next_chapter():
    if DATA.chapter < DATA.chapter_count:
        new_chapter = DATA.chapter + 1
        DATA.chapter = new_chapter
        DB.update_book(DATA.title, "last_chapter_read", new_chapter)
    else:
        pass

def prev_chapter():
    if DATA.chapter > 1:
        new_chapter = DATA.chapter - 1
        DATA.chapter = new_chapter
        DB.update_book(DATA.title, "last_chapter_read", new_chapter)
    else:
        pass
    
def prepare_data(df):        
    #TODO do not highlight words that are not words (numbers etc)
    # l_check = DB.check_word_list(df["lemma"].tolist())
    # v_check = DB.check_word_list(df["variation"].tolist())
    # highlight = [2 if (b1 and b2) else 1 if (b1 or b2) else 0 
    # for b1, b2 in zip(list1, list2)]

    lem_status_list = DB.get_status_for_words(list(df["lemma"]))
    var_status_list = DB.get_status_for_words(list(df["variation"]))
    highlight = []
    for v1, v2 in zip(lem_status_list, var_status_list):
        if v1 is None and v2 is None:
            highlight.append("new")
        elif (v1 == 0 and v2 == 0) or (v1 is None and v2 == 0) or (v2 is None and v1 == 0) or (v2 == 1 and v1 is None):
            highlight.append("unknown")
        elif (v1 == 1 and v2 == 0) or (v1 == 0 and v2 == 1):
            highlight.append("half")
        elif (v1 == 1 and v2 == 1) or (v1 == 1 and v2 is None):
            highlight.append("known")
        else:
            raise ValueError("Critical Error W3")

    df["highlight"] = highlight
    # highlight = df[["word", "highlight"]] TODO fix
    highlight = df
    return highlight

def epub2txt(epub_object, book_id):
    # Load EPUB file
    # Extract text from the EPUB
    text = ""
    chapter_counter = 1
    for item in epub_object.get_items():
        if item.get_type() == ebooklib.ITEM_DOCUMENT:
            content = item.get_body_content().decode('utf-8')
            soup = BeautifulSoup(content, 'html.parser')
            paragraphs = [re.sub(r'\s+', ' ', p.get_text(strip=True)) for p in soup.find_all('p')]
            text = '\n\n'.join(paragraphs).strip()
            if not text:
                continue
            print(f"importing chapter {chapter_counter}...")
            data = nlp.preprocess(text)
            DB.write_chapter_to_db(data, book_id, chapter_counter)
            chapter_counter += 1
    return chapter_counter - 1


def import_epub(path):
    load_dotenv()
    epub_book = epub.read_epub(path)
    title = epub_book.title
    id = DB.add_book(title, 1)
    try:
        book_id = str(id)
        chapter_cnt = epub2txt(epub_book, book_id)
        DB.update_book(title, "chapter_cnt", chapter_cnt)
    except Exception as e:
        DB.delete_book(title)
        raise e
    

def import_txt(path):
    load_dotenv()
    # target_path = os.getenv("TXT_OUTPUT_FOLDER")
    file_name = os.path.basename(path)
    id = DB.add_book(file_name, 1)
    try:
        text = read_txt(path)
        data = nlp.preprocess(text)
        book_id = str(id)
        DB.write_chapter_to_db(data, book_id, 1)
    except Exception as e:
        DB.delete_book(file_name)
        raise e
    
def get_book_list():
    return DB.list_books()

def get_word_info(index):
    lemma = DATA.chapter_df.loc[index, "lemma"]
    variation = DATA.chapter_df.loc[index, "variation"]
    word = DATA.chapter_df.loc[index, "word"]
    return word, lemma, variation
    
def save_ignored_words():
    df = DATA.display_data
    #TODO save variations as well 
    filtered_values = set(df.loc[(df["highlight"]) == "new", 'lemma'])
    DB.add_word_list(list(filtered_values))
    