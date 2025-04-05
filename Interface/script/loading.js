function setTheme(theme) {
    document.getElementById('theme-link').href = theme + '.css';
}

pywebview.api.get_theme().then(response => {
    setTheme(`style/${response}`)
}).catch(error => {
    alert(`Error: ${error}`);
});

