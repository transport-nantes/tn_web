// Slugifies inputs on the fly
$('#id_slug').on('input', () => {
    var slug = $('#id_slug').val();
    slug = slug.toLowerCase()
               .replace(/^[-_\s]+/g, '')
               .replace(/[-_\s]+/g, '-')
	           .replace(/[^\w-]/g, '');
    $('#id_slug').val(slug);
});
