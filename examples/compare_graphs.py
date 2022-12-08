"""
Code compares the computation time needed for different kinds of colexification analyses.
"""
from cltoolkit import Wordlist
from pacs.colexifications import (
        full_colexifications,
        affix_colexifications,
        common_substring_colexifications,
        )
from pacs.util import (
        load_gml_as_nx_graph,
        out_degree,
        in_degree,
        degree)
from tabulate import tabulate

from scipy.stats import spearmanr, kendalltau
import networkx as nx
import itertools
import igraph
from matplotlib import pyplot as plt
import numpy as np
import seaborn


graphA = load_gml_as_nx_graph("colexification-full.gml")
print("Loaded graph full")
graphB = load_gml_as_nx_graph("colexification-affix.gml", nx_cls=nx.DiGraph)
print("loaded graph affix")
graphC = load_gml_as_nx_graph("colexification-common-substring.gml")
print("loaded graph common")



# compute spearman correlations for the graphs with respect to their degree

deg_fc = degree(graphA, "family_count")
deg_af_out = out_degree(graphB, "family_count")
deg_af_in = in_degree(graphB, "family_count")
deg_af = degree(graphB, "family_count")
deg_sub = degree(graphC, "family_count")

table = []
matrix = [[1 for _ in range(4)] for _ in range(4)]
for (i, (mA, a)), (j, (mB, b)) in itertools.combinations(
        enumerate([
         ("Full Colexification", deg_fc),
         ("Affix Colexification (In-Degree)", deg_af_in),
         ("Affix Colexification (Out-Degree)", deg_af_out),
         ("Overlap Colexification", deg_sub)]),
        r=2):
    common_nodes = [x for x in a if x in b]
    values_a, values_b = [], []
    for node in common_nodes:
        values_a += [a[node]]
        values_b += [b[node]]
    r, p = kendalltau(values_a, values_b)
    matrix[i][j] = matrix[j][i] = r
    table += [[mA, mB, len(common_nodes), r, p]]
    plt.clf()
    for (node, val_a, val_b) in zip(
            common_nodes,
            values_a,
            values_b):
        plt.plot(val_a, val_b, "bo", markersize=3)
    plt.xlim(0, max(values_a))
    plt.ylim(0, max(values_b))
    
    # https://www.geeksforgeeks.org/plotting-correlation-matrix-using-python/
    plt.plot(np.unique(values_a), np.poly1d(np.polyfit(values_a, values_b, 1))
         (np.unique(values_a)), color='crimson')
    plt.xlabel(mA)
    plt.ylabel(mB)
    plt.savefig("{0}-{1}.png".format(mA, mB))
    plt.savefig("{0}-{1}.pdf".format(mA, mB))
    
plt.clf()

seaborn.heatmap(
        matrix, 
        xticklabels=["Full", "Affix-In", "Affix-Out", "Common"],
        yticklabels=["Full", "Affix-In", "Affix-Out", "Common"],
        )
plt.savefig("correlations.pdf")

print(tabulate(table, floatfmt=".4f"))
