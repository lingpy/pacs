"""
compare computing times and make sure output is identical
"""

from cltoolkit import Wordlist
from pacs.colexifications import (
        affix_colexifications,
        affix_colexifications_by_pairwise_comparison
        )
from pycldf import Dataset
from pyclts import CLTS
from lexibank_allenbai import Dataset as AllenBai

import timeit
import functools

wl = Wordlist([Dataset.from_metadata(AllenBai().cldf_dir.joinpath("cldf-metadata.json"))],
              ts=CLTS().bipa)

digraphA = affix_colexifications(wl)
digraphB = affix_colexifications_by_pairwise_comparison(wl)

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

if diffs:
    print(tabulate(diffs))
else:
    print("[i] no differences found for the fast and the slow computation of partial colexifications")

def colex(fun):
    fun(wl)

t_a = timeit.Timer(functools.partial(colex, affix_colexifications))
t_b = timeit.Timer(functools.partial(colex, affix_colexifications_by_pairwise_comparison))

t1 = t_a.timeit(10)
t2 = t_b.timeit(10)
print("Affix Colexification Fast: {0:.2f}".format(t1))
print("Affix Colexification Slow: {0:.2f}".format(t2))