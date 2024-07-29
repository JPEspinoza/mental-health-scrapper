"""
inserts the data into the database

"""

import sqlite3

# connect to the database
conn = sqlite3.connect("../data/db.sqlite3")
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
        description TEXT
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