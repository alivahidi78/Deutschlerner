function generateButtons() {
    let container = document.getElementById("btn_container");
    // container.innerHTML = ""; // Clear previous buttons
    let button = document.createElement("button");
    button.innerText = "NEW Button";
    button.className = "btn"
    button.onclick = function () {
        alert("You clicked the NEW Button");
    };
    container.appendChild(button);
}