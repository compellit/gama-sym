# Metrical annotation guidelines for Galician

## Monosyllables and other items that require a decision about stress

- **indefinite article** "un", "unha": CC p. 74 "El artículo determinado es proclítico. El indeterminado es tónico". 
- **"tal"**: put it as stressed to have it parallel with Spanish, see TNT §169, RAE átonas
	- however, unstressed as a conjunction meaning "like", "as" ("Tal a filla de Catilio", Saco e Arce, "Santa Eufemia")
- **"tan"**:
	- tnt p 192 (§169) "tan" es débil "tan alto como las nubes"
	- rae https://www.rae.es/ortograf%C3%ADa/palabras-%C3%A1tonas tan is unstressed
	- TNT §169 adverbs: "tan" is unstressed, "tal" is stressed, "el cual" same thing
- **"segundo"** as a preposition: stressed, CC p. 73
- **"beira do"**: Decided to have it as unstressed "beira do morto ninguén se achega" (Lamas Carvajal, "Á memoria do ilustre poeta gallego Francisco Añón")
- **"xunto de"**: Have it as unstressed
	- "xunto de min non virás" (Labarta, incipit "Soíño no mundo")
	- "xunto dela os paxariños (CG 2 - 60)
	- "e xunt'òn outeiro" (Labarta, incipit "Soíño no mundo")
- **"logo que"**: CC p. 73 preposiciones y conjunciones generalmente proclíticas
	- "logo que o paso apretei" (Añón, "O magosto")
- **cada**: TNT §168f diferencias regionales con predominancia de forma átona "cada día está más alto"

- **postposed possesives**:
	- Sosténdome, cos brazos seus me enlaza: "seus" will be marked as stressed
	- So-'an-do o_a-'tru-xo 'meu . Marking "meu" as stressed

- **proclitic after preposition**: I did it stressed, see below examples
	- puxo pra lle sopricar 1 4 7
	- Pra lles ir a arrimar outra tolena 2 3 6 7 10
	- De nos habilitar traballo a todos 2 6 8 10

- **"máis"** (stressed graphically in **19th text**, sometimes, whether it's an adverb or not)
	- "Poida ser que outra persoa / máis que ela de confianza / non teña e de por forza": Tagged as unstressed, see CC, p. 74: "Máis" [..] y "menos" [...] son tónicas cuando hacen el oficio de una conjunción, enlazando términos análogos de una frase. This is not the exact case, but it didn't look like a full adverb to me

## Items that are stressed or not depending on part of speech

### Interrogative vs. relative

- Phonologically stressed (interrogative) or not (relative) depending on part of speech.
- *Orthographically* all unaccented in current norm.
- However in **19th century text** orthography is whatever it is: sometimes accented, sometimes not, and regardless of phonological tonicity
- Examples:
	- que, quen, como (interrogative + verb | relative)
	- cal, onde, canto (interrogative + verb | relative)
	- cuanto (not current norm, but you do find this for "canto" in 19th cent. text

### Multiple enclitics

- "Núbraseme o corazón", (FN): Tagged 1 7, but 1 4 7 seems more natural rhythmically speaking


## General criteria

(work in progress)

We generally don't move far from lexical stresses and we're not handling cases of metrical destressing/extra stressing, which remain a minority:
  - An example of destressing is given in Caparrós, as a possible analysis for *yo soy ardiente / yo soy morena / yo soy el símbolo / de la pasión* destressing *soy* and extra stressing *de* to get a ternary rhythm.
  - This becomes too subjective (you need two annotators and a good agreement), and you can't really trace it back to orthographic stress. To evaluate a rule-based tool it is problematic. 

Only exception is as needed by acento estrófico:

```
Non toleo cando -> *Non / to- / *le- / o / *can-# / do
```
You need a metrical stress on \*can-do (even if it is an unstressed conjunction), because you can't have acento estrófico on *toleo*, so far from the line end. Besides, if you read this pausing at the line end ("without enjambment"), you need the stress there for reading.

## References

- CC = Gram Gallego común by Carballo Calero
- CG = Cantares Gallegos
- FN = Follas Novas
- RAE átonas: https://www.rae.es/ortograf%C3%ADa/palabras-%C3%A1tonas
- TNT = Navarro Tomás Pron Esp
