// Determine which options to show depending on if user chose subreddit or user
window.onload = function(){
    changes()
};

function changes() {
    $('[name="page"]').on('change', function() {
        if ($(this).attr('id') == 'subredditPage') {
            $('#amount-label').text('Enter Number of Posts');
            $("#encrypt-label").hide();
            $("#encrypted").hide();
            $("#notEncrypted").hide();
        } else {
            $('#amount-label').text('Enter Number of Comments');
            $("#encrypt-label").show();
            $("#encrypted").show();
            $("#notEncrypted").show();
        }
    });
}

function getUserInput() {
    let page_type = document.querySelector('input[name="page"]:checked').value;
    let page_name = document.getElementById("page-search").value;
    let no_posts = document.getElementById("no-posts").value;
    let sort_type = document.querySelector('input[name="sort"]:checked').value;
    let is_encrypted = document.querySelector('input[name="encryption"]:checked').value;

    let user_input = {
        'page_type': page_type,
        'page_name': page_name,
        'no_posts': parseInt(no_posts),
        'sort_type': sort_type,
        'is_encrypted' : is_encrypted
    }
    return JSON.stringify(user_input)
}

function getComments() {
    $.ajax({
            type: "POST",
            url: '/getuserinput',
            contentType: "application/json",
            async: false,
            data: getUserInput(),

            success: function (success_data) {
                console.log("Comments retrieved successfully and has been saved")
                console.log(success_data)
            },
    });
//    you can use code above or below (same result)

//    fetch("/getuserinput", {
//      method: "POST",
//      body: JSON.stringify(user_input)
//    }).then(res => {
//      console.log("Request complete! response:", res);
//    });

    showComments();
}

function showComments() {
    $.ajax({
            type: "POST",
            url: '/getuserinput',
            contentType: "application/json",
            async: false,
            data: getUserInput(),

            success: function (success_data) {
                if (success_data.comments){
                    console.log(success_data)
                    createTable(success_data.column_names, success_data.comments)
                    logData(success_data.column_names, success_data.comments)
                } else {
                    console.log("Error, could not retrieve comments")
                }
            },
        });
}

function logData(column_names, comments) {
    console.log(column_names);
    console.log(comments);
}

function addTable() {
    $('#table-div').append('<table id="table"></table>');
}

function removeTable() {
    $("#table").remove();
}

function createTable(column_names, comments) {
//  initialise div to remove an existing table
    removeTable();
//
    addTable();
    let table = document.getElementById('table');

    //  set column names/headers
    for (c=0; c<column_names.length; c++) {
        let header = document.createElement("th");
        header.innerHTML = column_names[c];
        table.appendChild(header);
    }

    //  fill in rows with comments
    for (y=0; y<comments.length; y++) {
        let tr = document.createElement("tr");
        table.appendChild(tr);
        for (x=0; x<comments[y].length; x++) {
            var td  = document.createElement("td");
            var txt = document.createTextNode(comments[y][x]);
            td.appendChild(txt);
            tr.appendChild(td);
        }
    }
}