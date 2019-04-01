"""
This is a tool that can take in lists of consonants and vowels (or other
sets of symbols) and randomly generate words based on them according to
a mathematical distribution, in this case Zipfian since that is common
in natural language data.

Inputs: 
- number of words to generate (integer, mandatory)
- number of syllables per word (optional integer, defaults to 1)
- filename of Yaml file (optional string, defaults to '' and renders Krau)

Output: 
- linebreak-separated list of generated words

TO DO: add another optional input for desired first letter of word.
This would require checking the first letter against the phonology, so we'll
need to include some exception handling.

int, (int), (string) -> print(strings)
"""


# Replaces starting point boilerplate with a decorator
import begin


# Distributions to use for weights
from scipy.stats import poisson, zipf

# Random choice function fnrom Numpy
from numpy.random import choice

# This will help make generating weights faster later
from itertools import groupby


# The input file will be in Yaml
import yaml


"""
NEW FUNCTION DEFINITIONS
"""

def poisson_weights(length, q=0.7)->list:
    """
    Returns a list of weights according to a Poisson distribution with
    the q value for the distribution as an optional argument.

    The length parameter is just an integer that will come from 
    things like len(consonants)

    int, (float) -> [floats]
    """
    q = q # relevant vs Zipf
    rv = poisson(q)
    weights = [rv.pmf(i) for i in range(length)]
    return weights


def zipf_weights(length, q=0.7)->list:
    """
    Alternative to the above using Zipf distribution.
    Note that this returns an array where the first element is 0,
    so we will be dropping that and adding to the index.

    int, (float) -> [floats]
    """
    length += 1 # dropping first value later
    shape = 1/q # scales inversely to Poisson
    return [zipf.pmf(i, shape) for i in range(length)][1:]


def add_weights_to_phonology(phonology, distro='zipf'):
    """
    This consumes a dictionary drawn from the Yaml specifying the
    langauge's phonology, and outputs a dictionary with added weights.
    """
    phono = phonology

    syls = phono['syllables']['vals'] # Syllable struture values
    syl_q = phono['syllables']['q']
    elements = phono['elements']

    if distro == 'poisson':
        weight_lifter = poisson_weights
    else:
        weight_lifter = zipf_weights

    # Add weights to dictionary for the syllable structures
    phono['syllables']['weights'] = weight_lifter(len(syls), syl_q)

    # Grab total set of unique characters in the syllable structures
    unique = ''.join(syls)
    unique = ''.join(k for k, g in groupby(sorted(unique)))

    # Add weights for each unique element appearing in the syl structs
    for u in unique:
        el_len = len(elements[u]['vals'])
        el_q = elements[u]['q']
        weights = weight_lifter(el_len, el_q)
        elements[u]['weights'] = weights

    phono['elements'] = elements
    return phono

def make_syllable(phonology)->str:
    """
    Builds a syllable according to a distribution of syllable structures
    taking each character in the string as a label.
    """
    # Get list of syllable structures and weights from the above
    syls = phonology['syllables']['vals'] 
    syl_weights = phonology['syllables']['weights']

    # Choose a syllable structure
    syl_struct = choice(syls, 1, syl_weights)[0]

    # Elements: C, V, etc.
    elements = phonology['elements'] 

    # Choose an element from each list of element vals according to the weights
    syl_out = ''
    for s in syl_struct:
        vs = elements[s]['vals']
        ws = elements[s]['weights']
        phone = choice(vs, 1, ws)[0]
        syl_out += phone
    return syl_out


def make_word(phonology, num_syllables, distro='zipf')->str:
    """
    Use the syllable-building function above to construct words
    """
    # Start by adding the weights to the phonology we've received
    phono = add_weights_to_phonology(phonology, distro)

    # Construct the word
    word = ''
    for i in range(num_syllables):
        word += make_syllable(phono)
    return word


# Try it out!
@begin.start # Entry point when run from console
def run(words='1', syllables='1', distribution='zipf', file='')->str:
    output = ''
    # Create the phonology, grabbing from file if specified
    if len(file) > 0:
        phonology = yaml.load(open(file, 'r'))
    else:
        phonology = yaml.load(open('hrau.yml', 'r'))

    # Create the words!
    for w in range(int(words)):
        word = make_word(phonology, int(syllables), distribution)
        output += word
        if w < int(words) - 1:
            output += '\n'
    outstring = phonology['language'] + ' language: ' + words + ' words'
    outstring += ' of ' + syllables + ' syllable(s) each.'
    print(outstring)
    print(output)