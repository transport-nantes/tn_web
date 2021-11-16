// Ask the server for slugs that contains the given string
async function get_slug_suggestions(slug) {
    data = await $.ajax({
        url: '/tb/ajax/get-slug-suggestions/',
        data: {
            partial_slug: slug
        },

    })
    return data
}

// When the user types a more than 5 long char slug,
// we ask the server for suggestions.
$("#id_slug").on("input", async function() {
    slug = $(this).val()
    if (slug.length > 5) {
        suggestions = await get_slug_suggestions(slug);
        datalist_html = ""
        for (suggestion of suggestions) {
            datalist_html += "<option value='" + suggestion + "'>"
        }
        $("#slug_list").html(datalist_html)
    }
})
