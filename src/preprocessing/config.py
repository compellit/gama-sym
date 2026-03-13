# Normalization and syllabification configuration file

from pathlib import Path

# Orthography processing

APOS = r"['‘’]"

config_dir = Path(__file__).parent

# IO

data_dir = Path(config_dir / "data")
text_level_replacements = data_dir / "prepro-text-level.tsv"
syllable_replacements = data_dir / "syll-postpro.tsv"

log_dir = "../logs"
log_fn_template = "log_prepro_{batch_id}.txt"
if not Path(log_dir).exists():
    Path(log_dir).mkdir(parents=True)

batch_cumulog = "prepro_cumu_log.txt"
