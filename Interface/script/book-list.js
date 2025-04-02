function generateButton(text, onclick) {
    let container = document.getElementById("btn_container");
    let button = document.createElement("button");
    button.innerText = text;
    button.className = "btn";
    button.onclick = onclick;
    container.appendChild(button);
}

function mainMenu() {
    pywebview.api.load_page("main.html");
}

function updateList() {
    let container = document.getElementById("btn_container");
    container.innerHTML = "";
    pywebview.api.get_book_list().then(response => {
        response.forEach(element => {
            let onclick = function() {
                pywebview.api.set_book_data(element).then(response => {
                    pywebview.api.load_page("book.html");
                }); 
            };
            generateButton(element[1], onclick);
        });
    });
}

window.onload = function () {
    // Wait for a brief moment before calling the function
    setTimeout(function () {
        updateList();
    }, 200);
};
