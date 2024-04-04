"""
loads all the files and stores them in an sqlite database
"""

import pandas as pd
import json
import sqlite3
from glob import glob
from clean import clean_string

files = glob('../data/reports/MentalByMonth*')

# open sqlite database
conn = sqlite3.connect("../data/db.sqlite3")
cursor = conn.cursor()

# load each file 
for file in files:
    with open(file) as f:
        file = json.load(f)
        report = file['report']

        commune = file['commune']
        commune = clean_string(commune)

        establishment = file['establishment']
        establishment = clean_string(establishment)

        commune_id = cursor.execute('SELECT id FROM commune WHERE name LIKE ?', (commune,))
        commune_id = cursor.fetchone()[0]

        month_order = file['month_order']

        # try to find the establishment
        try: 
            cursor.execute('''
            SELECT establishment.id
            FROM establishment
            JOIN commune on establishment.commune_id = commune.id
            WHERE establishment.name LIKE ? AND
                commune.id = ?''', 
                (establishment, commune_id)
            )
            establishment_id = cursor.fetchone()[0]
        except:
            establishment_id = None

        data = pd.DataFrame(file['data']).T
        data.columns = ['month', 'year', 'value']

        # remap months
        data['month2'] = data['month'].map({i: month for i, month in enumerate(month_order)})

        # if nan, replace with the original value
        # (sometimes instead of an id, the month is written as a string)
        data['month2'] = data['month2'].fillna(data['month'])

        for _, row, in data.iterrows():
            month = row['month2']
            year = row['year']
            value = row['value']

            cursor.execute(
                'INSERT INTO report (report, year, cohort, value, establishment, commune_id, establishment_id) VALUES (?,?,?,?,?,?,?)', 
                (report, int(year), month, int(value), establishment, commune_id, establishment_id)
            )


conn.commit()
