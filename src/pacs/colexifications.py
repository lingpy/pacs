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


def affix_candidates(sequence, min_length, min_diff):
    affixes = []
    slen = len(sequence)
    svert = sequence[::-1]
    # start with prefixes
    for i in range(min_length, slen-min_diff+1):
        affixes.append(sequence[:i])
        affixes.append(svert[:i][::-1])
    return affixes


def full_colexifications(
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


def affix_colexifications_by_pairwise_comparison(
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


def affix_colexifications(
        wordlist, 
        source_threshold=2,
        target_threshold=5,
        difference_threshold=2,
        concepts=None,
        concept_attr="concepticon_gloss",
        family=None):
    """
    Compute affix colexifications from a wordlist.

    @param wordlist: The wordlist in CLToolkit.
    @param source_threshold: the threshold of the word form that should be the suffix of the other word.
    @param target_threshold: the minimal length of the word functioning as target.
    @param difference_threshold: minimal length difference between source and target.
    """
    graph = nx.DiGraph()
    # concept conversion, using concepticon gloss as default
    concept_factory = lambda x: getattr(x, concept_attr)

    if family is None:
        languages = [language for language in wordlist.languages]
    else:
        languages = [language for language in wordlist.languages if language.family == family]
    if concepts is None:
        concepts = [concept_factory(concept) for concept in wordlist.concepts]
    
    aout = {}  # todo: delete
    cout = {}  # todo: delete
    for language in progressbar(languages, desc="computing colexifications"):
        affixes = defaultdict(list)
        valid_forms = [f for f in language.forms_with_sounds if f.concept]
        # first run, only extract source forms
        for form in valid_forms:
            wlen = len(form.sounds)
            if wlen >= target_threshold:
                for ngram in affix_candidates(tuple(form.sounds), source_threshold, difference_threshold):
                    affixes[ngram] += [form]
            aout[language.id] = affixes  # TODO: delete
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
        cout[language.id] = cols  # todo delete

        for source, targets in cols.values():
            concept = concept_factory(source.concept)
            try:
                graph.nodes[concept]["source_occurrences"] += [source.id]
                graph.nodes[concept]["source_forms"] += [str(source.sounds)]
                graph.nodes[concept]["source_varieties"] += [language.id]
                graph.nodes[concept]["source_languages"] += [language.glottocode]
                graph.nodes[concept]["source_families"] += [language.family]
            except KeyError:
                graph.add_node(
                        concept,
                        source_families=[language.family],
                        source_forms=[str(source.sounds)],
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
                tconcept = concept_factory(t.concept)
                try:
                    graph.nodes[tconcept]["target_occurrences"] += [t.id]
                    graph.nodes[tconcept]["target_forms"] += [str(t.sounds)]
                    graph.nodes[tconcept]["target_varieties"] += [language.id]
                    graph.nodes[tconcept]["target_languages"] += [language.glottocode]
                    graph.nodes[tconcept]["target_families"] += [language.family]
                except KeyError:
                    graph.add_node(
                            tconcept,
                            source_families=[],
                            source_forms=[],
                            source_languages=[],
                            source_occurrences=[],
                            source_varieties=[],
                            target_families=[language.family],                           
                            target_forms=[str(t.sounds)],
                            target_languages=[language.glottocode],
                            target_occurrences=[t.id],
                            target_varieties=[language.id],
                            )
                
                # add the edges
                try:
                    graph[concept][tconcept]["count"] += 1
                    graph[concept][tconcept]["source_forms"] += [str(source.sounds)]
                    graph[concept][tconcept]["target_forms"] += [str(t.sounds)]
                    graph[concept][tconcept]["varieties"] += [language.id]
                    graph[concept][tconcept]["languages"] += [language.glottocode]
                    graph[concept][tconcept]["families"] += [language.family]
                except KeyError:
                    graph.add_edge(
                            concept,
                            tconcept,
                            count=1,
                            source_forms=[str(source.sounds)],
                            target_forms=[str(t.sounds)],
                            varieties=[language.id],
                            languages=[language.glottocode],
                            families=[language.family],
                            )
    return graph


