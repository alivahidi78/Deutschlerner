import utils
import os
import webview
import traceback
from db import DB


class API:
    def get_book_list(self):
        l = utils.get_book_list()
        return l
    
    def open_files(self, file_types):
        file_paths = webview.windows[0].create_file_dialog(
            webview.OPEN_DIALOG,
            file_types=file_types
        )
        if file_paths:
            print("Selected file:", file_paths[0]) 
        return file_paths
    
    def open_txt(self):
        try:
            paths = self.open_files(("Text files (*.txt)",))
            for p in paths:
                utils.import_txt(p)
            return "File imported."
        except Exception as e:
            return f"An error occurred: {e}"
    
    def open_epub(self):
        try:
            paths = self.open_files(("Epub files (*.epub)",))
            for p in paths:
                utils.import_epub(p)
            return "File imported."
        except Exception as e:
            print(traceback.format_exc())
            return f"An error occurred: {e}"

    def load_page(self, page):
        utils.DATA.window.load_url(os.path.join("interface", page))

    def get_chapter(self):
        title, display_data, outof, page = utils.get_chapter()
        return title, page, outof, display_data
    
    def set_book_data(self, book_data):
        utils.set_book_data(book_data)

    def word_clicked(self, word, index):
        print(f"{index}: {word}")
        # utils.DATA.unknown_chapter_words.append(lemma)
        w, lemma, variation = utils.get_word_info(index)
        assert word == w
        return [index, lemma, variation]
    
    def save_word(self, index, word):
        try:
            DB.add_word(word, replace=True)
            return True
        except Exception as e:
            raise e
    
    def save_word_unknown(self, index, word):
        try:
            DB.add_word(word, 0, True)
            return True
        except Exception as e:
            raise e
    
    def request_prev(self):
        utils.prev_chapter()
        return f"Previous page requested"
    
    def request_next(self):
        utils.save_ignored_words()
        utils.next_chapter()
        return f"Next page requested"
