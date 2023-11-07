import os
os.environ['USE_PYGEOS'] = '0'
import base64
import esda
import libpysal as lps
import matplotlib
import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns
import pygeoda
import geoplot
import io

def _pysal_weights(gdf):
    weights_matrix = lps.weights.Queen.from_dataframe(gdf)
    weights_matrix.transform = "r"
    return weights_matrix

def _plot_lisa(lisa_object, temp_gdf, titles):
    
    temp_gdf = temp_gdf
    fig, ax = plt.subplots(1,2)

    temp_gdf["lisa"] = lisa_object.lisa_clusters()
    temp_gdf["lisa_pval"] = lisa_object.lisa_pvalues()
    lisa_colours = lisa_object.lisa_colors()
    lisa_labels = lisa_object.lisa_labels()


    for ctype, data in temp_gdf.groupby("lisa"):
        colour = lisa_colours[ctype]
        lbl = lisa_labels[ctype]
        data.plot(color = colour, ax = ax[0], label = lbl, edgecolor = "black", linewidth = 0.2)

    lisa_legend = [matplotlib.patches.Rectangle(xy=(0,0), width=5, height=5, color=color) for color in lisa_colours]
    ax[0].legend(lisa_legend, lisa_labels, fancybox=True, shadow=True, title=titles[0], loc="upper center", bbox_to_anchor=(0.5,0), ncol=2, fontsize="small")
    ax[0].axis('off')
        
    temp_gdf.plot(color='#eeeeee', ax=ax[1], edgecolor = 'black', linewidth = 0.2)
    temp_gdf[temp_gdf['lisa_pval'] <= 0.05].plot(color="#84f576", edgecolor = 'black', linewidth = 0.2, ax=ax[1])
    temp_gdf[temp_gdf['lisa_pval'] <= 0.01].plot(color="#53c53c", edgecolor = 'black', linewidth = 0.2, ax=ax[1])
    temp_gdf[temp_gdf['lisa_pval'] <= 0.001].plot(color="#348124", edgecolor = 'black', linewidth = 0.2, ax=ax[1])

    sig_colours = ['#eeeeee','#84f576','#53c53c','#348124']
    sig_labels = ["Not Significant", "p = 0.05", "p = 0.01", "p = 0.001"]
    sig_legend = [matplotlib.patches.Rectangle(xy=(0,0), width=5, height=5, color=color) for color in sig_colours]
    ax[1].legend(sig_legend, sig_labels, fancybox=True, shadow=True, title=titles[1], loc="upper center", bbox_to_anchor=(0.5,0), ncol=2, fontsize="small", title_fontsize="medium")
    ax[1].axis('off')
    ax[1].set_aspect("equal")

    fig.tight_layout()

    return fig

class Dataset:

    def __init__(self, gdf):
        
        self.gdf = gdf
        self.numeric_columns = list(gdf.select_dtypes(include=["number"]).columns)
        self.pysal_weights = _pysal_weights(gdf)
        self.geoda_object = pygeoda.open(gdf)
        self.geoda_weights = pygeoda.queen_weights(self.geoda_object)

    def overview_statistics(self):

        gdf = self.gdf
        crs = gdf.crs
        rows = gdf.shape[0]
        columns = gdf.shape[1]
        numeric_columns = self.numeric_columns
        excluded_columns = set(list(gdf.columns)) - set(numeric_columns)

        names = ["Coordinate System", "Features", "Attributes", "Included Attributes", "Excluded Attributes"]
        values = [[crs, rows, columns, numeric_columns, excluded_columns]]

        return pd.DataFrame(columns=names, data=values)

    def study_area_figure(self):

        gdf = self.gdf
        fig, ax = plt.subplots(1,1)
        gdf.plot(facecolor="none", ax=ax)
        ax.set_aspect("equal")
        fig.set_figheight(8)

        return fig

    def numeric_variables(self):
        
        numeric_variables = []

        for column_name in self.numeric_columns:
            numeric_variables.append(Variable(self.gdf, column_name, self.pysal_weights, self.geoda_weights))

        return numeric_variables

    def dataset_statistics(self):
        stat_array = []
        for var in self.numeric_variables():
            stat_array.append(var.variable_statistics())
        df = pd.concat(stat_array).round(3)
        return df
    
    def dataset_sample(self):
        gdf = self.gdf
        return gdf.drop(["geometry"], axis=1).sample(10)
    
    def correlation_figure(self):

        gdf = self.gdf

        fig, ax = plt.subplots(3,1)
        fig.set_figheight(12)

        corrs = ["pearson", "kendall", "spearman"]
        for i, corr_type in enumerate(corrs):
            correlation_matrix = gdf.corr(method=corr_type).round(2)
            sns.heatmap(correlation_matrix, cmap="RdBu_r", annot=True, cbar=True, square=True, ax=ax[i], annot_kws={"fontsize": 6})
            ax[i].set_title(str(corr_type).upper() + " Correlation")
        
        fig.tight_layout()
        return fig
    
    def pairplot_figure(self):

        gdf = self.gdf

        pairplot = sns.pairplot(gdf, kind='reg', diag_kind='hist', plot_kws={'marker': ".", 'line_kws':{'color':'red'}})

        return pairplot

class Variable:

    def __init__(self, gdf, column_name, pysal_weights, geoda_weights):

        self.dataset = gdf
        self.name = column_name
        self.values = gdf[column_name]
        self.weights_pysal = pysal_weights
        self.weights_geoda = geoda_weights

    def variable_statistics(self):

        values = self.values
        weights = self.weights_pysal

        statistics_df = pd.DataFrame(columns=["Name", "Count", "Mean", "Std", "Min", "25%", "Median (50%)", "75%", "Max","Skewness", "Kurtosis", "Unique", "Null", "Moran's I", "p-value (Moran's I)", "Geary's C", "p-value (Geary's C)"])
        df = self.values.describe().to_list()
        df.insert(0, self.name)

        df.extend((values.skew(), values.kurt(), values.nunique(), values.isna().sum()))

        global_moran = esda.moran.Moran(values, weights)
        global_geary = esda.geary.Geary(values, weights)
    
        df.extend((global_moran.I, global_moran.p_sim))
        df.extend((global_geary.C, global_geary.p_sim))
        
        statistics_df.loc[len(statistics_df)] = df
        statistics_df = statistics_df.set_index("Name")

        return statistics_df
    
    def descriptive_figure(self):

        gdf = self.dataset
        values = self.values
        name = self.name

        fig = plt.figure(figsize=(10,6))
        grid = plt.GridSpec(2,2, height_ratios=[0.5,4])
        g1 = plt.subplot(grid[0, 0])
        g2 = plt.subplot(grid[0:2, 1])
        g3 = plt.subplot(grid[1, 0])

        g1.boxplot(values, vert=False, widths=1)
        g1.set_title("Boxplot", fontweight="bold")

        sns.histplot(values, stat="probability", ax=g3)
        g3.set_title("Probability Histogram", fontweight="bold")
        g3.set_xlabel("Value")
        g3.set_ylabel("Probability")

        try:
            geoplot.cartogram(gdf, scale=name, ax=g2)
            geoplot.polyplot(gdf, facecolor='lightgray', edgecolor='white', ax=g2)
            g2.set_title("Cartogram", fontweight="bold")
            g2.set_aspect("equal")

        except Exception as exc:
            error_display_string = f"An error occured when generating this plot: \n{exc}"
            g2.text(0,0, error_display_string)

        fig.tight_layout(pad=0.1)
        
        return fig
    
    def local_moran_figure(self):

        temp_gdf = self.dataset
        weights_geoda = self.weights_geoda
        values = self.values
        undefined_values = values.isna().tolist()
        name = self.name

        local_moran = pygeoda.local_moran(weights_geoda, values, undefs=undefined_values)

        titles = ["Local Moran Clusters", "Local Moran Significance"]

        return _plot_lisa(local_moran, temp_gdf, titles)
    
    def local_geary_figure(self):

        temp_gdf = self.dataset
        weights = self.weights_geoda
        values = self.values
        undefined_values = values.isna().tolist()
        name = self.name

        local_geary = pygeoda.local_geary(weights, values, undefs=undefined_values)

        titles = ["Local Geary Clusters", "Local Geary Significance"]

        return _plot_lisa(local_geary, temp_gdf, titles)
    
    def choropleth_figure(self):

        gdf = self.dataset
        name = self.name

        fig, ax = plt.subplots(2,3)
        fig.set_size_inches(15,10)
        schemes = ["BoxPlot","EqualInterval","Quantiles","StdMean","MaximumBreaks","FisherJenks"]
        names = ["Boxmap","Equal Interval","Quantiles","Mean-Standard Deviation","Maximum Breaks","Fisher-Jenks"]

        for index in enumerate(ax.reshape(-1)):
            try:
                gdf.plot(ax=index[1],column=name, categorical=False, edgecolor = 'black', linewidth = 0.2, scheme=schemes[index[0]], legend=True, cmap="YlOrBr",legend_kwds={"loc": "upper center", "bbox_to_anchor": (0.5,0), "title": names[index[0]], "fmt": "{:.0f}", "interval": True, "fancybox": "True", "shadow": "True", "fontsize": "small", "ncol": 2, "title_fontsize": "medium"})
                index[1].axis('off')
                index[1].set_aspect("equal")
            except Exception as exc:
                error_display_string = f"An error occured when generating this plot: \n{exc}"
                index[1].text(0,0, error_display_string)

        plt.tight_layout()
        
        return fig


    