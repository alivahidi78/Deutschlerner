import os
import shutil
from dotenv import load_dotenv
import numpy as np
import pandas as pd
import ebooklib
from ebooklib import epub
from bs4 import BeautifulSoup
import re
import text_processing
from db import DB, Dictionary
import sys
import sqlite3

class DATA:
    current_page = None
    window = None
    text = None
    title = None
    processed_data = None
    book_data = None
    chapter = -1
    chapter_count = -1
    book_id = -1
    last_index = 0
    chapter_df = None
    cancel_import = False

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

def set_book_data(book_data):
    DATA.book_data = book_data
    DATA.book_id = DATA.book_data[0]
    DATA.title = DATA.book_data[1]
    DATA.chapter_count = DATA.book_data[2]
    DATA.chapter = DATA.book_data[3]
    DB.set_last_opened_book(DATA.book_id)
    
def get_sample_chapter_df():
    load_dotenv(resource_path(".env"))
    title = os.getenv("TEST_TITLE")
    set_book_data(["x", title, "x", "x"])
    df = DB.read_chapter_from_db("x", "x")
    return df    
    
def get_chapter():
    if not DATA.book_data:
        try:
            last_id = DB.get_last_opened_book()
            last_book_data = DB.find_book_by_id(last_id)
            if last_book_data:
                set_book_data(last_book_data)
                DATA.chapter_df = DB.read_chapter_from_db(DATA.book_id, DATA.chapter)
            else:
                DATA.chapter_df = get_sample_chapter_df()
        except:
            DATA.chapter_df = get_sample_chapter_df()
    else:
        DATA.chapter_df = DB.read_chapter_from_db(DATA.book_id, DATA.chapter)
    DATA.processed_data = prepare_data(DATA.chapter_df)    
    highlighted = DATA.processed_data[["word", "highlight"]]
    json_data = highlighted.reset_index().to_json(orient="records")
    
    prev_permitted = isinstance(DATA.chapter, int) and DATA.chapter > 1
    next_permitted = isinstance(DATA.chapter, int) and DATA.chapter < DATA.chapter_count
    response = [DATA.title, json_data, DATA.chapter_count, DATA.chapter, Dictionary.dict_exists, prev_permitted, next_permitted]
    
    return response

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
    pos = df["pos"].tolist()
    lem_status_list = DB.get_status_for_words(list(df["lemma"]))
    var_status_list = DB.get_status_for_words(list(df["variation"]))
    mapping = {
        "empty": "empty",
        None: "new",
        0: "unknown",
        1: "known"
    }
    df["h_lem"] = [mapping.get(item, item) for item in lem_status_list]
    df["h_var"] = [mapping.get(item, item) for item in var_status_list]
    highlight = []
    for pos, lem, var in zip(pos, lem_status_list, var_status_list):
        if (pos == "NUM" or pos == "PUNCT"):
            highlight.append("known")
        elif (var == "empty" and lem is None) or (var is None):
            highlight.append("new")
        elif (var == "empty" and lem == 1) or (var == 1):
            highlight.append("known")
        elif (var == 0 and lem == 1):
            highlight.append("half")
        elif (var == "empty" and lem == 0) or (var == 0):
            highlight.append("unknown")
        else:
            raise ValueError("Unexpected datapoint")
    df["highlight"] = highlight
    return df

def epub2txt(epub_object, book_id):
    # Load EPUB file
    # Extract text from the EPUB
    text = ""
    chapter_counter = 1
    for item in epub_object.get_items():
        if(DATA.cancel_import):
            return chapter_counter - 1
        if item.get_type() == ebooklib.ITEM_DOCUMENT:
            content = item.get_body_content().decode('utf-8')
            soup = BeautifulSoup(content, 'html.parser')
            paragraphs = [re.sub(r'\s+', ' ', p.get_text(strip=True)) for p in soup.find_all('p')]
            text = '\n\n'.join(paragraphs).strip()
            if not text:
                continue
            DATA.window.evaluate_js(f"setChapter({chapter_counter});")
            print(f"importing chapter {chapter_counter}...")
            data = text_processing.preprocess(text)
            DB.write_chapter_to_db(data, book_id, chapter_counter)
            chapter_counter += 1
    return chapter_counter - 1


def import_epub(path):
    DATA.cancel_import = False
    DB.collect_garbage()
    load_dotenv(resource_path(".env"))
    epub_book = epub.read_epub(path)
    title = epub_book.title
    id = DB.add_book(title, 1)
    DATA.window.evaluate_js(f"setBook('{title}');")
    try:
        book_id = str(id)
        chapter_cnt = epub2txt(epub_book, book_id)
        DB.update_book(title, "chapter_cnt", chapter_cnt)
        if(DATA.cancel_import):
            delete_book(title)
        else:
            DB.update_book(title, "fully_imported", 1)
    except Exception as e:
        delete_book(title)
        raise e
    

def import_txt(path):
    DATA.cancel_import = False
    DB.collect_garbage()
    load_dotenv(resource_path(".env"))
    file_name = os.path.basename(path)
    id = DB.add_book(file_name, 1)
    DATA.window.evaluate_js(f"setBook('{file_name}');")
    DATA.window.evaluate_js(f"setChapter(1);")
    try:
        text = read_txt(path)
        data = text_processing.preprocess(text)
        book_id = str(id)
        DB.write_chapter_to_db(data, book_id, 1)
        if(DATA.cancel_import):
            delete_book(file_name)
        else:
            DB.update_book(file_name, "fully_imported", 1)
    except Exception as e:
        delete_book(file_name)
        raise e
    
def get_book_list():
    return DB.list_books()

def delete_book(name):
    info = DB.get_book_info(name)
    id = info[0]
    name = info[1]
    chapter_cnt = info[2]
    for i in range(1, chapter_cnt + 1):
        DB.delete_chapter_from_db(id, i)
    DB.delete_book_desc(name)

def get_word_info(index):
    lemma = DATA.chapter_df.loc[index, "lemma"]
    variation = DATA.chapter_df.loc[index, "variation"]
    word = DATA.chapter_df.loc[index, "word"]
    return word, lemma, variation
    
def save_ignored_words():
    df = DATA.processed_data
    filtered_values = set(df.loc[(df["h_var"] == "empty") & (df["h_lem"] == "new") & (~df["pos"].isin(["NUM", "PUNCT"])), "lemma"])
    filtered_values.update(set(df.loc[(df["h_var"] == "new") & (~df["pos"].isin(["NUM", "PUNCT"])), "variation"]))
    DB.add_word_list(list(filtered_values))
    
def translate_google(text, source_language="de", target_language="en"):
    article = Dictionary.get_article(text)
    try:
        trans = text_processing.translate_google(text, source_language, target_language)
    except Exception as e:
        trans = None
    return [article, trans]

def translate(text):
    article = Dictionary.get_article(text)
    trans = Dictionary.get_translation(text)
    return [article, trans]

def get_loading_js():
    load_dotenv(resource_path(".env"))
    js_path = resource_path(os.getenv("LOADING_JS_PATH"))
    with open(js_path, 'r') as js_file:
        return js_file.read()
    
def import_dict_cc(txt_path):
    load_dotenv("config.txt")
    dict_path = os.getenv("DICT_PATH")
    articles_path = os.getenv("ARTICLES_PATH")
    df = pd.read_csv(txt_path, delimiter="\t", skiprows=9, header=None)
    df["genus"] = df[0].str.extract(r"\{(.*?)\}")
    cleanup_patterns = [r"\(.*?\)", r"\[.*?\]", r"\{.*?\}"]
    for pattern in cleanup_patterns:
        df[0] = df[0].str.replace(pattern, "", regex=True)
    df[0] = df[0].str.strip()
    
    df = df[df[0].notna() & df[0].str.match(r"^[A-Za-zÄäÖöÜüß\-]+$")]
    df = df.reset_index(drop=True)
    df.columns = ["text", "translation", "pos", "desc", "genus"]

    with sqlite3.connect(dict_path) as conn:
        df.to_sql("translation_table", conn, if_exists="replace", index=False)
    
    lemma_df = df[["text", "genus"]].rename(columns={"text": "lemma"})
    lemma_df = lemma_df[lemma_df["genus"].notna()].reset_index(drop=True)

    with sqlite3.connect(articles_path) as conn:
        lemma_df.to_sql("lemma_genus", conn, if_exists="replace", index=False)
    
def resource_path(relative_path):
    try:
        # PyInstaller creates a temp folder and stores path in _MEIPASS
        base_path = sys._MEIPASS
    except AttributeError:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)
    