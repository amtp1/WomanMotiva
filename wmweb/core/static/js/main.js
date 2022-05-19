function redirect_to_main_page(){
    window.location.replace("/");
}

function redirect_to_surgeons_page(){
    window.location.replace("surgeons");
}

$(document).ready(function () {
    $('#dtBasicExample').DataTable();
    $('.dataTables_length').addClass('bs-select');
});

function delete_profile(id){
    var data = new FormData(); // Init new FormData object.
    data.append("id", id); // Add mail address in the FormData object.
    fetch("del_profile/", {
        method: "POST",
        body: data,
        contentType: 'application/json',
        headers: {
            "X-Requested-With": "XMLHttpRequest",
            "X-CSRFToken": $.cookie("csrftoken")
        },
    }).then(function(response){
        response.json().then(
            function(data){
                if (data==true){
                    var surgeon_card = document.getElementById(`card_${id}`);
                    surgeon_card.remove();
                }
            }
        );
    });
}