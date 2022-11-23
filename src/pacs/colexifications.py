"""
Sequence operations.
"""
import itertools
import networkx as nx
from lingpy.align.pairwise import Pairwise
from collections import defaultdict
from lingpy.algorithm import extra
from lingpy.sequence.ngrams import get_all_ngrams
from lingpy.algorithm import clustering as cluster
import numpy as np
from tqdm import tqdm as progressbar


def get_colexifications(
        wordlist, family=None, concepts=None):
    """
    @param wordlist: A cltoolkit Wordlist instance.
    @param family: A string for a language family (valid in Glottolog). When set to None, won't filter by family.
    @param concepts: A list of concepticon glosses that will be compared with the glosses in the wordlist.
        If set to None, concepts won't be filtered.
    @returns: A networkx.Graph instance.
    """
    graph = nx.Graph()
    if family is None:
        languages = [language for language in wordlist.languages]
    else:
        languages = [language for language in wordlist.languages if language.family == family]
    if concepts is None:
        concepts = [concept.concepticon_gloss for concept in wordlist.concepts]

    for language in progressbar(languages, desc="compute colexifications"):
        cols = defaultdict(list)
        for form in language.forms_with_sounds:
            if form.concept and form.concept.concepticon_gloss in concepts:
                tform = str(form.sounds)
                cols[tform] += [form]

        # add nodes to the graph
        colexs = []
        for tokens, forms in cols.items():
            colexs += [
                    (
                        tokens, 
                        [f for f in forms if f.concept], 
                        [f.concept.id for f in forms if f.concept]
                        )
                    ]
            for (f, concept) in zip(colexs[-1][1], colexs[-1][2]):
                try:
                    graph.nodes[concept]["occurrences"] += [f.id]
                    graph.nodes[concept]["words"] += [tokens]
                    graph.nodes[concept]["varieties"] += [language.id]
                    graph.nodes[concept]["languages"] += [language.glottocode]
                    graph.nodes[concept]["families"] += [language.family]
                except KeyError:
                    graph.add_node(
                            concept,
                            occurrences=[f.id],
                            words=[tokens],
                            varieties=[language.id],
                            languages=[language.glottocode],
                            families=[language.family]
                            )

        for tokens, forms, all_concepts in colexs:
            if len(set(all_concepts)) > 1:
                for (f1, c1), (f2, c2) in itertools.combinations(zip(forms, all_concepts), r=2):
                    if c1 == c2:
                        continue
                    # identical concepts need to be excluded
                    try:
                        graph[c1][c2]["count"] += 1
                        graph[c1][c2]["words"] += [tokens]
                        graph[c1][c2]["varieties"] += [language.id]
                        graph[c1][c2]["languages"] += [language.glottocode]
                        graph[c1][c2]["families"] += [language.family]
                    except KeyError:
                        graph.add_edge(
                                c1,
                                c2,
                                count=1,
                                words=[tokens],
                                varieties=[language.id],
                                languages=[language.glottocode],
                                families=[language.family],
                                )
    for nA, nB, data in graph.edges(data=True):
        graph[nA][nB]["variety_count"] = len(set(data["varieties"]))
        graph[nA][nB]["language_count"] = len(set(data["languages"]))
        graph[nA][nB]["family_count"] = len(set(data["families"]))
    for node, data in graph.nodes(data=True):
        graph.nodes[node]["language_count"] = len(set(data["languages"]))
        graph.nodes[node]["variety_count"] = len(set(data["varieties"]))
        graph.nodes[node]["family_count"] = len(set(data["families"]))
    return graph


def weight_by_cognacy(
        graph, 
        threshold=0.45,
        cluster_method="infomap",
        ):
    """
    Function weights the data by computing cognate sets.

    :todo: compute cognacy for concept slots to determine self-colexification
    scores.
    """
    if cluster_method == "infomap":
        cluster_function = extra.infomap_clustering
    else:
        cluster_function = cluster.flat_upgma

    for nA, nB, data in graph.edges(data=True):
        if data["count"] > 1:
            # assemble languages with different cognates
            if data["count"] == 2:
                pair = Pairwise(data["words"][0], data["words"][1])
                pair.align(distance=True)
                if pair.alignments[0][2] <= threshold:
                    weight = 1
                else:
                    weight = 2
            else:
                matrix = [[0 for _ in data["words"]] for _ in data["words"]]
                for (i, w1), (j, w2) in itertools.combinations(
                        enumerate(data["words"]), r=2):
                    pair = Pairwise(w1.split(), w2.split())
                    pair.align(distance=True)
                    matrix[i][j] = matrix[j][i] = pair.alignments[0][2]

                results = cluster_function(
                        threshold, 
                        matrix,
                        taxa=data["languages"])
                weight = len(results)
        else:
            weight = 1
        graph[nA][nB]["cognate_count"] = weight


def get_transition_matrix(graph, steps=10, weight="weight", normalize=False):
    """
    Compute transition matrix following Jackson et al. 2019
    """
    # prune nodes excluding singletons
    nodes = []
    for node in graph.nodes:
        if len(graph[node]) >= 1:
            nodes.append(node)
    a_matrix: list[list[int]] = [[0 for _ in nodes] for _ in nodes]

    for node_a, node_b, data in graph.edges(data=True):
        idx_a, idx_b = nodes.index(node_a), nodes.index(node_b)
        a_matrix[idx_a][idx_b] = a_matrix[idx_b][idx_a] = data[weight]
    d_matrix = [[0 for _ in nodes] for _ in nodes]
    diagonal = [sum(row) for row in a_matrix]
    for i in range(len(nodes)):
        d_matrix[i][i] = 1 / diagonal[i]

    p_matrix = np.matmul(d_matrix, a_matrix)
    new_p_matrix = sum([np.linalg.matrix_power(p_matrix, i) for i in range(1,
                                                                           steps + 1)])

    # we can normalize the matrix by dividing by the number of time steps
    if normalize:
        new_p_matrix = new_p_matrix / steps

    return new_p_matrix, nodes, a_matrix


def get_affix_colexifications_by_pairwise_comparison(
        wordlist,
        source_threshold=2,
        target_threshold=5,
        difference_threshold=2,
        concepts=None,
        family=None):
    """
    """
    def affixes(tupA, tupB):
        if tupB[:len(tupA)] == tupA:
            return True
        elif tupB[-(len(tupA)):] == tupA:
            return True
        return False
    
    graph = nx.DiGraph()
    if family is None:
        languages = [language for language in wordlist.languages]
    else:
        languages = [language for language in wordlist.languages if language.family == family]
    if concepts is None:
        concepts = [concept.concepticon_gloss for concept in wordlist.concepts]
    
    for language in progressbar(languages, desc="computing colexifications"):
        cols = defaultdict(list)
        valid_forms = [f for f in language.forms_with_sounds if f.concept]
        for formA, formB in itertools.combinations(valid_forms, r=2):
            if formA.concept.id != formB.concept.id:
                sndsA, sndsB = tuple(formA.sounds), tuple(formB.sounds)
                lA, lB = len(formA.sounds), len(formB.sounds)
                if affixes(sndsA, sndsB):
                    if lA >= source_threshold and lB >= target_threshold and \
                            lB - lA >= difference_threshold:
                        try:
                            graph.nodes[formA.concept.id]["source_occurrences"] += [formA.id]
                            graph.nodes[formA.concept.id]["source_forms"] += [formA.form]
                            graph.nodes[formA.concept.id]["source_varieties"] += [language.id]
                            graph.nodes[formA.concept.id]["source_languages"] += [language.glottocode]
                            graph.nodes[formA.concept.id]["source_families"] += [language.family]
                        except KeyError:
                            graph.add_node(
                                    formA.concept.id,
                                    source_families=[language.family],
                                    source_forms=[formA.form],
                                    source_languages=[language.glottocode],
                                    source_occurrences=[formB.id],
                                    source_varieties=[language.id],
                                    target_families=[],
                                    target_forms=[],
                                    target_languages=[],
                                    target_occurrences=[],
                                    target_varieties=[],
                                    )
                        try:
                            graph.nodes[formB.concept.id]["target_occurrences"] += [formB.id]
                            graph.nodes[formB.concept.id]["target_forms"] += [formB.form]
                            graph.nodes[formB.concept.id]["target_varieties"] += [language.id]
                            graph.nodes[formB.concept.id]["target_languages"] += [language.glottocode]
                            graph.nodes[formB.concept.id]["target_families"] += [language.family]
                        except KeyError:
                            graph.add_node(
                                    formA.concept.id,
                                    source_families=[],
                                    source_forms=[],
                                    source_languages=[],
                                    source_occurrences=[],
                                    source_varieties=[],
                                    target_families=[language.family],
                                    target_forms=[formB.form],
                                    target_languages=[language.glottocode],
                                    target_occurrences=[formB.id],
                                    target_varieties=[language.id],
                                    )
                        # add the edges
                        try:
                            graph[formA.concept.id][formB.concept.id]["count"] += 1
                            graph[formA.concept.id][formB.concept.id]["source_forms"] += [formA.form]
                            graph[formA.concept.id][formB.concept.id]["target_forms"] += [formB.form]
                            graph[formA.concept.id][formB.concept.id]["varieties"] += [language.id]
                            graph[formA.concept.id][formB.concept.id]["languages"] += [language.glottocode]
                            graph[formA.concept.id][formB.concept.id]["families"] += [language.family]
                        except KeyError:
                            graph.add_edge(
                                    formA.concept.id,
                                    formB.concept.id,
                                    count=1,
                                    source_forms=[formA.form],
                                    target_forms=[formB.form],
                                    varieties=[language.id],
                                    languages=[language.glottocode],
                                    families=[language.family],
                                    )
                elif affixes(sndsB, sndsA):
                    if lB >= source_threshold and lA >= target_threshold and \
                            lA - lB >= difference_threshold:
                        try:
                            graph.nodes[formB.concept.id]["source_occurrences"] += [formB.id]
                            graph.nodes[formB.concept.id]["source_forms"] += [formB.form]
                            graph.nodes[formB.concept.id]["source_varieties"] += [language.id]
                            graph.nodes[formB.concept.id]["source_languages"] += [language.glottocode]
                            graph.nodes[formB.concept.id]["source_families"] += [language.family]
                        except KeyError:
                            graph.add_node(
                                    formB.concept.id,
                                    source_families=[language.family],
                                    source_forms=[formB.form],
                                    source_languages=[language.glottocode],
                                    source_occurrences=[formA.id],
                                    source_varieties=[language.id],
                                    target_families=[],
                                    target_forms=[],
                                    target_languages=[],
                                    target_occurrences=[],
                                    target_varieties=[],
                                    )
                        try:
                            graph.nodes[formA.concept.id]["target_occurrences"] += [formA.id]
                            graph.nodes[formA.concept.id]["target_forms"] += [formA.form]
                            graph.nodes[formA.concept.id]["target_varieties"] += [language.id]
                            graph.nodes[formA.concept.id]["target_languages"] += [language.glottocode]
                            graph.nodes[formA.concept.id]["target_families"] += [language.family]
                        except KeyError:
                            graph.add_node(
                                    formB.concept.id,
                                    source_families=[],
                                    source_forms=[],
                                    source_languages=[],
                                    source_occurrences=[],
                                    source_varieties=[],
                                    target_families=[language.family],
                                    target_forms=[formA.form],
                                    target_languages=[language.glottocode],
                                    target_occurrences=[formA.id],
                                    target_varieties=[language.id],
                                    )
                        # add the edges
                        try:
                            graph[formB.concept.id][formA.concept.id]["count"] += 1
                            graph[formB.concept.id][formA.concept.id]["source_forms"] += [formB.form]
                            graph[formB.concept.id][formA.concept.id]["target_forms"] += [formA.form]
                            graph[formB.concept.id][formA.concept.id]["varieties"] += [language.id]
                            graph[formB.concept.id][formA.concept.id]["languages"] += [language.glottocode]
                            graph[formB.concept.id][formA.concept.id]["families"] += [language.family]
                        except KeyError:
                            graph.add_edge(
                                    formB.concept.id,
                                    formA.concept.id,
                                    count=1,
                                    source_forms=[formB.form],
                                    target_forms=[formA.form],
                                    varieties=[language.id],
                                    languages=[language.glottocode],
                                    families=[language.family],
                                    )
    return graph


def get_affix_colexifications(
        wordlist, 
        source_threshold=2,
        target_threshold=5,
        difference_threshold=2,
        concepts=None,
        family=None):
    """
    Compute affix colexifications from a wordlist.

    @param wordlist: The wordlist in CLToolkit.
    @param source_threshold: the threshold of the word form that should be the suffix of the other word.
    @param target_threshold: the minimal length of the word functioning as target.
    @param difference_threshold: minimal length difference between source and target.
    """
    graph = nx.DiGraph()
    if family is None:
        languages = [language for language in wordlist.languages]
    else:
        languages = [language for language in wordlist.languages if language.family == family]
    if concepts is None:
        concepts = [concept.concepticon_gloss for concept in wordlist.concepts]
    
    aout = {}
    cout = {}
    for language in progressbar(languages, desc="computing colexifications"):
        affixes = defaultdict(list)
        valid_forms = [f for f in language.forms_with_sounds if f.concept]
        # first run, only extract source forms
        for form in valid_forms:
            tform = ("^",)+tuple(form.sounds)+("$",)
            wlen = len(form.sounds)
            if wlen >= target_threshold:
                for ngram in get_all_ngrams(tform):
                    if ngram[0] == "^" and ngram[-1] != "$" and \
                            wlen - (len(ngram)-1) >= difference_threshold and \
                            len(ngram)-1 >= source_threshold:
                        affixes[ngram[1:]] += [form]
                    elif ngram[-1] == "$" and ngram[0] != "^" and \
                            wlen - (len(ngram)-1) >= difference_threshold and \
                            len(ngram)-1 >= source_threshold:
                        affixes[ngram[:-1]] += [form]
            aout[language.id] = affixes
        cols = defaultdict(list)
        for form in valid_forms:
            tform = tuple(form.sounds)
            wlen = len(form.sounds)
            if wlen >= source_threshold and tform in affixes:
                targets, visited = [], []
                for affix in affixes[tform]:
                    if form.concept.id != affix.concept.id and affix.id not in visited:
                        targets += [affix]
                        visited += [affix.id]
                if targets:
                    cols[form.id] = (form, targets)
        cout[language.id] = cols

        for source, targets in cols.values():
            try:
                graph.nodes[source.concept.id]["source_occurrences"] += [source.id]
                graph.nodes[source.concept.id]["source_forms"] += [source.form]
                graph.nodes[source.concept.id]["source_varieties"] += [language.id]
                graph.nodes[source.concept.id]["source_languages"] += [language.glottocode]
                graph.nodes[source.concept.id]["source_families"] += [language.family]
            except KeyError:
                graph.add_node(
                        source.concept.id,
                        source_families=[language.family],
                        source_forms=[source.form],
                        source_languages=[language.glottocode],
                        source_occurrences=[source.id],
                        source_varieties=[language.id],
                        target_families=[],
                        target_forms=[],
                        target_languages=[],
                        target_occurrences=[],
                        target_varieties=[],
                        )
            for t in targets:
                try:
                    graph.nodes[t.concept.id]["target_occurrences"] += [t.id]
                    graph.nodes[t.concept.id]["target_forms"] += [t.form]
                    graph.nodes[t.concept.id]["target_varieties"] += [language.id]
                    graph.nodes[t.concept.id]["target_languages"] += [language.glottocode]
                    graph.nodes[t.concept.id]["target_families"] += [language.family]
                except KeyError:
                    graph.add_node(
                            t.concept.id,
                            source_families=[],
                            source_forms=[],
                            source_languages=[],
                            source_occurrences=[],
                            source_varieties=[],
                            target_families=[language.family],                           
                            target_forms=[t.form],
                            target_languages=[language.glottocode],
                            target_occurrences=[t.id],
                            target_varieties=[language.id],
                            )
                
                # add the edges
                try:
                    graph[source.concept.id][t.concept.id]["count"] += 1
                    graph[source.concept.id][t.concept.id]["source_forms"] += [source.form]
                    graph[source.concept.id][t.concept.id]["target_forms"] += [t.form]
                    graph[source.concept.id][t.concept.id]["varieties"] += [language.id]
                    graph[source.concept.id][t.concept.id]["languages"] += [language.glottocode]
                    graph[source.concept.id][t.concept.id]["families"] += [language.family]
                except KeyError:
                    graph.add_edge(
                            source.concept.id,
                            t.concept.id,
                            count=1,
                            source_forms=[source.form],
                            target_forms=[t.form],
                            varieties=[language.id],
                            languages=[language.glottocode],
                            families=[language.family],
                            )
    return graph, aout, cout


