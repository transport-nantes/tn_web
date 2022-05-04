// Calls server to get a list of all slugs and
// how many of each slug there are.
const MODEL_NAME = JSON.parse(document.getElementById('model_name').textContent);

async function get_slug_dict() {
    data = await $.ajax({
        url: '/tb/ajax/get-slug-dict/',
        data: {
            model_name: MODEL_NAME
        },
    })
    return data;
}

// Get an url from the server that leads to a list
// of all items with the given slug
async function get_url_list(slug) {
    data = await $.ajax({
        url: '/tb/ajax/get-url-list/',
        data: {
            slug: slug,
        },
    })
    return data;
}

$(document).ready(async function () {

    var slug_dict = await get_slug_dict();

    // Create a div in wich we will put the warning
    $("input[id='id_slug']").after('<div class="small" id="slug_warning"></div>');
    // On each change, we check the value of the slug.
    // If it matches with an item of the list of existing slugs, 
    // we display a message with a link to the list of items with the same slug.
    $("input[id='id_slug']").on('input', async function () {
        var slug = $(this).val();
        if (slug in slug_dict){
            var url_list = await get_url_list(slug);

            var message = "<p>Ce slug est partagé par <u><a"
            + " href='" + url_list["url"]+ "'>"
            + slug_dict[slug]

            if (slug_dict[slug] > 1){
                message += " items."
            }
            else{
                message += " item."
            }

            $("#slug_warning").html(message + "</a></u></p>");

        } else {
            $("#slug_warning").html("");
        }
    });
});
