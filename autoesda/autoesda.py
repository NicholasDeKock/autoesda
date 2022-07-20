"""Main module."""

import summary_page
import variable_information_page
import correlation_page

# import io
# import base64


def generate_report(gdf):


    summary_page_string = summary_page.summary_html(gdf)
    variable_information_string = variable_information_page.variable_information_html(gdf)
    variable_information_tab_string = variable_information_string[0]
    variable_information_div_string = variable_information_string[1]
    correlation_page_string = correlation_page.correlation_html(gdf)

    ##########----------HTML REPORT SETUP----------##########

    #Create String for HTML report
    html_string = str('''
    <!DOCTYPE html>
    <html>
    <head>
    <link rel="stylesheet" href="https://maxcdn.bootstrapcdn.com/bootstrap/3.3.1/css/bootstrap.min.css">
    <link rel="stylesheet" href="https://www.w3schools.com/w3css/4/w3.css">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <style>
    body {font-family: Arial;}

    /* Style the tab */
    .tab {
    overflow: hidden;
    border: 1px solid #ccc;
    background-color: #f1f1f1;
    }

    /* Style the buttons inside the tab */
    .tab button {
    background-color: inherit;
    float: left;
    border: none;
    outline: none;
    cursor: pointer;
    padding: 14px 16px;
    transition: 0.3s;
    font-size: 17px;
    }

    /* Change background color of buttons on hover */
    .tab button:hover {
    background-color: #ddd;
    }

    /* Create an active/current tablink class */
    .tab button.active {
    background-color: #ccc;
    }

    /* Style the tab content */
    .tabcontent {
    display: none;
    padding: 6px 12px;
    border: 1px solid #ccc;
    border-top: none;
    }

    div {
    padding:0px;
    }
    .table-hover tbody tr:hover td, .table-hover tbody tr:hover th {
    background-color: #d0e8f7;
    }
    .table{
        white-space: nowrap;
        width: 1%;
    }
    img {max-width:100%; height:auto}

    </style>
    </head>
    <body onload="openTab(event, 'Summary')">

    <h1>autoESDA report</h1>
    <p>Click on the buttons inside the tabbed menu:</p>

    <div class="tab">
        <button class="tablinks" onclick="openTab(event, 'Summary')">Summary</button>'''
        + variable_information_tab_string + '''
        <button class="tablinks" onclick="openTab(event, 'Correlation')">Correlation</button>
    </div>

    ''' + summary_page_string + '''
    ''' + variable_information_div_string + '''
    ''' + correlation_page_string + '''
    <script>
    function openTab(evt, tabName) {
    var i, tabcontent, tablinks;
    tabcontent = document.getElementsByClassName("tabcontent");
    for (i = 0; i < tabcontent.length; i++) {
        tabcontent[i].style.display = "none";
    }
    tablinks = document.getElementsByClassName("tablinks");
    for (i = 0; i < tablinks.length; i++) {
        tablinks[i].className = tablinks[i].className.replace(" active", "");
    }
    document.getElementById(tabName).style.display = "block";
    evt.currentTarget.className += " active";
    }
    </script>

    </body>
    </html> 

    ''')
    file = open('autoESDAreport.html', 'w')
    file.write(html_string)
    file.close()
    print('Success! Report has been saved to your working folder directory.')