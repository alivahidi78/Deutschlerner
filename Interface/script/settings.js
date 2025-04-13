function mainMenu() {
    pywebview.api.load_page("main.html");
}

function resetWords() {
    showOverlay();
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

function importDictCC(){
    showWaitOverlay();
    pywebview.api.import_dict_cc().then(response => {
        if (response)
            alert("Dictionary successfully imported!\nRestart the app to use offline dictionary.");
    }).catch(error => {
        alert(`Error: ${error}`);
    }).finally(() => {
        hideWaitOverlay();
    });
}

function setTheme(theme) {
    document.getElementById('theme-link').href = theme + '.css';
}

function showWaitOverlay() {
    document.getElementById("wait-overlay").style.display = "flex";
}

function hideWaitOverlay() {
    document.getElementById("wait-overlay").style.display = "none";
}

function showOverlay() {
    document.getElementById("overlay").style.display = "flex";
}

function hideOverlay() {
    document.getElementById("overlay").style.display = "none";
}

function confirmAction() {
    pywebview.api.reset_words().catch(error => {
        alert(`Error: ${error}`);
    }).finally(() => {
        hideOverlay();
    })
}

function cancelAction() {
    hideOverlay();
}

window.hideSettingsOverlay = hideOverlay
