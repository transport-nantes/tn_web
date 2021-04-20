$(document).ready(function(){

    $(".btn").click(function(){
            $.ajax({
                url: '',
                type: 'get', 
                data: {
                    button_text: $(this).text() 
                }, 
                success: function(response){
                    $(".A_value").text("A counter :  " + response.A_value);
                    $(".B_value").text("B counter :  " + response.B_value);
                    $(".C_value").text("C counter :  " + response.C_value);
                    $(".D_value").text("D counter :  " + response.D_value);
                }
            });
    });
});