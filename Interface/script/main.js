function continueReading(){
    pywebview.api.load_page("book.html");
}

function listBooks(){
    pywebview.api.load_page("book-list.html");
}

function importTxt(){
    pywebview.api.open_txt().then(response => {
        alert(response)
    }).catch(error => {
        alert(`Error: ${error}`);
    });
}

function importEpub(){
    pywebview.api.open_epub().then(response => {
        alert(response)
    }).catch(error => {
        alert(`Error: ${error}`);
    });
}