# GAMA · Galician Metrical Analyzer · Symbolic 

Our first system (symbolic) for metrical scansion in Galician, presented in the following work:

> Pablo Ruiz Fabo, Pauline Moreau, Anxo Alonso Pérez. (2026). Automatic Metrical Scansion of Galician Poetry: First Results. To appear in *Proceedings of PROPOR - 17th International Conference on Computational Processing of Portuguese*

## Introduction

The system is in `src`. An example client that runs both preprocessing and scansion on a text is at `src/run_clients.sh`.

From `src`, `run_prepro.py` runs preprocessing and `run_scan_eval.py` runs scansion. The  `-h` option shows available options. The instructions to reproduce results below also show examples how to use the tool.

We share the paper's evaluation data ([test set](./src/scansion/eval/data/README.md)), annotation [criteria](./src/scansion/eval/data/annotation-criteria.md), and the procedure to reproduce results.

Note: This repository reproduces the initial submission. Some improvements done before the camera-ready are not here yet. 

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

## To reproduce the paper

### Preprocessing

To reproduce preprocessing results, go to the `src` directory and run the following:

```bash
python run_prepro.py "../texts/gl_poems_test_010.txt" --preprocess --normalize --stress_possessives --disambiguate_stress --destress --run_id 104 --run_comment "reproduce lexical normalization"
```

That will output the results in `texts/out_104/`. The output file should reproduce `texts/out_103/gl_poems_test_010_pp_out_norm_spa_103.txt`

### Preprocessing evaluation

To reproduce preprocessing evaluation:

Go to the `src/preprocessing/eval` directory and run the evaluation with the command below, on the file just created by preprocessing. The reference data are at the path specified in the command:

```bash
python eval_prepro.py --hypothesis "../../../texts/out_104/gl_poems_test_010_pp_out_norm_spa_104.txt" --reference "../../../texts/out_103/gl_poems_test_010_pp_out_norm_spa_103_corrected_to_compute_wer.txt"
```

### Scansion results and evaluation

To reproduce **scansion results (Table 1)**, on the test set:

**(1): Original Spanish configuration**

```bash
python run_scan_eval.py "../texts/gl_poems_test_010.txt" "scansion/eval/data/gl_scansion_gold_test_010.tsv" 200 --use_jumper_es --skip_cleanup --metadata_path "scansion/eval/data/gl_scansion_gold_test_md_010.xlsx" --metadata_start 0 --run_comment "Repro config (1)"
```

This will output the scores to `out/scansion_gl_cumu_acc.tsv`, which reproduce those in the paper. The scansion output will be at `out/scansion_gl_eval_200.tsv`.

**(2): + Galician lexical resources**

```bash
python run_scan_eval.py "../texts/gl_poems_test_010.txt" "scansion/eval/data/gl_scansion_gold_test_010.tsv" 201 --skip_cleanup --metadata_path "scansion/eval/data/gl_scansion_gold_test_md_010.xlsx" --metadata_start 0 --run_comment "Repro scansion config (2)"
```

This will output the scores to `../out/scansion_gl_cumu_acc.tsv`, which reproduce those in the paper. The scansion output will be at `../out/scansion_gl_eval_201.tsv`.


**(3): + Galician lexical resources + Preprocessing (Best results)**

For this, we use the preprocessed text as input:

```bash
python run_scan_eval.py "../texts/out_103/gl_poems_test_010_pp_out_norm_spa_103.txt" "scansion/eval/data/gl_scansion_gold_test_010.tsv" 202 --metadata_path "scansion/eval/data/gl_scansion_gold_test_md_010.xlsx" --metadata_start 0 --run_comment "Repro scansion config (3)"
```

This will output the scores to `out/scansion_gl_cumu_acc.tsv`, which reproduce those in the paper. The scansion output will be at `out/scansion_gl_eval_202.tsv`.

### Detailed results per metrical difficulty type

To reproduce **Table 2 with detailed results per metrical difficulty type**, run the following command from `src`:

```bash
python -m scansion.eval.eval_line_types --gold "scansion/eval/data/gl_scansion_gold_test_md_010.xlsx" --predicted "../out/scansion_gl_eval_202.tsv" --testset_start_index 0 --result_format 'gumper' --log "../logs/log_met_details.txt" --run_id 202 --batch_comment "repro detailed eval 202" --model "Gumper" --eval_suffix ""
```

That will write the summary of results for the `test` part of Table 2 to `logs/log_met_details.txt`, based on the evaluation at `out/scansion_gl_eval_202.annot.tsv`.

### Per-meter results

These are in **Table 4**. They can be reproduced by running the notebook at `src/scansion/ana/per-meter-results.ipynb`, which uses the detailed evaluation above.
