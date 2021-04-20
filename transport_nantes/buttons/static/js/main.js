$(document).ready(function(){

    $(".btn").click(function(){
            $.ajax({
                url: '',
                type: 'get', 
                data: {
                    button_text: $(this).text()
                }, 
                success: function(response){
                    $("A_value").text(response.button_A)
                }
            });
    });
});