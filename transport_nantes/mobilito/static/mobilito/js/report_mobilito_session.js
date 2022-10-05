var mobilitoSessionSha1 = JSON.parse($('#mobilito_session_sha1').text());

$("#report-abuse-form").submit((e) => {
    e.preventDefault();
    var serializedData = $("#report-abuse-form").serialize();
    $.ajax({
        url: `/mobilito/ajax/report-session/${mobilitoSessionSha1}/`,
        type: 'POST',
        data: serializedData,
        success: () => {
            $("#report-abuse-div").modal('hide');
            $("#reported").toggleClass('d-none');
            $("#report-abuse").toggleClass('d-none');
            $("#reported").parent().css("pointer-events", "none");
        }
    });
});
