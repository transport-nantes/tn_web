// From django docs
function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            // Does this cookie string begin with the name we want?
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}

const isValidUrl = urlString => {
    try { 
        return Boolean(new URL(urlString)); 
    }
    catch(e){ 
        return false; 
    }
}

$("#id_article_link").on("input", (e) => {
    let UrlIsValid = isValidUrl(e.target.value);
    if (!UrlIsValid) {
        console.log("URL invalid : " + e.target.value);
        return;
    } 
    $.ajax({
        url: '/presse/ajax/fetch-og-data/',
        headers: {"X-CSRFToken": getCookie("csrftoken")},
        type: 'post',
        data: {
            url: $("#id_article_link").val(),
        },
        mode: 'same-origin',
        success: function (data) {
            $("#id_newspaper_name").val(data.newspaper_name);
            $("#id_article_title").val(data.title);
            $("#id_article_summary").val(data.description);
            $("#id_article_publication_date").val(data.publication_date.slice(0, 10));
            $("#id_article_link").prop("readonly", true)
        }
    })
});

$("#edit-link").click(() => {
    $("#id_article_link").prop("readonly", false);
});
