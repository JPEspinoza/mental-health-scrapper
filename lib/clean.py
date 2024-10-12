# string cleaning implementation
from unidecode import unidecode
import re

def clean_string(string):
    # strips all leading and trailing white spaces, replaces multiple spaces with a single space,
    # removes all quotes
    # removes all special characters
    # uppercases the string
    # remove parentheses and everything inside them

    return re.sub(' +', ' ', unidecode(string).replace("'", "").replace('"', '').replace('-', '').replace('.', '').upper().split('(')[0].rstrip(' *').lstrip('* ')) 
