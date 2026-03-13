# Test-set format

The files below can be shared upon request. A small amount of the material comes from unpublished editions of 19th-century text. We accessed these data under a reuse agreement with the data owners which does not allow us to redistribute publicly. 

File `gl_scansion_gold_test_010.tsv` is for evaluating stress match and meter match only, showing each line, its stress pattern and its meter.
- Original poem text before preprocessing
- Number of metrical syllables
- Stress patterns

File `gl_scansion_gold_test_md_010.xlsx` (also available as `gl_scansion_gold_test_md_010.tsv`) contains syllabification information (lexical and metrical), metaplasm annotations and poem metadata:
- Original poem text before preprocessing
- Preprocessed text (the one scansion was run on)
- Lexical syllabification
- Metrical syllabification (with metrical license annotations)
  - Synalepha is marked with `_`, dialepha with `÷`, syneresis with `^` and dieresis with `#`. An apostrophe makrs stressed syllables. We also have code in `scansion.utils` to convert this to Valença & Calegario's (2025) format
- The number of lexical and metrical syllables
- The stress patterns
- Poem metadata (author, title, work ID). This can be used to run scansion for each poem separately or for other analyses
