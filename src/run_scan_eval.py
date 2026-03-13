"""
Run Gumper (Galician Jumper) and (optionally) evaluate scansion output against gold stress patterns.
"""

import argparse
from importlib import reload
from pathlib import Path

from scansion.scan.gl import gumper  # Galician scansion
from scansion.scan.es import jumper  # Spanish scansion (there's a CLI option to use it)
import pandas as pd
import re

from scansion import config as scf
from scansion import utils as sut


def parse_args():
    parser = argparse.ArgumentParser(description="Gumper client for analyzing poems.")
    parser.add_argument("raw_lines", type=str, help="Lines to tag with Gumper")
    parser.add_argument("gold_location", type=str, help="Path to gold stress patterns")
    parser.add_argument("batch_id", type=str, help="ID of the batch to run")
    parser.add_argument("--metadata_path", type=str, default="", help="If given, will use poem IDs from this metadata file to group lines by poem.")
    parser.add_argument("--metadata_start", type=int, default=0, help="If metadata_path is given, start from this index in the metadata.")
    parser.add_argument("--use_jumper_es", action="store_true", help="If set, uses Spanish Jumper for scansion instead of Galician  Gumper.")
    parser.add_argument("--skip_cleanup", action="store_true", help="If set, does not do any additional preprocessing after the normalization output.")
    parser.add_argument("--run_comment", type=str, default="",)
    parser.add_argument("--skip_eval", action="store_true", help="If set, skips evaluation and only outputs scansion.")
    parser.add_argument("--out_dir", type=str, help="Output directory (applies when not running evaluation).")
    return parser.parse_args()


if __name__ == "__main__":
    # Reloads just for inteactive Ipython shell
    for mod in [gumper, jumper, sut, scf]:
        reload(mod)

    args = parse_args()    
    
    # Use Spanish Jumper or (default) Galician Gumper
    scansion_algo = jumper if args.use_jumper_es else gumper
    
    if args.skip_cleanup:
        reps_w = {}
        reps_t = {}
    else:
        reps_w = sut.load_w_replacements(scf)
        reps_t = sut.load_t_replacements(scf)

    all_poem_lines_out = []
    all_scansion_out = []

    out_patterns = []

    # read gold stress patterns
    if not args.skip_eval:
        gold_data = sut.read_gold_stress_patterns(args.gold_location)

    with open(Path(args.raw_lines)) as f:
        poem_text = f.read()
        poem_text_orig = poem_text
        if not args.skip_cleanup:
            poem_text = sut.cleanup_text(poem_text, reps_t)
            poem_text = sut.cleanup_text(poem_text, reps_w)
        poem_text = re.sub(r"#[^\n]+\n", "\n", poem_text)  # remove comments

    orig_lines = poem_text_orig.splitlines()

    if not args.skip_eval:
        assert len(orig_lines) == len(gold_data), "Number of lines in output does not match gold data."

    out_lines = []
    # do not group lines by poem (applies context window sequentially to all lines in file)
    if args.metadata_path == "" or args.skip_eval:
        esc = scansion_algo.escandir_texto(poem_text)
        for idx, ana in enumerate(esc):
            # esc columns: gumper prepro text, postpro text, nbSyll, metPat, metPat no antirhythmic
            out_ana = ana[0:3]
            out_ana.append(" ".join([str(x) for x in ana[3]]))  # stressed positions
            out_ana.append(" ".join([str(x) for x in ana[4]]))  # stressed positions no antirhythmic
            out_line = [orig_lines[idx]] + out_ana
            if not args.skip_eval:
                # add gold number of syllables and stress pattern
                out_line.extend([gold_data[idx][1], gold_data[idx][2]])
            out_lines.append(out_line)
    # group by poem (scans one poem at a time, context window always from within same poem)
    else:
        done_indices = 0

        # with metadata (group by column workId)
        #  nb: value for sheet_name key comes from config, where the variable name is
        #      metadata_sheet_name, but WORKBOOK PATH is given as CLI argument
        if args.metadata_path.endswith(".ods"):
            metadata_df = pd.read_excel(Path(args.metadata_path), sheet_name=scf.metadata_sheet_name, engine="odf")
        else:
            # assume xlsx
            assert args.metadata_path.endswith(".xlsx"), "Metadata file must be .ods, .xlsx or .xls"
            metadata_df = pd.read_excel(Path(args.metadata_path), sheet_name=scf.metadata_sheet_name)
        # add workId to lines and group by it
        work_ids = metadata_df["workId"].tolist()[args.metadata_start:]
        poem_lines = poem_text.splitlines()
        text_and_id = list(zip(work_ids[:len(poem_lines)], poem_lines))
        text_and_id_df = pd.DataFrame(text_and_id, columns=["workId", "line"])

        # go over poems
        poem_groups = text_and_id_df.groupby("workId")
        for grp in poem_groups:
            grp_name = grp[0]
            grp_df = grp[1]
            poem_lines = grp_df["line"].tolist()
            poem_text = "\n".join(poem_lines)
            poem_text = sut.cleanup_text(poem_text, reps_t)
            poem_text = sut.cleanup_text(poem_text, reps_w)
            esc = scansion_algo.escandir_texto(poem_text)
            for idx, ana in enumerate(esc):
                # esc columns: gumper prepro text, postpro text, nbSyll, metPat, metPat no antirhythmic
                out_ana = ana[0:3]
                out_ana.append(" ".join([str(x) for x in ana[3]]))
                out_ana.append(" ".join([str(x) for x in ana[4]]))  # stressed positions no antirhythmic
                out_line = [orig_lines[done_indices]] + out_ana
                # add gold number of syllables and stress pattern
                out_line.extend([gold_data[done_indices][1], gold_data[done_indices][2]])
                out_lines.append(out_line)
                done_indices += 1

    if not args.skip_eval:
        batch_output = Path(scf.oudir) / Path(f"scansion_gl_eval_{str.zfill(args.batch_id, 3)}").with_suffix(".tsv")
        batch_eval_quant = Path(scf.oudir) / "scansion_gl_cumu_acc.tsv"
               
        df = pd.DataFrame.from_records(out_lines,
            columns=["orig", "pre", "postpro", "sylA", "met", "met2", "sylG", "metG"])
        
        df["sylG"] = pd.to_numeric(df["sylG"], errors="coerce").astype("Int64")
    
        df["evalMet"] = (df["met"] == df["metG"]).astype(int)
        df["evalSyl"] = (df["sylA"] == df["sylG"]).astype(int)
        acc_met = df["evalMet"].sum() / len(df)
        acc_syl = df["evalSyl"].sum() / len(df)
        
        # rearrange columns
        df = df[["orig", "pre", "postpro", "evalSyl", "evalMet", "sylA", "met", "sylG", "metG", "met2"]]
    
        # write out    
        df.to_csv(batch_output, sep="\t", header=True, index=False, encoding="utf-8")
    
        # append to batch evaluation log
        with open(batch_eval_quant, "a") as beqf:
            if batch_eval_quant.stat().st_size == 0:
                beqf.write(f"batch_id\tacc_met\tacc_syl\tcomment\n")
            run_comment = args.run_comment if args.run_comment else ""
            batch_args = f"IN:{args.raw_lines}|||GOLD:{args.gold_location}|||OUT:{batch_output}"
            if args.metadata_path:
                batch_args += f"|||METADATA:{args.metadata_path}|||METADATA_START:{args.metadata_start}"
            beqf.write(f"{str.zfill(args.batch_id, 3)}\t{acc_met:.4f}\t{acc_syl:.4f}\t{args.run_comment}\t{batch_args}\n")
    else:
        # just output scansion without evaluation
        df = pd.DataFrame.from_records(out_lines,
            columns=["orig", "prepro", "postpro", "syl", "met", "met2"])
        batch_output = Path(args.out_dir) / Path(f"scansion_output_{str.zfill(args.batch_id, 3)}.tsv").with_suffix(".tsv")
        # orig + esc columns: gumper prepro text, postpro text, nbSyll, metPat, metPat no antirhythmic
        df.to_csv(batch_output, sep="\t", header=True, index=False, encoding="utf-8")