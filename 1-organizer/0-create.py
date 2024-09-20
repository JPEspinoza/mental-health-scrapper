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
create table data
(
    id               INTEGER            primary key,
    year             INTEGER,
    cohort           TEXT    not null,
    value            INTEGER not null,
    report_id        INTEGER not null   references report,
    commune_id       INTEGER not null   references commune,
    establishment_id INTEGER            references establishment,
    constraint data_unique
        unique (report_id, year, cohort, establishment_id, commune_id) on conflict replace
);
""")

# commit the changes and close the connection
conn.commit()
conn.close()