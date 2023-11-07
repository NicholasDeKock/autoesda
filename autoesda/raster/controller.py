import os
import time
import datetime
os.environ['USE_PYGEOS'] = '0'
from .model import *

def _encode_image(image):
    my_stringIObytes = io.BytesIO()
    image.tight_layout()
    image.figure.savefig(my_stringIObytes, format="png")
    my_stringIObytes.seek(0)
    plt.close()
    return base64.b64encode(my_stringIObytes.read()).decode("ascii")

def _summary_page(dataset):
    _summary_page_string = """
<div id="Summary" class="tabcontent">
<div class="grid-container">
    <div class="grid-item item-raster-information">
      <h2>Dataset Overview</h2>
      """ + dataset.overview_statistics().T.to_html(border="1", classes="dataframe mystyle") +"""
    </div>
    <div class="grid-item item-band-information">
      <h2>Descriptive Statistics</h2>
     """ + dataset.raster_statistics().T.to_html(border="1", classes="dataframe mystyle") + """
    </div>
  </div>
</div>"""
    
    return _summary_page_string

def _band_information_page(dataset):
    _tab_string = ""
    _band_information_page_string = ""

    for band in dataset.bands():
        _tab_string += str("""<button class="tablinks" onclick="openTab(event, '""" + band.name + """')">"""+ band.name +"""</button>\n""")
        _band_information_page_string += ("""
<div id='"""+ band.name +"""' class="tabcontent">
<div class="grid-container">
  <div class="grid-item item-band-statistics">
    <h2>Band Statistics</h2>
""" + band.band_statistics().T.round(3).to_html(border="1", classes="dataframe mystyle") + """
  </div>
  <div class="grid-item item-band-descriptive">
    <h2>Probability Histogram</h2>
    <img src="data:image/png;base64,""" + _encode_image(band.histogram_figure()) + """">
  </div>
  <div class="grid-item item-local-moran">
    <h2>Local Moran's I</h2>
    <img src="data:image/png;base64,""" + _encode_image(band.local_moran_figure()) + """">
  </div>
  <div class="grid-item item-local-geary">
    <h2>Local Geary's C</h2>
    <img src="data:image/png;base64,""" + _encode_image(band.local_geary_figure()) + """">
  </div>
  <div class="grid-item item-choropleth">
    <h2>Choropleth Maps</h2>
    <img src="data:image/png;base64,""" + _encode_image(band.choropleth_figure()) + """">
  </div>
</div>
</div>
        """)
    return _tab_string, _band_information_page_string

def _correlation_page(dataset):
    _correlation_page_string = """
    <div id="Correlation" class="tabcontent">
<div class="grid-container">
  <div class="grid-item item-correlation">
    <h2>Correlation Heatmaps</h2>
    <img src="data:image/png;base64,""" + _encode_image(dataset.correlation_figure()) + """">
  </div>
  <div class="grid-item item-pairplot">
    <h2>Pairwise Plot</h2>
    <img src="data:image/png;base64,""" + _encode_image(dataset.pairplot_figure()) + """">
  </div>
</div>
</div>
    """

    return _correlation_page_string

def _about_page(start_time):
    
    _about_page_string = """
    <div id="About" class="tabcontent">
      <h3> Thank you for using autoESDA</h3>

      <p>Check out our <a href="https://nicholasdekock.github.io/autoesda/report-user-guide.md"target="_blank">User Guide</a> for an explanation on how the report is generated and how it can be interpreted.</p>

      <p>The source code for this project can be viewed <a href="https://github.com/NicholasDeKock/autoESDA"target="_blank">here</a> - we welcome any suggestions and/or contributions.</p>

      <p><b>Report Saved: </b>""" + str(datetime.datetime.now()) +"""</p>

      <p><b>Generation Time: </b>""" + str(round(time.time() - start_time, 4))  +"""</p>
    </div>
    """
    
    return _about_page_string

def generate_report(input_data, filename="autoESDA-raster-report"):

  starttime = time.time()
  dataset = Raster(input_data)
  
  correlation_page_string = _correlation_page(dataset)
  summary_page_string = _summary_page(dataset)
  band_information = _band_information_page(dataset)
  band_information_tab_string = band_information[0]
  band_information_page_string = band_information[1]
  about_page_string = _about_page(starttime)

  html_string = str(
        """
<!DOCTYPE html>
<html>
<head>
<style>
body {font-family: Arial;}

/* Style the tab */
.tab {
overflow: hidden;
border: 1px solid #ccc;
background-color: #f1f1f1;
position: fixed;
top: 0;
width: 100%;
z-index: 1;
display: block;
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

.mystyle {
    font-size: 11pt; 
    font-family: Arial;
    border-collapse: collapse; 
    border: 1px solid silver;
    overflow-x: scroll;
}

.mystyle td, th {
    padding: 5px;
}

.mystyle tr:nth-child(even) {
    background: #E0E0E0;
}

.mystyle tr:hover {
    background: silver;
    cursor: pointer;
}

img {
max-width:100%; 
height:auto;
}

h2 {
text-align: left;
}

#div-section {
border: 2px solid;
border-radius: 25px; 
padding: 10px;
}

.grid-container {
  display: grid;
  grid-gap: 1rem;
  padding: 10px;
  overflow-x: auto;
}

.grid-item {
  background-color: #ffffff;
  text-align: center;
  padding: 5px;
  margin: 10;
  /* font-size: 30px; */
  border: 1px solid rgb(115, 115, 120);
  /* border-radius: 25px; */
  overflow-x: auto;
}

.item-raster-information {
  grid-row: 1;
  grid-column: 1;
}

.item-band-information {
  grid-row: 1;
  grid-column: 2;
}

.item-band-statistics {
    grid-row: 1;
    grid-column: 1;
}

.item-band-descriptive {
  grid-column: 1;
  grid-row: 2;
}

.item-local-moran {
  grid-column: 2;
  grid-row: 1;
}

.item-local-geary {
  grid-column: 3;
  grid-row: 1;
}

.item-choropleth {
  grid-column: 2 / span 2;
  grid-row: 2;
}

.item-correlation {
  grid-column: 1;
  grid-row: 1;
}

.item-pairplot {
  grid-column: 2;
  grid-row: 1;
}

</style>
</head>
<body onload="openTab(event, 'Summary')">
<!-- MENU BAR -->
<a href="https://github.com/NicholasDeKock/autoesda" target="_blank">
<div class="tab">
    <img src="data:image/png;base64,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" width="50" align="left">
    </a>
    <button class="tablinks" onclick="openTab(event, 'Summary')">Summary</button>
"""
+ band_information_tab_string +
"""
<button class="tablinks" onclick="openTab(event, 'Correlation')">Correlation</button>
<button class="tablinks" onclick="openTab(event, 'About')">About</button>
</div>
<br>
<br>
<br>
<!-- SUMMARY PAGE -->
""" 
+ summary_page_string + band_information_page_string +                   
"""

<!-- CORRELATION PAGE -->
""" + correlation_page_string + """
</div>

<!-- ABOUT PAGE -->
""" + about_page_string + """
</div>

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
   """)
    
  output_file_name = f"{filename}.html"
  file = open(output_file_name, "w")
  file.write(html_string)
  file.close()
  print(f"Success! Report has been saved to your working folder directory as '{output_file_name}'.")