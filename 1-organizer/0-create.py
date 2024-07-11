"""
inserts the data into the database
main: schema
    + tables
        commune: table
            + columns
                id: integer NN
                name: TEXT NN
                geometry: BLOB NN
                region: TEXT NN
                province: TEXT NN
                population: TEXT NN
            + keys
                commune_pk: PK (id)
        establishment: table
            + columns
                id: integer NN
                name: text NN
                address: text NN
                lat: REAL
                lon: real
                commune_id: integer NN
            + keys
                establishment_pk: PK (id)
            + foreign-keys
                establishment_commune_id_fk: foreign key (commune_id) -> commune[.commune_pk] (id)
        report: table
            + columns
                id: integer NN
                name: text NN
                description: text NN
            + keys
                report_pk: PK (id)
        data: table
            + columns
                id: integer NN
                report_id: integer NN
                year: integer NN
                cohort: text NN
                value: integer NN
                commune_id: integer NN
                establishment_id: integer
                establishment: text NN
            + keys
                data_pk: PK (id)
            + foreign-keys
                data_commune_id_fk: foreign key (commune_id) -> commune[.commune_pk] (id)
                data_establishment_id_fk: foreign key (establishment_id) -> establishment[.establishment_pk] (id)
"""

import sqlite3

# connect to the database
conn = sqlite3.connect("main.db")
cursor = conn.cursor()

# create the database
cursor.execute("""
    CREATE TABLE IF NOT EXISTS commune (
        id INTEGER PRIMARY KEY,
        name TEXT NOT NULL,
        geometry BLOB NOT NULL,
        region TEXT NOT NULL,
        province TEXT NOT NULL,
        population TEXT NOT NULL
    )
""")

cursor.execute("""
    CREATE TABLE IF NOT EXISTS establishment (
        id INTEGER PRIMARY KEY,
        name TEXT NOT NULL,
        address TEXT NOT NULL,
        lat REAL,
        lon REAL,
        commune_id INTEGER NOT NULL,
        FOREIGN KEY (commune_id) REFERENCES commune (id)
    )
""")

cursor.execute("""
    CREATE TABLE IF NOT EXISTS report (
        id INTEGER PRIMARY KEY,
        name TEXT NOT NULL,
        description TEXT NOT NULL
    )
""")

cursor.execute("""
    CREATE TABLE IF NOT EXISTS data (
        id INTEGER PRIMARY KEY,
        report_id INTEGER NOT NULL,
        year INTEGER NOT NULL,
        cohort TEXT NOT NULL,
        value INTEGER NOT NULL,
        commune_id INTEGER NOT NULL,
        establishment_id INTEGER,
        establishment TEXT NOT NULL,
        FOREIGN KEY (report_id) REFERENCES report (id),
        FOREIGN KEY (commune_id) REFERENCES commune (id),
        FOREIGN KEY (establishment_id) REFERENCES establishment (id)
    )
""")

# commit the changes and close the connection
conn.commit()
conn.close()