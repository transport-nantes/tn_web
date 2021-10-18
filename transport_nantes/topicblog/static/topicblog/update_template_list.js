async function update_template_list() {
  // get the url of the `template_update_url` view
  var url = $("#edition_form").attr("data-template-update-url");
  // get the selected content_type from the dropdown
  var content_type = $('#id_content_type').val();

  // If content type is empty, we should avoid calls to server. 
  if (content_type) {
    // initialize an AJAX request
    $.ajax({
        // set the url of the request (= localhost:8000/tb/ajax/update-template-list/)
        url: url,
        data: {
          // add the content_type to the GET parameters
          'content_type': content_type
        },
        // `data` is the return of the `update_template_list` view function
        success: function (data) {
          // replace the contents of the template input with the data that came from the server
          $("#id_template").html(data);
        }
        // Awaits for the AJAX call to finish to call the function `select_first_item`
        // It selects the first item of the dropdown list
      }).then(() => {select_first_item()});
  } else {
    $("#id_template").html("<option value=''>---------</option>");
  }
}

function select_first_item() {
  $('#id_template option[value="1"]').attr('selected', 'selected');
}

$("#id_content_type").change(async () => {
  await update_template_list()
});
