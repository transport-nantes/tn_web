var usernameField = document.getElementById("mobilito-username");
var editUsernameInputField = document.getElementById("mobilito-username-input");
var editBtn = document.getElementById("mobilito-username-edit-btn");
var editForm = document.getElementById("mobilito-username-edit-form");
var cancelBtn = document.getElementById("mobilito-username-cancel-btn");

editBtn.addEventListener("click", function() {
    usernameField.classList.add("d-none");
    editForm.classList.remove("d-none");
    editForm.classList.add("d-flex");
    editUsernameInputField.focus();
});
cancelBtn.addEventListener("click", function() {
    usernameField.classList.remove("d-none");
    editForm.classList.remove("d-flex");
    editForm.classList.add("d-none");
});
