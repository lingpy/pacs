#from lingpyd import *
#from lingpyd.meaning.colexification import *
#wl = Wordlist('ids.tsv')
#
#colexification_network(wl, entry='orthography', concept='concept',
#        output='gml', filename='ids', family='language')
#
from lingpy import *
import json
from glob import glob
from csvw.dsv import UnicodeDictReader
import networkx as nx
from collections import defaultdict
from itertools import combinations
from lingpy.convert.graph import networkx2igraph

data = glob('cldf/*.csv')
G = nx.Graph()
D = nx.DiGraph()
W = {0: ['doculect', 'glottocode', 'value', 'concept', 'concepticon_id',
    'concepticon_gloss']}

nodemap = {
        "plant (noun)": "plant",
        "river, stream, brook": "river",
        "spring, well": "spring",
        "row (vb)": "row",
        "tear (noun)": "tears"
        }


idx = 1
for f in data:
    meta = json.load(open(f+'-metadata.json'))
    language = meta['properties']['name']
    glottolog = f.split('-')[1][:-4]
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
                    G.nodes[row['Concept']]['weight'] += 1
                    G.nodes[row['Concept']]['language'] += [language]
                    G.nodes[row['Concept']]['glottolog'] += [glottolog]
                    D.nodes[row['Concept']]['weight'] += 1
                    D.nodes[row['Concept']]['language'] += [language]
                    D.nodes[row['Concept']]['glottolog'] += [glottolog]
                except:
                    G.add_node(
                            row['Concept'],
                            concepticon=meta['parameters'][row['Feature_ID']],
                            language=[language],
                            glottolog=[glottolog],
                            weight=1,
                            )
                    D.add_node(
                            row['Concept'],
                            concepticon=meta['parameters'][row['Feature_ID']],
                            language=[language],
                            glottolog=[glottolog],
                            weight=1,
                            )


    print('[i] analyzing {0} with {1} words'.format(
        meta['properties']['name'], len(wl)))
    for rowA, rowB in combinations(wl, r=2):
        valA, valB = rowA['Value'], rowB['Value']
        conA, conB = rowA['Concept'], rowB['Concept']
        
        # prevent loops
        if not conA == conB:

            if valA == valB:
                try:
                    G[conA][conB]['weight'] += 1
                    G[conA][conB]['language'] += [language]
                    G[conA][conB]['glottolog'] += [glottolog]
                    G[conA][conB]['form'] += [valA]
                except:
                    G.add_edge(
                            conA,
                            conB,
                            weight=1,
                            language=[language],
                            glottolog=[glottolog],
                            form=[valA]
                            )
            else:
                if (valA.startswith(valB) or valA.endswith(valB)) and len(valA)-len(valB) >= 3:
                    try:
                        D[conB][conA]['weight'] += 1
                        D[conB][conA]['language'] += [language]
                        D[conB][conA]['glottolog'] += [glottolog]
                        D[conB][conA]['form'] += [valA+'//'+valB]
                    except:
                        D.add_edge(
                                conB,
                                conA,
                                weight=1,
                                language=[language],
                                glottolog=[glottolog],
                                form=[valA+'//'+valB]
                                )
                elif (valB.startswith(valA) or valB.endswith(valA)) and len(valB)-len(valA) >= 3:
                    try:
                        D[conA][conB]['weight'] += 1
                        D[conA][conB]['language'] += [language]
                        D[conA][conB]['glottolog'] += [glottolog]
                        D[conA][conB]['form'] += [valB+'//'+valA]
                    except:
                        D.add_edge(
                                conA,
                                conB,
                                weight=1,
                                language=[language],
                                glottolog=[glottolog],
                                form=[valB+'//'+valA]
                                )



Wordlist(W).output('tsv', filename='ids-wordlist', ignore='all',
        prettify=False)

for n, d in G.nodes(data=True):
    d['language'] = ', '.join(d['language'])
    d['glottolog'] = ', '.join(d['glottolog'])
for n, d in D.nodes(data=True):
    d['language'] = ', '.join(d['language'])
    d['glottolog'] = ', '.join(d['glottolog'])

for nA, nB, d in G.edges(data=True):
    d['language'] = ', '.join(d['language'])
    d['glottolog'] = ', '.join(d['glottolog'])
    d['form'] = ', '.join(d['form'])

for nA, nB, d in D.edges(data=True):
    d['language'] = ', '.join(d['language'])
    d['glottolog'] = ', '.join(d['glottolog'])
    d['form'] = ', '.join(d['form'])



#G2 = networkx2igraph(G)
#D2 = networkx2igraph(D)

delis = []

for nA, nB, data in D.edges(data=True):
    if data['weight'] <= 10:
        delis += [(nA, nB)]
D.remove_edges_from(delis)
delis = []
for nA, nB, data in G.edges(data=True):
    if data['weight'] <= 5:
        delis += [(nA, nB)]
G.remove_edges_from(delis)
#D3 = networkx2igraph(D)
#
#
#d2id = {node['Name']: node.index for node in D2.vs}
#
#im = G2.community_infomap()
#for i, cluster in enumerate(im):
#    for node in cluster:
#        G2.vs[node]['infomap'] = i+1
#        D2.vs[d2id[G2.vs[node]['Name']]]['infomap'] = i+1
#        D3.vs[d2id[G2.vs[node]['Name']]]['infomap'] = i+1
#        D.nodes[G2.vs[node]['Name']]['infomap'] = i+1
#
#
#G2.write_gml('cliccs-1-colex.gml')
#D2.write_gml('cliccs-1-palex.gml')
#D3.write_gml('cliccs-1-palex-20.gml')

#with open('edges-partial-filtered.tsv', 'w') as f:
#    f.write('nodeA\tnodeB\tweight\n')
#    for nA, nB, data in D.edges(data=True):
#        if data['weight'] > 10:
#            f.write('{0}\t{1}\t{2}\n'.format(nA, nB, data['weight']))
#with open('nodes-partial-filtered.tsv', 'w') as f:
#    f.write('node\tinfomap\n')
#    for node, data in D.nodes(data=True):
#        f.write('\t'.join([node, str(data['infomap'])])+'\n')
#
#with open('edges-full-filtered.tsv', 'w') as f:
#    f.write('nodeA\tnodeB\tweight\n')
#    for nA, nB, data in D.edges(data=True):
#        if data['weight'] > 10:
#            f.write('{0}\t{1}\t{2}\n'.format(nA, nB, data['weight']))
#with open('nodes-full-filtered.tsv', 'w') as f:
#    f.write('node\tinfomap\n')
#    for node, data in D.nodes(data=True):
#        f.write('\t'.join([node, str(data['infomap'])])+'\n')


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

subG = G.subgraph(nodelist)
subD = D.subgraph(nodelist)
for node, data in subG.nodes(data=True):
    data['altname'] = nodemap.get(node, node)
for node, data in subD.nodes(data=True):
    data['altname'] = nodemap.get(node, node)
G2 = networkx2igraph(subG)
D2 = networkx2igraph(subD)
im = G2.community_infomap()
for i, cluster in enumerate(im):
    for node in cluster:
        G2.vs[node]['infomap'] = i+1
        D2.vs[node]['infomap'] = i+1

G2.write_gml('subset-colex.gml')
D2.write_gml('subset-palex.gml')

