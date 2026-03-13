# Metrical annotation criteria for Galician

## Monosyllables and other items where there is variation regarding stress

- **"beira do"**: We annotate it as unstressed: *beira do morto ninguén se achega* (Lamas Carvajal, "Á memoria do ilustre poeta gallego Francisco Añón")
- **"cada"**: We annotate as unstressed, in a parallel to Spanish: TNT §168f "diferencias regionales con predominancia de forma átona" *cada día está más alto*
- **"indefinite article"** "un", "unha": Stressed, following Carvalho Calero (CC) p. 74 "El artículo determinado es proclítico. El indeterminado es tónico". 
- **"logo que"**: CC p. 73 preposiciones y conjunciones generalmente proclíticas
	- *logo que o paso apretei* (Añón, "O magosto")
- **"máis"**: in **19th text**, it sometimes bears an accent mark whether it's an adverb or not, so the accent is not a reliable indicator of stress:
	- *Poida ser que outra persoa / máis que ela de confianza / non teña e de por forza*: Tagged as unstressed, see CC, p. 74: «"Máis" [..] y "menos" [...] son tónicas cuando hacen el oficio de una conjunción, enlazando términos análogos de una frase.» The example above is not this exact case, but "máis" does behave more closely to a conjunction than to an adverb
- **possessive after demonstrative**: Unstressed
  - *Pasa, eses teus luceiros apagando* (Lamas Carvajal, "Ben chegado")
  - De_a-'quel teu sus-pi-'rar (CG)
- **postposed possesives**: We annotate as stressed:
	- *Sosténdome, cos brazos seus me enlaza*: We annotate "seus" as stressed
	- *So-'an-do o_a-'tru-xo 'meu*. We annotate "meu" as stressed
- **proclitic after preposition**: We annotated as stressed, see below examples
	- *puxo pra lle sopricar* 1 4 7
	- *Pra lles ir a arrimar outra tolena* 2 3 6 7 10
	- *De nos habilitar traballo a todos* 2 6 8 10
    - *'To-das 'tres sin 'me 'dar re-sul-'ta-do* 1 3 5 6 9
- **"segundo"** stressed as a preposition (not just as an ordinal), CC p. 73
- **"tal"**: We annotate it as stressed for a parallel with Spanish, see TNT §169, RAE átonas
	- however, we annotate as unstressed when it is a conjunction meaning "like", "as" (*Tal a filla de Catilio*, Saco e Arce, "Santa Eufemia")
- **"tan"**:
	- TNT p 192 (§169) *tan* es débil *tan alto como las nubes*, we annotate as unstressed in a parallel with Spanish
	- RAE https://www.rae.es/ortograf%C3%ADa/palabras-%C3%A1tonas tan is unstressed
	- TNT §169 adverbs: *tan* is unstressed, *tal* is stressed, so is *el cual*
- **"xunto de"**: We annotate as unstressed
	- *xunto de min non virás* (Labarta, incipit "Soíño no mundo")
	- *xunto dela os paxariños* (CG2 18-II, p. 95)
	- *e xunt'òn outeiro* (Labarta, incipit "Soíño no mundo")
- **interjections**: for *oh*, *ou* and similar, we annotate stressed in agreement with DiPr.

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

(work in progress as more generalizations emerge)

We annotate these metaplasms: synalepha, dialepha, syneresis and dieresis. When stress shifts because of metaplasms, we annotate stress in the metrically stressed syllable. We're not handling cases of rhythmic destressing/extra stressing, which remain a minority.

An example of the type of destressing we're not annotating is given in Caparrós' description of Spanish metrics, as a possible analysis for Bécquer's *yo soy ardiente / yo soy morena / yo soy el símbolo / de la pasión*. Here, to obtain a ternary rhythm, it would be possible to destress *soy* in all lines and add an extra stress to lexically unstressed preposition *de* in the last line.

Other metaplasms occur in Galician (see RF), but they are represented orthographically, and metrical stress detection takes them into account based on the orthographic representation, so no extra annotation is needed. For instance, epenthesis in "voo" (flight) written as "voxo", to make it clear that two syllables are needed metrically, like in Pondal's *te leva o voxo constante*, or apheresis in Rosalía's *Ña muller, pilla esa roca*, where "miña" apperas as "ña". 

## References

- Caparrós = Domínguez Caparrós, J. (2010). *Métrica y Poética. Bases para la fundamentación de la métrica en la teoría literaria moderna*. Madrid: UNED.
- CC = Carballo Calero, R. (1966) *Gramática elemental del gallego común*. Vigo: Galaxia.
- CG = de Castro, Rosalía (1863). *Cantares Gallegos* \[1st ed\]. Vigo: Compañel.
- DiPr = Regueira (dir.) Dicionario de Pronunica da Lingua Galega. https://ilg.usc.es/pronuncia/
- CG2 = de Castro, Rosalía (1872). *Cantares Gallegos* \[2nd ed\]. Madrid: Leocadio López.
- FN = de Castro, Rosalia (1880). *Follas Novas*. Habana: La Propaganda Literaria.
- RAE átonas: https://www.rae.es/ortograf%C3%ADa/palabras-%C3%A1tonas
- RF = Rodríguez Fer, C. (1991). *Arte literaria*. Edicións Xerais.
- TNT = Navarro Tomás, T. (1991) \[25th ed\]. *Manual de pronunciacion española*. Madrid: CSIC.
