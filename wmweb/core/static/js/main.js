var surgeon_id = null;

function redirect_to_main_page() {
    window.location.replace("/");
}

function redirect_to_surgeons_page() {
    window.location.replace("surgeons");
}

function redirect_to_cities_page() {
    window.location.replace("cities");
}

function redirect_to_questions_page() {
    window.location.replace("questions");
}

function save_profile() {
    const image = document.getElementById("user_picture").files[0];
    const name = document.getElementsByName("name")[0];
    const city = document.getElementsByName("city")[0];
    const clinic = document.getElementsByName("clinic")[0];
    const wa_phone = document.getElementsByName("wa_phone")[0];
    const address = document.getElementsByName("address")[0];
    const instagram_link = document.getElementsByName("instagram_link")[0];

    if (!image) {
        alert("Нужно выбрать фотографию для профиля!");
    } else {
        if (!name.value || !city.value || !clinic.value || !wa_phone.value || !address.value || !instagram_link.value) {
            alert("Все поля должны быть заполнены!");
        } else {
            var data = new FormData(); // Init new FormData object.
            data.append("image", image); // Add id in the FormData object.
            data.append("name", name.value); // Add id in the FormData object.
            data.append("city", city.value); // Add id in the FormData object.
            data.append("clinic", clinic.value); // Add id in the FormData object.
            data.append("wa_phone", wa_phone.value); // Add id in the FormData object.
            data.append("address", address.value); // Add id in the FormData object.
            data.append("instagram_link", instagram_link.value); // Add id in the FormData object.
            fetch("save_profile/", {
                method: "POST",
                body: data,
                contentType: 'application/json',
                headers: {
                    "X-Requested-With": "XMLHttpRequest",
                    "X-CSRFToken": $.cookie("csrftoken")
                },
            }).then(function (response) {
                response.json().then(
                    function (data) {
                        if (data["response"]) {
                            redirect_to_surgeons_page();
                        }
                    }
                )
            })
        }
    }
}

function delete_profile(id) {
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
    }).then(function (response) {
        response.json().then(
            function (data) {
                ids_string = "";
                if (data["response"] == true) {
                    var surgeon_card = document.getElementById(`card_${id}`);
                    surgeon_card.remove();
                } else if (data["response"] == false) {
                    var deals = data["deals"];
                    $.cookie("delete_profile_id", id);
                    deals.forEach(element => {
                        ids_string += `${element}, `;
                    });
                    var delete_profile_modal = $('#DeleteProfile')
                    delete_profile_modal.find("h6").text("Удаление профиля приведет к удалению зависимых записей.\n" + `Идентификаторы записей: ${ids_string}`);
                    delete_profile_modal.modal("show");
                }
            }
        );
    });
}

function delete_city(id) {
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
    }).then(function (response) {
        response.json().then(
            function (data) {
                if (data == true) {
                    redirect_to_cities_page();
                }
            }
        );
    });
}

function delete_question(id) {
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
    }).then(function (response) {
        response.json().then(
            function (data) {
                if (data == true) {
                    redirect_to_questions_page();
                }
            }
        );
    });
}

function edit_profile_modal(id, name, city, wa_phone, instagram_link, clinic, address) {
    surgeon_id = id;
    //$.cookie("edit_surgeon_id", id);
    var edit_profile_modal = $('#EditProfile')
    edit_profile_modal.id = id;
    edit_profile_modal.find('.modal-title').text(`Изменить профиль #${id}`);
    edit_profile_modal.find('.edit_name').val(name);
    edit_profile_modal.find('.edit_city').val(city);
    edit_profile_modal.find('.edit_clinic').val(clinic);
    edit_profile_modal.find('.edit_wa_phone').val(wa_phone);
    edit_profile_modal.find('.edit_address').val(address);
    if (instagram_link != 'None') {
        edit_profile_modal.find('.edit_instagram_link').val(instagram_link);
    };
    edit_profile_modal.modal("show");
}

function edit_profile() {
    const image = document.getElementById("edit_user_picture").files[0];
    const name = document.getElementsByName("edit_name")[0];
    const city = document.getElementsByName("edit_city")[0];
    const clinic = document.getElementsByName("edit_clinic")[0];
    const wa_phone = document.getElementsByName("edit_wa_phone")[0];
    const address = document.getElementsByName("edit_address")[0];
    const instagram_link = document.getElementsByName("edit_instagram_link")[0];

    if (!image) {
        alert("Нужно выбрать фотографию для профиля!");
    } else {
        if (!name.value || !city.value || !clinic.value || !wa_phone.value || !address.value || !instagram_link.value) {
            alert("Все поля должны быть заполнены!");
        }
        else {
            var data = new FormData(); // Init new FormData object.
            data.append("surgeon_id", surgeon_id); // Add id in the FormData object.
            data.append("image", image); // Add id in the FormData object.
            data.append("name", name.value); // Add id in the FormData object.
            data.append("city", city.value); // Add id in the FormData object.
            data.append("clinic", clinic.value); // Add id in the FormData object.
            data.append("wa_phone", wa_phone.value); // Add id in the FormData object.
            data.append("address", address.value); // Add id in the FormData object.
            data.append("instagram_link", instagram_link.value); // Add id in the FormData object.
            fetch("edit_profile/", {
                method: "POST",
                body: data,
                contentType: 'application/json',
                headers: {
                    "X-Requested-With": "XMLHttpRequest",
                    "X-CSRFToken": $.cookie("csrftoken")
                },
            }).then(function (response) {
                response.json().then(
                    function (data) {
                        if (data["response"]) {
                            redirect_to_surgeons_page();
                        }
                    }
                )
            })
        }
    }
}

function enable_edit_settings() {
    $("#timeout").prop("disabled", false);
}

function myFunction() {
    // Declare variables
    var input, filter, table, tr, td, i, txtValue;
    input = document.getElementById("myInput");
    filter = input.value.toUpperCase();
    table = document.getElementById("MyOrdersTable");
    tr = table.getElementsByTagName("tr");
  
    // Loop through all table rows, and hide those who don't match the search query
    for (i = 0; i < tr.length; i++) {
      td_id = tr[i].getElementsByTagName("td")[0];
      if (td_id){
        txtValue = td_id.textContent || td_id.innerText;
        if (txtValue.toUpperCase().indexOf(filter) > -1) {
          tr[i].style.display = "";
        } else {
          tr[i].style.display = "none";
        }
      }
    }
}