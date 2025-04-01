// Display the text with each word clickable
const displayText = (text) => {
    const words = text.split(' '); // Split text into words
    const textContainer = document.getElementById('text');
    textContainer.innerHTML = ''; // Clear previous content

    words.forEach((word, index) => {
        const wordElement = document.createElement('span');
        wordElement.className = 'word';
        wordElement.innerText = word;
        wordElement.onclick = () => handleWordClick(index);
        textContainer.appendChild(wordElement);
    });
};

// Handle word click
const handleWordClick = (wordPosition) => {
    pywebview.api.word_clicked(wordPosition).then(response => {
        alert(response); // Show the response from the backend
    });
};

function updateText() {
    pywebview.api.get_text().then(response => {
        displayText(response[1])
        document.getElementById('title').innerHTML = response[0];
        document.getElementById('page_num').innerHTML = response[2] +'/'+response[3]
    });
}

window.onload = function () {
    // Wait for a brief moment before calling the function
    setTimeout(function () {
        updateText();
    }, 200); // delay
};