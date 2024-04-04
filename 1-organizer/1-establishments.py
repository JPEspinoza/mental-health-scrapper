"""
Adds the establishments to the database
"""

import pandas as pd
import re
import sqlite3
from clean import clean_string
from unidecode import unidecode

conn = sqlite3.connect("../data/db.sqlite3")
cursor = conn.cursor()

# wipe db
cursor.execute('DELETE FROM report')
cursor.execute('DELETE FROM establishment')

# load the file with the addresses
addresses = pd.read_csv('../data/establishments/establishments.csv', sep=';', index_col=0)
addresses = addresses[["Nombre Oficial", "Dirección", "Número", "Nombre Comuna", "Nombre Región", "LATITUD      [Grados decimales]", "LONGITUD [Grados decimales]"]]
addresses.dropna(inplace=True)

# clean 
addresses["Nombre Oficial"] = addresses["Nombre Oficial"].apply(clean_string)
addresses["Nombre Comuna"] = addresses["Nombre Comuna"].apply(clean_string)

# replace commas with dots
addresses['LATITUD      [Grados decimales]'] = addresses['LATITUD      [Grados decimales]'].apply(lambda x: re.sub(',', '.', x))
addresses['LONGITUD [Grados decimales]'] = addresses['LONGITUD [Grados decimales]'].apply(lambda x: re.sub(',', '.', x))

# insert 
for address in addresses.iterrows():
    name = address[1]['Nombre Oficial']
    street = address[1]['Dirección'] + ', ' + address[1]['Número'] + ', ' + address[1]['Nombre Región']
    latitude = address[1]['LATITUD      [Grados decimales]']
    longitude = address[1]['LONGITUD [Grados decimales]']

    try:
        # ensure that they are floats, some say 'No aplica' which we dont care about
        latitude = float(latitude)
        longitude = float(longitude)
    except:
        latitude = None
        longitude = None

    comuna = address[1]['Nombre Comuna']
    cursor.execute('SELECT id FROM commune WHERE name LIKE ?', (comuna,))
    comuna_id = cursor.fetchone()
    comuna_id = comuna_id[0]

    cursor.execute("INSERT INTO establishment (name, address, lat, lon, commune_id) VALUES (?, ?, ?, ?, ?)", (name, street, latitude, longitude, comuna_id))
    
conn.commit()