// Handle word click
const handleWordClick = (word, index) => {
    pywebview.api.word_clicked(word, index).then(response => {
        alert(response);
    });
};

const isPrePunctuation = (str) => {
    const punctuationRegex = /^[“«!.,?;:)}\]$%]+$/;
    return punctuationRegex.test(str);
}

const isPostPunctuation = (str) => {
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
    display_data = JSON.parse(display_data)
    previous_word = null
    display_data.forEach(element => {
        let text = element["word"]
        const wordElement = document.createElement('span');
        if (text.trim() === ""){
            newline = document.createElement("div");
            newline.innerText = "\n\n";
            textContainer.appendChild(newline);
        }
        else if (isPrePunctuation(text)){
            wordElement.className = 'word';
            wordElement.innerText = `${text}`;
            textContainer.appendChild(wordElement)
        } 
        else {
            wordElement.className = 'word';
            // if (highlight[i] == true) {
                //     wordElement.className = 'highlighted_word';
                // }
            if (isPostPunctuation(previous_word))
                wordElement.innerText = text;
            else
                wordElement.innerText = ` ${text}`;
            wordElement.onclick = () => handleWordClick(text, 5);
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
};

