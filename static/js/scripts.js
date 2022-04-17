// Determine which options to show depending on if user chose subreddit or user
window.onload = function() {
    changes()
};

function changes() {
//  when page loads or refreshes, hide these elements
    $("#loader").hide();
    $("#top-radio").prop("checked", true);
    $(".switch").hide();
    $("#chartContainer").hide();
    $("#show-graph-btn").hide();

    $('[name="page"]').on('change', function() {
        if ($(this).attr('id') == 'subredditPage') {
            $('#amount-label').text('Enter Number of Posts');
        } else {
            $('#amount-label').text('Enter Number of Comments');
        }
    });
}

// add event listener to the table slider
// when user clicks on slider, show appropriate visualisations
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

// add event listener to each row
// when user clicks on row, username is filled automatically
function addRowHandlers(table_id) {
  var table = document.getElementById(table_id);
  var rows = table.getElementsByTagName("tr");
  for (i = 0; i < rows.length; i++) {
    var currentRow = table.rows[i];
    var createClickHandler = function(row) {
      return function() {
        var cell = row.getElementsByTagName("td")[2];
        var username = cell.innerHTML;
        document.getElementById("page-search").value = username;
      };
    };
    currentRow.onclick = createClickHandler(currentRow);
  }
}

// retrieves user input
function getUserInput() {
    let page_type = document.querySelector('input[name="page"]:checked').value;
    let page_name = document.getElementById("page-search").value;
    let no_posts = document.getElementById("no-posts").value;
    let sort_type = document.querySelector('input[name="sort"]:checked').value;
    let is_encrypted = "no";
    // reddit username length cannot be > 20 or < 3
    if (page_name.length > 20) {
        is_encrypted = "yes";
    }

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
    $("#chartContainer").hide();
    $(".switch").hide();
//  when page loads, remove previously created visualisations
    removeAllTables();
    removeAllLineCharts();
//  show loader
    $("#loader").show();
    $.ajax({
        type: "POST",
        url: '/getuserinput',
        contentType: "application/json",
        async: true,
        // data field handles what we want to sent to backend
        data: getUserInput(),
        // success function handles incoming data from backend
        success: function (res) {
            if (res.connection == 'Successful') {
                console.log(res)
                processRedditData(res.column_names,
                    res.left_wing_dataset, res.right_wing_dataset)
                successAlert();
                console.log("Reddit data sent and received successfully!");
            } else if (res.connection == '404') {
                $("#loader").hide();
                warningAlert();
            } else {
                $("#loader").hide();
                failureAlert();
                console.log("Error, data could not be retrieved from flask server");
            }
        },
    });
}

function processRedditData(column_names, left_comments, right_comments){
    displayTable(column_names, left_comments, 'leftwing');
    displayTable(column_names, right_comments, 'rightwing');

//  make table rows clickable to easily get username
    addRowHandlers("leftwing-table");
    addRowHandlers("rightwing-table");

//  only show left-wing table initially
    hideAllTables();
    $("#leftwing-table").show();
    $("#show-graph-btn").show();

//  display all other visualisations
    displayPieChart(left_comments, right_comments);
    displayLineChart(left_comments, 'Left');
    displayLineChart(right_comments, 'Right');
}

function displayTable(column_names, comments, sentiment) {
    $("#loader").hide();
    $("#togBtn").prop('checked', false);
    $(".switch").show();
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
                let rounded_value = getReadableSentiment(comments[y][x]);
                value = rounded_value.toString() + "%";
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

function displayLineChart(dataset, sentiment) {
//  initialise chart dataset, format: {x: y, comments} -> {sentiment value: [counter, comments array]}
    let chart_data = {};
    let step = 1;
    for (let x=0; x<=100; x+=step) {
//      round sentiment to avoid floating point inaccuracies
//        let rounded_sentiment = parseFloat(x.toFixed(2));
//        let rounded_sentiment = round(x);
        chart_data[x] = [0, []];
    }

    console.log('initialised data:');
    console.log(chart_data);

//  fill in arrays and dictionary
    for (let row=0; row<dataset.length; row++) {
        let sentiment_val = dataset[row][0];
        let comment = dataset[row][1];
        let name = dataset[row][2];
        let rounded_sentiment = getReadableSentiment(sentiment_val);
        if (rounded_sentiment % step == 0) {
    //      get values from dictionary
            let counter = chart_data[rounded_sentiment][0];
            let comments = chart_data[rounded_sentiment][1];
    //      update values
            counter += 1;
            comments.push(comment);
    //      update dictionary
            chart_data[rounded_sentiment] = [counter, comments]
        }
    }

    console.log('filled dataset:');
    console.log(chart_data);

//  separate data from dictionary into separate arrays
    let x = [];
    let y = [];
    let comments = [];
    for (const [sentiment, values] of Object.entries(chart_data)) {
        x.push(sentiment);
        y.push(values[0]);
        comments.push(values[1]);
    }

    console.log('x axis values:');
    console.log(x);
    console.log('y axis values:');
    console.log(y);
    console.log('comments arrays');
    console.log(comments);

    var source = new Bokeh.ColumnDataSource({
        data: {
            'Sentiment': x,
            'Counter': y,
            'Comment': comments
        }
    });

    let page_type = document.querySelector('input[name="page"]:checked').value;
    let page_name = document.getElementById("page-search").value;

    // make the plot
    var plot = new Bokeh.Plot({
       title: sentiment + " Wing Sentiment Analysis for: " + page_type + page_name,
       plot_width: 650,
       plot_height: 650
    });

    // define axis titles, locations and add axis to the plot
    var xaxis = new Bokeh.LinearAxis({ axis_label: "Sentiment Weight (%)", axis_line_color: null });
    var yaxis = new Bokeh.LinearAxis({ axis_label: "Number of Comments", axis_line_color: null });
    plot.add_layout(xaxis, "below");
    plot.add_layout(yaxis, "left");

    let line_colour = "dodgerblue";
    if (sentiment == 'Right') {
        line_colour = "red";
    }

    // add a Line glyph
    var line = new Bokeh.Line({
       x: { field: "Sentiment" },
       y: { field: "Counter" },
       line_color: line_colour,
       line_width: 2
    });
    plot.add_glyph(line, source);

    // add hover tool for more interactiveness
    var tooltip = (
        "<div> <p> Sentiment Weight: @Sentiment%</p> </div>" +
        "<div> <p> Sample Comments: </p> <marquee behavior=\"scroll\" direction=\"left\">@Comment</marquee></div>"
    );
    var hover = new Bokeh.HoverTool({
        tooltips: tooltip
    });
    plot.add_tools(hover);

    // add extra tools
    plot.add_tools(new Bokeh.ResetTool());
    plot.add_tools(new Bokeh.PanTool());
    plot.add_tools(new Bokeh.ZoomInTool());
    plot.add_tools(new Bokeh.ZoomOutTool());
    plot.add_tools(new Bokeh.SaveTool());
    plot.toolbar_location = "right";

    // show plot
    let chart_div = '#' + sentiment + '-line-div';
    Bokeh.Plotting.show(plot, chart_div);

    console.log(sentiment + " Wing Line Chart Rendered Successfully!")
}

// Helper Functions
function successAlert() {
    $( "div.success" ).fadeIn( 300 ).delay( 3000 ).fadeOut( 400 );
}

function failureAlert() {
    $( "div.failure" ).fadeIn( 300 ).delay( 3000 ).fadeOut( 400 );
}

function warningAlert() {
    $( "div.warning" ).fadeIn( 300 ).delay( 3000 ).fadeOut( 400 );
}

function addTable() {
    $('#table-div').append('<table id="table"></table>');
}

function removeAllTables() {
    $("#leftwing-table").remove();
    $("#rightwing-table").remove();
}

function removeAllLineCharts() {
    $("#Left-line-div").empty();
    $("#Right-line-div").empty();
}

function hideAllTables() {
    $(".table").hide();
}

function round(value, precision) {
    var multiplier = Math.pow(10, precision || 0);
    return Math.round(value * multiplier) / multiplier;
}

function getReadableSentiment(value) {
    let threshold = 0.5;
    let formatted_val = Math.abs((1 - value / threshold) * 100);
    let rounded_value = round(formatted_val);
//    let readable_sentiment = rounded_value.toString() + "%";
    return rounded_value;
}

init();
