# teretaka
Linguistics-oriented algorithmic music

The core of this is a program I created for generating words for language construction (conlanging) using statistical distributions.

This repository is intended to be an extension of that project into music.

The core of this is a weighed choice, where the weights are generated from the probability mass functions of the Zipf and Poisson distributions.

Seen from above, the word-generation algorithm is roughly:

- Consume a Yaml file listing the phoneme classes (vowel, fricative, etc) in the target language in decreasing order of frequency.
- Generate the weights for each phoneme list, and the syllable structure list, using the PMF with a Q value for tuning the drop-off.
- For each character in the chosen syllable structure, use a weighted choice to grab a phoneme from each list indexed by that character.
- Output a word, and repeat as needed to have a long list of candidate words.

This lets us, for example, randomly choose "CVN" from the syllable structures. We then grab a consonant from the list called C, then a vowel from V, and then a nasal from N.

The Yaml might look like this, for example:

```
language: Proto-Korokso
# This language is phonologically simple but phonotactically complex.
# Orthography modified here to keep it to one character per phoneme.
# In this instance C = <ch>, S = <sh>
syllables: 
  vals: [CN, CNC, CNRS, SRN, VRS, CNRSR, SRSN, SRVN, SRSNC, SRSRN, SRSNRS, 
          CNRSR, SRNSRS, SRSRVNC, CVN]
  q: 0.3
elements:
  C: # Consonants
    vals: [k, s, r, h, t, S, y, C]
    q: 0.8
  S: # Stops
    vals: [k, t]
    q: 0.99
  R: # Sonorants except for /y/ and /h/
    vals: [s, r, S, C]
    q: 0.8
  N: # Syllable nuclei, including vowels and syllabic consonants
    # To reduce ambiguity, we use <R> for syllabic /r/, <H> for /h/, <F> for /S/, and /Q/ for /s/
    vals: [o, u, e, R, Q, i, H, F]
    q: 0.3
  V: # Vowels Only
    vals: [o, u, e, i]
    q: 0.9
```

Invocation goes like:
```
$ python3 main.py --words 10 --syllables 2 --file proto-korokso.yaml
```

This will output 10 words into the terminal that are 2 syllables each. For example:

```
Proto-Korokso language: 10 words of 2 syllable(s) each.
CirksSFh
SHrkskskCeuS
SQskrtrekSk
SiykroH
kCtSotCeo
kQCtSH
kSkruirtCkSR
krtHkskHt
krtukStH
trtrosRC
```

Look weird? That's because this language is supposed to have tons of consonants in a row! 

We're creating fantasy and sci-fi languages here, so weird is _expected_. Glory in it.

Copyright Brien Southward 2020
