"""Metrical analysis evaluation based on difficulty features of the lines"""

import argparse
from pathlib import Path
import json
import regex as re
from typing import Literal

import pandas as pd

from .. import utils as ut

# regex patterns for metadata extraction
COMPLEX_SYNALEPHA_RE = re.compile(r"(?:_[\p{L}+]_)+")
NO_DIPHTHONG_ACROSS_WORD_B_RE = re.compile(r"[aeiouáéíóúâêîôûàèìòùëïy][,;:.!?¿¡ ]* '?[aeiouáéíóúâêîôûàèìòùëïy]")
SYNALEPHA_ACROSS_PUNCT_RE = re.compile(r"_[,;:.!?¿¡]+_")


def extract_vowels(s):
    """
    Extract vowels from each syllable in a metrical syllables string, ignoring case.

    Args:
        s (str): Metrical syllables string (with stress marks)
    Returns:
        list: List of vowels in each syllable, in order
    """
    syll_list = s.split(" / ")
    syll_vwl_list = [re.search(r"[aeiouáéíóúâêîôûàèìòùëïy]", syll, flags=re.IGNORECASE) for syll in syll_list]
    vowels = [m.group(0).lower() if m else "" for m in syll_vwl_list]
    return vowels


def has_vowel_match(gold: str, pred: str) -> bool:
    """Check if the vowels in the predicted and gold strings match, ignoring case."""
    pred_vowels = extract_vowels(pred)
    gold_vowels = extract_vowels(gold)
    return pred_vowels == gold_vowels


def has_stress_pattern_match(gold: str, pred: str) -> bool:
    """Check if the stress patterns (stressed syllable positions) in the predicted and gold strings match."""
    pred_stress = [i + 1 for i, s in enumerate(pred.split(" / ")) if "*" in s]
    gold_stress = [i + 1 for i, s in enumerate(gold.split(" / ")) if "*" in s]
    return pred_stress == gold_stress


def has_syllable_segmentation_match_ignoring_stress(gold: str, pred: str) -> bool:
    """Check if the syllable segmentation in the predicted and gold strings match, ignoring stress marks."""
    pred_sylls = [re.sub(r"[*#]", "", s).strip() for s in pred.split(" / ")]
    gold_sylls = [re.sub(r"[*#]", "", s).strip() for s in gold.split(" / ")]
    return pred_sylls == gold_sylls


def last_stressed_position_match(gold: str, pred: str) -> bool:
    """Check if the last stressed syllable positions in the predicted and gold strings match."""
    pred_stress = [i + 1 for i, s in enumerate(pred.split(" / ")) if "*" in s]
    gold_stress = [i + 1 for i, s in enumerate(gold.split(" / ")) if "*" in s]
    if not pred_stress or not gold_stress:
        return False
    return pred_stress[-1] == gold_stress[-1]


def number_of_syllables_after_last_stress_match(gold: str, pred: str) -> tuple[bool, int]:
    """
    Check if the number of syllables after the last stressed syllable in the predicted and gold strings match.

    Args:
        gold (str): Gold standard syllabification with stress marks.
        pred (str): Predicted syllabification with stress marks.
    Returns:
        tuple[bool, int]: Whether the number matches across gold and predicted, number of sylables predicted after last stress

    """
    pred_sylls = pred.split(" / ")
    gold_sylls = gold.split(" / ")
    pred_stress = [i + 1 for i, s in enumerate(pred_sylls) if "*" in s]
    gold_stress = [i + 1 for i, s in enumerate(gold_sylls) if "*" in s]
    if not pred_stress or not gold_stress:
        return False, -1
    pred_nbr_after_last_stress = len(pred_sylls) - pred_stress[-1]
    gold_nbr_after_last_stress = len(gold_sylls) - gold_stress[-1]
    return (pred_nbr_after_last_stress == gold_nbr_after_last_stress, pred_nbr_after_last_stress)


def compute_meter(mets: str):
    """
    Compute the metrical syllable count from a metrical syllabification string,
    applying versification rules regarding line-final stress.

    Note that positions are 1-indexed in this function (to match the way we
    talk about stress patterns).

    Args:
        mets: Metrical syllabification string (with stress marks)

    Returns:
        tuple(int, str): The meter (number of metrical syllables) and the ending type
            (final stress, antepenult stress or penult)

    Raises:
        ValueError: If the metrical string has no stress marks or if the last stress
            is before preantepenult position.
    """
    # breakpoint()
    if not "*" in mets:
        raise ValueError("Line must have at least one stress")
    if not "#" in mets:
        print(f"Final stress for line {mets} not marked")
    met_sylls = mets.split(" / ")
    # we use 1-indexing to talk about syllable positions as in a stress pattern
    last_stressed_derived = [i + 1 for i, s in enumerate(met_sylls) if "*" in s][-1]
    if not "#" in mets:
        # assume last with asterisk is the last stressed
        last_stressed_marked = last_stressed_derived
    else:
        # 1-indexed
        last_stressed_marked = [i + 1 for i, s in enumerate(met_sylls) if "#" in s][-1]
    if last_stressed_derived != last_stressed_marked:
        last_stressed_derived = last_stressed_marked if last_stressed_marked > last_stressed_derived else last_stressed_derived
        print(f"Last stress mark mismatch for line {mets}")
    # nbr_after_last_stressed = len(met_sylls) - last_stressed
    if "*" in met_sylls[-1] and last_stressed_derived == len(met_sylls):
        final_meter = len(met_sylls) + 1
        equiv_finales = "final"
    elif len(met_sylls) - last_stressed_derived >= 2:
        if len(met_sylls) - last_stressed_derived > 3:
            # This is ValueError in the sense that the metrical string has a weird / impossible
            # last stress position
            raise ValueError("Last stress beyond sobreesdrújula position")
        final_meter = len(met_sylls) - 1
        equiv_finales = "antepenult"
    else:
        final_meter = len(met_sylls)
        equiv_finales = "penult"
    return final_meter, equiv_finales


def extract_results(result_fn: Path | str, orig_data_df: pd.DataFrame,
                    index_list: list[int] | None = None,
                    result_format: Literal['json', 'gumper'] = 'json') -> pd.DataFrame:
    """
    Extract results from evaluation JSONL file and compare with original data, printing
    accuracy scores for different groups of lines (e.g. those with different types of metrical licenses or phonological characteristics)

    Args:
        result_fn: path to the JSONL file with evaluation results (fields similar to LLM eval format)
        orig_data_df: dataframe from the original TSV file with the data used for training and evaluation (that the JSONL training data are populated from)
        index_list: optional list of indices to select a subset of rows from orig_data
    Returns:
        DataFrame with line metadata columns and evaluation    
    """
    # prepare output containers
    global out_md  # global cos want to iterate over its keys outside the function
    source_idx = []  # index in the testset
    orig_texts = []
    gold_nbr_met_sylls = []
    pred_nbr_met_sylls = []
    equiv_finales = []
    out_predictions = []
    out_correct = []
    out_evals = {"exact_match": [], "vowel_match": [], "stress_pattern_match": [],
                 "segmentation_match": [], "meter_match": []}
    out_md = {"has_synalepha": [], "has_dialepha": [], "has_syneresis": [], "has_dieresis": [],
              "has_slph_across_punctuation": [], "has_complex_slph": [],
              "has_no_diphth_across_word_b": []}
    # read results and complete dataset (train/test). The original data are used to get/compute metadata about the lines
    if result_format == 'json':
        with open(result_fn, "r", encoding="utf-8") as f:
            test_objs = [json.loads(line) for line in f.readlines()]
    else:
        # Gumper output format
        test_objs = pd.read_csv(result_fn, sep="\t", header=0, keep_default_na=False)
        test_objs.rename(columns={"orig": "line_text"}, inplace=True)
        test_objs = test_objs.to_dict(orient="records")

    # extract part of original data corresponding to the test items
    orig_data_test = orig_data_df.iloc[index_list] if index_list is not None else orig_data_df
    # populate output dataframe
    text_col = 'text' if 'text' in orig_data_test.columns else 'origText'
    to2idx = {}
    for idx, to in enumerate(test_objs):
        try:
            to_idx = orig_data_test.loc[orig_data_test[text_col] == to["line_text"].strip()].index[0]
        except IndexError:
            if result_format == 'gumper':
                print(
                    f"Assigning Gumper line [{idx}] {to['line_text'].strip()} to {orig_data_test.iloc[idx][text_col]}.")
                to_idx = orig_data_test.index[idx]
        to2idx[to["line_text"].strip()] = to_idx
    stos = sorted(test_objs, key=lambda x: to2idx[x["line_text"].strip()])

    for idx, to in enumerate(stos):
        # breakpoint()
        # metadata / line complexity features based on golden annots ----------
        source_idx.append(idx)
        orig_infos = orig_data_test.iloc[idx]
        text_col = 'text' if 'text' in orig_data_test.columns else 'origText'
        orig_texts.append(orig_infos[text_col])
        gold_nbr_met_sylls.append(orig_infos['nbrMetSyll'])
        # if pd.isna(orig_infos['equivFinales']):
        #     breakpoint()
        equiv_finales.append(orig_infos['equivFinales'])
        mets = orig_infos['metSylls']
        out_md["has_synalepha"].append(int(bool("_" in mets)))
        out_md["has_dialepha"].append(int(bool("÷" in mets)))
        out_md["has_syneresis"].append(int(bool("^" in mets)))
        out_md["has_dieresis"].append(int(bool("#" in mets)))
        out_md["has_complex_slph"].append(int(bool(re.search(COMPLEX_SYNALEPHA_RE, mets))))
        out_md["has_no_diphth_across_word_b"].append(int(bool(re.search(NO_DIPHTHONG_ACROSS_WORD_B_RE, mets))))
        out_md["has_slph_across_punctuation"].append(int(bool(re.search(SYNALEPHA_ACROSS_PUNCT_RE, mets))))
        #   add this for the general case (JSONL output)
        if result_format != 'gumper':
            out_predictions.append(to['prediction'].strip())
            out_correct.append(to['gold'].strip())
        else:
            out_predictions.append(pd.NA)
            out_correct.append(pd.NA)

        # evals ---------------------------------------------------------------

        #  gumper format, only measures are meter match and stress pattern match
        #     because it does not perform syllabification, only stress assignment directly
        if result_format == 'gumper':
            out_evals["stress_pattern_match"].append(to['evalMet'])
            out_evals["meter_match"].append(to['evalSyl'])
            pred_nbr_met_sylls.append(to['sylA'])
            wdiffs = equiv_finales = out_predictions = [pd.NA] * len(test_objs)  # to have same array length
            for gumkey in ["exact_match", "segmentation_match", "vowel_match"]:
                out_evals[gumkey].append(pd.NA)

        #  general case, with syllabification in output and in JSONL
        else:
            # exact match ---------------------------------
            if to['gold'].strip() == to['prediction'].strip():
                out_evals["exact_match"].append(1)
            else:
                out_evals["exact_match"].append(0)
            # segmentation match --------------------------
            out_evals["segmentation_match"].append(
                int(has_syllable_segmentation_match_ignoring_stress(to['gold'].strip(), to['prediction'].strip())))
            # meter match ----------------------------------
            try:
                gold_meter, gold_equiv_finales = compute_meter(to['gold'].strip())
                # this should never occur unless manual annotation error in gold,
                # left it here for symmetry with the pred part
            except ValueError as ve:
                print(f"Skipping meter match for line {idx + 1} [{to['gold'].strip()}] due to GOLD error: {ve}")
                gold_meter = gold_equiv_finales = 0
            #   compute_meter raises ValueError under some conditions, handle it here
            try:
                pred_meter, pred_equiv_finales = compute_meter(to['prediction'].strip())
            except ValueError as ve:
                print(
                    f"{'~' * 20} Skipping meter match for line {idx + 1} [{to['prediction'].strip()}] due to PRED error: {ve}")
                pred_meter = pred_equiv_finales = 0
            #   evaluate match ----------------------------
            if gold_meter == pred_meter and gold_equiv_finales == pred_equiv_finales:
                out_evals["meter_match"].append(1)
            else:
                out_evals["meter_match"].append(0)
            #   populate predicted meter list used in output dataframe
            #   note: populate equiv_finales is not populated here but from test annots, above 
            pred_nbr_met_sylls.append(pred_meter)

            # call these with gold first
            out_evals["vowel_match"].append(int(has_vowel_match(to['gold'].strip(), to['prediction'].strip())))
            out_evals["stress_pattern_match"].append(
                int(has_stress_pattern_match(to['gold'].strip(), to['prediction'].strip())))

            wdiffs = [ut.word_diff(g, p) if g.strip() != p.strip() else "" for g, p in
                      zip(out_correct, out_predictions)]

    # create output dataframe
    out_df = pd.DataFrame({
        "sIdx": source_idx,
        "orig_text": orig_texts,
        "correct": out_correct,
        "predicted": out_predictions,
        "wdiffs": wdiffs,
        **out_evals,
        **out_md,
        "gold_nbr_met_sylls": gold_nbr_met_sylls,
        "pred_nbr_met_sylls": pred_nbr_met_sylls,
        "equiv_finales": equiv_finales
    })
    return out_df


def write_match_stats(res_df, col_name, outf=None, label=None):
    matches = res_df[col_name].sum()
    total = len(res_df)
    out_label = label if label is not None else col_name
    acc = matches / total if total > 0 else 0.0
    print(f"{out_label + ':':<30} {matches}/{total} ({acc:.2%})")
    with open(outf, "a", encoding="utf-8") as f:
        f.write(f"{out_label + ':':<30}\t{matches}/{total} ({acc:.2%})\n")


def process_md_column(col_name: str, totals_col='exact_match', outf=None):
    """
    Process a column to compute and print accuracy for items where the column is true.

    Args:
        col_name (str): Name of the metadata column to process.
        totals_col (str): The scores will be calculated as a proportion of this column.
        outf (Path | str): Output file path to append results to.
    """
    items_with_feature = res_df[res_df[col_name] == 1]
    correct_with_feature = items_with_feature[totals_col].sum()
    total_with_feature = len(items_with_feature)
    acc_with_feature = correct_with_feature / total_with_feature if total_with_feature > 0 else "no rows for the feature"
    print(
        f"  - {col_name:<30}\t{correct_with_feature}/{total_with_feature:}\t({acc_with_feature:.2%} of {total_with_feature / len(res_df):.2%})")
    with open(outf, "a", encoding="utf-8") as f:
        f.write(
            f"{col_name + ':':<30}\t{correct_with_feature:>3}/{total_with_feature:>3}\t({acc_with_feature:.2%} of {total_with_feature / len(res_df):.2%})\n")


def parse_args():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(description="Evaluate scansion results.")
    parser.add_argument("--gold", "-g", type=str, required=True,
                        help="Gold annotations in TSV format (the JSONL are created from this).")
    parser.add_argument("--predicted", "-p", type=str, required=True, help="System predictions.")
    parser.add_argument("--testset_start_index", "-t", type=int, required=True,
                        help="Index at which the testset starts in the gold data. Assumes test items at the end of the file (i.e. if the complete file is the test corpus, index is 0.")
    parser.add_argument("--result_format", "-f", type=str, required=False, default='json',
                        choices=['json', 'gumper'],
                        help="'json' is JSONL,  'gumper' is Gumper-style output.")
    parser.add_argument("--log", "-l", type=str, required=True, help="Log with result summary.")
    parser.add_argument("--run_id", "-r", type=str, required=True, help="Run ID for the output files")
    parser.add_argument("--eval_suffix", "-v", type=str, required=True,
                        help="If you run eval with same input but different settings, you can set this suffix so that the latter output does not overwrite previous one.")
    parser.add_argument("--batch_comment", "-c", type=str, required=True, help="Comment about run.")
    parser.add_argument("--model", "-m", type=str, required=False, help="Model/configuration name (for logging only).")
    return parser.parse_args()


if __name__ == "__main__":
    # will always run from project root
    # CLI args
    args = parse_args()
    orig_df = pd.read_excel(args.gold, sheet_name="dataAll", header=0, keep_default_na=False)
    eval_file = args.predicted
    # eval output with a table for each difficulty feature (synalepha, dieresis, etc)
    out_eval_start = Path(eval_file)
    suffix = args.eval_suffix or ""
    if args.result_format == "json":
        eval_file_annot = out_eval_start.with_name(f"{out_eval_start.stem}{suffix}.tsv")
    else:
        # in gumper format original extension is .tsv, so use a different suffix for annotated output
        eval_file_annot = out_eval_start.with_name(f"{out_eval_start.stem}{suffix}.annot.tsv")
    batch_id = args.run_id
    index_list = list(range(args.testset_start_index, len(orig_df)))

    # run eval
    res_df = extract_results(eval_file, orig_df, index_list=index_list, result_format=args.result_format)
    out_log = Path(args.log)

    # write out
    with open(out_log, "a", encoding="utf-8") as f:
        batch_id_str = f"# Batch ID: {batch_id} [{args.model}]\n\n" if args.model is not None else f"# Batch ID: {batch_id}\n\n"
        f.write(batch_id_str)
        f.write(f"Comment: {args.batch_comment}\n\n")
        f.write(f"Eval items: {eval_file}\n")
        f.write(f"Original data file: {args.gold}\n")
        f.write(f"Eval items analyzed: {eval_file_annot}\n")
        f.write(f"Number of items evaluated: {len(res_df)}\n\n")

    evals_to_print = {
        "exact_match": "Exact matches",
        "vowel_match": "Vowel matches",
        "stress_pattern_match": "Stress pattern matches",
        "segmentation_match": "Syllable segmentation matches",
        "meter_match": "Meter matches"
    }
    for k, v in evals_to_print.items():
        write_match_stats(res_df, k, label=v, outf=out_log)

    print("\nExact match stats per line type:")
    with open(out_log, "a", encoding="utf-8") as f:
        f.write("\nExact match stats per line type:\n")

    for colname in out_md.keys():
        if args.result_format == "gumper":
            process_md_column(colname, totals_col="stress_pattern_match", outf=out_log)
        else:
            process_md_column(colname, totals_col="exact_match", outf=out_log)

    with open(out_log, "a", encoding="utf-8") as f:
        f.write("\n\n")

    ut.rename_results_df_column(res_df)
    res_df.to_csv(eval_file_annot, sep="\t", header=True, index=False, encoding="utf-8")