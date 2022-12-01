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
from pycldf import Dataset
from pyclts import CLTS
from tabulate import tabulate

bipa = CLTS().bipa

wl = Wordlist([Dataset.from_metadata("allenbai/cldf/cldf-metadata.json")],
              ts=bipa)

graph = full_colexifications(wl)
digraphA = affix_colexifications(wl)
digraphB = affix_colexifications_by_pairwise_comparison(wl)
graphB = common_substring_colexifications(wl)

diffs = []
for nA, nB, data in digraphA.edges(data=True):
    countA = data["count"]
    try:
        countB = digraphB[nA][nB]["count"]
        source_a, target_a = " / ".join(data["source_forms"]), " / ".join(data["target_forms"])
        source_b, target_b = " / ".join(digraphB[nA][nB]["source_forms"]), " / ".join(digraphB[nA][nB]["target_forms"])
    except:
        countB = 0
        source_a, target_a = " / ".join(data["source_forms"]), " / ".join(data["target_forms"])
        source_b, target_b = "", ""
    if countA != countB:
        diffs += [(nA, nB, countA, countB, source_a, target_a, source_b, target_b)]
    
print(tabulate(diffs))

