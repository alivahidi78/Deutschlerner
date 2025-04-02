import os
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

def get_text():
    load_dotenv()
    DATA.title = os.getenv("TEST_TITLE")
    DATA.text = read_txt(os.getenv("TEST_FILE_PATH"))
    DATA.display_data = list(pre_process(DATA.text))
    return DATA.title, DATA.display_data

def get_chapter():
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

def epub2txt(epub_path, txt_chapter_folder):
    # Load EPUB file
    book = epub.read_epub(epub_path)
    # Extract text from the EPUB
    text = ""
    chapter_counter = 1
    for item in book.get_items():
        if item.get_type() == ebooklib.ITEM_DOCUMENT:
            content = item.get_body_content().decode('utf-8')
            chapter_filename = os.path.join(txt_chapter_folder, f"Chapter_{chapter_counter}.txt")
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

def import_epub():
    pass
