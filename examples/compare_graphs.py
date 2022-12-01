"""
Code compares the computation time needed for different kinds of colexification analyses.
"""
from cltoolkit import Wordlist
from pacs.colexifications import (
        full_colexifications,
        affix_colexifications,
        common_substring_colexifications,
        affix_colexifications_by_pairwise_comparison
        )
from pyclics.util import write_gml
from pycldf import Dataset
from pyclts import CLTS
from tabulate import tabulate

from scipy.stats import spearmanr
import networkx as nx
import itertools

wl = Wordlist([Dataset.from_metadata("idssegmented/cldf/cldf-metadata.json")],
              ts=CLTS().bipa)

graphA = full_colexifications(wl)
graphB = affix_colexifications(wl)
graphC = common_substring_colexifications(wl)




print("[i] writing graphs to file")
write_gml(graphA, "colexification-full.gml")
write_gml(graphB, "colexification-affix.gml")
write_gml(graphC, "colexification-common-substring.gml")

# compute spearman correlations for the graphs with respect to their degree

deg_fll = dict(nx.degree(graphA, weight="family_count"))
deg_aff = dict(nx.degree(graphB, weight="family_count"))
deg_sub = dict(nx.degree(graphC, weight="family_count"))

table = []
for (mA, a), (mB, b) in itertools.combinations(
        [("full", deg_fll),
         ("affix", deg_aff),
         ("substring", deg_sub)],
        r=2):
    common_nodes = [x for x in a if x in b]
    values_a, values_b = [], []
    for node in common_nodes:
        values_a += [a[node]]
        values_b += [b[node]]
    r, p = spearmanr(values_a, values_b)
    table += [[mA, mB, r, p]]
print(tabulate(table))