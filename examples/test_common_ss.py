from cltoolkit import Wordlist
from pacs.colexifications import full_colexifications, common_substring_colexifications
from pycldf import Dataset
from pyclts import CLTS
from pacs.util import write_gml
from tabulate import tabulate

bipa = CLTS().bipa


wl = Wordlist([Dataset.from_metadata("allenbai/cldf/cldf-metadata.json")],
              ts=bipa)

graph = full_colexifications(wl)
graph2 = common_substring_colexifications(wl)

table = []
for nA, nB, data in graph2.edges(data=True):
    if data["count"] >= 2:
        try:
            table += [[
                nA,
                nB,
                data["count"],
                data["substrings"],
                graph[nA][nB]["count"]]]
        except:
            table += [[
                nA,
                nB,
                data["count"],
                data["substrings"],
                0]]

print(tabulate(sorted(table, key=lambda x: (x[2], x[3]), reverse=True)))

write_gml(graph, "colex.gml")
write_gml(graph2, "susgraph.gml")
