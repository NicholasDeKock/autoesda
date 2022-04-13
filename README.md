# autoESDA


[![image](https://img.shields.io/pypi/v/autoesda.svg)](https://pypi.python.org/pypi/autoesda)
[![image](https://img.shields.io/conda/vn/conda-forge/autoesda.svg)](https://anaconda.org/conda-forge/autoesda)
![Conda](https://img.shields.io/conda/dn/conda-forge/autoesda)
[![image](https://github.com/NicholasDeKock/autoesda/workflows/docs/badge.svg)](https://nicholasdekock.github.io/autoesda/)
[![image](https://github.com/NicholasDeKock/autoesda/workflows/build/badge.svg)](https://github.com/giswqs/autoesda/actions?query=workflow%3Abuild)
[![image](https://img.shields.io/pypi/l/autoesda?color=yellow&label=Licence&logo=BSD-3-Clause)](https://opensource.org/licenses/BSD-3-Clause)
![Visitor Badge](https://visitor-badge.laobi.icu/badge?page_id=NicholasDeKock.autoesda)

**A Python package that automates the exploratory spatial data analysis (ESDA) process by summarising the results into an HTML report**
___
## Table of Contents
1. [Introduction](https://github.com/NicholasDeKock/autoesda#Introduction)
2. [Key features](https://github.com/NicholasDeKock/autoesda#Keyfeatures)
3. [Installation](https://github.com/NicholasDeKock/autoesda#Installation)
4. [Dependancies](https://github.com/NicholasDeKock/autoesda#Dependancies)
5. [Usage](https://github.com/NicholasDeKock/autoesda#Usage)
6. [Examples](https://github.com/NicholasDeKock/autoesda#Examples)
7. [Contributing](https://github.com/NicholasDeKock/autoesda#Contributing)
8. [License](https://github.com/NicholasDeKock/autoesda#License)
9. [References](https://github.com/NicholasDeKock/autoesda#References)
10. [Credits](https://github.com/NicholasDeKock/autoesda#Credits)
___
### 1. Introduction
Numerous areas exploratory spatial data analysis (ESDA) process is repetative, time consuming
___
### 2. Key features
- **HTML output report**
- **Extent map**
- **Dataset overview** (coordinate system, number of rows/columns, which rows/columns have been included/excluded in the report)
- **Descriptive statistics** (count, mean, standard deviation, minimum/maximum, 25^th^/50^th^/75^th^ percentiles)
- **Sample of dataset**
- **Boxplot**
- **Histogram**
- **Moran's I simulation** (moran's I, number of features, p-value, z-score, number of permutations)
- **Local Indicator of Spatial Autocorrelation** (local scatterplot, LISA cluster map)
- **Choropleth maps** (quantiles, equal intervals, natural breaks, and percentiles classification schemes)
- **Correlation** (correlation matrix/heatmap, pairwise plot)
___
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
___
### 4. Dependancies
- [geopandas](https://github.com/geopandas/geopandas)
- [pysal](https://github.com/pysal/pysal)
- [matplotlib](https://github.com/matplotlib/matplotlib)
- [libpysal](https://github.com/pysal/libpysal)
- [esda](https://github.com/pysal/esda)
- [splot](https://github.com/pysal/splot)
- [seaborn](https://github.com/mwaskom/seaborn)
___
### 5. Usage
___
### 6. Examples
___
### 7. Contributing
___
### 8. License
This software is available under the BSD-3-Clause license.

For more information, see the [LICENSE](https://github.com/NicholasDeKock/autoesda/blob/main/LICENSE) file which contains details on the history of this software, terms & conditions for usage, and a disclaimer of all warranties.
___
### 9. References
___
### 10. Credits
This package was created with [Cookiecutter](https://github.com/cookiecutter/cookiecutter) and the [giswqs/pypackage](https://github.com/giswqs/pypackage) project template.
