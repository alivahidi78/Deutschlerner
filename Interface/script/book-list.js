let book_to_delete = null

function generateButton(text, onclick, del) {
    let container = document.getElementById("btn_container");
    let book_btn = document.createElement("button");
    book_btn.innerText = text;
    book_btn.className = "book_btn";
    book_btn.onclick = onclick;
    container.appendChild(book_btn);

    let del_btn = document.createElement("button");
    del_btn.innerText = "Delete";
    del_btn.className = "delete_btn";
    del_btn.onclick = del
    container.append(del_btn)
}

function mainMenu() {
    pywebview.api.load_page("main.html");
}

function updateList() {
    let container = document.getElementById("btn_container");
    container.innerHTML = "";
    pywebview.api.get_book_list().then(response => {
        if(!response){
            container.innerHTML = "<i>No books imported yet!<i/>";
            return;
        }
        response.forEach(element => {
            let onclick = function () {
                pywebview.api.set_book_data(element).then(response => {
                    pywebview.api.load_page("book.html");
                });
            };
            let del = function () {
                book_to_delete = element;
                document.getElementById("book_name").innerHTML = book_to_delete[1];
                showOverlay();
            }
            generateButton(element[1], onclick, del);
        })
    }).catch(error => {
        alert(`Error: ${error}`);
    });
}

function showOverlay() {
    document.getElementById("overlay").style.display = "flex";
}

function hideOverlay() {
    document.getElementById("overlay").style.display = "none";
}

function confirmAction() {
    pywebview.api.delete_book(book_to_delete).catch(error => {
        alert(`Error: ${error}`);
    }).finally(() => {
        hideOverlay();
        book_to_delete = null;
        updateList();
    })
}

function cancelAction() {
    book_to_delete = null
    hideOverlay();
}

window.hideListOverlay = hideOverlay
window.updateBookList = updateList
