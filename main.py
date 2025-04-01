import webview
import os
import utils
from api import API

if __name__=="__main__":
    api = API()
    utils.DATA.window = webview.create_window("Title", url=os.path.join("interface", "book.html"), js_api=api, min_size=(800,600) )
    webview.start()
