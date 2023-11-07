
import os
os.environ['USE_PYGEOS'] = '0'
import esda
import libpysal
import matplotlib.pyplot as plt
import pandas as pd
import base64
import io
import seaborn as sns
import xarray
import numpy as np
import shapely
import rasterio
import geopandas as gpd
import pygeoda
import matplotlib
import mapclassify

def _vectorize(raster_dataset):
    
    def create_id_dataarray(raster_dataset):
            y = raster_dataset.y
            x = raster_dataset.x

            data = np.reshape(np.arange(0,len(y)*len(x)),(len(y),len(x))).astype(int)

            ds = xarray.DataArray(data = data,dims = ['y','x'], coords = {'y': y, 'x': x}, attrs = raster_dataset.attrs)
            ds.rio.write_crs(raster_dataset.rio.crs, inplace=True)
            
            return ds

    def create_raster_df(raster_dataset):
            raster_df = raster_dataset.to_dataframe(name="VALUE", dim_order=["x","y","band"])
            raster_df.reset_index(inplace=True)
            raster_df["band"] = 'Band ' + raster_df["band"].astype(str)
            raster_df = raster_df.pivot(index=["x", "y"], columns=["band"], values="VALUE")

            return raster_df

    def create_polygon_df(ds, raster_dataset):
            
            myarray = ds.to_numpy()
            value_array = []
            geom_array = []

            for polygon, value in rasterio.features.shapes(myarray, transform = raster_dataset.rio.transform()):
                    value_array.append(value)
                    geom_array.append(shapely.geometry.shape(polygon))

            gdf = gpd.GeoDataFrame()
            gdf['ID'] = value_array
            gdf['geometry'] = geom_array
            gdf.set_crs(crs=raster_dataset.rio.crs, inplace=True)

            return gdf

    id_dataarray = create_id_dataarray(raster_dataset)

    id_df = id_dataarray.to_dataframe("ID", dim_order=["x","y"])
    raster_df = create_raster_df(raster_dataset)
    polygon_df = create_polygon_df(id_dataarray, raster_dataset)
    polygon_df.set_index("ID", inplace=True)

    joined_with_attrs = pd.concat([id_df, raster_df], axis=1, join="inner")
    joined_with_attrs.reset_index(inplace=True)
    joined_with_attrs.set_index('ID', inplace=True)

    final_polygons = polygon_df.merge(joined_with_attrs, on="ID")
    final_polygons.drop(columns=["x","y","spatial_ref"], inplace=True)

    if raster_dataset.rio.nodata != None:
        numeric_columns = list(final_polygons.select_dtypes(include=["int64", "float64", "float32"]).columns)
        final_polygons.replace(raster_dataset.rio.nodata, np.nan, inplace=True)
        final_polygons.dropna(how='all',subset=numeric_columns, inplace=True)

    final_polygons = final_polygons.reset_index()
    final_polygons.drop(columns=["ID"], inplace=True)

    return final_polygons

def _pysal_weights(band):
    queen_weights_matrix_wsp = libpysal.weights.Queen.from_xarray(band, n_jobs=-1)
    queen_weights_matrix_w = libpysal.weights.WSP2W(libpysal.weights.WSP(queen_weights_matrix_wsp.sparse.astype(float)))
    queen_weights_matrix_w.index = queen_weights_matrix_wsp.index
    return queen_weights_matrix_w

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
        data.plot(color = colour, ax = ax[0], label = lbl)

    lisa_legend = [matplotlib.patches.Rectangle(xy=(0,0), width=5, height=5, color=color) for color in lisa_colours]
    ax[0].legend(lisa_legend, lisa_labels, fancybox=True, shadow=True, title=titles[0], loc="upper center", bbox_to_anchor=(0.5,0), ncol=2, fontsize="small")
    ax[0].axis('off')
    ax[0].set_aspect("equal")
        
    temp_gdf.plot(color='#eeeeee', ax=ax[1])
    temp_gdf[temp_gdf['lisa_pval'] <= 0.05].plot(color="#84f576", ax=ax[1])
    temp_gdf[temp_gdf['lisa_pval'] <= 0.01].plot(color="#53c53c", ax=ax[1])
    temp_gdf[temp_gdf['lisa_pval'] <= 0.001].plot(color="#348124", ax=ax[1])

    sig_colours = ['#eeeeee','#84f576','#53c53c','#348124']
    sig_labels = ["Not Significant", "p = 0.05", "p = 0.01", "p = 0.001"]
    sig_legend = [matplotlib.patches.Rectangle(xy=(0,0), width=5, height=5, color=color) for color in sig_colours]
    ax[1].legend(sig_legend, sig_labels, fancybox=True, shadow=True, title=titles[1], loc="upper center", bbox_to_anchor=(0.5,0), ncol=2, fontsize="small", title_fontsize="medium")
    ax[1].axis('off')
    ax[1].set_aspect("equal")

    fig.tight_layout()

    return fig

class Raster:

    def __init__(self, raster):

        self.raster = raster
        self.vectorised = _vectorize(raster)
        self.geoda_object = pygeoda.open(self.vectorised)
        self.geoda_weights = pygeoda.queen_weights(self.geoda_object)

    def overview_statistics(self):
         
        raster = self.raster
        crs = raster.rio.crs.to_string()
        bands = raster.shape[0]
        rows = raster.shape[1]
        columns = raster.shape[2]
        resolution = raster.rio.resolution()
        extent = raster.rio.bounds()
        metadata = raster.attrs

        names = ["Coordinate System", "Bands", "Rows", "Columns", "Cell Resolution", "Extent", "Metadata"]
        values = [[crs, bands, rows, columns, resolution, extent, metadata]]
        
        return pd.DataFrame(columns=names, data=values)

    def bands(self):

        bands = []

        for band in self.raster:
            bands.append(Band(band, self.vectorised, self.geoda_object, self.geoda_weights))

        return bands

    def raster_statistics(self):

        stat_array =[]
        bands = self.bands()
        for band in bands:
            stat_array.append(band.band_statistics())
        df = pd.concat(stat_array)

        return df

    def correlation_figure(self):

        gdf = self.vectorised

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

        gdf = self.vectorised

        pairplot = sns.pairplot(gdf, kind='reg', diag_kind='hist', plot_kws={'marker': ".", 'line_kws':{'color':'red'}})

        return pairplot
    
class Band:

    def __init__(self, band, vectorised, geoda_object, geoda_weights):
        
        self.name = "Band " + str(band.band.values)
        self.band = band.rio.update_attrs(new_attrs={"nodatavals": [band.rio.nodata]})
        self.datatype = band.dtype
        self.crs = band.rio.crs
        self.nodatavalue = band.rio.nodata
        self.bandseries = band.to_series()
        self.bandnodataremoved = self.bandseries[self.bandseries !=band.rio.nodata]
        
        self.vectorised = vectorised
        self.geoda_weights = geoda_weights

        self.pysal_weights = _pysal_weights(self.band)

    def histogram_figure(self):
         
        band = self.band
        nodata = self.nodatavalue

        fig, ax = plt.subplots(1,1)
        sns.histplot(band.where(band != nodata).stack(z=("x", "y")), stat="probability", ax=ax)
        ax.set_xlabel("Cell Value")
        ax.set_ylabel("Probability")

        return fig 
         
    def band_statistics(self):

        band = self.band
        nodata = self.nodatavalue
        
        statistics_df = pd.DataFrame(columns=["Name", "Count", "Mean", "Std", "Min", "25%", "Median (50%)", "75%", "Max", "DataType", "NoData", "Moran's I", "p-value (Moran's I)", "Geary's C", "p-value (Geary's C)"])
        df = band.where(band != nodata).to_dataframe(name='data')
        df = df['data'].describe().to_list()
        df.insert(0, self.name)

        df.insert(9, self.datatype)
        df.insert(10, self.nodatavalue)

        global_moran = esda.moran.Moran(self.bandnodataremoved, self.pysal_weights)
        global_geary = esda.geary.Geary(self.bandnodataremoved, self.pysal_weights)

        df.extend((global_moran.I, global_moran.p_sim))
        df.extend((global_geary.C, global_geary.p_sim))

        statistics_df.loc[len(statistics_df)] = df
        statistics_df = statistics_df.set_index("Name")

        return statistics_df
    
    def local_moran_figure(self):
        
        temp_gdf = self.vectorised
        name = self.name
        values = temp_gdf[name]
        geoda_weights = self.geoda_weights
        
        local_moran = pygeoda.local_moran(geoda_weights, values)

        titles = ["Local Moran Clusters", "Local Moran Significance"]

        return _plot_lisa(local_moran, temp_gdf, titles)
    
    def local_geary_figure(self):
        
        temp_gdf = self.vectorised
        name = self.name
        values = temp_gdf[name]
        geoda_weights = self.geoda_weights
        
        local_geary = pygeoda.local_geary(geoda_weights, values)

        titles = ["Local Geary Clusters", "Local Geary Significance"]

        return _plot_lisa(local_geary, temp_gdf, titles)
    
    def choropleth_figure(self):
         
        band = self.band
        nodata = self.nodatavalue
        band_without_nodata = band.where(band != nodata)


        fig, ax = plt.subplots(2,3)
        fig.set_size_inches(15,10)

        schemes = ["box_plot","equal_interval","quantiles","std_mean","maximum_breaks","fisher_jenks"]
        names = ["Boxmap","Equal Interval","Quantiles","Mean-Standard Deviation","Maximum Breaks","Fisher-Jenks"]

        for index in enumerate(ax.reshape(-1)):
            bins = mapclassify.classify(band_without_nodata.to_series().dropna(), scheme=schemes[index[0]]).bins
            band_without_nodata.plot(cmap="YlOrBr", robust=True, levels=bins, ax=index[1])
            index[1].set_aspect("equal")
            index[1].set_xlabel("Longitude")
            index[1].set_ylabel("Latitude")
            index[1].set_title(names[index[0]])

        return fig



