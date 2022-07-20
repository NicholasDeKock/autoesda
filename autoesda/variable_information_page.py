"""Module to create the Variable Information Page."""
import matplotlib.pyplot as plt
import libpysal as lps
from esda.moran import (Moran, Moran_Local)
from splot.esda import (moran_scatterplot, lisa_cluster, plot_moran_simulation)
from matplotlib.offsetbox import AnchoredText
import io
import base64

##########----------NUMERIC COLUMN SUMMARIES----------##########

def variable_information_html(gdf):

    numeric_columns = list(gdf.select_dtypes(include=["int64","float64"]).columns)
    excluded_columns = set(list(gdf.columns))-set(numeric_columns)

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

    #Create String for all Tabs and all div/figures

    tab_string = ""
    div_string = ""
    count = 0
    for cols in numeric_columns:
        tab_string+=str('<button class="tablinks" onclick="openTab(event, \'' + cols +  '\')">' + cols + '</button>\n')
        div_string+=str('<div id="' + cols + '" class="tabcontent table-responsive"><img src="data:image/png;base64,' + image_array[count] +'"></div>\n')
        count=count+1

    return tab_string, div_string