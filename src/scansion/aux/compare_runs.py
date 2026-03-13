"""Compare Gumper runs as created by :mod:`run_scan_eval.py`."""


import argparse
from importlib import reload
from pathlib import Path

import pandas as pd

from scansion import config as scf


def parse_args():
    """
    Parse command line arguments.
    """
    parser = argparse.ArgumentParser(description="Compare Gumper batches.")
    parser.add_argument("batch_1", type=str, help="ID (pad to 3 digits) for the first batch.")
    parser.add_argument("batch_2", type=str, help="ID (pad to 3 digits) for the second batch.")
    return parser.parse_args()


def compare_values(val1, val2):
    if val1 == 1 and val2 == 0:
        return 'worse'
    elif val1 == 0 and val2 == 1:
        return 'better'
    else:
        return 'same'


def compare_runs(df1, df2, compare_columns, additional_columns_from_df1=None):
    """
    Compare multiple columns between df1 and df2 and return a copy of df2 with:
      - selected columns from df1
      - new columns indicating whether each value got 'better', 'worse', or stayed the 'same'

    Args:
        df1 (pd.DataFrame): First DataFrame (baseline)
        df2 (pd.DataFrame): Second DataFrame (to be augmented)
        compare_columns (list of str): List of column names to compare
        additional_columns_from_df1 (list of str): Columns from df1 to copy into the output

    Returns:
        pd.DataFrame: Comparison (augmented df2)
    """
    result = df2.copy()

    for col in compare_columns:
        if col not in df1.columns or col not in df2.columns:
            raise ValueError(f"Column '{col}' must exist in both DataFrames.")

        result[f'C{col}'] = df1[col].combine(df2[col], compare_values)

    if additional_columns_from_df1:
        for col in additional_columns_from_df1:
            if col in df1.columns:
                result[f"{col}1"] = df1[col]
            else:
                raise ValueError(f"Column '{col}' not found in df1.")

    return result



if __name__ == "__main__":
    for modu in [scf]:
        reload(modu)

    args = parse_args()

    # Load the two batches
    df1 = pd.read_csv(Path(scf.oudir) / f"scansion_gl_eval_{args.batch_1}.tsv", sep="\t")
    df2 = pd.read_csv(Path(scf.oudir) / f"scansion_gl_eval_{args.batch_2}.tsv", sep="\t")

    # Define columns to compare
    compare_columns = [
        'evalMet', 'evalSyl'
    ]
    additional_columns_from_df1 = ['sylA', 'met']

    # Compare the batches
    comparison_result = compare_runs(
        df1, df2, compare_columns, additional_columns_from_df1
    )
    # change column order
    comparison_result = comparison_result[[
        'CevalSyl', 'CevalMet',
        'orig', 'pre', 'postpro',
        'evalSyl', 'evalMet',
        'sylA', 'met', 'metG', 'met1'
    ]]
    
    # Save the comparison result to a new file
    output_file = Path(scf.logdir) / f"compare_{str.zfill(str(args.batch_1), 3)}_{str.zfill(str(args.batch_2), 3)}.tsv"
    comparison_result.to_csv(output_file, sep="\t", index=False)
    print(f"Comparison saved to {output_file}")
