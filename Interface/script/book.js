function requestPrev() {
    pywebview.api.request_prev().then(response => {
        alert(response);
    });
}

function requestNext() {
    pywebview.api.request_next().then(response => {
        alert(response);
    });
}

// Handle word click
const handleWordClick = (word, index) => {
    pywebview.api.word_clicked(word, index).then(response => {
        alert(response);
    });
};

const displayText = (display_data) => {
    // TODO better structure
    words = display_data[0]
    index = display_data[1]
    highlight = display_data[2]
    const textContainer = document.getElementById('text');
    textContainer.innerHTML = ''; // Clear previous content

    for (let i = 0; i < words.length; i++) {
        const wordElement = document.createElement('span');
        if (highlight[i] == true) {
            wordElement.className = 'highlighted_word';
        } else {
            wordElement.className = 'word';
        }
        wordElement.innerText = words[i];
        wordElement.onclick = () => handleWordClick(words[i], index[i]);
        if (words[i] == '\n'){
            newline = document.createElement("div");
            newline.innerText = "\n";
            textContainer.appendChild(newline);
        }
        textContainer.appendChild(wordElement)
    };
};

function updateText() {
    pywebview.api.get_text().then(response => {
        document.getElementById('title').innerHTML = response[0];
        document.getElementById('page_num').innerHTML = response[1] + '/' + response[2]
        displayText(response[3])
    });
}

function mainMenu() {
    pywebview.api.load_page("main.html");
}

window.onload = function () {
    // Wait for a brief moment before calling the function
    setTimeout(function () {
        updateText();
    }, 200);
};

