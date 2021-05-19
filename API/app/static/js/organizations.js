$( document ).ready(function() {
    $("#get_organization_dropdown, #update_organization_dropdown, #delete_organization_dropdown").on( "click", function() {
        var this_element = this;
        $.get("/get_organizations", function(data, status){
            $(this_element).parent().children('.dropdown-menu').empty();
            if (data.length == 0){
                $(this_element).parent().children('.dropdown-menu').append('<a class="dropdown-item">No organizations found</a>');
            }
            data.forEach(function (value){
                $(this_element).parent().children('.dropdown-menu').append('<a class="dropdown-item">'+value+'</a>');
            });
        })
        .fail(function(){
            toastr.error("Failed to get organizations.");
        });
    });


    $(".dropdown-menu.get-organization, .dropdown-menu.update-organization").on("click", "a", function() {
        var this_element = this;
        var organization_name = $(this_element).text().trim();
        if (organization_name == "No organizations found" || organization_name == "" || organization_name == "" || organization_name == undefined){
            toastr.warning("Please select valid organization.");
            return;
        } else {
            $(this_element).parents('.dropdown').children('.dropdown-toggle').text($(this_element).text());

            $.get("/get_organization/"+organization_name, function(data, status){
                
                $(this_element).parents("form").children(".buckets").children("input").remove();
                $(this_element).parents("form").children(".buckets").children(".dropdown").remove();
                data[organization_name].buckets.forEach(function (value){
                    if ($(this_element).parent().hasClass("get-organization")){
                        $(this_element).parents("form").children(".buckets").append(
                            '<input class="form-control" type="text" value="'+value+'" readonly>'
                        );
                    }
                    else if ($(this_element).parent().hasClass("update-organization")){
                        $(this_element).parents("form").children(".buckets").append(
                            '<div class="dropdown mt-1">\
                                <button class="btn btn-secondary btn-block dropdown-toggle buckets-dropdown-button" data-toggle="dropdown" aria-expanded="false" type="button">'+value+'</button>\
                                <div class="dropdown-menu buckets-dropdown-menu">\
                                </div>\
                            </div>'
                        );
                    }
                })
            })
            .fail(function( xhr, statusText, message ){
                if(xhr.status == 404){
                    toastr.error("Organization "+organization_name+" not found.");
                } else{
                    toastr.error("Failed to get "+organization_name+" organization.");
                }
            });
        }
    });


    $(".dropdown-menu.delete-organization").on("click", "a", function() {
        var this_element = this;
        if ($(this_element).text() == "No organizations found" || $(this_element).text() == "" || $(this_element).text().trim() == "" || $(this_element).text() == undefined){
            toastr.warning("Please select valid organization.");
            return;
        } else{
            $(this).parents('.dropdown').children('.dropdown-toggle').text($(this).text());
        }
    });


    $("#add_organization_add, #update_organization_add").on( "click", function() {
        $(this).parent().parent().append(
            '<div class="dropdown mt-1">\
                <button class="btn btn-secondary btn-block dropdown-toggle buckets-dropdown-button" data-toggle="dropdown" aria-expanded="false" type="button">Dropdown </button>\
                <div class="dropdown-menu buckets-dropdown-menu">\
                </div>\
            </div>'
        );
    });

    $("#add_organization_remove, #update_organization_remove").on( "click", function() {
        $(this).parents(".buckets").children(".dropdown").last().remove();
    });

    $(document).on( "click", ".buckets-dropdown-button", function() {
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
        .fail(function( xhr, statusText, message ){
            toastr.error("Failed to get buckets.");
        });
    });

    $(document).on("click", ".buckets-dropdown-menu a", function() {
        var this_element = this;
        var bucket_name = $(this_element).text().trim();
        if (bucket_name == "No buckets found" || bucket_name == "" || bucket_name == "" || bucket_name == undefined){
            toastr.warning("Please create a bucket or select a valid one.");
            return;
        } else {
            $(this_element).parents('.dropdown').children('.dropdown-toggle').text($(this_element).text());
        }
    });


    $("#add_organization_submit").on("click", function() {
        var this_element = this;
        var organization_name = $("#add_organization_name").val().trim();
        var organization_data = {"buckets":[]}

        if (organization_name == "No organizations found" || organization_name == "" || organization_name.trim() == "" || organization_name == undefined || organization_name == "Dropdown"){
            toastr.warning("Organization id not valid.");
            return;
        }

        $(this_element).parents("form").children(".buckets").children(".dropdown").each(function (index, element){
            var text = $(element).children("button").text().trim();
            if (text != null && text != undefined && text != "" && text != "Dropdown"){
                organization_data.buckets.push(text);
            }
        });

        if(organization_data.buckets.length == 0){
            toastr.warning(organization_name + " organization doesn't have any buckets assigned.");
            return;
        }

        $.post( "/add_organization", JSON.stringify({"organization": organization_name, "organization_data": organization_data}), function( data, statusText, xhr) {
            if(data.search("added") > -1 && xhr.status == 200){
                toastr.success("Organization "+organization_name+" added.");
            } else{
                toastr.error("Failed to add "+organization_name+" organization. Bucket missmatch.");
            }
        })
        .fail(function(){
            toastr.error("Failed to add "+organization_name+" organization.");
        });
    });


    $("#update_organization_submit").on("click", function() {
        var this_element = this;
        var organization_name = $("#update_organization_dropdown").text().trim();
        var organization_data = {"buckets":[]}

        if (organization_name == "No organizations found" || organization_name == "" || organization_name.trim() == "" || organization_name == undefined || organization_name == "Dropdown"){
            toastr.warning("Organization id not valid.");
            return;
        }

        $(this_element).parents("form").children(".buckets").children(".dropdown").each(function (index, element){
            var text = $(element).children("button").text().trim();
            if (text != null && text != undefined && text != "" && text != "Dropdown"){
                organization_data.buckets.push(text);
            }
        });

        $.post( "/update_organization/"+organization_name, JSON.stringify({"organization_data": organization_data}), function( data, statusText, xhr ) {
            if(data.search("updated") > -1 && xhr.status == 200){
                toastr.success("Organization "+organization_name+" updated.");
            } else{
                toastr.error("Failed to update "+organization_name+" organization.");
            };
        })
        .fail(function( xhr, statusText, message ){
            if(xhr.status == 404){
                toastr.error("Organization "+organization_name+" not found.");
            } else{
                toastr.error("Failed to update "+organization_name+" organization.");
            }
        });
    });
    

    $("#delete_organization_submit").on("click", function() {
        var organization_name = $("#delete_organization_dropdown").text().trim();

        if (organization_name == "No organizations found" || organization_name == "" || organization_name.trim() == "" || organization_name == undefined || organization_name == "Dropdown"){
            toastr.warning("Organization id not valid.");
            return;
        }

        $.ajax({
            url: "/delete_organization/"+organization_name,
            type: 'DELETE'
        })
        .done( function(data, statusText, xhr) {
            if(data.search("deleted") > -1 && xhr.status == 200){
                toastr.success("Organization "+organization_name+" deleted.");
            } else {
                toastr.error("Failed to delete "+organization_name+" organization.");
            }
        })
        .fail(function( xhr, statusText, message ){
            if(xhr.status == 404){
                toastr.error("Organization "+organization_name+" not found.");
            } else{
                toastr.error("Failed to delete "+organization_name+" organization.");
            }
        });
    });

});