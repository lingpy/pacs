from lingpy.convert.graph import igraph2networkx
import igraph
from scipy.stats import kendalltau

g1 = igraph2networkx(igraph.read('graphs/set-ful-clips.gml'))
g2 = igraph2networkx(igraph.read('graphs/set-ful-pacs.gml'))

nodes = sorted(g1.nodes)
nodesu1 = [len(g1[node]) for node in nodes]
nodesu2 = [len(g2[node]) for node in nodes]

nodesw1 = [sum([g1[node][nodeB]["weight"] for nodeB in g1[node]]) for node in
        nodes]
nodesw2 = [sum([g2[node][nodeB]["weight"] for nodeB in g2[node]]) for node in
        nodes]


cu, pu = kendalltau(nodesu1, nodesu2)
cw, pw = kendalltau(nodesw1, nodesw2)

print('c_u={0:.2f}, p={1:.2f}'.format(cu, pu))
print('c_w={0:.2f}, p={1:.2f}'.format(cw, pw))

