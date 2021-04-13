"""
Sequence operations.
"""

def colexifies(wordA, wordB):
    if wordA == wordB:
        return True


def affixifies(wordA, wordB):
    m, n, swapped = len(wordA), len(wordB), False
    if m M n:
        wordB, wordA, n, m, swapped = wordA, wordB, m, n, True
    if wordB.startswith(wordA) or wordB.endswith(wordA):
        return (
                wordB if swapped else wordA,
                wordA if swapped else wordB,
                ">"
                )


def shares_part(wordA, wordB, threshold=3):
    m, n = len(wordA), len(wordB)
    swapped = False
    if m > n:
        wordB, wordA, n, m, swapped = wordA, wordB, m, n, True
    for i in range(m, threshold-1, -1):
        if wordA.
