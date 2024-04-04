"""
this script loads the EstablishmentByCommune json files and generates a typescript
array of constants for the commune names and their respective establishments
"""

import json
import os
import glob

# load the json files
files = glob.glob('data/EstablishmentsByCommune-*.json')

# load the json files
data = {}
for file in files:
    with open(file, 'r') as f:
        a = json.load(f)

        commune = a['commune']
        establishments = a['data']

        data[commune] = establishments

for key in data:
    commune = key
    establishments = data[key]
    print("{", end="")
    print(f"commune: '{commune}', establishments: {establishments}", end="")
    print("},", sep="")
