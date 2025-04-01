import webview
import tkinter as tk
from tkinter import filedialog
import os

class API:
    def open_file(self):
        root = tk.Tk()
        root.withdraw()  # Hide the Tkinter root window
        file_path = filedialog.askopenfilename()  # Open native file dialog
        
        if file_path:
            with open(file_path, "r", encoding="utf-8") as file:
                content = file.read()
            return {"name": file_path, "content": content[:500]}  # Limit content for display
        return None

    def load_page(self, page):
        window.load_url(os.path.join("interface", page))

    def get_text(self):
        title= "Lorem Ipsum"
        text= """Lorem ipsum dolor sit amet, consetetur sadipscing elitr, sed diam nonumy eirmod tempor invidunt ut labore et dolore magna aliquyam erat, sed diam voluptua. At vero eos et accusam et justo duo dolores et ea rebum. Stet clita kasd gubergren, no sea takimata sanctus est Lorem ipsum dolor sit amet. Lorem ipsum dolor sit amet, consetetur sadipscing elitr, sed diam nonumy eirmod tempor invidunt ut labore et dolore magna aliquyam erat, sed diam voluptua. At vero eos et accusam et justo duo dolores et ea rebum. Stet clita kasd gubergren, no sea takimata sanctus est Lorem ipsum dolor sit amet."""
        page= 1
        outof=10
        return title, text, page, outof

    def word_clicked(self, word_position):
        print(f"Word at position {word_position} clicked!")
        return f"Word {word_position} clicked!"

api = API()
window = webview.create_window("Title", url=os.path.join("interface", "bookpage.html"), js_api=api, min_size=(800,600) )

webview.start()
