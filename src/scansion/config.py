from pathlib import Path

config_dir = Path(__file__).parent

# data 

# To be able to do some substitutions after prepreprocesing, in scansion directly.
# (Some may be not needeed with current preprocessing, but did not thoroughly test)

word_bound_replacements = Path(config_dir / "data") / "replacements_w.txt"
text_level_replacements = Path(config_dir / "data") / "replacements_t.txt"

# IO

oudir = Path(config_dir.parent.parent / "out")
logdir = Path(config_dir.parent.parent / "logs")

# for gumper eval, when choosing to group lines by poem -----------
metadata_sheet_name = "dataAll"


for dname in [oudir, logdir]:
    if not Path(dname).exists():
        Path(dname).mkdir(parents=True)

