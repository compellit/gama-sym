# Test-set format

It contains the following information (whether in the .tsv or .xlsx version):
- Original poem text before preprocessing
- Preprocessed text (the one scansion was run on)
- Lexical syllabification
- Metrical syllabification (with metrical license annotations)
  - Synalepha is marked with `_`, dialepha with `÷`, syneresis with `^` and dieresis with `#`. An apostrophe makrs stressed syllables. We also have code in `scansion.utils` to convert this to Valença & Calegario (2025) format
- The number of lexical and metrical syllables
- The stress patterns
- Poem metadata so that we can identify each poem individually (author, title, work ID)
