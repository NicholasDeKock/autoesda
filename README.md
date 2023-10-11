# autoESDA


[![image](https://img.shields.io/pypi/v/autoesda.svg)](https://pypi.python.org/pypi/autoesda)
[![image](https://img.shields.io/conda/vn/conda-forge/autoesda.svg)](https://anaconda.org/conda-forge/autoesda)
![Conda](https://img.shields.io/conda/dn/conda-forge/autoesda)
[![image](https://github.com/NicholasDeKock/autoesda/workflows/docs/badge.svg)](https://nicholasdekock.github.io/autoesda/)
[![image](https://github.com/NicholasDeKock/autoesda/workflows/build/badge.svg)](https://github.com/giswqs/autoesda/actions?query=workflow%3Abuild)
[![image](https://img.shields.io/pypi/l/autoesda?color=yellow&label=Licence&logo=BSD-3-Clause)](https://opensource.org/licenses/BSD-3-Clause)
![Visitor Badge](https://visitor-badge.laobi.icu/badge?page_id=NicholasDeKock.autoesda)

**A Python package that automates the exploratory spatial data analysis (ESDA) process by summarising the results into an HTML report.**

## Table of Contents
1. **Introduction**
2. **Key features**
3. **Installation**
4. **Dependancies**
5. **Usage**
6. **Examples**
7. **Contributing**
8. **License**
9. **References**
10. **Credits**

### 1. Introduction
Exploratory spatial data analysis (ESDA) is a term used to describe a various functions used to gain a surface-level understanding of a spatial dataset. Currently the ESDA process is repetitive as each of these functions need to be calculated individually. This makes it quite a time consuming process and also includes a large margin for human-induced errors. Additionally, results are not often easily viewed side-by-side for easy comparison and sharing with people who may not have the technical skills to do so.

**autoesda** is the solution to this by allowing the user to execute one line of code to generate an information-rich HTML report that can easily be shared with others.

### 2. Key features
- **HTML output report**
- **Extent map**
- **Dataset overview** (coordinate system, number of rows/columns, which rows/columns have been included/excluded in the report)
- **Descriptive statistics** (count, mean, standard deviation, minimum/maximum, 25<sup>th</sup>/50<sup>th</sup>/75<sup>th</sup> percentiles)
- **Sample of dataset**
- **Boxplot**
- **Histogram**
- **Moran's I simulation** (moran's I, number of features, p-value, z-score, number of permutations)
- **Local Indicator of Spatial Autocorrelation** (local scatterplot, LISA cluster map)
- **Choropleth maps** (quantiles, equal intervals, natural breaks, and percentiles classification schemes)
- **Correlation** (correlation matrix/heatmap, pairwise plot)

### 3. Installation
**autoesda** is available on [PyPI](https://pypi.org/project/autoesda/), to install **autoesda**, run this command in your terminal:
```
pip install autoesda
```
[geopandas](https://github.com/geopandas/geopandas) is a primary dependancy of **autoesda** and there are known challenges assosciated with using pip to install geopandas. The recommended strategy is thus, to use **autoesda** in a `conda environment`.

For advanced users, you can follow [this](https://geopandas.org/en/stable/getting_started/install.html) documentation which will guide you through the geopandas installation by downloading the [unofficial binary files](https://www.lfd.uci.edu/~gohlke/pythonlibs/) of some of the [geopandas](https://github.com/geopandas/geopandas) dependancies.

**autoesda** is also available on [conda-forge](https://anaconda.org/conda-forge/autoesda). If you have [Anaconda](https://www.anaconda.com/products/distribution#download-section) or [Miniconda](https://docs.conda.io/en/latest/miniconda.html) installed on your computer you can use this command in your Anaconda/Miniconda prompt:
```
conda install autoesda
```

### 4. Dependancies
- [geopandas](https://github.com/geopandas/geopandas)
- [pysal](https://github.com/pysal/pysal)
- [matplotlib](https://github.com/matplotlib/matplotlib)
- [libpysal](https://github.com/pysal/libpysal)
- [esda](https://github.com/pysal/esda)
- [splot](https://github.com/pysal/splot)
- [seaborn](https://github.com/mwaskom/seaborn)

### 5. Usage
To start off with, you need to ensure that you have imported both *geopandas* and *autoesda*.
```
import geopandas as gpd
import autoesda
```

Once both libraries have been sucessfully imported, you can import your dataset as a GeoDataFrame. This is done using *geopandas*. To read more about compatible file types, read the geopandas [documentation](https://geopandas.org/en/stable/docs/user_guide/io.html). In this example, a shapefile is imported.
```
gdf = gpd.read_file(r'example-file-path\example-shapefile.shp')
```

Once your data is stored in a GeoDataFrame, you can generate the report. 
```
autoesda.generate_report(gdf)
```

The report will be saved to your working file directory.

### 6. Example Reports
| Vector Reports | Raster Reports |
| ---------- | ---------- |
| [Old COJ Demographic Data](https://autoesda.github.io/autoESDA-static/)| Global Terrestrial Precipitation <br>  [Band 1](Link) \| [Band 2](Link) \| [Band 3](Link) \| [Stacked](Link) |
| [AirbBnB Chicago 2015](https://nicholasdekock.github.io/autoesda/example_reports/v1-airbnb.html) | |
| [Grid 100](https://nicholasdekock.github.io/autoesda/example_reports/v2-grid100.html) | |
| [South African 2011 Census](https://nicholasdekock.github.io/autoesda/example_reports/v3-southafrica.html) | |
| [Natural Earth Country Boundaries](https://nicholasdekock.github.io/autoesda/example_reports/v4-naturalearth.html) | |
| [Malaria in Colombia](https://nicholasdekock.github.io/autoesda/example_reports/v5-colombia.html) | |
| [USA Election Results](https://nicholasdekock.github.io/autoesda/example_reports/v6-usa.html) | |

### 7. Contributing
Click [here](https://github.com/NicholasDeKock/autoesda/issues/new/choose) to report bugs

Click [here](https://github.com/NicholasDeKock/autoesda/issues/new/choose) to request a new feature

If you would like to assist with fixing bugs, further development or writing documentation you are most welcome to do so. Use the [issues](https://github.com/NicholasDeKock/autoesda/issues) page to guide what you can assist with. 

In order to make a contribution you will need to:

1. Fork the autoesda repository on GitHub.
2. Clone your fork locally.
3. Commit your changes to your branch on GitHub
4. Once you are satsfied that your work is suitable, submit a pull request through the GitHub website.

### 8. License
This software is available under the BSD-3-Clause license.

For more information, see the [LICENSE](https://github.com/NicholasDeKock/autoesda/blob/main/LICENSE) file which contains details on the history of this software, terms & conditions for usage, and a disclaimer of all warranties.

### 9. References
When citing this library, please reference the following:

de Kock, N., Rautenbach, V., and Fabris-Rotelli, I.: TOWARDS AN OPEN SOURCE PYTHON LIBRARY FOR AUTOMATED EXPLORATORY SPATIAL DATA ANALYSIS, Int. Arch. Photogramm. Remote Sens. Spatial Inf. Sci., XLIII-B4-2022, 91–98, https://doi.org/10.5194/isprs-archives-XLIII-B4-2022-91-2022, 2022.

### 10. Credits
This package was created with [Cookiecutter](https://github.com/cookiecutter/cookiecutter) and the [giswqs/pypackage](https://github.com/giswqs/pypackage) project template.
