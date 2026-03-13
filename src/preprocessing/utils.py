"""Utilities for normalization and lexical syllabification."""

from collections import OrderedDict
import logging
import re
import types
import unicodedata


utils_logger = logging.getLogger("main.utils")

from syllabification import g2s as g2s


def load_text_replacements(config: types.ModuleType, ignore_flagged=False) -> OrderedDict[re.Pattern, str]:
    """
    Loads regex contexts and replacements from a file whose path is given at :obj:`config`.
    The replacements may affect multiple words.
    
    Args:
        config (types.ModuleType): The configuration to load.
        ignore_flagged (bool, optional): Whether to ignore expressions tagged with 'skip'
           in the data.
    Returns:
        OrderedDict[re.Pattern, str]: OrderedDict with expressions and their replacements 
    """
    replacements: OrderedDict[re.Pattern, str] = OrderedDict()
    with open(config.text_level_replacements, "r", encoding="utf-8") as f:
        for line in f:
            if line.startswith("#"):
                continue
            line = re.sub(" #.+", "", line)  # Remove comments
            # replacements may finish with a space, we strip all left, but right only newline
            if line.count("\t") == 2:
                key, value, action = line.lstrip().rstrip("\n\r").split("\t")
            else:
                assert line.count("\t") == 1, "Line should contain one or two tab-delimited columns."
                action = None
                key, value = line.lstrip().rstrip("\n\r").split("\t")
            if ignore_flagged and action == "skip":
                continue
            elif action == "cs":
                replacements[re.compile(fr"{key}", re.U)] = value
            else:
                replacements[re.compile(fr"{key}", re.I | re.U)] = value
    return replacements


def load_syllable_replacements(config: types.ModuleType) -> OrderedDict[re.Pattern, tuple[str, str]]:
    """
    Loads replacements for a syllable sequence expressed as a string from a file,
    whose path is given at :obj:`config`.

    Args:
        config: Configuration object containing the path to the syllable replacements file.

    Returns:
        OrderedDict: A dictionary with compiled regex patterns as keys and, as values,
                     a tuple with their replacements and a postprocessing instruction.
    """
    replacements: OrderedDict[re.Pattern, tuple[str, str]] = OrderedDict()
    with open(config.syllable_replacements, "r", encoding="utf-8") as f:
        for line in f:
            if line.startswith("#"):
                continue
            line = re.sub(" #.+", "", line)  # Remove comments
            # replacements may finish with a space, we strip all left, but right only newline
            # postpro refers to information to modify postprocessing, see the data file
            # at scf.syllable_replacements
            key, value, postpro = line.lstrip().rstrip("\n\r").split("\t")
            replacements[re.compile(fr"{key}", re.I|re.U)] = (value, postpro)
    return replacements


def destress_word(word: str, case_mask: list=None) -> str:
    """
    Remove stress marks from a word.

    Args:
        word (str): The word to destress.
        case_mask (list): A list with the same length as the word, with 1 if the character
            at that position should be uppercased, and 0 if it should be lowercased.

    Returns:
        str: The destressed word.
    """
    #TODO shouldn't the stress mark be dynamic c/o cli args?
    word = re.sub(r"[´]", "", word)  # Remove stress marks    
    normalized_word = unicodedata.normalize('NFD', word)
    unaccented_chars = [char for char in normalized_word if unicodedata.combining(char) == 0]
    if case_mask is not None:
        assert len(word) == len(case_mask), "Word and case mask must have the same length."
        final_word = []
        for cidx, cm in enumerate(case_mask):
            final_word.append(unaccented_chars[cidx].lower()) if cm == 0 else \
                final_word.append(unaccented_chars[cidx])
        return "".join(final_word)
    else:
        return "".join(unaccented_chars)


def destress_word_simple(word: str, case_mask: list=None) -> str:
    """
    Remove stress marks from a word, without case masking.
    Note: This is used with syllabified output, where the stress mark has been
    prefixed to the syllable (when applicable), that's why simply removing the stress mark
    is fine rather than removing the diacritic but keeping the vowel.

    Args:
        word (str): The word to destress.

    Returns:
        str: The destressed word.
    """
    #TODO shouldn't the stress mark be dynamic c/o cli args?
    word = re.sub(r"[´]", "", word)  # Remove stress marks
    if case_mask is not None:
        assert len(word) == len(case_mask), "Word and case mask must have the same length."
    final_word = word
    if case_mask is not None:
        final_word = []
        for cidx, cm in enumerate(case_mask):
            final_word.append(word[cidx].lower()) if cm == 0 else final_word.append(word[cidx])
        final_word = "".join(final_word)
    return final_word


def _disambiguate_syll_stress(tok: str, syl_list:list) -> str:
    """
    Make stressed syllable unambiguous in a token; similar to Spanish orthographic
    stress rules, but applying only to the last syllable of polysyllabic words, as
    altering other contexts did not reliably improve metrical stress detection.
    """
    reps = {"a": "á", "e": "é", "o": "ó"}
    newtok = None
    for diph in g2s.UNACCENTED_DIPHTHONGS_GL:
        if re.search(rf"{diph}s?$", tok.lower()):
            if not re.search(r"[áéíóú]", tok.lower()):
                newdiph = diph
                for key, value in reps.items():
                    newdiph = re.sub(key, value, newdiph)
                newtok = tok.replace(diph, newdiph)
    if newtok is not None and newtok != tok:
        utils_logger.debug(f"Disamb Stress: [{tok}] to [{newtok}] context [{"".join(syl_list)}]")
        return newtok
    return tok


def detokenize(tokens: list, sep=' ') -> str:
    opening_punct = {'¡', '¿', '(', '[', '{', '«', '„'}
    closing_punct = {'!', '?', '.', ')', ']', '}', '»', '...'}

    result = []
    for token in tokens:
        if token in opening_punct:
            # attach to next word, so store as pending prefix
            result.append(token)
        elif token in closing_punct or token in {',', ';', ':'}:
            # attach to previous word (no space before)
            if result:
                result[-1] += token
            else:
                result.append(token)
        else:
            # check if last token was an opening punctuation mark
            if result and result[-1] in opening_punct:
                # merge with previous (opening punct)
                result[-1] = result[-1] + token
            else:
                result.append(token)
    return sep.join(result)


def destress_possessives(txt: str, syllabified=True) -> str:
    """
    Remove stress marks from possessive pronouns (tú, mí, sí, él, etc.) in a text.

    Args:
        txt (str): The input text.
        syllabified (bool): Whether the text is syllabified. If True, it assumes
            that the stress mark is prefixed to the syllable.

    Returns:
        str: The text with destressed possessive pronouns.
    """
    if syllabified:
        # In syllabified text, the stress mark is prefixed to the syllable
        txt = re.sub(r"\b['](séus?)\b", r"\1", txt, flags=re.I | re.U)
        txt = re.sub(r"\b[']([nv])-ós-([oa]s?)\b", r"\1-os-\2", txt, flags=re.I | re.U)
    else:
        # In non-syllabified text, the stress mark is on the vowel
        txt = re.sub(r"\b(séus?|[nv]ós[oa]s?)\b", lambda m: destress_word(m.group(0)), txt, flags=re.I | re.U)
    return txt