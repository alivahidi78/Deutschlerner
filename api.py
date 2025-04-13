import utils
import os
import webview
import traceback
from db import DB, Dictionary


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
        paths = self.open_files(("Text files (*.txt)",))
        if paths is None:
            return False 
        for p in paths:
            utils.import_txt(p)
        if utils.DATA.cancel_import:
            return False
        return True
    
    def open_epub(self):
        paths = self.open_files(("Epub files (*.epub)",))
        if paths is None:
            return False 
        for p in paths:
            utils.import_epub(p)
        if utils.DATA.cancel_import:
            return False
        return True

    def load_page(self, page):
        utils.DATA.window.load_url(os.path.join("interface", page))
        utils.DATA.current_page = page
        loading_code = utils.get_loading_js()
        utils.DATA.window.evaluate_js(loading_code)
        
    def get_current_page(self):
        return utils.DATA.current_page

    def get_chapter(self):
        return utils.get_chapter()
    
    def set_book_data(self, book_data):
        utils.set_book_data(book_data)

    def word_clicked(self, index, word):
        print(f"{index}: {word}")
        w, lemma, variation = utils.get_word_info(index)
        assert word == w
        if(variation is None and not DB.word_exists(lemma)):
            self.save_word_unknown(index, lemma)
        if(variation is not None and not DB.word_exists(variation)):
            self.save_word_unknown(index, variation)
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
        
    def forget_word(self, index, word):
        try:
            DB.delete_word(word)
            return True
        except Exception as e:
            raise e
    
    def dictionary_exists(self):
        return Dictionary.dict_exists
        
    def google_translate(self, index, word):
        return utils.translate_google(word)
        
    def translate(self, index, word):
        return utils.translate(word)
    
    def request_prev(self):
        utils.prev_chapter()
        return f"Previous page requested"
    
    def request_next(self):
        utils.next_chapter()
        return f"Next page requested"
    
    def save_ignored_words(self):
        utils.save_ignored_words()
    
    def delete_book(self, data):
        return utils.delete_book(data[1])
    
    def reset_words(self):
        return DB.reset_words()
    
    def get_theme(self):
        active_theme = DB.get_active_theme()
        if(active_theme == 0): #TODO
            return "default-light"
        else:
            return "default-dark"
    
    def change_theme(self, option):
        DB.set_active_theme(option)

    def cancel_import(self):
        utils.DATA.cancel_import = True
        
    def import_dict_cc(self):
        paths = self.open_files(("Text files (*.txt)",))
        
        if paths is None:
            return False 
        for p in paths:
            utils.import_dict_cc(p)
        if utils.DATA.cancel_import:
            return False
        return True