import utils
import os
import webview
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
        return f"{index}: {word}"
    
    def request_prev(self):
        utils.prev_chapter()
        return f"Previous page requested"
    
    def request_next(self):
        utils.next_chapter()
        return f"Next page requested"
