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
