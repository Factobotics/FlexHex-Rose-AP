$( document ).ready(function() {
    $("#get_measurement_dropdown, #update_measurement_dropdown, #delete_measurement_dropdown, #subscribe_measurement_dropdown_button, #show_subscription_dropdown_button, #pr_measurement_dropdown, #delete_measurement_dropdown").on( "click", function() {
        var this_element = this;
        $.get("/get_measurements", function(data, status){
            $(this_element).parent().children('.dropdown-menu').empty();
            if (data.length == 0){
                $(this_element).parent().children('.dropdown-menu').append('<a class="dropdown-item">No measurements found</a>');
            }
            data.forEach(function (value){
                $(this_element).parent().children('.dropdown-menu').append('<a class="dropdown-item">'+value+'</a>');
            });
        });
    });

    $("#get_measurement_dropdown_menu").on("click", "a", function() {
        var this_element = this;
        var measurement_name = $(this_element).text().trim();
        if (measurement_name == "No measurements found" || measurement_name == "" || measurement_name == "" || measurement_name == undefined){
            toastr.warning("Please select valid measurement.");
            return;
        } else {
            $(this_element).parents('.dropdown').children('.dropdown-toggle').text($(this_element).text());

            $.get("/get_measurement/"+measurement_name, function(data, status){
                $(this_element).parents("form").find(".entities-table").find("tbody").empty();
                data[measurement_name].subscription_data.entities.forEach(function(entity_data){
                    $(this_element).parents("form").find(".entities-table").find("tbody").append(
                        '<tr>\
                            <td>'+entity_data.id+'</td>\
                            <td>'+entity_data.id_type+'</td>\
                            <td>'+entity_data.type+'</td>\
                            <td>'+entity_data.type_type+'</td>\
                        </tr>'
                    );
                });

                $(this_element).parents("form").find(".tags-table").find("tbody").empty();
                for (const [key, value] of Object.entries(data[measurement_name].influx_data.tags)) {
                    $(this_element).parents("form").find(".tags-table").find("tbody").append(
                    '<tr>\
                        <td>'+key+'</td>\
                        <td>'+value+'</td>\
                    </tr>');
                };

                $(this_element).parents("form").find(".fields-table").find("tbody").empty();
                for (const [key, value] of Object.entries(data[measurement_name].influx_data.fields)) {
                    $(this_element).parents("form").find(".fields-table").find("tbody").append(
                    '<tr>\
                        <td>'+key+'</td>\
                        <td>'+value+'</td>\
                    </tr>');
                };
            });
        }
    });


    $("#update_measurement_dropdown_menu").on("click", "a", function() {
        var this_element = this;
        var measurement_name = $(this_element).text().trim();
        if (measurement_name == "No measurements found" || measurement_name == "" || measurement_name == "" || measurement_name == undefined){
            toastr.warning("Please select valid measurement.");
            return;
        } else {
            $(this_element).parents('.dropdown').children('.dropdown-toggle').text($(this_element).text());

            $.get("/get_measurement/"+measurement_name, function(data, status){
                $(this_element).parents("form").find(".entities-table").find("tbody").empty();

                data[measurement_name].subscription_data.entities.forEach(function(entity_data){
                    $(this_element).parents("form").find(".entities-table").find("tbody").append(
                        '<tr>\
                            <td><input type="text" class="form-control entity-id" value="'+entity_data.id+'"/></td>\
                            <td>\
                                <div class="dropdown entity-id-type">\
                                    <button class="btn btn-secondary dropdown-toggle id-type-select" data-toggle="dropdown" aria-expanded="false" type="button">'+entity_data.id_type+'</button>\
                                    <div class="dropdown-menu entity-type-dropdown-menu">\
                                        <a class="dropdown-item">pattern</a>\
                                        <a class="dropdown-item">exact</a>\
                                    </div>\
                                </div>\
                            </td>\
                            <td><input type="text" class="form-control entity-type" value="'+entity_data.type+'"/></td>\
                            <td>\
                                <div class="dropdown entity-type-type">\
                                    <button class="btn btn-secondary dropdown-toggle type-type-select" data-toggle="dropdown" aria-expanded="false" type="button">'+entity_data.type_type+'</button>\
                                    <div class="dropdown-menu entity-type-dropdown-menu">\
                                        <a class="dropdown-item">pattern</a>\
                                        <a class="dropdown-item">exact</a>\
                                    </div>\
                                </div>\
                            </td>\
                        </tr>'
                    );
                });

                $(this_element).parents("form").find(".tags-table").find("tbody").empty();
                for (const [key, value] of Object.entries(data[measurement_name].influx_data.tags)) {
                    $(this_element).parents("form").find(".tags-table").find("tbody").append(
                        '<tr>\
                            <td><input type="text" class="form-control tag-id" value="'+key+'"/></td>\
                            <td><input type="text" class="form-control entity-property" value="'+value+'"/></td>\
                        </tr>'
                    );
                };

                $(this_element).parents("form").find(".fields-table").find("tbody").empty();
                for (const [key, value] of Object.entries(data[measurement_name].influx_data.fields)) {
                    $(this_element).parents("form").find(".fields-table").find("tbody").append(
                        '<tr>\
                            <td><input type="text" class="form-control field-id" value="'+key+'"/></td>\
                            <td><input type="text" class="form-control entity-property" value="'+value+'"/></td>\
                        </tr>'
                    );
                };
            });
        }
    });


    $("#delete_measurement_dropdown_menu, #subscribe_measurement_dropdown_menu, #pr_measurement_dropdown_menu, #delete_measurement_dropdown_menu").on("click", "a", function() {
        var this_element = this;
        if ($(this_element).text() == "No measurements found" || $(this_element).text() == "" || $(this_element).text().trim() == "" || $(this_element).text() == undefined){
            toastr.warning("Please select valid measurement.");
            return;
        } else{
            $(this).parents('.dropdown').children('.dropdown-toggle').text($(this).text());
        }
    });


    $("#add_measurement_add_entity, #update_measurement_add_entity").on( "click", function() {
        $(this).parents(".form-group").find("tbody").append(
            '<tr>\
            <td><input type="text" class="form-control entity-id" /></td>\
            <td>\
                <div class="dropdown entity-id-type">\
                    <button class="btn btn-secondary dropdown-toggle id-type-select" data-toggle="dropdown" aria-expanded="false" type="button">Dropdown </button>\
                    <div class="dropdown-menu entity-type-dropdown-menu">\
                        <a class="dropdown-item">pattern</a>\
                        <a class="dropdown-item">exact</a>\
                    </div>\
                </div>\
            </td>\
            <td><input type="text" class="form-control entity-type" /></td>\
            <td>\
                <div class="dropdown entity-type-type">\
                    <button class="btn btn-secondary dropdown-toggle type-type-select" data-toggle="dropdown" aria-expanded="false" type="button">Dropdown </button>\
                    <div class="dropdown-menu entity-type-dropdown-menu">\
                        <a class="dropdown-item">pattern</a>\
                        <a class="dropdown-item">exact</a>\
                    </div>\
                </div>\
            </td>\
        </tr>');
    });

    $("#add_measurement_remove_entity, #update_measurement_remove_entity").on( "click", function() {
        $(this).parents(".form-group").find("tbody").children().last().remove();
    });


    $("#add_measurement_add_tag, #update_measurement_add_tag").on( "click", function() {
        $(this).parents(".form-group").find("tbody").append(
            '<tr>\
                <td><input type="text" class="form-control tag-id" /></td>\
                <td><input type="text" class="form-control entity-property" /></td>\
            </tr>'
        );
    });

    $("#add_measurement_add_field, #update_measurement_add_field").on( "click", function() {
        $(this).parents(".form-group").find("tbody").append(
            '<tr>\
                <td><input type="text" class="form-control field-id" /></td>\
                <td><input type="text" class="form-control entity-property" /></td>\
            </tr>'
        );
    });

    $("#add_measurement_remove_tag, #update_measurement_remove_tag, #add_measurement_remove_field, #update_measurement_remove_field").on( "click", function() {
        $(this).parents(".form-group").find("tbody").children().last().remove();
    });

    $(document).on("click", ".entity-type-dropdown-menu a", function() {
        $(this).parents(".dropdown").children("button").text($(this).text().trim());
    });

    $("#add_measurement_submit").on("click", function() {
        var this_element = this;
        var measurement_name = $("#add_measurement_name").val().trim();
        var influx_data = {"fields": {}, "tags": {}};
        var subscription_data = {"entities": []};
        var broke = false;

        if (measurement_name == "No measurements found" || measurement_name == "" || measurement_name.trim() == "" || measurement_name == undefined || measurement_name == "Dropdown"){
            toastr.warning("Measurement id "+measurement_name+" is not valid.");
            return;
        }
            
        $("#add_entities_table > table > tbody").children().each(function (index, element){
                
            var entity = {"id": "", "id_type": "", "type": "", "type_type": ""};
            $(element).children().each(function (td_index, td_element){
                
                if ($(td_element).children('input').length == 1){
                    if ($(td_element).children('input').hasClass("entity-id")){
                        entity.id = $(td_element).children('input').val();
                    } else if($(td_element).children('input').hasClass("entity-type")){
                        entity.type = $(td_element).children('input').val();
                    }
                } else if ($(td_element).children('.dropdown').length == 1){
                    if($(td_element).children('.dropdown').hasClass("entity-id-type")){
                        entity.id_type = $(td_element).children('.dropdown').children("button").text();
                    } else if($(td_element).children('.dropdown').hasClass("entity-type-type")){
                        entity.type_type = $(td_element).children('.dropdown').children("button").text();
                    }
                }
            })
            // console.log(entity);
            if(entity.id_type.trim() == "Dropdown" || entity.type_type.trim() == "Dropdown" ){
                toastr.warning("Please select valid types for entities.");
                broke = true;
                return;
            }
            if(entity.id.trim() == "" || entity.id.trim() == undefined){
                toastr.warning("Please fill in all ID fields.");
                broke = true;
                return;
            }
            if(entity.type.trim() == "" || entity.type.trim() == undefined){
                toastr.warning("Please fill in all type fields.");
                broke = true;
                return;
            }
            subscription_data.entities.push(entity);
        });
        if(broke) return;

        $("#add_tags_table > table > tbody").children().each(function (index, element){
               
            var key = undefined;
            var value = undefined;
        
            $(element).children().each(function (td_index, td_element){
                if ($(td_element).children('input').hasClass("tag-id")){
                    key = $(td_element).children('input').val();
                } else if ($(td_element).children('input').hasClass("entity-property")){
                    value = $(td_element).children('input').val();
                }

            });

            if(key == undefined || value == undefined || key == "" && value != "" || key != "" && value == ""){
                toastr.warning("Please fill in tags.");
                broke = true;
                return;
                
            } else if (key == "" || value == ""){
                console.log("Empty tags.");
            } else {
                influx_data.tags[key] = value;
            }

            

        });
        // console.log(influx_data);
        if(broke) return;


        $("#add_fields_table > table > tbody").children().each(function (index, element){
               
            var key = undefined;
            var value = undefined;
        
            $(element).children().each(function (td_index, td_element){
                if ($(td_element).children('input').hasClass("field-id")){
                    key = $(td_element).children('input').val();
                } else if ($(td_element).children('input').hasClass("entity-property")){
                    value = $(td_element).children('input').val();
                }

            });

            if(key == undefined || value == undefined || key == "" && value != "" || key != "" && value == ""){
                toastr.warning("Please fill in fields.");
                broke = true;
                return;
                
            } else if (key == "" || value == ""){
                console.log("Empty fields.");
            } else {
                influx_data.fields[key] = value;
            }
        });

        if(broke) return;


        $.post( "/add_measurement", JSON.stringify({"measurement": measurement_name, "measurement_data": {"influx_data": influx_data, "subscription_data": subscription_data}}), function( data, statusText, xhr) {
            if(data.search("added") > -1 && xhr.status == 200){
                toastr.success("Measurement "+measurement_name+" added.");
            } else{
                toastr.error("Failed to add "+measurement_name+" measurement. Bucket missmatch.");
            }
        })
        .fail(function(){
            toastr.error("Failed to add "+measurement_name+" measurement.");
        });
    });


    $("#update_measurement_submit").on("click", function() {
        var this_element = this;
        var measurement_name = $("#update_measurement_dropdown").text().trim();
        var influx_data = {"fields": {}, "tags": {}};
        var subscription_data = {"entities": []};
        var broke = false;

        if (measurement_name == "No measurements found" || measurement_name == "" || measurement_name.trim() == "" || measurement_name == undefined || measurement_name == "Dropdown"){
            toastr.warning("Measurement id "+measurement_name+" is not valid.");
            return;
        }
            
        $("#update_entities_table > table > tbody").children().each(function (index, element){
                
            var entity = {"id": "", "id_type": "", "type": "", "type_type": ""};
            $(element).children().each(function (td_index, td_element){
                
                if ($(td_element).children('input').length == 1){
                    if ($(td_element).children('input').hasClass("entity-id")){
                        entity.id = $(td_element).children('input').val();
                    } else if($(td_element).children('input').hasClass("entity-type")){
                        entity.type = $(td_element).children('input').val();
                    }
                } else if ($(td_element).children('.dropdown').length == 1){
                    if($(td_element).children('.dropdown').hasClass("entity-id-type")){
                        entity.id_type = $(td_element).children('.dropdown').children("button").text();
                    } else if($(td_element).children('.dropdown').hasClass("entity-type-type")){
                        entity.type_type = $(td_element).children('.dropdown').children("button").text();
                    }
                }
            })
            if(entity.id_type.trim() == "Dropdown" || entity.type_type.trim() == "Dropdown" ){
                toastr.warning("Please select valid types for entities.");
                broke = true;
                return;
            }
            if(entity.id.trim() == "" || entity.id.trim() == undefined){
                toastr.warning("Please fill in all ID fields.");
                broke = true;
                return;
            }
            if(entity.type.trim() == "" || entity.type.trim() == undefined){
                toastr.warning("Please fill in all type fields.");
                broke = true;
                return;
            }
            subscription_data.entities.push(entity);
        });
        if(broke) return;

        $("#update_tags_table > table > tbody").children().each(function (index, element){
               
            var key = undefined;
            var value = undefined;
        
            $(element).children().each(function (td_index, td_element){
                if ($(td_element).children('input').hasClass("tag-id")){
                    key = $(td_element).children('input').val();
                } else if ($(td_element).children('input').hasClass("entity-property")){
                    value = $(td_element).children('input').val();
                }

            });

            if(key == undefined || value == undefined || key == "" && value != "" || key != "" && value == ""){
                toastr.warning("Please fill in tags.");
                broke = true;
                return;
                
            } else if (key == "" || value == ""){
                console.log("Empty tags.");
            } else {
                influx_data.tags[key] = value;
            }

            

        });
        if(broke) return;


        $("#update_fields_table > table > tbody").children().each(function (index, element){
               
            var key = undefined;
            var value = undefined;
        
            $(element).children().each(function (td_index, td_element){
                if ($(td_element).children('input').hasClass("field-id")){
                    key = $(td_element).children('input').val();
                } else if ($(td_element).children('input').hasClass("entity-property")){
                    value = $(td_element).children('input').val();
                }

            });

            if(key == undefined || value == undefined || key == "" && value != "" || key != "" && value == ""){
                toastr.warning("Please fill in fields.");
                broke = true;
                return;
            } else if (key == "" || value == ""){
                console.log("Empty fields.");
            } else {
                influx_data.fields[key] = value;
            }
        });

        if(broke) return;

        // console.log({"measurement_data": {"influx_data": influx_data, "subscription_data": subscription_data}})
        $.post( "/update_measurement/"+measurement_name, 
        JSON.stringify({"measurement_data": {"influx_data": influx_data, "subscription_data": subscription_data}}), 
        function( data, statusText, xhr ) {
            if(data.search("updated") > -1 && xhr.status == 200){
                toastr.success("Measurement "+measurement_name+" updated.");
            } else{
                toastr.error("Failed to update "+measurement_name+" measurement.");
            };
        })
        .fail(function( xhr, statusText, message ){
            if(xhr.status == 404){
                toastr.error("Measurement "+measurement_name+" not found.");
            } else{
                toastr.error("Failed to update "+measurement_name+" measurement.");
            }
        });
    });
    

    $("#delete_measurement_submit").on("click", function() {
        // var this_element = this;
        var measurement_name = $("#delete_measurement_dropdown").text().trim();

        if (measurement_name == "No measurements found" || measurement_name == "" || measurement_name.trim() == "" || measurement_name == undefined || measurement_name == "Dropdown"){
            toastr.warning("Measurement id "+measurement_name+" is not valid.");
            return;
        }

        $.ajax({
            url: "/delete_measurement/"+measurement_name,
            type: 'DELETE'
        })
        .done( function(data, statusText, xhr) {
            if(data.search("deleted") > -1 && xhr.status == 200){
                toastr.success("Measurement "+measurement_name+" deleted.");
            } else {
                toastr.error("Failed to delete "+measurement_name+" measurement.");
            }
        })
        .fail(function( xhr, statusText, message ){
            if(xhr.status == 404){
                toastr.error("Measurement "+measurement_name+" not found.");
            } else{
                toastr.error("Failed to delete "+measurement_name+" measurement.");
            }
        });
    });

});