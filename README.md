# Code and data for our paper Automatic Metrical Scansion of Galician Poetry: First Results

The system is in `src`. From there `run_prepro.py` runs preprocessing and `run_scan_eval.py` runs scansion.

For peer review, we share the procedure and data to reproduce results on the paper's evaluation data (test set). This is for peer review only, not for redistribution. We will publicly distribute both test data and the larger development data upon publication.

To reproduce, large files that don't fit anonymous.4open.science would need to be downloaded. The following command downloads them to the required directory:

```bash
./download_large_files.sh
```

Then the system can be run and reproduces the paper. 


## Preprocessing

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

## Scansion results and evaluation

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

This will output the scores to `out/scansion_gl_cumu_acc.tsv`, which reproduce those in the paper. The scansion output will be at `out/scansion_gl_eval_201.tsv`.


**(3): + Galician lexical resources + Preprocessing**

For this, we use the preprocessed text as input:

```bash
python run_scan_eval.py "../texts/out_103/gl_poems_test_010_pp_out_norm_spa_103.txt" "scansion/eval/data/gl_scansion_gold_test_010.tsv" 202 --metadata_path "scansion/eval/data/gl_scansion_gold_test_md_010.xlsx" --metadata_start 0 --run_comment "Repro scansion config (3)"
```

This will output the scores to `out/scansion_gl_cumu_acc.tsv`, which reproduce those in the paper. The scansion output will be at `out/scansion_gl_eval_202.tsv`.

### Detailed results per metrical difficulty type

To reproduce **Table 2 with detailed results per metrical difficulty type**, run the following command from `src`:

```bash
%run scansion/eval/eval_line_types.py --gold "scansion/eval/data/gl_scansion_gold_test_md_010.xlsx" --predicted "../out/scansion_gl_eval_202.tsv" --testset_start_index 0 --result_format 'gumper' --log "../logs/log_met_details.txt" --run_id 202 --batch_comment "repro detailed eval 202" --model "Gumper" --eval_suffix ""
```

That will write the summary of results for the `test` part of Table 2 to `logs/log_met_details.txt`, based on the evaluation at `out/scansion_gl_eval_202.annot.tsv`.

### Per-meter results

These are in **Appendix F, table 7**. They can be reproduced by running the notebook at `src/scansion/ana/per-meter-results.ipynb`, which uses the detailed evaluation above.
