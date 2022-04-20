"""Main module."""

import geopandas as gpd
import pysal as ps
import matplotlib.pyplot as plt
import libpysal as lps
from esda.moran import (Moran, Moran_Local)
from splot.esda import (moran_scatterplot, lisa_cluster, plot_moran_simulation)
from matplotlib.offsetbox import AnchoredText
import seaborn as sns
from seaborn import heatmap
import io
import base64


def generate_report(gdf):
    numeric_columns = list(gdf.select_dtypes(include=["int64","float64"]).columns)
    excluded_columns = set(list(gdf.columns))-set(numeric_columns)

    ##########----------SUMMARY PAGE----------##########

    #Create snapshot plot of Study Area
    study_area = gdf.plot(facecolor="none")
    study_area.figure.set_figheight(7)
    my_stringIObytes = io.BytesIO()
    study_area.figure.savefig(my_stringIObytes, format='jpg')
    my_stringIObytes.seek(0)
    study_area_image = base64.b64encode(my_stringIObytes.read()).decode('ascii')

    #Create Dataset Overview Table
    overview_string = '''
    <table class="table table-striped table-hover">
        </tr>
            <tr>
            <td>Coordinate System</td>
            <td>''' + str(gdf.crs) + '''</td>
        </tr>
        <tr>
            <td>Columns</td>
            <td>''' + str(gdf.shape[1]) + '''</td>
        </tr>
        <tr>
            <td>Rows</td>
            <td>''' + str(gdf.shape[0]) + '''</td>
        </tr>
        <tr>
            <td>Excluded Columns</td>
            <td>''' + str(excluded_columns) + '''</td>
        </tr>
        <tr>
            <td>Included Columns</td>
            <td>''' + str(numeric_columns) + '''</td>
    </table>'''

    #Create Descriptive Statistics Table
    descriptive_statistics = gdf.describe().round(2).to_html(classes="table table-striped table-hover", border = 0)

    #Create Sample Tables
    without_geom = gdf.drop(['geometry'], axis=1)
    head = without_geom.head(n=5).round(2).to_html(classes="table table-striped table-hover", border = 0)
    tail = without_geom.tail(n=5).round(2).to_html(classes="table table-striped table-hover", border = 0)

    #Create Summary Page HTML
    summary_page = '''
    <div class="table-responsive">
    <table>
    <tr>
        <td>
            <div>
                <h2>Study Area</h2>
                <img src="data:image/png;base64,''' + study_area_image +'''">
            </div>
        </td>
        <td>
            <div>
                <h2>Dataset Overview</h2>
                ''' + overview_string + '''
            </div>
            <div>
                <h2>Descriptive Statistics</h2>
                ''' + descriptive_statistics + '''
            </div>
        </td>
    </tr>
    <tr>
        <td>
            <h2>Sample Rows</h2>
            <div>
                <h3>First 5 rows</h3>
                ''' + head + '''
            </div>
        </td>
    </tr
    <tr>
        <td>
            <div>
                <h3>Last 5 rows</h3>
                ''' + tail + '''
            </div>
        </td>
    </tr>
    </table>
    </div>'''

    ##########----------NUMERIC COLUMN SUMMARIES----------##########

    #Create Spatial weights matrix
    weight_matrix = lps.weights.Queen.from_dataframe(gdf)
    weight_matrix.transform = 'r'

    image_array = []
    for cols in numeric_columns:

        #Create plot and grid
        plt.figure(figsize = (20, 12))
        grid = plt.GridSpec(3, 4, height_ratios=[1,4,7])
        #Populate grid with subplots
        g1 = plt.subplot(grid[0, 0])
        g2 = plt.subplot(grid[0:2,1])
        g3 = plt.subplot(grid[0:2,2])
        g4 = plt.subplot(grid[0:2,3])
        g5 = plt.subplot(grid[1,0])
        g6 = plt.subplot(grid[2,0])
        g7 = plt.subplot(grid[2,1])
        g8 = plt.subplot(grid[2,2])
        g9 = plt.subplot(grid[2,3])

        #Boxplot
        g1.boxplot(gdf[cols], vert=False)
        g1.set_title('Boxplot of ' + cols)

        #Moran's Calculations
        column_values = gdf[cols].values
        moransI_queen = Moran(gdf[cols], weight_matrix)
        moran_local = Moran_Local(column_values, weight_matrix)


        #Reference Distribution
        plot_moran_simulation(moransI_queen,aspect_equal=False, ax=g2)
        g2.set_title("Reference Distribution of " + cols)
        anchorText = "Moran's I: " + str(round(moransI_queen.I, 5)) + "\nn: " + str(moransI_queen.n) + "\np-value: " + str(moransI_queen.p_sim) + "\nz-score: " + str(round(moransI_queen.z_sim,5)) + "\nPermutations: " + str(moransI_queen.permutations)
        at = AnchoredText(anchorText, prop=dict(size=10), frameon=True, loc='upper right')
        g2.add_artist(at)
        #LISA Scatterplot
        moran_scatterplot(moran_local, p=0.05, ax=g3, aspect_equal=False)
        g3.set_title("Morans Local Scatterplot of " + cols)
        g3.set_xlabel(cols)
        g3.set_ylabel('Spatial Lag of ' + cols)
        #LISA Cluster Map
        lisa_cluster(moran_local, gdf, ax=g4, legend_kwds={'loc': 'best'})
        g4.set_title("LISA Cluster Map of " + cols)

        #Histogram
        g5.hist(gdf[cols], color='teal',edgecolor='black')
        g5.set_title('Histogram of ' + cols)
        g5.set_xlabel(cols)
        g5.set_ylabel('Count')

        #Quantiles
        g6.set_title('Quantiles')
        gdf.plot(ax = g6, column=cols, scheme='quantiles', legend=True, legend_kwds={'loc': 'best', 'title': cols, "fmt": "{:.0f}"})
        #Equal Intervals
        g7.set_title('Equal Intervals')
        gdf.plot(ax = g7, column=cols, scheme='equal_interval', legend=True, legend_kwds={'loc': 'best', 'title': cols, "fmt": "{:.0f}"})
        #Natural breaks
        g8.set_title('Natural Breaks')
        gdf.plot(ax = g8, column=cols, scheme='natural_breaks', legend=True, legend_kwds={'loc': 'best', 'title': cols, "fmt": "{:.0f}"})
        #Percentiles
        g9.set_title('Percentiles')
        gdf.plot(ax = g9, column=cols, scheme='Percentiles', legend=True, legend_kwds={'loc': 'best', 'title': cols, "fmt": "{:.0f}"})

        plt.tight_layout()
        my_stringIObytes = io.BytesIO()
        plt.savefig(my_stringIObytes, format='jpg')
        my_stringIObytes.seek(0)
        image_array.append(base64.b64encode(my_stringIObytes.read()).decode('ascii'))
        plt.close()

    #Correlation
    correlation_matrix = gdf.corr()
    correlation_heatmap = sns.heatmap(correlation_matrix, cmap='RdBu_r', annot=True, cbar=False, square=True)
    my_stringIObytes = io.BytesIO()
    plt.savefig(my_stringIObytes, format='jpg', bbox_inches='tight',pad_inches=0.5)
    my_stringIObytes.seek(0)
    correlation_heatmap_image = base64.b64encode(my_stringIObytes.read()).decode('ascii')
    plt.close()

    #Pairplot
    pairplot = sns.pairplot(gdf, height=1.5,plot_kws=dict(marker="."))
    my_stringIObytes = io.BytesIO()
    plt.savefig(my_stringIObytes, format='jpg')
    my_stringIObytes.seek(0)
    pairplot = base64.b64encode(my_stringIObytes.read()).decode('ascii')

    ##########----------HTML REPORT SETUP----------##########

    #Create String for all Tabs and all div/figures

    tab_string = ""
    div_string = ""
    count = 0
    for cols in numeric_columns:
        tab_string+=str('<button class="tablinks" onclick="openTab(event, \'' + cols +  '\')">' + cols + '</button>\n')
        div_string+=str('<div id="' + cols + '" class="tabcontent table-responsive"><img src="data:image/png;base64,' + image_array[count] +'"></div>\n')
        count=count+1

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
        + tab_string + '''
        <button class="tablinks" onclick="openTab(event, 'Correlation')">Correlation</button>
    </div>

    <div id="Summary" class="tabcontent">
        ''' + summary_page + '''
    </div>'''
    + div_string + '''
    <div id="Correlation" class="tabcontent">
    <table>
        <tr>
            <td>
                <div class="table-responsive">
                    <h2>Correlation Heatmap</h2>
                    <img src="data:image/png;base64,''' + correlation_heatmap_image +'''">
                </div>
            </td>
            <td>
                <div class="table-responsive">
                    <h2>Pairplot</h2>
                    <img src="data:image/png;base64,''' + pairplot +'''">
                </div>
            </td>
        </tr>
    </table>

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

def generate_html_string(gdf):
    numeric_columns = list(gdf.select_dtypes(include=["int64","float64"]).columns)
    excluded_columns = set(list(gdf.columns))-set(numeric_columns)

    ##########----------SUMMARY PAGE----------##########

    #Create snapshot plot of Study Area
    study_area = gdf.plot(facecolor="none")
    study_area.figure.set_figheight(7)
    my_stringIObytes = io.BytesIO()
    study_area.figure.savefig(my_stringIObytes, format='jpg')
    my_stringIObytes.seek(0)
    study_area_image = base64.b64encode(my_stringIObytes.read()).decode('ascii')

    #Create Dataset Overview Table
    overview_string = '''
    <table class="table table-striped table-hover">
        </tr>
            <tr>
            <td>Coordinate System</td>
            <td>''' + str(gdf.crs) + '''</td>
        </tr>
        <tr>
            <td>Columns</td>
            <td>''' + str(gdf.shape[1]) + '''</td>
        </tr>
        <tr>
            <td>Rows</td>
            <td>''' + str(gdf.shape[0]) + '''</td>
        </tr>
        <tr>
            <td>Excluded Columns</td>
            <td>''' + str(excluded_columns) + '''</td>
        </tr>
        <tr>
            <td>Included Columns</td>
            <td>''' + str(numeric_columns) + '''</td>
    </table>'''

    #Create Descriptive Statistics Table
    descriptive_statistics = gdf.describe().round(2).to_html(classes="table table-striped table-hover", border = 0)

    #Create Sample Tables
    without_geom = gdf.drop(['geometry'], axis=1)
    head = without_geom.head(n=5).round(2).to_html(classes="table table-striped table-hover", border = 0)
    tail = without_geom.tail(n=5).round(2).to_html(classes="table table-striped table-hover", border = 0)

    #Create Summary Page HTML
    summary_page = '''
    <div class="table-responsive">
    <table>
    <tr>
        <td>
            <div>
                <h2>Study Area</h2>
                <img src="data:image/png;base64,''' + study_area_image +'''">
            </div>
        </td>
        <td>
            <div>
                <h2>Dataset Overview</h2>
                ''' + overview_string + '''
            </div>
            <div>
                <h2>Descriptive Statistics</h2>
                ''' + descriptive_statistics + '''
            </div>
        </td>
    </tr>
    <tr>
        <td>
            <h2>Sample Rows</h2>
            <div>
                <h3>First 5 rows</h3>
                ''' + head + '''
            </div>
        </td>
    </tr
    <tr>
        <td>
            <div>
                <h3>Last 5 rows</h3>
                ''' + tail + '''
            </div>
        </td>
    </tr>
    </table>
    </div>'''

    ##########----------NUMERIC COLUMN SUMMARIES----------##########

    #Create Spatial weights matrix
    weight_matrix = lps.weights.Queen.from_dataframe(gdf)
    weight_matrix.transform = 'r'

    image_array = []
    for cols in numeric_columns:

        #Create plot and grid
        plt.figure(figsize = (20, 12))
        grid = plt.GridSpec(3, 4, height_ratios=[1,4,7])
        #Populate grid with subplots
        g1 = plt.subplot(grid[0, 0])
        g2 = plt.subplot(grid[0:2,1])
        g3 = plt.subplot(grid[0:2,2])
        g4 = plt.subplot(grid[0:2,3])
        g5 = plt.subplot(grid[1,0])
        g6 = plt.subplot(grid[2,0])
        g7 = plt.subplot(grid[2,1])
        g8 = plt.subplot(grid[2,2])
        g9 = plt.subplot(grid[2,3])

        #Boxplot
        g1.boxplot(gdf[cols], vert=False)
        g1.set_title('Boxplot of ' + cols)

        #Moran's Calculations
        column_values = gdf[cols].values
        moransI_queen = Moran(gdf[cols], weight_matrix)
        moran_local = Moran_Local(column_values, weight_matrix)


        #Reference Distribution
        plot_moran_simulation(moransI_queen,aspect_equal=False, ax=g2)
        g2.set_title("Reference Distribution of " + cols)
        anchorText = "Moran's I: " + str(round(moransI_queen.I, 5)) + "\nn: " + str(moransI_queen.n) + "\np-value: " + str(moransI_queen.p_sim) + "\nz-score: " + str(round(moransI_queen.z_sim,5)) + "\nPermutations: " + str(moransI_queen.permutations)
        at = AnchoredText(anchorText, prop=dict(size=10), frameon=True, loc='upper right')
        g2.add_artist(at)
        #LISA Scatterplot
        moran_scatterplot(moran_local, p=0.05, ax=g3, aspect_equal=False)
        g3.set_title("Morans Local Scatterplot of " + cols)
        g3.set_xlabel(cols)
        g3.set_ylabel('Spatial Lag of ' + cols)
        #LISA Cluster Map
        lisa_cluster(moran_local, gdf, ax=g4, legend_kwds={'loc': 'best'})
        g4.set_title("LISA Cluster Map of " + cols)

        #Histogram
        g5.hist(gdf[cols], color='teal',edgecolor='black')
        g5.set_title('Histogram of ' + cols)
        g5.set_xlabel(cols)
        g5.set_ylabel('Count')

        #Quantiles
        g6.set_title('Quantiles')
        gdf.plot(ax = g6, column=cols, scheme='quantiles', legend=True, legend_kwds={'loc': 'best', 'title': cols, "fmt": "{:.0f}"})
        #Equal Intervals
        g7.set_title('Equal Intervals')
        gdf.plot(ax = g7, column=cols, scheme='equal_interval', legend=True, legend_kwds={'loc': 'best', 'title': cols, "fmt": "{:.0f}"})
        #Natural breaks
        g8.set_title('Natural Breaks')
        gdf.plot(ax = g8, column=cols, scheme='natural_breaks', legend=True, legend_kwds={'loc': 'best', 'title': cols, "fmt": "{:.0f}"})
        #Percentiles
        g9.set_title('Percentiles')
        gdf.plot(ax = g9, column=cols, scheme='Percentiles', legend=True, legend_kwds={'loc': 'best', 'title': cols, "fmt": "{:.0f}"})

        plt.tight_layout()
        my_stringIObytes = io.BytesIO()
        plt.savefig(my_stringIObytes, format='jpg')
        my_stringIObytes.seek(0)
        image_array.append(base64.b64encode(my_stringIObytes.read()).decode('ascii'))
        plt.close()

    #Correlation
    correlation_matrix = gdf.corr()
    correlation_heatmap = sns.heatmap(correlation_matrix, cmap='RdBu_r', annot=True, cbar=False, square=True)
    my_stringIObytes = io.BytesIO()
    plt.savefig(my_stringIObytes, format='jpg', bbox_inches='tight',pad_inches=0.5)
    my_stringIObytes.seek(0)
    correlation_heatmap_image = base64.b64encode(my_stringIObytes.read()).decode('ascii')
    plt.close()

    #Pairplot
    pairplot = sns.pairplot(gdf, height=1.5,plot_kws=dict(marker="."))
    my_stringIObytes = io.BytesIO()
    plt.savefig(my_stringIObytes, format='jpg')
    my_stringIObytes.seek(0)
    pairplot = base64.b64encode(my_stringIObytes.read()).decode('ascii')

    ##########----------HTML REPORT SETUP----------##########

    #Create String for all Tabs and all div/figures

    tab_string = ""
    div_string = ""
    count = 0
    for cols in numeric_columns:
        tab_string+=str('<button class="tablinks" onclick="openTab(event, \'' + cols +  '\')">' + cols + '</button>\n')
        div_string+=str('<div id="' + cols + '" class="tabcontent table-responsive"><img src="data:image/png;base64,' + image_array[count] +'"></div>\n')
        count=count+1

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
        + tab_string + '''
        <button class="tablinks" onclick="openTab(event, 'Correlation')">Correlation</button>
    </div>

    <div id="Summary" class="tabcontent">
        ''' + summary_page + '''
    </div>'''
    + div_string + '''
    <div id="Correlation" class="tabcontent">
    <table>
        <tr>
            <td>
                <div class="table-responsive">
                    <h2>Correlation Heatmap</h2>
                    <img src="data:image/png;base64,''' + correlation_heatmap_image +'''">
                </div>
            </td>
            <td>
                <div class="table-responsive">
                    <h2>Pairplot</h2>
                    <img src="data:image/png;base64,''' + pairplot +'''">
                </div>
            </td>
        </tr>
    </table>

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
    return html_string