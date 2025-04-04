// Handle word click
let word_index = -1;

const handleWordClick = (word, index) => {
    word_index = index
    const textarea = document.getElementById('search');
    pywebview.api.word_clicked(word, index).then(response => {
        let lemma = response[1]
        let variation = response[2]
        if (variation)
            textarea.value = variation
        else
            textarea.value = lemma
    });
};

const saveWord = () => {
    const textarea = document.getElementById('search');
    word = textarea.value;
    pywebview.api.save_word(word_index, word).then(response => {
        if(!response)
            alert(response);
        updateText();
    });
}

const saveWordUnknown = () => {
    const textarea = document.getElementById('search');
    word = textarea.value;
    pywebview.api.save_word_unknown(word_index, word).then(response => {
        if(!response)
            alert(response);
        updateText();
    });
}


const isRightPunctuation = (str) => {
    const punctuationRegex = /^[“«!.,?;:)}\]$%]+$/;
    return punctuationRegex.test(str);
}

const isLeftPunctuation = (str) => {
    const punctuationRegex = /^[„»({[]+$/;
    return punctuationRegex.test(str);
}

const isAmbPunctuation = (str) => {
    const punctuationRegex = /^['"-<>@#^&*|\\\/=+_`~]+$/;
    return punctuationRegex.test(str);
}

const displayText = (display_data) => {
    const textContainer = document.getElementById('text');
    textContainer.innerHTML = ''; // Clear previous content
    previous_word = null
    display_data = JSON.parse(display_data)
    display_data.forEach(element => {
        let index = element["index"]
        let text = element["word"]
        let highlight = element["highlight"]
        const wordElement = document.createElement('span');
        if (text.trim() === "") {
            newline = document.createElement("div");
            newline.innerText = "\n";
            textContainer.appendChild(newline);
        }
        else if (isRightPunctuation(text)) {
            wordElement.className = 'word';
            wordElement.innerText = `${text}`;
            textContainer.appendChild(wordElement)
        }
        else {
            if (highlight == "new")
                wordElement.className = 'new_word';
            else if (highlight == "known")
                wordElement.className = 'known_word';
            else if (highlight == "half")
                wordElement.className = 'half_known_word';            
            else if (highlight == "unknown")
                wordElement.className = 'unknown_word';

            if (isLeftPunctuation(previous_word))
                wordElement.innerText = text;
            else
                wordElement.innerText = ` ${text}`;

            wordElement.onclick = () => handleWordClick(text, index);
            textContainer.appendChild(wordElement)
        }
        previous_word = text
    });
};

function updateText() {
    pywebview.api.get_chapter().then(response => {
        document.getElementById('title').innerHTML = response[0];
        document.getElementById('page_num').innerHTML = response[1] + '/' + response[2];
        displayText(response[3]);
    });
}

function requestPrev() {
    pywebview.api.request_prev().then(response => {
        updateText();
    });
}

function requestNext() {
    pywebview.api.request_next().then(response => {
        updateText();
    });
}


function mainMenu() {
    pywebview.api.load_page("main.html");
}

function bookList() {
    pywebview.api.load_page("book-list.html");
}

window.onload = function () {
    // Wait for a brief moment before calling the function
    setTimeout(function () {
        updateText();
    }, 200);

    setInterval(updateText, 30000);
};
