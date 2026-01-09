"""
Word-Error Rate (WER) evaluation script with werpy.
See https://github.com/analyticsinmotion/werpy
"""

import argparse
from pathlib import Path

import pandas as pd
import werpy


def parse_args():
    parser = argparse.ArgumentParser(description="Get WER given a reference and a results file.")
    parser.add_argument("--reference", "-g", type=str, help="Reference path.")
    parser.add_argument("--hypothesis", "-s", type=str, help="Result path.")
    parser.add_argument("--output_dir", "-o", type=str, help="Output directory.")
    parser.add_argument("--run_id", "-r", type=str, help="ID for the run.")
    return parser.parse_args()

def read_lines(filepath: str):
    with open(filepath, "r", encoding="utf-8") as f:
        lines = [line.strip() for line in f.readlines()]
    return lines


if __name__ == "__main__":
    args = parse_args()
    ref_lines = read_lines(args.reference)
    res_lines = read_lines(args.hypothesis)
    
    summary = werpy.summary(ref_lines, res_lines)
    #print(summary)
    
    # lines where levenshtein distance > 0, see https://github.com/analyticsinmotion/werpy
    lines_with_mismatch = summary[summary["ld"] > 0]
    print("Lines with mismatch:", len(lines_with_mismatch))
    
    wers = werpy.wer(ref_lines, res_lines)
    print(wers)

    summary.to_csv(Path(args.output_dir) / f"log_wer_{args.run_id}_summary.tsv", sep="\t", index=False)
    with open(Path(args.output_dir) / f"log_wer_{args.run_id}_result.txt", "w", encoding="utf-8") as f:
        f.write(f"WER: {wers}\n")
        f.write(f"Lines with mismatch: {len(lines_with_mismatch)}\n")
