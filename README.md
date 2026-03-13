# GAMA · Galician Metrical Analyzer · Symbolic 

Our first system (symbolic) for metrical scansion in Galician, presented in the following work:

> Pablo Ruiz Fabo, Pauline Moreau, Anxo Alonso Pérez. (2026). Automatic Metrical Scansion of Galician Poetry: First Results. To appear in *Proceedings of PROPOR - 17th International Conference on Computational Processing of Portuguese*

## Introduction

The system is in `src`. An example client that runs both preprocessing and scansion on a text is at `src/run_clients.sh`.

From `src`, `run_prepro.py` runs preprocessing and `run_scan_eval.py` runs scansion. The  `-h` option shows available options. The instructions to reproduce results below also show examples how to use the tool.

Note: This repository corresponds to the initial submission. Some improvements done before the camera-ready are not here yet. 

### Setup

Required packages are in [`requirements.txt`](./requirements.txt). 

To run the system, some large files that wouldn't fit without LFS need to be downloaded. The following command downloads them to the required directory (script must be executable):

```bash
./download_large_files.sh
```

Then the system can be run and reproduces the initial version of the paper. 

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