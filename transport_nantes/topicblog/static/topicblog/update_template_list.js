$("#id_item_type").change(function () {
    var url = $("#edition_form").attr("data-template-update-url");  // get the url of the `template_update_url` view
    var content_type = $(this).val();  // get the selected content_type from the dropdown

    $.ajax({                       // initialize an AJAX request
      url: url,                    // set the url of the request (= localhost:8000/tb/ajax/update-template-list/)
      data: {
        'content_type': content_type       // add the content_type to the GET parameters
      },
      success: function (data) {   // `data` is the return of the `update_template_list` view function
        $("#id_template").html(data);  // replace the contents of the template input with the data that came from the server
      }
    });

  });