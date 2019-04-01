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


# Prase command line arguments
import argparse

args_parser = argparse.ArgumentParser(description='Generate random words.')

args_parser.add_argument('w', type=int, nargs='?', default=1,
    help='number of words to generate')

args_parser.add_argument('s', type=int, nargs='?', default=1,
    help='number of syllables per word')

args_parser.add_argument('file', type=float, nargs='?', default='', 
    help='filename to read, defaults to empty string')

args = args_parser.parse_args()



# Get command line arguments for number of words and syllables per word
w, s = args.w, args.s

# Create the phonology. Grab the file argument if possible
phonology = {}

if len(args.file) > 0:
    phonology = yaml.load(open(args.file, 'r'))
else:
    phonology = { 'language': 'Hrau',

                'syllables': {
                    'vals':   ['CV', 'CD', 'IAV', 'CVF', 'D', 'V', 'CDF', 
                                'IAD', 'CVOF', 'IADF', 'CDOF', 'IAVF', 'IAVO', 
                                'IADO', 'IAVOF', 'IAODOF'],
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


def make_syllable(phonology, mu=0.3)->str:
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


"""
OLD FUNCTION DEFINITIONS
"""

def old_choose_phoneme(phonemes, mu=0.3)->str:
    """
    Choose random phonemes using a Poisson distribution as weights.
    Note that this is also used to choose syllable structures.

    We are using the probability mass function of the Poisson 
    distribution to generate an array of floats that is equal in 
    length to the array of strings we receive as input. THese then 
    work as the weights that we use to randomly choose a phoneme
    from the list of strings consumed as the first input variable.

    [strings], float -> string
    """
    rv = poisson(mu)
    weights = [rv.pmf(i) for i in range(len(phonemes))]
    return choice(phonemes, 1, weights)[0]


def old_make_syllable(elements, mu=0.3)->str:
    """
    Parse syllable structures and replace with random phonemes.
    This goes through a list of syllable structures derived from 
    the dictionary's S value and then replaces each character in 
    the string with an element from the list of phonemes that
    corresponds to the character in the syllable structure.

    dictionary, float -> string
    """
    structure = list(choose_phoneme(elements['S']))

    # Pull list of mu values

    output = ""
    for st in structure:
        output += choose_phoneme(elements[st], mu)
    return output


def make_word(elements, num_syllables, mu=0.3)->str:
    """
    This is a short function that uses a list comprehension
    to assemble a word built from syllables created 
    with make_syllable() above.

    dictionary, int, float -> string
    """
    word = [make_syllable(elements, mu) for i in range(num_syllables)]
    return "".join(word)
    

def make_vocab(elements, num_words, num_syllables, mu=0.3)->list:
    """
    This function spits out a list of strings, where each
    element is generated using make_word, which will later be
    printed out or sent to a file with linebreaks added.

    dictionary, int, int -> [strings]
    """
    vocab = [make_word(elements, num_syllables) for i in range(num_words)]
    return vocab


# Try it out!
w, s, mu = args.w, args.s, args.mu

words = make_vocab(elements, w, s, mu)

words_output = "\n".join(words)

print(words_output)