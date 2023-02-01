from pacs.util import (
        load_gml_as_nx_graph,
        write_gml,
        out_degree,
        in_degree,
        degree)
import networkx as nx
import igraph

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


nodes = {
        "BATHE": "bathe",
        "BLIND": "blind",
        "BLINK": "to blink",
        "DIVE": "dive",
        "EYE": "eye",
        "EYEBROW": "eyebrow",
        "EYELASH": "eyelash",
        "EYELID": "eyelid",
        "FLOAT": "flow",
        "FLOWING BODY OF WATER": "river",
        "PLANT (SOMETHING)": "plant (v.)",
        "PLANT (VEGETATION)": "plant (n.)",
        "SAP": "sap",
        "SHORE": "shore",
        "SPLASH": "splash",
        "SPRING OR WELL": "spring",
        "SWIM": "swim",
        "TEAR (OF EYE)": "tear",
        "THIRST": "thirst",
        "TIDE": "tide",
        "TREE": "tree",
        "WATER": "water",
        "WATERFALL": "waterfall",
        "WHIRLPOOL": "whirlpool",
        }


graph_a = igraph.load("colexification-full.gml")
graphA = load_gml_as_nx_graph("colexification-full.gml")
print("Loaded graph full")
graphB = load_gml_as_nx_graph("colexification-affix.gml", nx_cls=nx.DiGraph)
print("loaded graph affix")
graphC = load_gml_as_nx_graph("colexification-overlap.gml")
print("loaded graph common")

for i, comms in enumerate(graph_a.community_infomap(vertex_weights="family_count",
        edge_weights="family_count")):
    for node in comms:
        n = graph_a.vs[node]["label"]
        if n in graphA:
            graphA.nodes[graph_a.vs[node]["label"]]["community"] = str(i+1)
        if n in graphB:
            graphB.nodes[graph_a.vs[node]["label"]]["community"] = str(i+1)
        if n in graphC:
            graphC.nodes[graph_a.vs[node]["label"]]["community"] = str(i+1)

for n in nodes:
    if n not in graphA:
        print(n)



# filter by n families
remove_edges_a, remove_edges_b, remove_edges_c = [], [], []
for node_a, node_b, data in graphA.edges(data=True):
    if data["family_count"] < 2:
        remove_edges_a.append((node_a, node_b))

for node_a, node_b, data in graphB.edges(data=True):
    if data["family_count"] < 5:
        remove_edges_b.append((node_a, node_b))

for node_a, node_b, data in graphC.edges(data=True):
    if data["family_count"] < 6:
        remove_edges_c.append((node_a, node_b))

graphA.remove_edges_from(remove_edges_a)
graphB.remove_edges_from(remove_edges_b)
graphC.remove_edges_from(remove_edges_c)

subgraph_a = nx.subgraph(graphA, nodes)
subgraph_b = nx.subgraph(graphB, nodes)
subgraph_c = nx.subgraph(graphC, nodes)

write_gml(subgraph_a, "subgraph-full.gml")
write_gml(subgraph_b, "subgraph-affix.gml")
write_gml(subgraph_c, "subgraph-common-substring.gml")
