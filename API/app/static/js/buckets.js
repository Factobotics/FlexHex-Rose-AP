$( document ).ready(function() {
    $("#get_bucket_dropdown, #update_bucket_dropdown, #delete_bucket_dropdown").on( "click", function() {
        var this_element = this;
        $.get("/get_buckets", function(data, status){
            $(this_element).parent().children('.dropdown-menu').empty();
            if (data.length == 0){
                $(this_element).parent().children('.dropdown-menu').append('<a class="dropdown-item">No buckets found</a>');
            }
            data.forEach(function (value){
                $(this_element).parent().children('.dropdown-menu').append('<a class="dropdown-item">'+value+'</a>');
            });
        })
        .fail(function(){
            toastr.error("Failed to get buckets.");
        });
    });

    $("#get_bucket_dropdown_menu, #update_bucket_dropdown_menu").on("click", "a", function() {
        var this_element = this;
        var bucket_name = $(this_element).text().trim();
        if (bucket_name == "No buckets found" || bucket_name == "" || bucket_name == "" || bucket_name == undefined){
            toastr.warning("Please select valid bucket.");
            return;
        } else {
            $(this_element).parents('.dropdown').children('.dropdown-toggle').text($(this_element).text());

            $.get("/get_bucket/"+bucket_name, function(data, status){
                $(this_element).parents("form").children(".measurements").children("input").remove();
                $(this_element).parents("form").children(".measurements").children(".dropdown").remove();
                data[bucket_name].measurements.forEach(function (value){
                    // console.log($(this_element).parent());
                    // console.log($(this_element).parent().hasClass("get-measurement"));
                    // console.log($(this_element).parent().hasClass("update-measurement"));

                    if ($(this_element).parent().hasClass("get-measurement")){
                        $(this_element).parents("form").children(".measurements").append(
                            '<input class="form-control" type="text" value="'+value+'" readonly>'
                        );
                    }
                    else if ($(this_element).parent().hasClass("update-measurement")){
                        $(this_element).parents("form").children(".measurements").append(
                            '<div class="dropdown mt-1">\
                                <button class="btn btn-secondary btn-block dropdown-toggle measurement-dropdown-button" data-toggle="dropdown" aria-expanded="false" type="button">'+value+'</button>\
                                <div class="dropdown-menu measurement-dropdown-menu">\
                                </div>\
                            </div>'
                        );
                    }
                })
            })
            .fail(function( xhr, statusText, message ){
                if(xhr.status == 404){
                    toastr.error("Bucket "+bucket_name+" not found.");
                } else{
                    toastr.error("Failed to get "+bucket_name+" bucket.");
                }
            });
        }
    });


    $(".dropdown-menu.delete-bucket").on("click", "a", function() {
        var this_element = this;
        if ($(this_element).text() == "No buckets found" || $(this_element).text() == "" || $(this_element).text().trim() == "" || $(this_element).text() == undefined){
            toastr.warning("Please select valid bucket.");
            return;
        } else{
            $(this).parents('.dropdown').children('.dropdown-toggle').text($(this).text());
        }
    });


    $("#add_bucket_add, #update_bucket_add").on( "click", function() {
        $(this).parent().parent().append(
            '<div class="dropdown mt-1">\
                <button class="btn btn-secondary btn-block dropdown-toggle measurement-dropdown-button" data-toggle="dropdown" aria-expanded="false" type="button">Dropdown </button>\
                <div class="dropdown-menu measurement-dropdown-menu">\
                </div>\
            </div>'
        );
        
    });

    $("#add_bucket_remove, #update_bucket_remove").on( "click", function() {
        $(this).parents(".measurements").children(".dropdown").last().remove();
    });


    $(document).on( "click", ".measurement-dropdown-button", function() {
        var this_element = this;
        $.get("/get_measurements", function(data, status){
            $(this_element).parent().children('.dropdown-menu').empty();
            if (data.length == 0){
                $(this_element).parent().children('.dropdown-menu').append('<a class="dropdown-item">No measurements found</a>');
            }
            data.forEach(function (value){
                $(this_element).parent().children('.dropdown-menu').append('<a class="dropdown-item">'+value+'</a>');
            });
        })
        .fail(function( xhr, statusText, message ){
            toastr.error("Failed to get measurements.");
        });
    });

    $(document).on("click", ".measurement-dropdown-menu a", function() {
        var this_element = this;
        var bucket_name = $(this_element).text().trim();
        if (bucket_name == "No measurements found" || bucket_name == "" || bucket_name == "" || bucket_name == undefined){
            toastr.warning("Please create a measurement or select a valid one.");
            return;
        } else {
            $(this_element).parents('.dropdown').children('.dropdown-toggle').text($(this_element).text());
        }
    });


    $("#add_bucket_submit").on("click", function() {
        var this_element = this;
        var bucket_name = $("#add_bucket_name").val().trim();
        var bucket_data = {"measurements":[]}

        if (bucket_name == "No buckets found" || bucket_name == "" || bucket_name.trim() == "" || bucket_name == undefined || bucket_name == "Dropdown"){
            toastr.warning("Bucket id not valid.");
            return;
        }

        $(this_element).parents("form").children(".measurements").children(".dropdown").each(function (index, element){
            var text = $(element).children("button").text().trim();

            if (text != null && text != undefined && text != "" && text != "Dropdown"){
                bucket_data.measurements.push(text);
            }
        });

        if(bucket_data.measurements.length == 0){
            toastr.warning(bucket_name + " bucket doesn't have any measurements assigned.");
            return;
        }

        $.ajax({
            url: "/add_bucket",
            type: 'POST',
            contentType:"application/json",
            dataType:"json",
            data: JSON.stringify({"bucket": bucket_name, "bucket_data": bucket_data})
        })
        .done( function( data, statusText, xhr ) {
            if (verbose) console.log(data);
            if (verbose) console.log(statusText);
            if (verbose) console.log(xhr);
            if(data["message"].search("added") > -1 && xhr.status == 201){
                toastr.success(data["message"]);
            } else{
                toastr.error("Failed to add "+bucket_name+" bucket. Measurement missmatch.");
            }
        })
        .fail(function( xhr, statusText, message ){
            if (verbose) console.log(xhr);
            if (verbose) console.log(statusText);
            if (verbose) console.log(message);
            toastr.error("Failed to add "+bucket_name+" bucket.");
        });
    });

    $("#update_bucket_submit").on("click", function() {
        var this_element = this;
        var bucket_name = $("#update_bucket_dropdown").text().trim();
        var bucket_data = {"measurements":[]}

        if (bucket_name == "No buckets found" || bucket_name == "" || bucket_name.trim() == "" || bucket_name == undefined || bucket_name == "Dropdown"){
            toastr.warning("Bucket id not valid.");
            return;
        }

        $(this_element).parents("form").children(".measurements").children(".dropdown").each(function (index, element){
            var text = $(element).children("button").text().trim();
            if (text != null && text != undefined && text != "" && text != "Dropdown"){
                bucket_data.measurements.push(text);
            }
        });

        if(bucket_data.measurements.length == 0){
            toastr.warning(bucket_name + " bucket doesn't have any measurements assigned.");
            return;
        }

        
        $.ajax({
            url: "/update_bucket/"+bucket_name,
            type: 'POST',
            contentType:"application/json",
            dataType:"json",
            data: JSON.stringify({"bucket_data": bucket_data})
        })
        .done( function( data, statusText, xhr ) {
            if (verbose) console.log(data);
            if (verbose) console.log(statusText);
            if (verbose) console.log(xhr);
            if(data["message"].search("updated") > -1 && xhr.status == 202){
                toastr.success(data["message"]);
            } else{
                toastr.error("Failed to update "+bucket_name+" bucket.");
            };
          })
        .fail(function( xhr, statusText, message ){
            if (verbose) console.log(xhr);
            if (verbose) console.log(statusText);
            if (verbose) console.log(message);
            if(xhr.status == 404){
                toastr.error("Bucket "+bucket_name+" not found.");
            } else{
                toastr.error("Failed to update "+bucket_name+" bucket.");
            }
        });
    });
    

    $("#delete_bucket_submit").on("click", function() {
        // var this_element = this;
        var bucket_name = $("#delete_bucket_dropdown").text().trim();

        if (bucket_name == "No buckets found" || bucket_name == "" || bucket_name.trim() == "" || bucket_name == undefined || bucket_name == "Dropdown"){
            toastr.warning("Bucket id not valid.");
            return;
        }

        $.ajax({
            url: "/delete_bucket/"+bucket_name,
            type: 'DELETE'
        })
        .done( function(data, statusText, xhr) {
            if(data.search("deleted") > -1 && xhr.status == 200){
                toastr.success("Bucket "+bucket_name+" deleted.");
            } else {
                toastr.error("Failed to delete "+bucket_name+" bucket.");
            }
        })
        .fail(function( xhr, statusText, message ){
            if(xhr.status == 404){
                toastr.error("Bucket "+bucket_name+" not found.");
            } else{
                toastr.error("Failed to delete "+bucket_name+" bucket.");
            }
        });
    });

});