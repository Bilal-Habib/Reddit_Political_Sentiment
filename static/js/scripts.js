// Determine which options to show depending on if user chose subreddit or user
window.onload = function(){
    changes()
};

function changes() {
//  when page loads or refreshes, hide these elements
    $("#loader").hide();
    $("#encrypt-label").hide();
    $("label[for=encrypted],#encrypted").hide();
    $("label[for=notEncrypted],#notEncrypted").hide();
    $("#notEncrypted").prop("checked", true);
    $(".switch").hide();
    $("#chartContainer").hide();

    $('[name="page"]').on('change', function() {
        if ($(this).attr('id') == 'subredditPage') {
            $('#amount-label').text('Enter Number of Posts');
            $("#encrypt-label").hide();
            $("label[for=encrypted],#encrypted").hide();
            $("label[for=notEncrypted],#notEncrypted").hide();
        } else {
            $('#amount-label').text('Enter Number of Comments');
            $("#encrypt-label").show();
            $("#encrypted").show();
            $("label[for=encrypted],#encrypted").show();
            $("label[for=notEncrypted],#notEncrypted").show();
        }
    });
}

function init() {
    document.addEventListener('DOMContentLoaded', function () {
      let checkbox = document.querySelector('input[type="checkbox"]');

      checkbox.addEventListener('change', function () {
    //  when checked show right wing comments table and hide left wing
        if (checkbox.checked) {
          hideAllTables();
          $("#rightwing-table").show();
          console.log('Checked');
        } else {
          hideAllTables();
          $("#leftwing-table").show();
          console.log('Not checked');
        }
      });
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

function showComments() {
    $(".switch").hide();
    removeAllTables();
    $("#loader").show();
    $.ajax({
        type: "POST",
        url: '/getuserinput',
        contentType: "application/json",
        async: true,
        data: getUserInput(),

        success: function (success_data) {
            if (success_data){
                console.log(success_data)
                processRedditData(success_data.column_names, success_data.left_wing_dataset, success_data.right_wing_dataset)
            } else {
                console.log("Error, could not retrieve comments")
            }
        },
    });
}

function processRedditData(column_names, left_comments, right_comments){
    displayTable(column_names, left_comments, 'leftwing');
    displayTable(column_names, right_comments, 'rightwing');
    hideAllTables();
    $("#leftwing-table").show();
    displayPieChart(left_comments, right_comments);

    displayLineChart(left_comments, right_comments);
}

function addTable() {
    $('#table-div').append('<table id="table"></table>');
}

function removeAllTables() {
    $("#leftwing-table").remove();
    $("#rightwing-table").remove();
}

function hideAllTables() {
    $(".table").hide();
}

//function round(num) {
//    var m = Number((Math.abs(num) * 100).toPrecision(15));
//    return Math.round(m) / 100 * Math.sign(num);
//}

function round(value, precision) {
    var multiplier = Math.pow(10, precision || 0);
    return Math.round(value * multiplier) / multiplier;
}

function getReadableSentiment(value) {
    let threshold = 0.5;
    let rounded_value = round(((1 - value / threshold) * 100), 2);
    let readable_sentiment = rounded_value.toString() + "%";
    return readable_sentiment;
}

function displayTable(column_names, comments, sentiment) {
    $("#loader").hide();
    $(".switch").show();
//  TODO: WRITE CODE TO RESET TOGGLE SWITCH TO BE OFF/SHOW LEFT WING COMMENTS
    $("#chartContainer").show();
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
            let td  = document.createElement("td");
            let value = "";
            if (x == 0) {
                value = getReadableSentiment(comments[y][x])
            } else {
                value = comments[y][x];
            }
            let txt = document.createTextNode(value);
            td.appendChild(txt);
            tr.appendChild(td);
        }
    }
//  e.g. id="leftwing-table"
    let table_id = sentiment + '-table';
    table.setAttribute('id', table_id)
    table.setAttribute('class', 'table')

    console.log("Table sentiment value: " + sentiment)
    console.log(table);
}

function displayPieChart(left_comments, right_comments) {
    let total = left_comments.length + right_comments.length;
    let no_left = left_comments.length;
    let no_right = right_comments.length;
    var chart = new CanvasJS.Chart("chartContainer", {
        animationEnabled: true,
        title: {
            text: "Ratio of Left-Wing and Right-Wing Comments"
        },
        data: [{
            type: "pie",
            startAngle: 90,
            yValueFormatString: "##0.00\"%\"",
            showInLegend: "true",
            legendText: "{label}",
//            indexLabelFontSize: 16,
            indexLabel: "{label} - {y}",
            dataPoints: [
                {y: (no_left/total)*100, label: "Left-Wing"},
                {y: (no_right/total)*100, label: "Right-Wing"},
            ]
        }]
    });
    chart.render();
    console.log('Pie Chart Rendered Successfully!')
}

function displayLineChart(left, right) {
//  combine left and right wing data
    let dataset = left.concat(right);
//  x array stores (sentiment) values from 0 to 1 going up by e.g. 0.1
    let x = [];
    for (let i=0; i <=1; i+=0.1) x.push(i);
//  initialise y array with zero's
    let y = new Array(x.length);
    for (let i=0; i<x.length; ++i) y[i] = 0;

    let names = [[], [],  [],  [],  [],  [],  [],  [],  [],  [], []]
    let comments = [[], [], [], [], [], [], [], [], [], [], []]

//  y array stores a counter for the sentiment values
    for (let row=0; row<dataset.length; row++) {
        let sentiment_val = dataset[row][0];
        let comment = dataset[row][1];
        let name = dataset[row][2];
        let rounded_sentiment = round(sentiment_val, 1);
        let index = parseInt(rounded_sentiment*10);
        y[index] += 1;
        names[index].push(name);
        comments[index].push(comment);
    }

    var source = new Bokeh.ColumnDataSource({
        data: {
            'Sentiment': x,
            'Count': y,
        }
    });

    let page_type = document.querySelector('input[name="page"]:checked').value;
    let page_name = document.getElementById("page-search").value;

    // make the plot
    var plot = new Bokeh.Plot({
       title: "Sentiment Analysis for: " + page_type + page_name,
       plot_width: 800,
       plot_height: 800
    });

    // add axes to the plot
    var xaxis = new Bokeh.LinearAxis({ axis_label: "Sentiment Value", axis_line_color: null });
    var yaxis = new Bokeh.LinearAxis({ axis_label: "Number of Comments", axis_line_color: null });
    plot.add_layout(xaxis, "below");
    plot.add_layout(yaxis, "left");

    // add a Line glyph
    var line = new Bokeh.Line({
       x: { field: "Sentiment" },
       y: { field: "Count" },
       line_color: "#666699",
       line_width: 2
    });
    plot.add_glyph(line, source);

    Bokeh.Plotting.show(plot);

    console.log("Line Chart Rendered Successfully!")
}

init();
