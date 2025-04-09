function setTheme(theme) {
    document.getElementById('theme-link').href = theme + '.css';
}

pywebview.api.get_theme().then(response => {
    setTheme(`style/${response}`)
}).catch(error => {
    alert(`Error: ${error}`);
});

pywebview.api.get_current_page().then(response => {
    switch (response) {
        case "book.html":
            window.updateText();
            break;
        case "book-list.html":
            window.hideListOverlay();
            window.updateBookList();
            break;
        case "settings.html":
            window.hideSettingsOverlay();
            break;
        default:
            break;
    }
}).catch(error => {
    alert(`Error: ${error}`);
});