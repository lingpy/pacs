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

wl = Wordlist([Dataset.from_metadata("idssegmented/cldf/cldf-metadata.json")],
              ts=CLTS().bipa)

graphA = full_colexifications(wl)
graphB = affix_colexifications(wl)
graphC = common_substring_colexifications(wl)


print(len(graphA.edges()))
print(len(graphB.edges()))
print(len(graphC.edges()))
