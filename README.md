# Inference of Partial Colexifications from Multilingual Wordlists: Supplementary Material

This repository provides the supplementary material for the study "Inference of Partial Colexifications from Multilingual Wordlists", currently under review. When using the code in this repository, please cite the following paper:

> List, Johann-Mattis (2023): Inference of Partial Colexifications from Multilingual Wordlists. Preprint, not peer reviewed. Chair of Multilingual Computational Linguistics: Passau.

## 1 Getting Started

In order to install the package, just use PIP, after having git-cloned the package:
```
$ git clone https://github.com/lingpy/pacs.git
$ cd pacs
$ pip install -e .
```

For the concrete usage of the `pacs` package, more documentation and examples will be given in the future.

## 2 Preparing to Run the Experiments Described in the Paper

In order to set up the data (IDS and Allen's Bai data), open a terminal in the folder `pacs` and git-clone the two repositories:

```
$ cd examples
$ git clone https://github.com/intercontinental-dictionary-series/idssegmented
$ cd idssegmented
$ git checkout v0.2
$ cd ..
$ git clone https://github.com/lexibank/allenbai.git
$ cd allenbai
$ git checkout v4.0.0
$ cd ..
```

You can also open a terminal in the `examples` folder and run the Makefile:

```
$ make download
```

To install all secondary packages needed for the computation, please type:

```
$ pip install -r requirements.txt
```

## 2 Running the Experiments

The scripts for the experiments are all provided in the folder `examples`. You can run them by opening a terminal in the folder and then calling them by typing `python script.py` in the terminal. Please make sure to use a fresh virtual environment, to make sure no conflicts of old versions occur (which may cause this workflow to fail).

### 2.1 Compute Colexification Networks

The following command computes three different kinds of colexification networks (full, affix, and overlap).

```
$ python compute-graphs.py
```

This will (re)create the files:

* `colexification-full.gml`
* `colexification-affix.gml`
* `colexification-overlap.gml`

The Makefile can also be used by typing: 

```
$ make colexifications 
```


### 2.2 Computation Time Comparison

In order to run the experiment on the computation time comparison, you can either type:

```
$ python computing-time-comparison.py
```

Or use the Makefile:

```
$ make computation-time
```

### 2.3 Compare the Degree Distributions of the Graphs

The graphs which were computed for the study are provided in the zip-folder `colexification-graphs.zip`, since they would otherwise be rather large. You need to unzip them in the `examples` folder if you want to run this experiment without having run the code in §2.1. 

In order to compare the degree distributions, type:

```
$ python compare-graphs.py
```

Or type:

```
$ make compare-graphs
```

This will output the following table:

```
---------------------------------  ---------------------------------  ----  -------  ------
Full Colexification                Affix Colexification (In-Degree)   1308   0.0960  0.0000
Full Colexification                Affix Colexification (Out-Degree)  1308   0.5034  0.0000
Full Colexification                Overlap Colexification             1307   0.1179  0.0000
Affix Colexification (In-Degree)   Affix Colexification (Out-Degree)  1308  -0.0830  0.0000
Affix Colexification (In-Degree)   Overlap Colexification             1307   0.4212  0.0000
Affix Colexification (Out-Degree)  Overlap Colexification             1307  -0.0488  0.0104
---------------------------------  ---------------------------------  ----  -------  ------
```

It will also create plots of the data.

### 2.4 Extract Sub-Graphs from the Data

In order to extract subgraphs reported in the paper from the data, type:

```
$ python extract-subgraphs.py
```

Or type:

```
$ make subgraphs
```

This will create three files:

* `subgraph-full.gml`
* `subgraph-affix.gml`
* `subgraph-overlap.gml`

