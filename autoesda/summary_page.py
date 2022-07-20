"""Module to create the Summary Page."""

import geopandas as gpd
import io
import base64


def summary_html(gdf):

    numeric_columns = list(gdf.select_dtypes(include=["int64","float64"]).columns)
    excluded_columns = set(list(gdf.columns))-set(numeric_columns)

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
    summary_page_string = '''
    <div id="Summary" class="tabcontent">
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
        </div>
    </div>'''

    return summary_page_string