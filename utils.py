import os
from dotenv import load_dotenv
import numpy as np

class DATA:
    window = None
    text = None
    title = None
    display_data = None

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
    
    

def pre_process(text):
    #TODO delete after database is set up
    test_list = ["kein", "Bett", "Greg"]
    check_highlight = np.vectorize(lambda value : value in test_list)
    paragraphs = [p.strip() for p in text.split("\n") if p.strip()]
    word_list = np.empty(0)
    highlight = np.empty(0)
    index = np.empty(0)
    word_count = 0

    for pa in paragraphs:
        words = [w.strip() for w in pa.split(" ") if w.strip()]
        index = np.append(index, np.arange(word_count, word_count + len(words)))
        word_count = word_count + len(words)
        words.append("\n")
        highlight = np.append(highlight, check_highlight(words))
        index = np.append(index, -1)
        word_list = np.append(word_list, words)
    return word_list.tolist(), index.tolist(), highlight.tolist()
