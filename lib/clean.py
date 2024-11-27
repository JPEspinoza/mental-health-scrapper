# string cleaning implementation
from unidecode import unidecode
import re

def clean_string(string: str):
    # strips all leading and trailing white spaces, replaces multiple spaces with a single space,
    # removes all quotes
    # removes all special characters
    # uppercases the string
    # remove parentheses and everything inside them

    string = re.sub(' +', ' ', unidecode(string).replace("'", "").replace('"', '').replace('-', '').replace('.', '').upper().split('(')[0].rstrip(' *').lstrip('* ')) 

    if string == 'COIHAIQUE':
        return 'COYHAIQUE'
    if string == 'PAIGUANO':
        return 'PAIHUANO'
    if string == "AISEN":
        return "AYSEN"
    if string == "MARCHIHUE":
        return "MARCHIGUE"
    
    return string