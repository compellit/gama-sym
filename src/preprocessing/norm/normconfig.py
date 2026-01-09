"""Normalization configuration file for Galician XIX c. texts"""

from pathlib import Path

# resources -------------------------------------

config_dir = Path(__file__).parent
IVDICO = (config_dir.parent / "data" / "vocab-gl-merged.pkl").resolve()
IVDICO_ES = (config_dir.parent / "data" / "vocab-es-aspell-expanded.txt.pkl").resolve()
LMPATH= (config_dir.parent / "data" / "nos-127.klm.bin").resolve()
LANGUAGES = ("gl", "es")

# candidate generation --------------------------
 
#TODO should no longer be needed to have list (not string) for accented characters,
alphabet = ('bcdfghjklmnpqrstvwxyzaeiou', ['á', 'é', 'í', 'ó', 'ú', 'ü', 'ñ', 'ç'])
accent_check_in_regexes = bool(1)

# To penalize edits that delete a vowel accent
# (consonants with diacritics like ç and ñ are not considered,
# they are not in the list of accented characters in editor.py)
# If set this to 0, it will not penalize
acc_ins_penalty = -0.5 # for now negative values penalize. 

# lm scoring ------------------------------------

lm_window = 4

