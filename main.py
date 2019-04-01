"""
This is a tool that can take in lists of consonants and vowels (or other
sets of symbols) and randomly generate words based on them according to
a mathematical distribution, in this case Zipfian since that is common
in natural language data.

Inputs: 
number of words to generate (int, mandatory)
number of syllables per word (optional int, defaults to 1)
mu value for Poisson distribution (optinal float, defaults to 0.3)

Output: linebreak-separated list of generated words

TO DO: add third optional input for desired first letter of word

int, (int), (float) -> [strings]
"""

# Distribution to use for weights
from scipy.stats import poisson

# Random choice function fnrom Numpy
from numpy.random import choice

# Standard module, a parser for command-line arguments
import argparse

args_parser = argparse.ArgumentParser(description='Generate random words.')

args_parser.add_argument('w', type=int, nargs='?', default=1,
    help='number of words to generate')

args_parser.add_argument('s', type=int, nargs='?', default=1,
    help='number of syllables per word')

args_parser.add_argument('mu', type=float, nargs='?', default=0.3, 
    help='mu value for the Poisson distribution, defaults to 0.3')

args = args_parser.parse_args()

"""
PHONEMIC VARIABLES

Later I will write a parser or domain-specific language that allows for
a standard text input for all of this information. For now, these are
defined at this scope and would be changed on a per-language basis.

Here we define the sets of characters we are using to represent the phonemes
in the language. The elements of the lists can be more than one character
if the language has a finite set of permitted diphthongs, rhymes, etc. 
Each array should be ordered from most frequent phoneme to least frequent. 
This is becausevwe generate an equal-length array of floats as weights for 
randomly selecting an element from each of these lists.
"""

# Consonants permitted at syllable onset when unaccompanied
consonants = ['k', 't', 'r', 'n', 's', 'h', 
            'l', 'f', 'm', 'y', 'j', 'p', 'w']

# Consonants permitted before accompaniments
initials = ['k', 't', 's', 'n', 'h', 'f', 'p', 
            'm', 'j']

# These are the consonants allowed to form the second element in clusters
accompaniments = ['y', 'r', 'w']

# Vowels that occur as single syllable nuclei
vowels = ['i', 'u', 'o', 'e', 'a']

# Diphthongs, which in this language cannot occur together with 
# offglides or with ccompaniments
diphthongs = ['ei', 'oi', 'ai', 'uo', 'ou', 'au']

# Consonants peritted at the ends of syllables
finals = ['n', 's', 'r', 'm']

# These are the permitted offglides from vowels: two semivowels and /h/
# For clarity of orthography, /w/ and /y/ are written <u> and <i> here
offglides = ['i', 'h', 'u']

# Permitted syllable structures. These use one-letter abbreviations
# of the names of the lists above.
# Note this is also in descending order of frequency!
syllables = ['CV', 'CD', 'IAV', 'CVF', 'D', 'V', 'CDF', 'IAD', 'CVOF', 
            'IADF', 'CDOF', 'IAVF', 'IAVO', 'IADO', 'IAVOF', 'IAODOF']

# All of the above then gets put into a dictionary. We will be using
elements = {'C': consonants,
            'I': initials,
            'A': accompaniments,
            'V': vowels,
            'D': diphthongs,
            'F': finals,
            'O': offglides,
            'S': syllables
           }


"""
Function declarations

These basically just compose on each other.
"""

def choose_phoneme(phonemes, mu=0.3)->str:
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


def make_syllable(elements, mu=0.3)->str:
    """
    Parse syllable structures and replace with random phonemes.
    This goes through a list of syllable structures derived from 
    the dictionary's S value and then replaces each character in 
    the string with an element from the list of phonemes that
    corresponds to the character in the syllable structure.

    dictionary, float -> string
    """
    structure = list(choose_phoneme(elements['S']))
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