import webview
import os
import utils
from api import API
import sqlite3
from db import *

if __name__=="__main__":
    database = DB()
    api = API()
    utils.DATA.window = webview.create_window("Deutschlerner", url=os.path.join("interface", "book.html"), js_api=api, min_size=(800,600))
    webview.start()
