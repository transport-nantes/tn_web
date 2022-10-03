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

async function checkForDuplicate(url) {
    let data = await $.ajax({
        url: '/presse/ajax/check-for-duplicate/',
        type: 'GET',
        headers: { "X-CSRFToken": getCookie('csrftoken') },
        data: {
            'url': url
        },
        mode: 'same-origin',
    })
    return data;
}

$("#id_article_link").on("change", async (e) => {
    let UrlIsValid = isValidUrl(e.target.value);
    if (!UrlIsValid) {
        return;
    } 
    $.ajax({
        url: '/presse/ajax/fetch-og-data/',
        // Because we use CSRF protection, we add CSRF token to headers,
        // so django doesn't prevent us from posting
        // https://docs.djangoproject.com/fr/4.0/ref/csrf/#ajax
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
        }
    })
    let data = await checkForDuplicate(e.target.value);
    console.log(data);
    if (data.is_duplicate) {
        window.location.href = data.edit_url;
    }
});
