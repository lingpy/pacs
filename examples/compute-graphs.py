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
from pacs.util import write_gml
from pycldf import Dataset
from pyclts import CLTS

wl = Wordlist([Dataset.from_metadata("idssegmented/cldf/cldf-metadata.json")],
              ts=CLTS().bipa)

graphA = full_colexifications(wl)
graphB = affix_colexifications(wl, source_threshold=2, target_threshold=5)
graphC = common_substring_colexifications(wl, minimal_length_threshold=4,
        difference_threshold=3)

print("[i] writing graphs to file")
write_gml(graphA, "colexification-full.gml")
write_gml(graphB, "colexification-affix.gml", )
write_gml(graphC, "colexification-overlap.gml")


