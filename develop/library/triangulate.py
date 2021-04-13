import library.data as libdat
from matplotlib.tri import Triangulation
import networkx as nx
from scipy.spatial.distance import euclidean

def get_triangles(langd):
#langd = {k: v for k, v in libdat.get_languages().items() if k in libdat.selected}
    TriAngles = nx.Graph()
    xs, ys, langs = [], [], []
    for lang, vals in sorted(langd.items(), key=lambda x: x[0].lower()):
        TriAngles.add_node(lang, lat=float(vals['latitude']), lon=float(
            vals['longitude']), subgroup=vals['subgroup'],
            family=vals['family'], name=vals['name'])
        langs += [lang]
        xs += [float(vals['latitude'])]
        ys += [float(vals['longitude'])]
    tri = Triangulation(xs, ys)
    
    for i, j in tri.edges:
        TriAngles.add_edge(langs[i], langs[j], 
                distance=euclidean(
                    [
                        TriAngles.node[langs[i]]['lon'],
                        TriAngles.node[langs[i]]['lat']
                        ],
                    [
                        TriAngles.node[langs[j]]['lon'],
                        TriAngles.node[langs[j]]['lat']
                        ],
                    ))
    return TriAngles
