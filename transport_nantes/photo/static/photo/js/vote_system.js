/**
 * Cast vote when the user has already voted on any photo.
 * This function is called when the user clicks on the vote button
 * It doesn't refresh the page on refresh, it just updates the DOM, contrary to
 * the first vote function
 * @param {boolean} vote_value "upvote"
 * @param {HTMLElement} element "the button that has been pressed to cast vote"
 */
function castVote(vote_value, element) {
    $.ajax({
        url: window.location.href,
        headers: { "X-CSRFToken": getCookie("csrftoken") },
        type: 'post',
        data: {
            vote_value: vote_value,
        },
        mode: 'same-origin',
        success: () => {
            applySelectedVoteStyles(element);
        },
        error: (data) => {
            console.log(data);
        }
    });
}
/**
 * This function is called on the first vote for a user (anon or not)
 * The first vote is using a modal form that is serialized and sent to the server
 * The next votes aren't using a form and a modal for simplicity.
 * It reloads the page on completion to get in the "has voted" state.
 * @param {string} data 
 * @param {HTMLElement} element 
 */
function castFirstVote(data, element) {
    $.ajax({
        url: window.location.href,
        headers: { "X-CSRFToken": getCookie("csrftoken") },
        type: 'post',
        data: data,
        mode: 'same-origin',
        success: () => {
            applySelectedVoteStyles(element);
            $('#first-vote-div').modal('hide');
        },
        error: (data) => {
            console.log(data);
        },
        complete: () => {
            // Reloading the page forces the user to enter in the "has voted"
            // state and can now cast votes without the modal
            window.location.reload();
        }
    });

}


/**
 * 
 * @param {HTMLElement} element Element that is being applied the styles
 */
function applySelectedVoteStyles(element) {
    ['border-blue-light','bg-blue-light','font-blue-dark'].map(
        (className) => {
            element.classList.toggle(className);
        }
    )
}

var upvoteButton = document.getElementById("upvote-button");
var anonVoteForm = document.getElementById("first-vote-form");

// has_voted is directly embedded in the HTML from Django
if (has_voted) {
    upvoteButton.addEventListener("click", function () {
        castVote("upvote", this);
    });
} else {
    // Change the display size of captcha
    $('#id_captcha_1').attr('size', 5);
    anonVoteForm.addEventListener("submit", (e) => {
        e.preventDefault();
        $('#id_vote_value').val('upvote');
        var data = $('#first-vote-form').serialize();
        castFirstVote(data, upvoteButton);
    })
}
