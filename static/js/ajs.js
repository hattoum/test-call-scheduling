function refresh(){
    $.ajax(
            {
        type: "GET",
        url: "/",
        contentType: "application/json",
        dataType: 'json',
        success: function(result) {
            location.reload()

    } 
 });
}

$(".delete").click(function(){
    var id = $(this).attr("id");
    console.log("BIND", id)
    $.ajax(
            {
        type: "POST",
        url: "/add",
        contentType: "application/json",
        dataType: 'json',
        data: JSON.stringify({
            "name": id
        }),
        success: function(result) {
            console.log("deleted")
            location.reload()
        },
        error: function(result) {
            console.log("error")
        }

    })
})

// Do refresh() every 10 seconds
setInterval(refresh, 10000);
