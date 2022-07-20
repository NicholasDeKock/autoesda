"""Module to create the Correlation Page."""
import matplotlib.pyplot as plt
import io
import base64
import seaborn as sns
from seaborn import heatmap

def correlation_html(gdf):
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

    correlation_page_string = '''
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
        </div>
        '''

    return correlation_page_string