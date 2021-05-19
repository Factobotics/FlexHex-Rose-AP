$( document ).ready(function() {
    $("#show_subscription_dropdown_menu").on("click", "a", function() {
        var this_element = this;
        var measurement_name = $(this_element).text().trim();
        if (measurement_name == "No measurements found" || measurement_name == "" || measurement_name == "" || measurement_name == undefined){
            toastr.warning("Please select valid measurement.");
            return;
        } else {
            $(this_element).parents('.dropdown').children('.dropdown-toggle').text($(this_element).text());

            $.get("/get_measurement_subscription/"+measurement_name, function(data, status){
                $("#subscriptions").empty();
                data.forEach(element => {
                    $("#subscriptions").append(
                        '<pre>'+
                        JSON.stringify(element, null, 4)
                        +'</pre>'
                    );
                });
                if (data.length == 0){
                    toastr.error("Measurement doesn't have any subscriptions.");
                    return;
                }
            })
            .fail(function(xhr, two, three){
                $("#subscriptions").empty();
                if (xhr.responseJSON){
                    if (typeof xhr.responseJSON.detail === 'object' && xhr.responseJSON.detail !== null){
                        for (const [key, value] of Object.entries(xhr.responseJSON.detail)) {
                            toastr.error(value);
                        }
                    } else{
                        toastr.error(xhr.responseJSON.detail);
                    }
                } else{
                    console.error(xhr.status, statusText, xhr.response);  
                }
                toastr.error("Failed to get "+measurement_name+" measurement subscriptions.");
            });
        }
    });


    $("#subscription_submit").on("click", function() {
        var measurement_name = $("#subscribe_measurement_dropdown_button").text().trim();

        if (measurement_name == "No measurements found" || measurement_name == "" || measurement_name.trim() == "" || measurement_name == undefined || measurement_name == "Dropdown"){
            toastr.warning("Measurement id "+measurement_name+" is not valid.");
            return;
        }

        $.post( "/subscribe_to_measurement/"+measurement_name,
        function(data) {
            toastr.success(data);
        })
        .fail(function(xhr, statusText, message){
            if (xhr.responseJSON){
                if (typeof xhr.responseJSON.detail === 'object' && xhr.responseJSON.detail !== null){
                    for (const [key, value] of Object.entries(xhr.responseJSON.detail)) {
                        toastr.error(value);
                    }
                } else{
                    toastr.error(xhr.responseJSON.detail);
                }
            } else{
                console.error(xhr.status, statusText, xhr.response);  
            }
            toastr.error("Failed to subscribe to "+measurement_name+" measurement.");
        });
    });


    $("#resume_measurement_subscription_submit").on("click", function() {
        var measurement_name = $("#pr_measurement_dropdown").text().trim();

        if (measurement_name == "No measurements found" || measurement_name == "" || measurement_name.trim() == "" || measurement_name == undefined || measurement_name == "Dropdown"){
            toastr.warning("Measurement id "+measurement_name+" is not valid.");
            return;
        }

        $.ajax({
            url: "/resume_measurement_subscription/"+measurement_name,
            type: 'PATCH'
        })
        .done(function(data, statusText, xhr) {
            if(data.search("resumed") > -1 && xhr.status == 200){
                toastr.success("Measurement "+measurement_name+" subscription resumed.");
            } else {
                console.info(xhr.status, statusText, data);
                toastr.warning(data);
            }
        })
        .fail(function( xhr, statusText, message ){
            if (xhr.responseJSON){
                if (typeof xhr.responseJSON.detail === 'object' && xhr.responseJSON.detail !== null){
                    for (const [key, value] of Object.entries(xhr.responseJSON.detail)) {
                        toastr.error(value);
                    }
                } else{
                    toastr.error(xhr.responseJSON.detail);
                }
            } else{
                console.error(xhr.status, statusText, xhr.response);  
            }
            toastr.error("Failed to resume "+measurement_name+" measurement subscription.");
        });
    });


    $("#pause_measurement_subscription_submit").on("click", function() {
        var measurement_name = $("#pr_measurement_dropdown").text().trim();

        if (measurement_name == "No measurements found" || measurement_name == "" || measurement_name.trim() == "" || measurement_name == undefined || measurement_name == "Dropdown"){
            toastr.warning("Measurement id "+measurement_name+" is not valid.");
            return;
        }

        $.ajax({
            url: "/pause_measurement_subscription/"+measurement_name,
            type: 'PATCH'
        })
        .done( function(data, statusText, xhr) {
            if(data.search("paused") > -1 && xhr.status == 200){
                toastr.success("Measurement "+measurement_name+" subscription paused.");
            } else {
                console.info(xhr.status, statusText, data);
                toastr.warning(data);
            }
        })
        .fail(function( xhr, statusText, message ){
            if (xhr.responseJSON){
                if (typeof xhr.responseJSON.detail === 'object' && xhr.responseJSON.detail !== null){
                    for (const [key, value] of Object.entries(xhr.responseJSON.detail)) {
                        toastr.error(value);
                    }
                } else{
                    toastr.error(xhr.responseJSON.detail);
                }
            } else{
                console.error(xhr.status, statusText, xhr.response);  
            }
            toastr.error("Failed to pause "+measurement_name+" measurement subscription.");
        });
    });

    
    $("#delete_measurement_subscription_submit").on("click", function() {
        var measurement_name = $("#delete_measurement_dropdown").text().trim();

        if (measurement_name == "No measurements found" || measurement_name == "" || measurement_name.trim() == "" || measurement_name == undefined || measurement_name == "Dropdown"){
            toastr.warning("Measurement id "+measurement_name+" is not valid.");
            return;
        }

        $.ajax({
            url: "/delete_measurement_subscription/"+measurement_name,
            type: 'DELETE'
        })
        .done( function(data, statusText, xhr) {
            if(data.search("deleted") > -1 && xhr.status == 200){
                toastr.success("Measurement "+measurement_name+" subscription deleted.");
            } else {
                console.info(xhr.status, statusText, data);
                toastr.warning(data);
            }
        })
        .fail(function( xhr, statusText, message ){
            if (xhr.responseJSON){
                if (typeof xhr.responseJSON.detail === 'object' && xhr.responseJSON.detail !== null){
                    for (const [key, value] of Object.entries(xhr.responseJSON.detail)) {
                        toastr.error(value);
                    }
                } else{
                    toastr.error(xhr.responseJSON.detail);
                }
            } else{
                console.error(xhr.status, statusText, xhr.response);
            }
            toastr.error("Failed to delete "+measurement_name+" measurement subscription.");
        });
    });
    
});