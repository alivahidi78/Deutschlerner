import webview
import os
import utils
from api import API
import sqlite3
from db import DB, Dictionary

if __name__=="__main__":
    api = API()
    DB.initialize_db()
    Dictionary.initialize_dictionary()
    utils.DATA.window = webview.create_window("Deutschlerner", url=os.path.join("interface", "main.html"), js_api=api, min_size=(800,600))
    utils.DATA.current_page = "main.html"
    loading_js = utils.get_loading_js()
    webview.start(func = lambda : utils.DATA.window.evaluate_js(loading_js))
