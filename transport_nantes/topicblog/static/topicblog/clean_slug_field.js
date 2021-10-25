// Slugifies inputs on the fly
$('#id_slug').on('input', () => {
    var slug = $('#id_slug').val();
    slug = slug.toLowerCase()
               .replace(/ /g,'-')
               .replace(/[-]+/g, '-')
               .replace(/[^\w-]+/g,'')
               .replace("_", "-");
    $('#id_slug').val(slug);
});
