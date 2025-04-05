function setTheme(theme) {
    document.getElementById('theme-link').href = theme + '.css';
}

function mainMenu() {
    pywebview.api.load_page("main.html");
}

function changeTheme() {
    var selectedOption = document.getElementById('themeMenu').value;
    pywebview.api.change_theme(selectedOption).then(response => {
        pywebview.api.get_theme().then(response => {
            setTheme(`style/${response}`)
        }).catch(error => {
            alert(`Error: ${error}`);
        });
    }).catch(error => {
        alert(`Error: ${error}`);
    });
}

document.getElementById('actionMenu').selectedIndex = 1
