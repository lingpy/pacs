"""
Sequence operations.
"""
import itertools
import networkx as nx
from collections import defaultdict
from tqdm import tqdm as progressbar


def sounds_without_plus(form):
    return tuple([str(s) for s in form.sound_objects if s.type not in ("marker", "tone")])



def extend_nodes(graph, node, **kw):
    if not node in graph:
        graph.add_node(node, **kw)
    else:
        for k, v in kw.items():
            graph.nodes[node][k] += v


def extend_edges(graph, node_a, node_b, **kw):
    try:
        graph[node_a][node_b]
        for k, v in kw.items():
            graph[node_a][node_b][k] += v
    except:
        graph.add_edge(node_a, node_b, **kw)


def add_counts(graph, counts=None):
    counts = counts or [
            ("varieties", "variety"), ("languages", "language"),
            ("families", "family"), ("forms", "form")]
    for nA, nB, data in graph.edges(data=True):
        for pl, sg in counts:
            graph[nA][nB][sg+"_count"] = len(set(data[pl]))
    for node, data in graph.nodes(data=True):
        for pl, sg in counts:
            graph.nodes[node][sg+"_count"] = len(set(data[pl]))


def substring_candidates(sequence, min_length, min_diff):
    """
    Return substring candidates which recur in the beginning or end of a word.

    NOTE: function is not used for now.
    """
    slen, j = len(sequence), len(sequence)
    i = 0
    out = []
    while i != j and i < j:
        # copy the sequence
        new_sequence = sequence[i:j]
        if len(new_sequence) >= min_length:
            if slen - len(new_sequence) >= min_diff:
                out += [new_sequence]
            # loop over the new sequence
            for k in range(1, len(new_sequence)):
                segment_a, segment_b = new_sequence[:k], new_sequence[k:]
                if len(segment_a) >= min_length and slen - len(segment_a) >= min_diff:
                    out += [segment_a]
                if len(segment_b) >= min_length and slen - len(segment_b) >= min_diff:
                    out += [segment_b]
        i += 1
        j -= 1
    return out





def affix_candidates(sequence, min_length, min_diff):
    affixes = []
    slen = len(sequence)
    svert = sequence[::-1]
    # start with prefixes
    for i in range(min_length, slen-min_diff+1):
        affixes.append(sequence[:i])
        affixes.append(svert[:i][::-1])
    return affixes


def affixes(tupA, tupB):
    """
    Simple affix check for tuples.
    """
    if tupB[:len(tupA)] == tupA:
        return True
    elif tupB[-(len(tupA)):] == tupA:
        return True
    return False



def full_colexifications(
        wordlist, 
        family=None, 
        languages=None,
        concept_attr="concepticon_gloss",
        form_factory=None
        ):
    """
    @param wordlist: A cltoolkit Wordlist instance.
    @param family: A string for a language family (valid in Glottolog). When set to None, won't filter by family.
    @param concepts: A list of concepticon glosses that will be compared with the glosses in the wordlist.
        If set to None, concepts won't be filtered.
    @returns: A networkx.Graph instance.

    @todo: discuss if we should add a form_factory, deleting tones,
           and the like, for this part of the analysis as well,
           as we do for partial colexifications
    """
    graph = nx.Graph()
    # concept lookup checks for relevant concepticon attribute
    concept_factory = lambda x: getattr(x, concept_attr) if x else None
    form_factory = form_factory or sounds_without_plus
    
    if languages is None:
        if family is None:
            languages = [language for language in wordlist.languages]
        else:
            languages = [language for language in wordlist.languages if language.family == family]
    concepts = [concept_factory(concept) for concept in wordlist.concepts if concept_factory(concept)]

    for language in languages:
        cols = defaultdict(list)
        for form in language.forms_with_sounds:
            if concept_factory(form.concept) in concepts:
                tform = str(form.sounds)
                cols[tform] += [form]

        # add nodes to the graph
        colexs = []
        for tokens, forms in cols.items():
            colexs += [
                    (
                        tokens, 
                        [f for f in forms if f.concept], 
                        [concept_factory(f.concept) for f in forms if concept_factory(f.concept)]
                        )
                    ]
            for (f, concept) in zip(colexs[-1][1], colexs[-1][2]):
                extend_nodes(
                        graph,
                        concept,
                        forms=[f.id],
                        words=[tokens],
                        languages=[language.glottocode],
                        varieties=[language.id],
                        families=[language.family]
                        )

        for tokens, forms, all_concepts in colexs:
            if len(set(all_concepts)) > 1:
                for (f1, c1), (f2, c2) in itertools.combinations(zip(forms, all_concepts), r=2):
                    if c1 == c2:
                        continue
                    extend_edges(
                            graph,
                            c1,
                            c2,
                            count=1,
                            forms=["{0} / {1}".format(f1.id, f2.id)],
                            words=[tokens],
                            varieties=[language.id],
                            languages=[language.glottocode],
                            families=[language.family]
                            )
    add_counts(graph)
    return graph


def affix_colexifications_by_pairwise_comparison(
        wordlist,
        source_threshold=2,
        target_threshold=5,
        difference_threshold=2,
        form_factory=None,
        concept_attr="concepticon_gloss",
        family=None):
    """
    """
    
    graph = nx.DiGraph()
    if family is None:
        languages = [language for language in wordlist.languages]
    else:
        languages = [language for language in wordlist.languages if language.family == family]

    form_factory = form_factory or sounds_without_plus
    concept_factory = lambda x: getattr(x, concept_attr) if x else None

    
    for language in progressbar(languages, desc="computing affix colexifications (pairwise)"):
        cols = defaultdict(list)
        valid_forms = [(f, form_factory(f), concept_factory(f.concept)) for f in language.forms_with_sounds if concept_factory(f.concept)]
        for (formA, sndsA, concept_a), (formB, sndsB, concept_b) in itertools.combinations(valid_forms, r=2):
            lA, lB = len(sndsA), len(sndsB)
            if concept_a and concept_a != concept_b:
                if affixes(sndsA, sndsB):
                    if lA >= source_threshold and lB >= target_threshold and \
                            lB - lA >= difference_threshold:
                        try:
                            graph.nodes[concept_a]["source_occurrences"] += [formA.id]
                            graph.nodes[concept_a]["source_forms"] += [" ".join(sndsA)]
                            graph.nodes[concept_a]["source_varieties"] += [language.id]
                            graph.nodes[concept_a]["source_languages"] += [language.glottocode]
                            graph.nodes[concept_a]["source_families"] += [language.family]
                        except KeyError:
                            graph.add_node(
                                    concept_a,
                                    source_families=[language.family],
                                    source_forms=[" ".join(sndsA)],
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
                            graph.nodes[concept_b]["target_occurrences"] += [formB.id]
                            graph.nodes[concept_b]["target_forms"] += [" ".join(sndsB)]
                            graph.nodes[concept_b]["target_varieties"] += [language.id]
                            graph.nodes[concept_b]["target_languages"] += [language.glottocode]
                            graph.nodes[concept_b]["target_families"] += [language.family]
                        except KeyError:
                            graph.add_node(
                                    concept_b,
                                    source_families=[],
                                    source_forms=[],
                                    source_languages=[],
                                    source_occurrences=[],
                                    source_varieties=[],
                                    target_families=[language.family],
                                    target_forms=[" ".join(sndsB)],
                                    target_languages=[language.glottocode],
                                    target_occurrences=[formB.id],
                                    target_varieties=[language.id],
                                    )
                        # add the edges
                        try:
                            graph[concept_a][concept_b]["count"] += 1
                            graph[concept_a][concept_b]["source_forms"] += [" ".join(sndsA)]
                            graph[concept_a][concept_b]["target_forms"] += [" ".join(sndsB)]
                            graph[concept_a][concept_b]["varieties"] += [language.id]
                            graph[concept_a][concept_b]["languages"] += [language.glottocode]
                            graph[concept_a][concept_b]["families"] += [language.family]
                        except KeyError:
                            graph.add_edge(
                                    concept_a,
                                    concept_b,
                                    count=1,
                                    source_forms=[" ".join(sndsA)],
                                    target_forms=[" ".join(sndsB)],
                                    varieties=[language.id],
                                    languages=[language.glottocode],
                                    families=[language.family],
                                    )
                elif affixes(sndsB, sndsA):
                    if lB >= source_threshold and lA >= target_threshold and \
                            lA - lB >= difference_threshold:
                        try:
                            graph.nodes[concept_b]["source_occurrences"] += [formB.id]
                            graph.nodes[concept_b]["source_forms"] += [" ".join(sndsB)]
                            graph.nodes[concept_b]["source_varieties"] += [language.id]
                            graph.nodes[concept_b]["source_languages"] += [language.glottocode]
                            graph.nodes[concept_b]["source_families"] += [language.family]
                        except KeyError:
                            graph.add_node(
                                    concept_b,
                                    source_families=[language.family],
                                    source_forms=[" ".join(sndsB)],
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
                            graph.nodes[concept_a]["target_occurrences"] += [formA.id]
                            graph.nodes[concept_a]["target_forms"] += [" ".join(sndsA)]
                            graph.nodes[concept_a]["target_varieties"] += [language.id]
                            graph.nodes[concept_a]["target_languages"] += [language.glottocode]
                            graph.nodes[concept_a]["target_families"] += [language.family]
                        except KeyError:
                            graph.add_node(
                                    concept_a,
                                    source_families=[],
                                    source_forms=[],
                                    source_languages=[],
                                    source_occurrences=[],
                                    source_varieties=[],
                                    target_families=[language.family],
                                    target_forms=[" ".join(sndsB)],
                                    target_languages=[language.glottocode],
                                    target_occurrences=[formA.id],
                                    target_varieties=[language.id],
                                    )
                        # add the edges
                        try:
                            graph[concept_b][concept_a]["count"] += 1
                            graph[concept_b][concept_a]["source_forms"] += [" ".join(sndsB)]
                            graph[concept_b][concept_a]["target_forms"] += [" ".join(sndsA)]
                            graph[concept_b][concept_a]["varieties"] += [language.id]
                            graph[concept_b][concept_a]["languages"] += [language.glottocode]
                            graph[concept_b][concept_a]["families"] += [language.family]
                        except KeyError:
                            graph.add_edge(
                                    concept_b,
                                    concept_a,
                                    count=1,
                                    source_forms=[" ".join(sndsB)],
                                    target_forms=[" ".join(sndsA)],
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
        concept_attr="concepticon_gloss",
        form_factory=None,
        family=None
        ):
    """
    Compute affix colexifications from a wordlist.

    @param wordlist: The wordlist in CLToolkit.
    @param source_threshold: the threshold of the word form that should be the suffix of the other word.
    @param target_threshold: the minimal length of the word functioning as target.
    @param difference_threshold: minimal length difference between source and target.
    @param concept_attr: the attribute of the Concept class in CL Toolkit.
    @param family: select if you want to restrict colexifications to one family.
    """
    graph = nx.DiGraph()
    # concept conversion, using concepticon gloss as default
    concept_factory = lambda x: getattr(x, concept_attr) if x else None
    form_factory = form_factory or sounds_without_plus

    if family is None:
        languages = [language for language in wordlist.languages]
    else:
        languages = [language for language in wordlist.languages if language.family == family]

    for language in progressbar(languages, desc="computing affix colexifications"):
        affixes = defaultdict(list)
        valid_forms = [(f, concept_factory(f.concept), form_factory(f)) for f in language.forms_with_sounds if concept_factory(f.concept)]
        # first run, only extract source forms
        for (form, concept, tform) in valid_forms:
            wlen = len(tform)
            if wlen >= target_threshold:
                for ngram in affix_candidates(tform, source_threshold, difference_threshold):
                    affixes[ngram] += [(form, concept, tform)]
        cols = defaultdict(list)
        for (form, concept, tform) in valid_forms:
            wlen = len(tform)
            if wlen >= source_threshold and tform in affixes:
                targets, visited = [], set()
                for (affixed_form, concept_b, tform_b) in affixes[tform]:
                    if concept != concept_b and affixed_form.id not in visited:
                        targets += [(affixed_form, concept_b, " ".join(tform_b))]
                        visited.add(affixed_form.id)
                if targets:
                    cols[form.id] = ((form, concept, " ".join(tform)), targets)

        for (source, concept, tform), targets in cols.values():
            extend_nodes(
                    graph, 
                    concept, 
                    source_families=[language.family],
                    source_forms=[tform],
                    source_languages=[language.glottocode],
                    source_occurrences=[source.id],
                    source_varieties=[language.id],
                    target_families=[],
                    target_forms=[],
                    target_languages=[],
                    target_occurrences=[],
                    target_varieties=[],
                    varieties=[language.id],
                    families=[language.family],
                    languages=[language.glottocode]
                    )
            for (t, tconcept, tform_b) in targets:
                extend_nodes(
                        graph,
                        tconcept,
                        source_families=[],
                        source_forms=[],
                        source_languages=[],
                        source_occurrences=[],
                        source_varieties=[],
                        target_families=[language.family],                           
                        target_forms=[tform_b],
                        target_languages=[language.glottocode],
                        target_occurrences=[t.id],
                        target_varieties=[language.id],
                        varieties=[language.id],
                        families=[language.family],
                        languages=[language.glottocode]
                        )
                
                # add the edges
                extend_edges(
                        graph,
                        concept,
                        tconcept,
                        count=1,
                        source_forms=[tform],
                        target_forms=[tform_b],
                        varieties=[language.id],
                        languages=[language.glottocode],
                        families=[language.family]
                        )
    add_counts(graph, counts=[
        ("varieties", "variety"),
        ("families", "family"),
        ("languages", "language")
    ])
    return graph


def common_ngrams(
        language, 
        minimal_length_threshold=2, 
        difference_threshold=2,
        form_factory=None,
        concept_factory=None,
        candidates=None
        ):
    """
    Return all ngrams recurring in more than one word for a CL Toolkit language.

    Note that common ngrams here are those which occur in affix position.
    """
    form_factory = form_factory or sounds_without_plus
    if not concept_factory:
        concept_factory = lambda x: getattr(x, "concepticon_gloss") if x else None
    candidates = candidates or affix_candidates
    valid_forms = [(f, concept_factory(f.concept), form_factory(f)) for f in
            language.forms_with_sounds if concept_factory(f.concept) and
            len(form_factory(f)) >= minimal_length_threshold +
            difference_threshold]

    ngrams = defaultdict(list)
    for (form, concept, tform) in valid_forms:
        for ngram in candidates(
            tform, minimal_length_threshold, difference_threshold
        ):
            ngrams[ngram] += [(form, concept, " ".join(tform), tform)]
            
    return sorted(
            [(a, b) for a, b in ngrams.items() if len(b) > 1],
            key=lambda x: len(x[0]),
            reverse=True)


def common_substring_colexifications(
        wordlist,
        minimal_length_threshold=4,
        difference_threshold=3,
        concept_attr="concepticon_gloss",
        form_factory=None,
        family=None):
    """
    Compute common substring colexifications from a wordlist.

    @param wordlist: The wordlist in CLToolkit.
    @param minimal_length_threshold: the threshold of the word form that should be the suffix of the other word.
    @param difference_threshold: minimal length difference between source and target.
    """
    graph = nx.Graph()
    # concept conversion, using concepticon gloss as default
    concept_factory = lambda x: getattr(x, concept_attr) if x else None
    form_factory = form_factory or sounds_without_plus

    if family is None:
        languages = [language for language in wordlist.languages]
    else:
        languages = [language for language in wordlist.languages if language.family == family]

    for language in progressbar(languages, desc="computing common substring colexifications"):
        ngrams = common_ngrams(
                language, 
                minimal_length_threshold=minimal_length_threshold,
                difference_threshold=difference_threshold,
                form_factory=form_factory,
                concept_factory=concept_factory
                )
        visited_forms = set()
        for ngram, forms in ngrams:
            for (f_a, concept_a, str_a, tup_a), (f_b, concept_b, str_b, tup_b) in itertools.combinations(forms, r=2):
                if concept_a != concept_b and str(f_a.sounds) != str(f_b.sounds):
                    # check for visited form identifiers to only count each substring once
                    if (f_a.id, f_b.id) in visited_forms:
                        pass
                    elif affixes(tup_a, tup_b) or affixes(tup_b, tup_a):
                        visited_forms.update([(f_a.id, f_b.id), (f_b.id, f_a.id)])
                    else:
                        visited_forms.update([(f_a.id, f_b.id), (f_b.id, f_a.id)])
                        for (concept, form, tform) in ((concept_a, f_a, str_a), (concept_b, f_b, str_b)):
                            extend_nodes(
                                    graph,
                                    concept,
                                    families=[language.family],
                                    languages=[language.glottocode],
                                    forms=[form.id],
                                    varieties=[language.id]
                                    )
                        extend_edges(
                                graph,
                                concept_a,
                                concept_b,
                                count=1,
                                forms=["{0} {1}".format(f_a.id, f_b.id)],
                                substrings=[" ".join(ngram)],
                                varieties=[language.id],
                                languages=[language.glottocode],
                                families=[language.family],
                            )
    add_counts(graph)
    return graph

