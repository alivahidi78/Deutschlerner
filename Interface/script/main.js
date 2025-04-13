function continueReading() {
    pywebview.api.load_page("book.html");
}

function listBooks() {
    pywebview.api.load_page("book-list.html");
}

function settings() {
    pywebview.api.load_page("settings.html");
}

function showOverlay() {
    document.getElementById("overlay").style.display = "flex";
}

function hideOverlay() {
    document.getElementById("overlay").style.display = "none";
}

function showSupportOverlay() {
    document.getElementById("support-overlay").style.display = "flex";
}

function hideSupportOverlay() {
    document.getElementById("support-overlay").style.display = "none";
}


function importTxt() {
    showOverlay();
    pywebview.api.open_txt().then(response => {
        if (response)
            alert("Book successfully imported!");
    }).catch(error => {
        alert(`Error: ${error}`);
    }).finally(() => {
        hideOverlay();
    });
}

function importEpub() {
    showOverlay();
    pywebview.api.open_epub().then(response => {
        if (response)
            alert("Book successfully imported!");
    }).catch(error => {
        alert(`Error: ${error}`);
    }).finally(() => {
        hideOverlay();
    });
}

function cancelImport() {
    hideOverlay();
    pywebview.api.cancel_import().then(response=>{

    }).catch(error => {
        alert(`Error: ${error}`);
    });
}

function support(){
    showSupportOverlay();
}

function cancelSupport(){
    hideSupportOverlay();
}

function setBook(book) {
    document.getElementById("book_name").innerHTML = book;
}

function setChapter(chapter) {
    document.getElementById("chapter_name").innerHTML = chapter;
}

window.hideMainOverlay = hideOverlay