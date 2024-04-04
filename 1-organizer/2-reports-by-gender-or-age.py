"""
loads all the files and stores them in an sqlite database
"""

import pandas as pd
import json
import sqlite3
from glob import glob
from clean import clean_string

files = glob('../data/reports/MentalByAge*') + glob('../data/reports/MentalByGender*')

# open sqlite database
conn = sqlite3.connect("../data/db.sqlite3")
cursor = conn.cursor()

# wipe table
cursor.execute('DELETE FROM report')

# load each file 
for file in files:
    with open(file) as f:
        file = json.load(f)

        report = file['report']

        commune = file['commune']
        commune = clean_string(commune)

        establishment = file['establishment']
        establishment = clean_string(establishment)

        columns = file['columns']

        data = pd.DataFrame(file['data']).T
        data.columns = columns

        # store in database
        for index, row, in data.iterrows():
            year = row['year']
            for column in columns[1:]:
                # find commune
                commune_id = cursor.execute('SELECT id FROM commune WHERE name = ?', (commune,))
                commune_id = cursor.fetchone()[0]

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

                value = row[column]
                cursor.execute(
                    'INSERT INTO report (report, year, cohort, value, establishment, commune_id, establishment_id) VALUES (?,?,?,?,?,?,?)', 
                    (report, int(year), column, int(value), establishment, commune_id, establishment_id)
                )

conn.commit()
