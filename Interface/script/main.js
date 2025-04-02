function continueReading(){
    pywebview.api.load_page("book.html");
}

function listBooks(){
    pywebview.api.load_page("book-list.html");
}

function importTxt(){
    pywebview.api.open_file("Text files", "*.txt").then(response => {

    });
}

function importEpub(){
    pywebview.api.open_file("Epub files", "*.epub").then(response => {

    });
}