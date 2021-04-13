# Partial Colexifications

This package collects initial experimental code on partial colexifications,
which will eventually be turned into a full-fledge library in the style of
pyclics and can then also be turned into a web application such as the
[CLICS](https://clics.clld.org) database.

Initial code on partial colexifications can be found in the folder `develop`. Here, you find one initial experiment which computes partial (prefix and suffix) colexifications as well as substring colexifications from the data submitted along with the CLICS-1 database from 2014 (we use this CLICS database for development and will later include all data assembled for CLICS-2 and CLICS-3). 

To make the results accessible, a small subset was created from the data, which shows only a selected collection of body parts. Results are given in GML form, which can be inspected with Cytoscape and similar graph manipulation software. 

To run this initial code, just use the script `palex.py`:

```
$ python palex.py
```

You will need `lingpy`, `networkx` and `pyglottolog`, as well as the Glottolog data (https://github.com/glottolog/glottolog) to run this script.

An additional experiment serves to plot the data for the colexification of "eye", "water", and "tears". To run this code, you need to install `matplotlib` and `cartopy`. Then, you can run the code as:

```
$ python cart.py
```

And it will create two maps, one showing all languages in the sample, and one showing only the South-East Asian part.
