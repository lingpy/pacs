from lingpy import *
import json
from glob import glob
from csvw.dsv import UnicodeDictReader
import networkx as nx
from collections import defaultdict
from itertools import combinations
from lingpy.convert.graph import networkx2igraph
from pyglottolog import Glottolog


def get_colexifications(wordA, wordB, threshold=3):
    if wordA == wordB:
        return "="
    # swap words if one is longer than the other
    swapped = False
    m, n = len(wordA), len(wordB)
    if m > n:
        swapped = True
        wordA, wordB, m, n = wordB, wordA, n, m
    
    # check for suffix 
    if (wordB.startswith(wordA) or wordB.endswith(wordA)) and n-m >= threshold:
        return ">" if not swapped else "<"

    # check for partial colex
    # make threshold part of the length of the string
    t = int(m/2+0.5)
    if t < threshold:
        t = threshold
    for i in range(m-1, t-1, -1):
        if (
                wordB.startswith(wordA[:i]) or 
                wordB.endswith(wordA[:i]) or
                wordB.startswith(wordA[-i:]) or
                wordB.endswith(wordA[-i:])
                ):
            return "-"


def add_edge(graph, conceptA, conceptB, **keywords):
    try:
        graph[conceptA][conceptB]["weight"] += 1
        for key, value in keywords.items():
            graph[conceptA][conceptB][key] += [value]
    except:
        graph.add_edge(conceptA, conceptB, weight=1, **{k: [v] for k, v in
            keywords.items()})



data = glob('../develop/cldf/*.csv')
G = nx.Graph()
D = nx.DiGraph()
P = nx.Graph()
W = {0: ['doculect', 'glottocode', 'value', 'concept', 'concepticon_id',
    'concepticon_gloss']}

glot = Glottolog("/home/mattis/data/datasets/glottolog")

idx = 1
for f in data:
    meta = json.load(open(f+'-metadata.json'))
    language = meta['properties']['name']
    glottolog = f.split('-')[1][:-4]
    try:
        family = glot.languoid(glottolog).family.name
    except:
        family = glottolog+'-?'
    with UnicodeDictReader(f) as reader:
        wl = []
        for row in reader:
            if len(row['Value']) >= 3:
                wl += [row]
                W[idx] = [
                        meta['properties']['name'],
                        f.split('-')[1][:-4],
                        row['Value'],
                        row['Concept'],
                        meta['parameters'][row['Feature_ID']],
                        row['Feature_ID'].split('/')[-1]
                        ]
                idx += 1
                try:
                    for graph in [G, D, P]:
                        graph.nodes[row['Concept']]['weight'] += 1
                        graph.nodes[row['Concept']]['language'] += [language]
                        graph.nodes[row['Concept']]['glottolog'] += [glottolog]
                        graph.nodes[row['Concept']]["family"] += [family]
                except:
                    for graph in [G, D, P]:
                        graph.add_node(
                                row['Concept'],
                                concepticon=meta['parameters'][row['Feature_ID']],
                                language=[language],
                                glottolog=[glottolog],
                                family=[family],
                                weight=1,
                                )

    print('[i] analyzing {0} with {1} words {2}'.format(
        meta['properties']['name'], len(wl), family))
    for rowA, rowB in combinations(wl, r=2):
        valA, valB = rowA['Value'], rowB['Value']
        conA, conB = rowA['Concept'], rowB['Concept']
        
        # prevent loops
        if not conA == conB:
            cols = get_colexifications(valA, valB, threshold=3)
            if cols == "=":
                add_edge(G, conA, conB, language=language, glottolog=glottolog,
                        form=valA, family=family)
            elif cols == "<":
                add_edge(D, conB, conA, language=language, glottolog=glottolog,
                        form=valB+'//'+valA, family=family)
            elif cols == ">":
                add_edge(D, conA, conB, language=language, glottolog=glottolog,
                        form=valA+'//'+valB, family=family)
            elif cols == "-":
                add_edge(P, conA, conB, language=language, glottolog=glottolog,
                        form=valA+'//'+valB, family=family)

Wordlist(W).output('tsv', filename='ids-wordlist', ignore='all',
        prettify=False)
for graph in [G, D, P]:
    print('edges : {0}'.format(len(graph.edges)))
    for n, d in graph.nodes(data=True):
        for k in ["language", "glottolog", "family"]:
            d[k] = ', '.join(d[k])
    for nA, nB, d in graph.edges(data=True):
        d['families'] = len(set(d["family"]))
        for k in ["language", "glottolog", "family", "form"]:
            d[k] = ", ".join(d[k])

GGG = networkx2igraph(D)



delis = []
for nA, nB, data in D.edges(data=True):
    if data['families'] <= 2:
        delis += [(nA, nB)]
D.remove_edges_from(delis)
delis = []
for nA, nB, data in G.edges(data=True):
    if data['families'] <= 5:
        delis += [(nA, nB)]
G.remove_edges_from(delis)
delis = []
for nA, nB, data in P.edges(data=True):
    if data['families'] <= 10:
        delis += [(nA, nB)]
P.remove_edges_from(delis)



nodelist = [
        "plant (noun)",
        "wood",
        "tree",
        "eyelid",
        "eyelash",
        "eyebrow",
        "blink",
        "blind",
        "eye",
        "tear (noun)",
        "water",
        "shore", "river, stream, brook", "whirlpool" 
        "spring, well", 
        "tide",
        "lowtide"
        "hightide",
        "waterfall",
        "bathe",
        "row (vb)",
        "thirst",
        "dive",
        "float",
        "swim",
        "splash",
        "sap"]

nodemap = {
        "plant (noun)": "plant",
        "river, stream, brook": "river",
        "spring, well": "spring",
        "row (vb)": "row",
        "tear (noun)": "tears"
        }


PP = networkx2igraph(P)
GG = networkx2igraph(G)
DD = networkx2igraph(D)

GG.write_gml('graphs/set-ful-clics.gml')
GGG.write_gml('graphs/test_graph.gml')
DD.write_gml('graphs/set-ful-clips.gml')
PP.write_gml('graphs/set-ful-pacs.gml')

subG = G.subgraph(nodelist)
subD = D.subgraph(nodelist)
subP = P.subgraph(nodelist)
for node, data in subG.nodes(data=True):
    data['altname'] = nodemap.get(node, node)
for node, data in subD.nodes(data=True):
    data['altname'] = nodemap.get(node, node)
for node, data in subP.nodes(data=True):
    data['altname'] = nodemap.get(node, node)

G2 = networkx2igraph(subG)
D2 = networkx2igraph(subD)
P2 = networkx2igraph(subP)
im = G2.community_infomap()
for i, cluster in enumerate(im):
    for node in cluster:
        G2.vs[node]['infomap'] = i+1
        D2.vs[node]['infomap'] = i+1
        P2.vs[node]['infomap'] = i+1

G2.write_gml('graphs/subset-clics.gml')
D2.write_gml('graphs/subset-clips.gml')
P2.write_gml('graphs/subset-pacs.gml')

