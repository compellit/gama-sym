# Test-set format

The .tsv version is for stress match and meter match and only shows the line, its stress pattern and its meter.
- Original poem text before preprocessing
- Number metrical syllables
- Stress patterns

The .xlsx version contains poem metadata (allows to group lines for a single poem before running scansion). It also has syllabification information (lexical and metrical) and metaplasm annotations:
- Original poem text before preprocessing
- Preprocessed text (the one scansion was run on)
- Lexical syllabification
- Metrical syllabification (with metrical license annotations)
  - Synalepha is marked with `_`, dialepha with `÷`, syneresis with `^` and dieresis with `#`. An apostrophe makrs stressed syllables. We also have code in `scansion.utils` to convert this to Valença & Calegario (2025) format
- The number of lexical and metrical syllables
- The stress patterns
- Poem metadata so that we can identify each poem individually (author, title, work ID)
