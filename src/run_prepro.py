"""
Lexical normalization and lexical syllabification for 19th-century Galician text.
"""

import argparse
import copy
from importlib import reload
import logging
from pathlib import Path
import re
import sys
import time

from preprocessing import config as cf
from preprocessing import utils as ut
from preprocessing.norm import lm_manager as lmg
from preprocessing.norm import normalizer
from preprocessing.norm import normconfig as ncf
from preprocessing.data import stress_info as sti
from syllabification import g2s

PUNCT_TO_REMOVE = ".,;?!¿¡:«»()”“„"
PUNCT_TO_SPACE = "—"
PUNCT_RE = re.compile(f"([{PUNCT_TO_REMOVE}]+)", re.UNICODE)
PUNCT_TO_SPACE_RE = re.compile(f"([{PUNCT_TO_SPACE}]+)", re.UNICODE)


def parse_args():
    """
    Parse command line arguments.
    """
    parser = argparse.ArgumentParser(description="Normalization and lexical syllabification client.")
    parser.add_argument("input_file", type=Path, help="Path to the input file containing text.")
    parser.add_argument("--preprocess", "-p", action="store_true",
                        help="Preprocess the input text modernizing some sequences (without altering metrically relevant content).")
    parser.add_argument("--output_syllabification", "-y", action="store_true", help="Output syllabied in addition to normalized text.")
    parser.add_argument("--stress_marks", type=str, choices=["acute", "circumflex", "allupper"], default="acute",
                        help="How to mark the stressed syllable in the output. The 'circumflex' and 'acute' options prefix a stress mark "
                             "to the stressed syllable, while 'allupper' makes it all caps.")
    parser.add_argument("--destress", "-d", action="store_true",
                        help="In syllabified output, remove stress marking if the syllable is lexically unstressed.")
    parser.add_argument("--normalize", "-n", action="store_true",
                        help="Replace out of vocabulary by in-vocabulary forms from an inflected forms dictionary.")
    parser.add_argument("--disambiguate_stress", "-s", action="store_true",
                        help="Add an accent mark to make a stressed syllable unambiguous "
                             "(similar to Spanish conventions) in the text that will be passed to metrical scansion. "
                             "Applies only if --normalize is set.")
    parser.add_argument("--stress_possessives", "-m", action="store_true",
                        help="Add a stress mark to preposed possessives in the text that will be passed to metrical scansion. "
                             "Helps scansion find the stress pattern, but is not useful for other types of preprocessing.")
    parser.add_argument("--run_id", "-b", type=str, default="")
    parser.add_argument("--run_comment", type=str, default="")
    return parser.parse_args()


def preprocess_orthography(txt: str, ignore_flagged=True) -> str:
    """
    Preprocess the input text to modernize some sequences without altering metrically relevant content.

    Args:
        txt (str): The input text to preprocess.
        ignore_flagged (bool): Whether to ignore expressions tagged with 'skip'
            in the replacement data.

    Returns:
        str: The preprocessed text.
    """
    pat2rep = ut.load_text_replacements(cf, ignore_flagged=ignore_flagged)
    for pat, rep in pat2rep.items():
        txt = re.sub(pat, rep, txt)
    return txt


def postprocess_syllable_str(syllable_str: str) -> str:
    """
    Postprocess the syllable sequence (as a string), according to the rules in
    :obj:`cf.syllable_replacements`.

    Args:
        syllable_str (str): The input syllable string.

    Returns:
        str: The post-processed syllable string.
    """
    # Remove unwanted characters and format the syllable string
    pat2rep = ut.load_syllable_replacements(cf)
    for pat, (rep, postpro_info) in pat2rep.items():
        # only apply postprocessing instructions if the pattern matches
        if re.search(pat, syllable_str):
            if postpro_info == "unstressed":
                syllable_str = syllable_str.lower()
        # apply the replacement (it's case insensitive so lowercasing above
        # does not affect the replacement)
        syllable_str = re.sub(pat, rep, syllable_str)

    return syllable_str


def apply_syll_and_norm(line_list: list[str]) -> tuple[list[tuple], list[str]]:
    """
    If CLI args ask for it, normalizes text. Always syllabifies each word, applying
    :func:`syllabification.g2s.syllabify_full` to a list of lines.
    
    Args:
        line_list (list[str]): A list of lines to syllabify / normalize.
    
    Returns:
        tuple: A tuple containing two lists:
            - A list of tuples, containing syllabified words with stress marks, without,
              and the stressed syllable position.
            - A list of strings with the syllabified words without stress marks.
    """
    # load data for preprocessing (word or regex lists)
    out_lines = [] # syllabification after orthographic preprocessing
    out_lines_running_text = [] # orthographic preprocessing
    for line in line_list:
        text = line.strip()
        # replacements that may affect a sequence of words
        text = re.sub(PUNCT_TO_SPACE_RE, " ", text)
        if args.preprocess:
            text = preprocess_orthography(text, ignore_flagged=not(args.stress_possessives))
            text = re.sub(PUNCT_RE, r" \1 ", text)
        words = [tok for tok in re.split(r"\s+", text) if tok.strip() != ""]
        out_line = []
        out_line_running_text = []

        # handle apostrophes
        updated_words = []

        for widx, word in enumerate(words):
            has_apos = re.search(r"(\w+)['‘’](\w*)", word)
            if not has_apos:
                updated_words.append(word)
                continue

            word_orig = word
            base = has_apos.group(1)
            suffix = has_apos.group(2)

            split_parts = [base]
            if suffix:
                split_parts.append(suffix.strip())

            # Generate vowel edits for base
            edits_noapos = [base + v for v in ['a', 'e', 'o']]
            ed_scos = []

            # Prepare a simulated token list for context computation
            simulated_toklist = updated_words + [base] + words[widx + 1:]
            simulated_idx = len(updated_words)  # index where base would be inserted
            wlc, wrc = nglm.find_context_for_token(base, simulated_idx, simulated_toklist)

            for ed in edits_noapos:
                ed_sco = nglm.find_logprob_in_context(ed, (wlc, wrc))
                ed_scos.append((ed, ed_sco))

            best_ed_cand = sorted(ed_scos, key=lambda x: -x[1])

            if not best_ed_cand:
                updated_words.append(word_orig)
            else:
                new_word = best_ed_cand[0][0]
                updated_words.append(new_word)
                if len(split_parts) > 1:
                    updated_words.extend(split_parts[1:])

                logger.debug(
                    f"Replace Apostrophe: [{word_orig}] to [{new_word}]+[{split_parts[1:] if len(split_parts) > 1 else ''}] context [{' '.join(updated_words)}]")

        # handle other norm cases than apostrophes
        for widx, word in enumerate(updated_words):
            if re.search(PUNCT_RE, word):
                out_line.append((word, word, word, -1))  # no syllabification
                out_line_running_text.append(re.sub(PUNCT_TO_SPACE_RE, " ", word).replace("-", ""))
                continue
            # remove punctuation (but hypen) from words
            word = re.sub(PUNCT_TO_SPACE_RE, " ", word)
            word = word.replace("-", "")
            if word.strip() == "":
                continue
            # check if needs diacritic stress
            #   if in list, line with unaccented and accented variants are scored
            #   with n-gram lm and the best is chosen
            if word in sti.diacritic_stress:
                updated_words = words[0:widx] + [word] + words[widx+1:]
                wlc, wrc = nglm.find_context_for_token(word, widx, updated_words)                                                       
                sco_unstressed = nglm.find_logprob_in_context(word, (wlc, wrc))
                sco_stressed = nglm.find_logprob_in_context(sti.diacritic_stress[word], (wlc, wrc))
                if sco_stressed > sco_unstressed:
                    word_orig = word
                    word = sti.diacritic_stress[word]
                    logger.debug(f"LM Dia Stress: [{word_orig}] to [{sti.diacritic_stress[word_orig]}] context [{' '.join(updated_words)}]")
            # do token norm before syllabification
            # normalizer is `nmlzr` instantiated in main block
            if args.normalize and word not in nmlzr.vocab:                
                # version of word with initial caps may be in vocabulary, neutralize
                if word.lower() not in nmlzr.vocab:
                    # test if exact match in Spanish (castellanismo)
                    if False and (word in nmlzr_es.vocab or word.lower() in nmlzr_es.vocab):
                        logger.debug(f"Accept castellanismo [{word}]")
                    else:
                        wcands = nmlzr.collect_candidates(word)
                        best_cand = nmlzr.rank_candidates(word, updated_words, widx, wcands, nglm)
                        if best_cand is not None:
                            logger.debug(f"LM Ed Norm: [{word}] to [{best_cand.form}]")
                        else:
                            logger.debug(f"No Norm: [{word}]")
                        word = best_cand.form if best_cand is not None else word
                        # respect case in orig text, using a case mask
                        case_mask_norm = nmlzr.create_case_mask(word)
                        word_cased = "".join([cha.upper() if cm == 1 else cha for (cha, cm) in zip(list(word), case_mask_norm)])
                        word = word_cased
            words_before_pos = copy.deepcopy(updated_words)
            
            # sylllabification only after preprocessing each line as above
            syllables = g2s.syllabify_full(re.sub(PUNCT_TO_SPACE_RE, " ", word), disambiguate_stress=args.disambiguate_stress)
            syllables_orig = syllables
            # several representations of the syllabified word are stored,
            # along with the stressed syllable position
            syllables = (postprocess_syllable_str(syllables[0]), # stressed syllable in uppercase
                         postprocess_syllable_str(syllables[1]), # stressed syllable preceded by a diacritic
                         postprocess_syllable_str(syllables[2]), # no extra indication of stress
                         syllables[-1]) # stressed syllable position
            out_line.append(syllables)
            out_line_running_text.append(syllables[2].replace("-", ""))
        if len(out_line) > 0:
            out_lines.append(out_line)
        if len(out_line_running_text) > 0:
            out_lines_running_text.append(out_line_running_text)
    return out_lines, out_lines_running_text


if __name__ == "__main__":
    # Just for interactive shell
    reload(cf)
    reload(g2s)
    reload(ncf)
    reload(normalizer)
    reload(sti)
    reload(ut)

    args = parse_args()
    input_file = args.input_file
    
    # Prepare logging
    for h in logging.root.handlers[:]:
        logging.root.removeHandler(h)
    logger = logging.getLogger("main")
    logger.handlers.clear()
    logger.setLevel(logging.DEBUG)
    lfh = logging.FileHandler(Path(cf.log_dir) / cf.log_fn_template.format(batch_id=str.zfill(args.run_id, 3), mode="w"))
    lch  = logging.StreamHandler(sys.stdout)
    lfh.setLevel(logging.DEBUG)
    lch.setLevel(logging.DEBUG)
    log_format_file = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    log_format_console = logging.Formatter('%(message)s')
    lfh.setFormatter(log_format_file)
    lch.setFormatter(log_format_console)
    logger.addHandler(lfh)
    logger.addHandler(lch)

    start_time = time.time()
    print("- Start: ", time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()))
    
    # Load input text
    with open(input_file, "r", encoding="utf8") as f:
        lines_to_process = f.readlines()
    
    # Prepare norm, called by apply_syllabification
    if args.normalize:
        nmlzr = normalizer.Normalizer(ncf)
        nmlzr_es = normalizer.Normalizer(ncf, lang="es")
        #pos_tagger = 
    else:
        print("Normalization off, run with --normalize to enable.")
    
    # Prepare n-gram language model
    nglm = lmg.KenLMManager() 
    
    # Normalization and syllabification
    out_lines, out_lines_running_text = apply_syll_and_norm(lines_to_process)
    
    # Destressing
    if args.destress:
        destress_function = ut.destress_word_simple
        # destress in running text
        out_lines_running_text_destressed = copy.deepcopy(out_lines_running_text)
        for lidx, olrt in enumerate(out_lines_running_text):
            for widx, syll_info in enumerate(olrt):
                if syll_info.lower() in sti.atonas_gl:
                    # if the word is unstressed, remove the stress mark
                    out_lines_running_text_destressed[lidx][widx] = destress_function(syll_info.replace("´", ""))
        # destress in syllabified output
        # create a mutable copy of the syllabified output
        out_lines_destressed = []
        for ol in out_lines:
            out_lines_destressed.append(list(ol))
        for slidx, ol in enumerate(out_lines):
            for swidx, syll_info in enumerate(ol):
                if syll_info[2].lower().replace("-", "") in sti.atonas_gl:
                    case_mask = [1 if char.isupper() else 0 for char in syll_info[2]]
                    # if the word is unstressed, remove the stress mark
                    out_lines_destressed[slidx][swidx] = (destress_function(syll_info[0], case_mask),
                                                          destress_function(syll_info[1], case_mask),
                                                          destress_function(syll_info[2], case_mask),
                                                          syll_info[3])

    # Outputs
    #breakpoint()
    out_run_id = f"_{str.zfill(args.run_id, 3)}" if args.run_id else ""
    out_dir_id = f"out{out_run_id}"
    if not Path(input_file.parent / out_dir_id).exists():
        Path(input_file.parent / out_dir_id).mkdir(parents=True)

    #   Syllabification
    if args.output_syllabification:
        infix_pp_syll = "_pp_syll_out" if args.preprocess else "_syll_out"
        infix_pp_syll += out_run_id
        output_file_syll = input_file.parent / out_dir_id / Path(input_file.stem + infix_pp_syll + input_file.suffix)
        with output_file_syll.open(mode="w", encoding="utf8") as outf:
            for line in out_lines:
                syll_index_to_output = 0 if args.stress_marks == "allupper" else 1
                outf.write(" ".join([tu[syll_index_to_output] for tu in line]) + "\n")

    #   Running text (always preprocessed)
    if args.preprocess and not args.normalize:
        infix_pp_text = "_pp_out"
        infix_pp_text += out_run_id
        output_file_pp = input_file.parent / out_dir_id / Path(input_file.stem + infix_pp_text + input_file.suffix)
        with output_file_pp.open(mode="w", encoding="utf8") as outf:
            for line in out_lines_running_text:
                outf.write(ut.detokenize(line) + "\n")
    
    #   Destressed syllabification
    if args.output_syllabification:
        if args.destress and not args.normalize:
            infix_destressed = "_pp_syll_out_des" if args.preprocess else "_syll_out_des"
            infix_destressed += out_run_id
            output_file_syll_destressed = input_file.parent / out_dir_id / Path(input_file.stem + infix_destressed + input_file.suffix)
            with output_file_syll_destressed.open(mode="w", encoding="utf8") as outf:
                for line in out_lines_destressed:
                    syll_index_to_output = 0 if args.stress_marks == "allupper" else 1
                    outf.write(" ".join([tu[syll_index_to_output] for tu in line]) + "\n")

    #   Destressed running text
    if args.destress and args.preprocess and not args.normalize:
        infix_pp_destressed = "_pp_out_des"
        infix_pp_destressed += out_run_id
        output_file_pp_destressed = input_file.parent / out_dir_id / Path(input_file.stem + infix_pp_destressed + input_file.suffix)
        with output_file_pp_destressed.open(mode="w", encoding="utf8") as outf:
            for line in out_lines_running_text_destressed:
                outf.write(ut.detokenize(line) + "\n")
    
    #   With norm
    #      Syllabification
    #         This normalized but not destressed output is only for debugging (you need destressed output for Gumper)
    if args.output_syllabification:
        if args.normalize and not args.destress:
            infix_syll_norm = "_pp_syll_out_norm" if args.preprocess else "_syll_out_norm"
            if args.disambiguate_stress:
                infix_syll_norm += "_spa"
            infix_syll_norm += out_run_id
            output_file_syll_destressed = input_file.parent / out_dir_id / Path(input_file.stem + infix_syll_norm + input_file.suffix)
            with output_file_syll_destressed.open(mode="w", encoding="utf8") as outf:
                for line in out_lines:
                    syll_index_to_output = 0 if args.stress_marks == "allupper" else 1
                    outf.write(" ".join([tu[syll_index_to_output] for tu in line]) + "\n")
        if args.destress and args.normalize:
            infix_destressed = "_pp_syll_out_des_norm" if args.preprocess else "_syll_out_des_norm"
            if args.disambiguate_stress:
                infix_destressed += "_spa"
            infix_destressed += out_run_id
            output_file_syll_destressed = input_file.parent / out_dir_id / Path(input_file.stem + infix_destressed + input_file.suffix)
            with output_file_syll_destressed.open(mode="w", encoding="utf8") as outf:
                for line in out_lines_destressed:
                    syll_index_to_output = 0 if args.stress_marks == "allupper" else 1
                    outf.write(" ".join([tu[syll_index_to_output] for tu in line]) + "\n")

    #      Running text: Forgetting about "des" infix cos for running text it's the same as "pp_out"
    if args.destress and args.preprocess and args.normalize:
        infix_pp_destressed = "_pp_out_norm"
        if args.disambiguate_stress:
            infix_pp_destressed += "_spa"
        infix_pp_destressed += out_run_id
        output_file_pp_destressed = input_file.parent / out_dir_id / Path(input_file.stem + infix_pp_destressed + input_file.suffix)
        with output_file_pp_destressed.open(mode="w", encoding="utf8") as outf:
            for line in out_lines_running_text_destressed:
                outf.write(ut.detokenize(line) + "\n")
    print("- End: ", time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()))
    total_min, total_secs = divmod(time.time() - start_time, 60)
    logger.info(f"- Duration:  {total_min}m {total_secs:.2f}s")
    
    if args.run_comment:
        batch_info_path = Path(input_file.parent) / cf.batch_cumulog 
        with open(batch_info_path, mode="a") as batch_info:
            if batch_info_path.exists() and batch_info_path.stat().st_size == 0:
                batch_info.write(f"Batch ID\tComment\n")
            batch_info.write(f"{args.run_id}\t{args.run_comment}\n")
