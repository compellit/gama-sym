"""Metrical analysis evaluation"""

import argparse
from collections import defaultdict, deque
from pathlib import Path
import json
import regex as re

import pandas as pd

from scripts.create_ft_format_lex2met import format_valenca
import utils as ut


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
    pred_stress = [i+1 for i, s in enumerate(pred.split(" / ")) if "*" in s]
    gold_stress = [i+1 for i, s in enumerate(gold.split(" / ")) if "*" in s]
    return pred_stress == gold_stress


def has_syllable_segmentation_match_ignoring_stress(gold: str, pred: str) -> bool:
    """Check if the syllable segmentation in the predicted and gold strings match, ignoring stress marks."""
    pred_sylls = [re.sub(r"[*#]", "", s).strip() for s in pred.split(" / ")]
    gold_sylls = [re.sub(r"[*#]", "", s).strip() for s in gold.split(" / ")]
    return pred_sylls == gold_sylls


def last_stressed_position_match(gold: str, pred: str) -> bool:
    """Check if the last stressed syllable positions in the predicted and gold strings match."""
    pred_stress = [i+1 for i, s in enumerate(pred.split(" / ")) if "*" in s]
    gold_stress = [i+1 for i, s in enumerate(gold.split(" / ")) if "*" in s]
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
    pred_stress = [i+1 for i, s in enumerate(pred_sylls) if "*" in s]
    gold_stress = [i+1 for i, s in enumerate(gold_sylls) if "*" in s]
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
    #breakpoint()
    if not "*" in mets:
        raise ValueError("Line must have at least one stress")
    #if not "#" in mets:
    #    print(f"Final stress for line {mets} not marked")
    met_sylls = mets.split(" / ")
    # we use 1-indexing to talk about syllable positions as in a stress pattern
    last_stressed_derived = [i+1 for i, s in enumerate(met_sylls) if "*" in s][-1]
    if not "#" in mets:
        # assume last with asterisk is the last stressed
        last_stressed_marked = last_stressed_derived
    else:
        # 1-indexed
        last_stressed_marked = [i + 1 for i, s in enumerate(met_sylls) if "#" in s][-1]
    if last_stressed_derived != last_stressed_marked:
        last_stressed_derived = last_stressed_marked if last_stressed_marked > last_stressed_derived else last_stressed_derived
        print(f"Last stress mark mismatch for line {mets}")
    #nbr_after_last_stressed = len(met_sylls) - last_stressed
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


def extract_results(result_fn: Path|str, orig_data_df: pd.DataFrame, index_list: list[int]|None=None) -> pd.DataFrame:
    """
    Extract results from evaluation JSONL file and compare with original data, printing
    accuracy scores for different groups of lines (e.g. those with different types of metrical licenses or phonological characteristics)
    
    Args:
        result_fn: path to the JSONL file with evaluation results (fields are similar to the OpenAI eval format)
        orig_data_df: dataframe from the original TSV file with the data used for training and evaluation (that the JSONL training data are populated from)
        index_list: optional list of indices to select a subset of rows from orig_data
    Returns:
        DataFrame with line metadata columns and evaluation    
    """
    # prepare output containers
    global out_md # global cos want to iterate over its keys outside the function
    source_idx = [] # index in the testset
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
    with open(result_fn, "r", encoding="utf-8") as f:
        test_objs= [json.loads(line) for line in f.readlines()]
    # extract part of original data corresponding to the test items
    orig_data_test = orig_data_df.iloc[index_list] if index_list is not None else orig_data_df
    # populate output dataframe
    valenca_args = {'remove_punct': args.remove_punct, 'task': 'lex'}
    orig_data_test['valenca'] = orig_data_test['lexSylls'].apply(format_valenca, **valenca_args)
    # Not sure why I asked to replace '#' is asked, cos '#' should never be in in lexSylls,
    # maybe it is precisely in case some erroneous data have it
    orig_data_test['valenca'] = orig_data_test['valenca'].apply(lambda x: x.replace("#", ""))
    # Figure out order of test objects based on their occurrence in orig_data_test
    # (i.e. dataframe with test-set).
    # Needed because in some cases output order may not match input order (seen with OpenAI eval outputs, or perhaps when batching with different input lengths)
        # Approach: for each key (line_text), collect all positions in orig_data_test,
        # then assign each test object occurrence the next available position,
        # then sort test objects by assigned position
    # 1) Collect all positions for each key in orig_data_test
    positions = defaultdict(deque)
    # This preserves the DataFrame index values as "positions"
    for key, idx in zip(orig_data_test["valenca"].astype(str).str.strip(), orig_data_test.index):
        positions[key].append(idx)
    # (Optional) ensure sorted positions per key
    for k in positions:
        positions[k] = deque(sorted(positions[k]))
    # 2) Assign an index to EACH test object occurrence (consume from the left)
    for to in test_objs:
        key = to["line_text"].strip()
        if positions[key]:
            to["_sort_idx"] = positions[key].popleft()
        else:
            # key not found enough times in orig_data_test (or not found at all)
            #to["_sort_idx"] = float("inf")
            raise ValueError(f"No remaining positions for key={key!r}")
    # 3) Sort using the per-occurrence assigned index
    stos = sorted(test_objs, key=lambda x: x["_sort_idx"])
    # stos = sorted(test_objs, key=lambda x: to2idx[x["line_text"].strip()])
    for idx, to in enumerate(stos):
        #breakpoint()
        source_idx.append(idx)
        orig_infos = orig_data_test.iloc[idx]
        text_col = 'text' if 'text' in orig_data_test.columns else 'origText'
        orig_texts.append(orig_infos[text_col])
        #if 'eem' in orig_infos[text_col]:
        #    breakpoint()
        gold_nbr_met_sylls.append(orig_infos['nbrMetSyll'])
        if pd.isna(orig_infos['equivFinales']):
            breakpoint()
        equiv_finales.append(orig_infos['equivFinales'])
        mets = orig_infos['metSylls']
        out_md["has_synalepha"].append(int(bool("_" in mets)))
        out_md["has_dialepha"].append(int(bool("÷" in mets)))
        out_md["has_syneresis"].append(int(bool("^" in mets)))
        out_md["has_dieresis"].append(int(bool("#" in mets)))      
        out_md["has_complex_slph"].append(int(bool(re.search(COMPLEX_SYNALEPHA_RE, mets))))
        out_md["has_no_diphth_across_word_b"].append(int(bool(re.search(NO_DIPHTHONG_ACROSS_WORD_B_RE, mets))))
        out_md["has_slph_across_punctuation"].append(int(bool(re.search(SYNALEPHA_ACROSS_PUNCT_RE, mets))))
        out_predictions.append(to['prediction'].strip())
        out_correct.append(to['gold'].strip())
        # evals
        # exact match
        gold_part = to['gold'].strip()
        pred_part = to['prediction'].strip()
        if args.ignore_last_stress_mark:
            gold_part = gold_part.replace("#", "")
            pred_part = pred_part.strip().replace("#", "")
        if args.ignore_case:
            gold_part = gold_part.lower()
            pred_part = pred_part.lower()
        exact_match_test = gold_part == pred_part
        if exact_match_test:
            out_evals["exact_match"].append(1)
        else:
            out_evals["exact_match"].append(0)
        # segmentation match
        out_evals["segmentation_match"].append(int(has_syllable_segmentation_match_ignoring_stress(to['gold'].strip(), to['prediction'].strip())))
        # meter match
        try:
            gold_meter, gold_equiv_finales = compute_meter(to['gold'].strip())
            # this should never occur unless manual annotation error in gold,
            # left it here for symmetry 
        except ValueError as ve:
            print(f"Skipping meter match for line {idx + 1} [{to['gold'].strip()}] due to GOLD error: {ve}")
            gold_meter = gold_equiv_finales = 0
        #   compute_meter raises ValueError under some conditions, handle it here
        try:
            pred_meter, pred_equiv_finales = compute_meter(to['prediction'].strip())
        except ValueError as ve:
            print(f"{'~'*20} Skipping meter match for line {idx + 1} [{to['prediction'].strip()}] due to PRED error: {ve}")
            pred_meter = pred_equiv_finales = 0
        #   evaluate match
        if gold_meter == pred_meter and gold_equiv_finales == pred_equiv_finales:
            out_evals["meter_match"].append(1)
        else:
            out_evals["meter_match"].append(0)
        #   populate predicted meter list used in output dataframe
        #   note: populate equiv_finales is not populated here but from test annots, above 
        pred_nbr_met_sylls.append(pred_meter)

        # call these with gold first
        out_evals["vowel_match"].append(int(has_vowel_match(to['gold'].strip(), to['prediction'].strip())))
        out_evals["stress_pattern_match"].append(int(has_stress_pattern_match(to['gold'].strip(), to['prediction'].strip())))
    
    wdiffs = [ut.word_diff(g, p) if g.strip() != p.strip() else "" for g, p in zip(out_correct, out_predictions)]
        
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


def process_md_column(col_name: str, outf=None):
    """Process a column to compute and print accuracy for items where the column is true."""
    items_with_feature = res_df[res_df[col_name] == 1]
    correct_with_feature = items_with_feature['exact_match'].sum()
    total_with_feature = len(items_with_feature)
    acc_with_feature = correct_with_feature / total_with_feature if total_with_feature > 0 else "no rows for the feature"
    print(f"  - {col_name:<30}\t{correct_with_feature}/{total_with_feature:}\t({acc_with_feature:.2%} of {total_with_feature/len(res_df):.2%})")
    with open(outf, "a", encoding="utf-8") as f:
        f.write(f"{col_name+':':<30}\t{correct_with_feature:>3}/{total_with_feature:>3}\t({acc_with_feature:.2%} of {total_with_feature/len(res_df):.2%})\n")


def parse_args():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(description="Evaluate scansion results.")
    parser.add_argument("--gold", "-g", type=str, required=True, help="Gold annotations in TSV formats (that the JSON field for training is populated from).")
    parser.add_argument("--predicted", "-p", type=str, required=True, help="System predictions.")
    parser.add_argument("--testset_start_index", "-t", type=int, required=True, help="Index at which the testset starts in the gold data. Assumes test items are contiguous and at the end of the gold data.")
    parser.add_argument("--log", "-l", type=str, required=True, help="Log with result summary.")
    parser.add_argument("--run_id", "-r", type=str, required=True, help="Batch ID for the output files")
    parser.add_argument("--eval_suffix", "-v", type=str, required=False, default="", help="If you run eval with same input but different settings, you can set this suffix so that the latter output does not overwrite previous one.")
    parser.add_argument("--batch_comment", "-c", type=str, required=True, help="Comment about batch.")
    parser.add_argument("--model", "-m", type=str, required=False, help="Model name (for logging only).")
    parser.add_argument("--ignore_last_stress_mark",
                        action="store_true", required=False, help="Ignore or consider whether the '#' mark was added to the final stress")
    parser.add_argument("--ignore_case", action="store_true", required=False, help="Ignore case for exact match.")
    parser.add_argument("--remove_punct", action="store_true", required=False, help="Remove punctuation marks when formatting scansion .")
    return parser.parse_args()


if __name__ == "__main__":
    # will always run from project root
    # CLI args
    args = parse_args()
    orig_df = pd.read_csv(args.gold, header=0, sep="\t", keep_default_na=False)
    eval_file = args.predicted
    eval_out_for_annot = eval_file + f"_{args.eval_suffix}" if args.eval_suffix else eval_file
    eval_file_annot = Path(eval_out_for_annot).with_suffix(".tsv")
    batch_id = args.run_id
    index_list = list(range(args.testset_start_index, len(orig_df)))

    # run eval
    res_df = extract_results(eval_file, orig_df, index_list=index_list)
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
        process_md_column(colname, outf=out_log)

    with open(out_log, "a", encoding="utf-8") as f:
        f.write("\n\n")

    ut.rename_results_df_column(res_df)
    res_df.to_csv(eval_file_annot, sep="\t", header=True, index=False, encoding="utf-8")
