# GAMA · Galician Metrical Analyzer · Symbolic 

Our first system (symbolic) for metrical scansion in Galician, presented in the following work:

> Pablo Ruiz Fabo, Pauline Moreau, Anxo Alonso Pérez. (2026). Automatic Metrical Scansion of Galician Poetry: First Results. In *Proceedings of the 17th International Conference on Computational Processing of Portuguese (PROPOR 2026) - Vol. 1*, pp. 994–1004, Salvador, Brazil. Association for Computational Linguistics. https://aclanthology.org/2026.propor-1.101/

A web interface using the system is deployed at https://prf2.org/gama/.

**Newer version:** A later version of the system, installable with pip and with a command line and Python interface, is at [compellit/gama](https://github.com/compellit/gama). It reproduces the published results (see its [evaluation](https://github.com/compellit/gama/tree/main/evaluation)).

## Introduction

The system is in `src`. An example client that runs both preprocessing and scansion on a text is at `src/run_clients.sh`.

From `src`, `run_prepro.py` runs preprocessing and `run_scan_eval.py` runs scansion. The  `-h` option shows available options.

Note: This repository corresponds to the initial submission. Some improvements done before the camera-ready are not here; they are in [compellit/gama](https://github.com/compellit/gama), which reproduces the camera-ready results. 

### Setup

Required packages are in [`requirements.txt`](./requirements.txt). 

To run the system, some large files that wouldn't fit without LFS need to be downloaded. The following command downloads them to the required directory (script must be executable):

```bash
./download_large_files.sh
```

## Example

To get an example output, you can run `run_clients.sh` (from `src`, script must be executable). This runs preprocessing and scansion with the same options used for the paper. There is an example poem in the script already, but you can pass a file with your own text using the `-p` flag. The command (using the poem already in the script) is: 

```bash
./run_clients.sh -r 300 
```

This will create a directory called `../texts/run_300/` with the poem at `../texts/run_300/example_001.txt`. Preprocessing output will be in `../texts/run_300/out_300` and scansion output will be at `../texts/run_300/out_300/scansion_output_300.tsv`. The value of `-r` is a run-ID. 

To run with your own poem (here at path `../texts/example_input_poem.txt`, the command would be (using 301 as a run ID):

```bash
./run_clients.sh -r 301 -p ../texts/example_input_poem.txt
```

## Data

- [Annotation criteria](./src/scansion/eval/data/annotation-criteria.md).

- [Test data](./src/scansion/eval/data/README.md).