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

function save_profile(){
    const image = document.getElementById("user_picture").files[0];
    const name = document.getElementsByName("name")[0];
    const city = document.getElementsByName("city")[0];
    const clinic = document.getElementsByName("clinic")[0];
    const wa_phone = document.getElementsByName("wa_phone")[0];
    const instagram_link = document.getElementsByName("instagram_link")[0];

    if (!image){
        alert("Нужно выбрать фотографию для профиля!");
    }else{
        if(!name.value || !city.value || !clinic.value || !wa_phone.value || !instagram_link.value){
            alert("Все поля должны быть заполнены!");
        }else{
            var data = new FormData(); // Init new FormData object.
            data.append("image", image); // Add id in the FormData object.
            data.append("name", name.value); // Add id in the FormData object.
            data.append("city", city.value); // Add id in the FormData object.
            data.append("clinic", clinic.value); // Add id in the FormData object.
            data.append("wa_phone", wa_phone.value); // Add id in the FormData object.
            data.append("instagram_link", instagram_link.value); // Add id in the FormData object.
            fetch("save_profile/", {
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
                        if (data["response"]){
                            redirect_to_surgeons_page();
                        }
                    }
                )})
        }
    }
}

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

function edit_profile(id, name, city, wa_phone, instagram_link, clinic){
    $.cookie("edit_surgeon_id", id);
    var edit_profile_modal = $('#EditProfile')
    edit_profile_modal.id = id;
    edit_profile_modal.find('.modal-title').text(`Изменить профиль #${id}`);
    edit_profile_modal.find('.name').val(name);
    edit_profile_modal.find('.city').val(city);
    edit_profile_modal.find('.clinic').val(clinic);
    edit_profile_modal.find('.wa_phone').val(wa_phone);
    if (instagram_link != 'None'){
        edit_profile_modal.find('.instagram_link').val(instagram_link);
    };
    edit_profile_modal.modal("show");
}

function show_toast(){
    const myToastEl = document.getElementById('myToast');
    myToastEl.addEventListener('show.bs.toast');
}