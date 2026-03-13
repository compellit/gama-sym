"""Utilities for scansion"""

from collections import OrderedDict
import difflib
from pathlib import Path
import re
from typing import Literal

from scansion import config as cf


def cleanup_text(text, replacements=None):
    """
    Cleans up the text by removing unwanted characters and formatting
    and applying some replacements for single words and expresions.
    """
    if replacements is not None:
        for key, value in replacements.items():
            text = re.sub(key, value, text)
    text = text.replace("'", "")
    text = text.replace("’", "")
    text = text.replace("‘", "")
    text = text.strip()
    return text


def load_w_replacements(config) -> OrderedDict:
    """
    Loads replacements for a file, they affect a single word.
    """
    replacements = OrderedDict()
    with open(config.word_bound_replacements, "r", encoding="utf-8") as f:
        for line in f:
            if line.startswith("#"):
                continue
            key, value = line.strip().split("\t")
            replacements[re.compile(fr"\b{key}\b", re.I)] = value
    return replacements


def load_t_replacements(config):
    """
    Loads the replacements from a file. The replacements may affect multiple words.
    """
    replacements = OrderedDict()
    with open(config.text_level_replacements, "r", encoding="utf-8") as f:
        for line in f:
            if line.startswith("#"):
                continue
            key, value = line.strip().split("\t")
            replacements[re.compile(fr"{key}", re.I)] = value
    return replacements


def write_output_file(poem_lines, outinfo, poem_id):
    """
    Writes the output to a file.
    """
    # outinfo is Jumper output format (list of lists)
    out_lines = []
    for outer_idx, info_list in enumerate(outinfo):
        for idx, info in enumerate(info_list):
            postpro_text = info[1]
            keeps = [poem_lines[outer_idx][idx], postpro_text,  # orig lines + my own postpro
                     info[2],                                   # nbSyll, met, met no antirhythmic
                     " ".join([str(x) for x in info[3]]),
                     " ".join([str(x) for x in info[4]]),
                     f"{100*info[-1]:.2f}",                     # match ratio with pattern
                     info[-2]]                                  # meter name
            out_lines.append(keeps)
    ouname = cf.oufi.stem + f"_{str.zfill(poem_id, 3)}" + cf.oufi.suffix
    with open(cf.oufi.with_name(ouname), "w", encoding="utf-8") as oufh:
        for line in out_lines:
            oufh.write("\t".join([str(x) for x in line]) + "\n")


def write_output_file_generic(poem_lines, outinfo, infn) -> None:
    """
    Writes the output to a file.
    
    Args:
        poem_lines (list of list of str): List of poems, each poem is a list of its lines.
        outinfo (list of list): Jumper output format (list of lists).
        infn (str): Input filename to derive output filename from.
    Returns:
        None
    """
    # outinfo is Jumper output format (list of lists)
    out_lines = []
    for outer_idx, info_list in enumerate(outinfo):
        for idx, info in enumerate(info_list):
            postpro_text = info[1]
            keeps = [poem_lines[outer_idx][idx], postpro_text,  # orig lines + my own postpro
                     info[2],                                   # nbSyll, met, met no antirhythmic
                     " ".join([str(x) for x in info[3]]),
                     " ".join([str(x) for x in info[4]]),
                     f"{100*info[-1]:.2f}",                     # match ratio with pattern
                     info[-2]]                                  # meter name
            out_lines.append(keeps)
    ouname = cf.oufi.stem + f"_{Path(infn).name}" + cf.oufi.suffix
    with open(cf.oufi.with_name(ouname), "w", encoding="utf-8") as oufh:
        for line in out_lines:
            oufh.write("\t".join([str(x) for x in line]) + "\n")


def read_gold_stress_patterns(gold_location):
    """
    Reads the gold stress patterns from a file.
    """
    gold = []
    with open(gold_location, "r", encoding="utf-8") as f:
        for idx, line in enumerate(f):
            if idx == 0 or line.startswith("#"):
                continue
            orig_text, nb_syll_gold, met_gold = line.strip().split("\t")
            gold.append((orig_text, nb_syll_gold, met_gold))
    return gold


def word_diff(a: str, b: str) -> str:
    """
    Return a git --word-diff style diff between two strings.
    """
    seqm = difflib.SequenceMatcher(None, a, b)
    out = []
    for tag, i1, i2, j1, j2 in seqm.get_opcodes():
        if tag == "equal":
            out.append(a[i1:i2])
        elif tag == "insert":
            out.append("{+" + b[j1:j2] + "+}")
        elif tag == "delete":
            out.append("[-" + a[i1:i2] + "-]")
        elif tag == "replace":
            out.append("[-" + a[i1:i2] + "-]{+" + b[j1:j2] + "+}")
    return "".join(out)


def format_valenca(mana: str, task: Literal['met', 'lex'] = 'met', remove_punct=False, mark_last_stress=False) -> str:
    """
    Format metrical analysis with conventions in Valença & Calegario (2025).

    Args:
        mana (str): Metrical analysis string.
        task (str): Task type, default is 'met'. 'met' takes running text as input,
            'lex' takes lexical syllabification, both output the metrical scansion format.
        remove_punct (bool): Whether to remove punctuation marks. Default is False.
    """
    # detokenize so that punctuation does not interfere with syllable marking
    mana_list = mana.split(" ")
    mana = ut.detokenize(mana_list)
    # remove punctuation marks if caller asks for it
    if remove_punct:
        mana = PUNCT_RE.sub("", mana)
        mana = re.sub(r" {2,}", " ", mana)
        mana = mana.strip()
    # add syllable boundaries across words
    mana = mana.replace(" ", " / ")
    # remove dieresis mark
    mana = mana.replace("#", "")
    # add syllable boundaries within words
    mana = mana.replace("-", "- / ")
    # front stress marks
    mana_list = mana.split(" / ")
    mana_list = ["'" + form.replace("'", "") if "'" in form else form for form in mana_list]
    mana = " / ".join(mana_list)
    # remove synalepha mark
    mana = mana.replace("_", " ")
    # remove the dialepha mark
    mana = mana.replace("÷", "")
    # remove syneresis mark
    mana = mana.replace("^", "")
    mana = mana.replace("'", "*")
    # remove extra spaces
    mana = re.sub(r" {2,}", " ", mana)
    # find last stressed syllable and add the "#" sign after it
    mana_list = mana.split(" / ")
    if mark_last_stress:
        # add stress mark
        last_stressed = [i for i, x in enumerate(mana_list) if "*" in x][-1]
        mana_list[last_stressed] += "#"
    out = " / ".join(mana_list)
    return out


def rename_results_df_column(evdf):
    column_mapping = {
        'orig_text': 'txt',
        'predicted': 'prd',
        'correct': 'gld',
        'exact_match': 'emt',
        'vowel_match': 'vmt',
        'stress_pattern_match': 'smt',
        'segmentation_match': 'gmt',
        'meter_match': 'mmt',
        'has_synalepha': 'slh',
        'has_dialepha': 'dlp',
        'has_syneresis': 'syn',
        'has_dieresis': 'die',
        'has_slph_across_punctuation': 'slp',
        'has_complex_slph': 'slc',
        'has_no_diphth_across_word_b': 'ndb',
        'gold_nbr_met_sylls': 'gsy',
        'pred_nbr_met_sylls': 'psy',
        'equiv_finales': 'eqf'
    }

    evdf.rename(columns={col: column_mapping[col] for col in evdf.columns if col in column_mapping}, inplace=True)
