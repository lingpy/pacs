import igraph
from lingpy.convert.graph import igraph2networkx
import networkx as nx
import cartopy.feature as cfeature
#from cartopy.feature import NaturalEarthFeature
import numpy as np

import cartopy.crs as ccrs
import matplotlib.pyplot as plt
from matplotlib.patches import Wedge, Circle
import library.map as cfeature
from pyglottolog import Glottolog

import json

glot = Glottolog("/home/mattis/data/datasets/glottolog")

G_ = igraph.read('graphs/test_graph.gml')

concepts = {}
for node in G_.vs:
    attrs = node.attributes()
    concepts[attrs['Name']] = node.index

G = nx.DiGraph()

for node in G_.vs:
    atr = node.attributes()
    G.add_node(atr['Name'], **atr)
for edge in G_.es:
    atr = edge.attributes()
    G.add_edge(
            G_.vs[edge.source].attributes()['Name'],
            G_.vs[edge.target].attributes()['Name'],
            **atr)


names = {}
try:
    coords = json.load(open('coords.json'))
except:
    coords = {}
    for node, data in G.nodes(data=True):
        for name, gc in zip(data["language"].split(", "),
                data["glottolog"].split(', ')):
            if gc in coords:
                pass
            else:
                print(gc)
                gentry = glot.languoid(gc)
                lat, lon = gentry.latitude, gentry.longitude
                if lat and lon:
                    lat = float(lat)
                    lon = float(lon)
                    coords[gc] = (lat, lon)
    with open('coords.json') as f:
        json.dump(coords, f)

# assemble data
water = G["water"]["tear (noun)"]
eye = G["eye"]["tear (noun)"]

languages = {k: [0, 0] for k in coords}
for l, g in zip(water["language"].split(", "), water["glottolog"].split(", ")):
    languages[g][0] = 1
for l, g in zip(eye["language"].split(", "), eye["glottolog"].split(", ")):
    languages[g][1] = 1

fig = plt.figure(figsize=[20, 10])
data_crs = ccrs.PlateCarree()
ax = fig.add_subplot(1, 1, 1, projection=ccrs.PlateCarree())
ax.coastlines(resolution='50m')
ax.add_feature(cfeature.LAND)
ax.add_feature(cfeature.OCEAN)
ax.add_feature(cfeature.BORDERS, linestyle=':')
ax.add_feature(cfeature.LAKES, alpha=0.5)
ax.add_feature(cfeature.RIVERS)

for language, (water, eye) in sorted(languages.items(), key=lambda x:
        sum(x[1])):
    lat, lon = coords[language]
    if water and eye:
        print(language)
    wedge = Wedge(
            [lon, lat],
            2.5,
            0, 
            360,
            facecolor="white",
            transform=data_crs,
            zorder=50,
            edgecolor="black",
            alpha=0.75
            )
    ax.add_patch(wedge)
    if water:
        wedgeW = Wedge(
                [lon, lat],
                2.5,
                90,
                270,
                facecolor="crimson", #"#b4c7dcff",
                transform=data_crs,
                zorder=50,
                edgecolor="black",
                )
        ax.add_patch(wedgeW)
    if eye:
        wedgeW = Wedge(
                [lon, lat],
                2.5,
                271,
                89,
                facecolor="cornflowerblue", #"#f7d1d5ff",
                transform=data_crs,
                zorder=50,
                edgecolor="black",
                )
        ax.add_patch(wedgeW)
plt.plot(0, 0, 'o', color="crimson", #"#b4c7dcff", 
        markersize=5, label="water")
plt.plot(0, 0, 'o', color="cornflowerblue", 
        #"#f7d1d5ff", 
        markersize=5, label="eye")
plt.legend(loc=2)

plt.savefig('map.pdf')



fig = plt.figure(figsize=[20, 10])
data_crs = ccrs.PlateCarree()
ax = fig.add_subplot(1, 1, 1, projection=ccrs.PlateCarree())
ax.set_extent(
            [
                85, 
                115, 
                31,
                5,
                ], crs=ccrs.PlateCarree())

ax.coastlines(resolution='50m')
ax.add_feature(cfeature.LAND)
ax.add_feature(cfeature.OCEAN)
ax.add_feature(cfeature.BORDERS, linestyle=':')
ax.add_feature(cfeature.LAKES, alpha=0.5)
ax.add_feature(cfeature.RIVERS)

for language, (water, eye) in sorted(languages.items(), key=lambda x:
        sum(x[1])):
    lat, lon = coords[language]
    wedge = Wedge(
            [lon, lat],
            0.5,
            0, 
            360,
            facecolor="white",
            transform=data_crs,
            zorder=50,
            edgecolor="black",
            alpha=0.75
            )
    ax.add_patch(wedge)
    if language == 'nort2740':
        wedge = Wedge(
            [lon, lat],
                0.75,
                0, 
                360,
                facecolor="black",
                transform=data_crs,
                zorder=50,
                edgecolor="black",
                alpha=0.75
                )
        ax.add_patch(wedge)

    if water:
        wedgeW = Wedge(
                [lon, lat],
                0.5,
                90,
                270,
                facecolor="crimson", #"#b4c7dcff",
                transform=data_crs,
                zorder=50,
                edgecolor="black",
                )
        ax.add_patch(wedgeW)
    if eye:
        wedgeW = Wedge(
                [lon, lat],
                0.5,
                271,
                89,
                facecolor="cornflowerblue", #"#f7d1d5ff",
                transform=data_crs,
                zorder=50,
                edgecolor="black",
                )
        ax.add_patch(wedgeW)
plt.plot(0, 0, 'o', color="crimson", #"#b4c7dcff", 
        markersize=5, label="water")
plt.plot(0, 0, 'o', color="cornflowerblue", 
        #"#f7d1d5ff", 
        markersize=5, label="eye")
plt.legend(loc=2)

plt.savefig('map2.pdf')

