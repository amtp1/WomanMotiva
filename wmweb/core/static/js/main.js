function redirect_to_main_page(){
    window.location.replace("/");
}

function redirect_to_surgeons_page(){
    window.location.replace("surgeons");
}

function redirect_to_cities_page(){
    window.location.replace("cities");
}

function redirect_to_questions_page(){
    window.location.replace("questions");
}

$(document).ready(function () {
    $('#dtBasicExample').DataTable();
    $('.dataTables_length').addClass('bs-select');
});

function delete_profile(id){
    var data = new FormData(); // Init new FormData object.
    data.append("id", id); // Add id in the FormData object.
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
                ids_string = "";
                if (data["response"]==true){
                    var surgeon_card = document.getElementById(`card_${id}`);
                    surgeon_card.remove();
                }else if (data["response"]==false){
                    var deals = data["deals"];
                    $.cookie("delete_profile_id", id);
                    deals.forEach(element => {
                        ids_string += `${element}, `;
                    });
                    var delete_profile_modal = $('#DeleteProfile')
                    delete_profile_modal.find("h6").text("Удаление профиля приведет к удалению зависимых записей.\n"+`Идентификаторы записей: ${ids_string}`);
                    delete_profile_modal.modal("show");
                }
            }
        );
    });
}

function delete_city(id){
    var data = new FormData(); // Init new FormData object.
    data.append("id", id); // Add id in the FormData object.
    fetch("del_city/", {
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
                    redirect_to_cities_page();
                }
            }
        );
    });
}

function delete_question(id){
    var data = new FormData(); // Init new FormData object.
    data.append("id", id); // Add id in the FormData object.
    fetch("del_question/", {
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
                    redirect_to_questions_page();
                }
            }
        );
    });
}

function edit_profile(id, name, city, wa_phone, instagram_link){
    $.cookie("edit_surgeon_id", id);
    var edit_profile_modal = $('#EditProfile')
    edit_profile_modal.id = id;
    edit_profile_modal.find('.modal-title').text(`Изменить профиль #${id}`);
    edit_profile_modal.find('.name').val(name);
    edit_profile_modal.find('.city').val(city);
    edit_profile_modal.find('.wa_phone').val(wa_phone);
    if (instagram_link != 'None'){
        edit_profile_modal.find('.instagram_link').val(instagram_link);
    };
    edit_profile_modal.modal("show");
}