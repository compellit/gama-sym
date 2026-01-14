# Test-set format

The .tsv version is for evaluating stress match and meter match only, showing each line, its stress pattern and its meter.
- Original poem text before preprocessing
- Number of metrical syllables
- Stress patterns

The .xlsx version contains syllabification information (lexical and metrical), metaplasm annotations and poem metadata:
- Original poem text before preprocessing
- Preprocessed text (the one scansion was run on)
- Lexical syllabification
- Metrical syllabification (with metrical license annotations)
  - Synalepha is marked with `_`, dialepha with `÷`, syneresis with `^` and dieresis with `#`. An apostrophe makrs stressed syllables. We also have code in `scansion.utils` to convert this to Valença & Calegario's (2025) format
- The number of lexical and metrical syllables
- The stress patterns
- Poem metadata (author, title, work ID). This can be used to run scansion for each poem separately or for other analyses
