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


# Distribution to use for weights
from scipy.stats import poisson

# Random choice function fnrom Numpy
from numpy.random import choice

# This will help make generating weights faster later
from itertools import groupby


# The input file will be in Yaml
import yaml


"""
NEW FUNCTION DEFINITIONS
"""

def poisson_weights(length, mu=0.3)->list:
    """
    Returns a list of weights according to a Poisson distribution with
    the mu value for the distribution as an optional argument.

    The length parameter is just an integer that will come from 
    things like len(consonants)

    int, (float) -> [floats]
    """
    rv = poisson(mu)
    weights = [rv.pmf(i) for i in range(length)]
    return weights


def choose_poisson(strings, mu=0.3)->str:
    """
    Chooses an element from a list of strings using a Poisson distribution.
    The Poisson distribution is from Scipy and choice is from Numpy.
    """
    weights = make_poisson_weights(len(strings), mu)
    return choice(strings, 1, weights)[0]


def make_syllable(phonology)->str:
    """
    Builds a syllable according to a distribution of syllable structures
    taking each character in the string as a label.
    """
    phono = phonology
    syls = phono['syllables']['vals'] # Get list of syllable structures
    syl_mu = phono['syllables']['mu'] # Get mu value for choosing structure

    s_weights = poisson_weights(len(syls), syl_mu) # Make list of weights
    syl_struct = choice(syls, 1, s_weights)[0] # Our chosen syllable structure

    elements = phono['elements'] # Elements: C, V, etc.

    # Create dictionary of weights indexed by unique members of elements
    weights = {}
    # Here we extract every unique element of the syllable structure string
    unique = ''.join(k for k, g in groupby(sorted(syl_struct)))
    # Go through those unique elements to create a weights dictionary
    for u in unique:
        l = len(elements[u]['vals'])
        m = elements[u]['mu']
        weights[u] = poisson_weights(l, m)

    # Choose an element from each list of element vals according to the weights
    syl_out = ''
    for s in syl_struct:
        syl_out += choice(elements[s], 1, weights[s])
    return syl_out


def make_word(phonology, num_syllables)->str:
    """
    Use the syllable-building function above to construct words
    """
    word = ''
    for i in range(num_syllables):
        word += make_syllable(phonology)
    return word


# Try it out!
@begin.start # Entry point when run from console
def run(num_words=1, num_syllables=1, file='')->str:
    output = ''
    # Create the phonology, grabbing from file if specified
    if len(file) > 0:
        phonology = yaml.load(open(file, 'r'))
    else:
        phonology = { 'language': 'Hrau',

                    'syllables': {
                        'vals':   ['CV', 'CD', 'IAV', 'CVF', 'D', 'V', 'CDF', 
                                    'IAD', 'CVOF', 'IADF', 'CDOF', 'IAVF', 
                                    'IAVO', 'IADO', 'IAVOF', 'IAODOF'],
                        'mu': 0.3},

                    'elements': {
                        'C': {  'vals': 
                                ['k', 't', 'r', 'n', 's', 'h', 'l', 'f', 'm',
                                 'y', 'j', 'p', 'w'],
                                'mu': 0.3},

                        'V': {  'vals': ['i', 'u', 'o', 'e', 'a'],
                                'mu': 0.3},

                        'D': {  'vals': ['ei', 'oi', 'ai', 'uo', 'ou', 'au'],
                                'mu': 0.5},

                        'I': {  'vals': ['k', 't', 's', 'n', 'h', 'f', 'p', 
                                        'm', 'j'],
                                'mu': 0.5},

                        'A': {  'vals': ['y', 'r', 'w'],
                                'mu': 0.3},

                        'F': {  'vals': ['n', 's', 'r', 'm'],
                                'mu': 0.5},

                        'O': {  'vals': ['i', 'h', 'u'],
                                'mu': 0.2}
                    }
                }
    # Create the words!
    for w in range(num_words):
        word = make_word(phonology, num_syllables)
        output += word
        output += '\n'
    return output
