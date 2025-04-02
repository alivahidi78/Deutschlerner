import tkinter as tk
from tkinter import filedialog
import utils
import os

class API:
    def open_file(self, typename, type):
        root = tk.Tk()
        root.withdraw()  # Hide the Tkinter root window
        file_path = filedialog.askopenfilename(filetypes=[(typename, type)])
        # if file_path:
        #     with open(file_path, "r", encoding="utf-8") as file:
        #         content = file.read()
        #     return {"name": file_path, "content": content[:500]}  # Limit content for display
        return None

    def load_page(self, page):
        utils.DATA.window.load_url(os.path.join("interface", page))

    def get_text(self):
        title, display_data = utils.get_text()
        page = 1
        outof = 2
        return title, page, outof, display_data

    def word_clicked(self, word, index):
        print(f"{index}: {word}")
        return f"{index}: {word}"
    
    def request_prev(self):
        print(f"Previous page requested")
        return f"Previous page requested"
    
    def request_next(self):
        print(f"Next page requested")
        return f"Next page requested"
