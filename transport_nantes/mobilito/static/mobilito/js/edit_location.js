var locationField = document.getElementById("mobilito-session-location");
var editLocationInputField = document.getElementById("mobilito-session-location-input");
var editBtn = document.getElementById("mobilito-session-edit-btn");
var editForm = document.getElementById("mobilito-session-edit-form");
var cancelBtn = document.getElementById("mobilito-session-cancel-btn");

editBtn.addEventListener("click", function() {
    locationField.classList.add("d-none");
    editForm.classList.remove("d-none");
    editForm.classList.add("d-flex");
    editLocationInputField.focus();
});
cancelBtn.addEventListener("click", function() {
    locationField.classList.remove("d-none");
    editForm.classList.remove("d-flex");
    editForm.classList.add("d-none");
});
