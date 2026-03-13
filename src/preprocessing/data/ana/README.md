# Vocabulary for text normalization

From Linguakit but adding some forms with clitics from the Apertium dictionary.

See https://github.com/citiususc/Linguakit/tree/master/tagger/gl/lexicon

May also try https://github.com/citiususc/Linguakit/tree/master/tagger/histgz/lexicon additionally.

## remove non-words from Linguakit dictionary

sed 's/ /\n/g' dicc.src | grep -Pv '^[A-Z0-9]{5,8}$'| grep -Pv '^[IVXLCDM]+$' | grep -Pv '^[0-9]+$' | sort | uniq

## Apertium inflected forms dictionary

It gives > 13 million forms, but can be filtered to remove some unlikely patterns.

git clone https://github.com/apertium/lttoolbox.git
git clone https://github.com/apertium/apertium.git
cd apertium-glg

Once you get it to compile:

lt-comp lr apertium-glg.glg.dix apertium-glg.glg.bin
lt-comp rl apertium-glg.glg.dix apertium-glg-gen.bin
lt-expand apertium-glg.glg.dix|sed 's/:.*//g' > apertium-glg-expanded.txt
sort apertium-glg-expanded.txt | uniq > apertium-glg-expanded-uniq.txt

Use this gzipped, it's huge.

## get forms with clitics from Apertium dictionary

All word-final

### llles?

grep -P 'lles?$' apertium-glg-expanded-uniq.txt | sort | uniq > new_vocab_gl/lles.txt

## mos / nos / vos / chos / llos and singular if applies

grep -P '(?:[mnv]|ll|ch)[oa]s?$' apertium-glg-expanded-uniq.txt | sort | uniq > new_vocab_gl/m@s-n@s-v@s-ch@s-ll@s.txt

### me / te / se

grep -P '[mts]e$' apertium-glg-expanded-uniq.txt | sort | uniq > new_vocab_gl/metese.txt

### some counts for the above

wc -l new_vocab_gl/*
   428319 new_vocab_gl/linguakit_dicc_src.txt
  1961887 new_vocab_gl/lles.txt
  2544750 new_vocab_gl/lolas.txt
   871719 new_vocab_gl/metese.txt
  3912160 new_vocab_gl/m@s-n@s-v@s-ch@s-ll@s.txt
  9718835 total

### merged

cat new_vocab_gl/* > new_vocab_gl.temp

sort new_vocab_gl.temp | uniq > new_vocab_gl.temp.uniq

## count comparison

### current

wc -l new_vocab_gl.temp.uniq 
9384349 new_vocab_gl.temp.uniq

### old

wc -l apertium-glg-expanded-uniq.txt 
13011702 apertium-glg-expanded-uniq.txt

## prune forms with clitic sequences that seem unlikely

grep -Pv '(llesnos?|llesvos?|vosnos?|nosvos?|voslles?|noslles?|volles?|nolles?|vonos?|volles?|nolles?|melles?|telles?|chenos?|chevos?|chelles?|cheme|chete|chese)$' new_vocab_gl.temp.uniq > new_vocab_less_clitics.txt

wc -l new_vocab_less_clitics.txt 
6756656 new_vocab_less_clitics.txt

