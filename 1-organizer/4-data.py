
import pandas as pd
import json
import sqlite3
from glob import glob
import os
from clean import clean_string

# files = os.listdir("../0-scrapper/responses/")
files = glob("../0-scrapper/responses/*-AttendanceByProfessional.json")

# open sqlite database
conn = sqlite3.connect("../data/db.sqlite3")
cursor = conn.cursor()

cursor.execute('DELETE FROM data')
conn.commit()

# load each file 
for path in files:
    with open(path) as f:
        data = json.load(f)

        # get column names
        variables = data["results"][0]["variables"]
        columns = []
        for variable in variables:
            columns.append(variable["label"])

        # get data
        data = data["results"][0]["data"]["valueList"]
        df = pd.DataFrame(data).T
        df.columns = columns

        # drop "Tipo" column
        df = df.drop(columns=["Tipo"])

        # set columns to int
        df["Total_Ambos_sexos"] = df["Total_Ambos_sexos"].astype(int)
        df["Año"] = df["Año"].astype(int)
        df["Profesional"] = df["Profesional"].astype(int)

        # get stringtable
        # map the "Profesional" column to the stringTable, the values in the column are the indexes of the stringTable
        # if there is no stringtble, the column already has the values
        try:
            stringTable = data["results"][0]["stringTable"]["valueList"]
            df["Profesional"] = df["Profesional"].map(lambda x: stringTable[x])
        except:
            pass
        
        # extract metadata from path
        filename = path.split("/")[-1]

        establishment = filename.split("-")[1]
        report = filename.split("-")[2].split(".")[0]

        # clean
        establishment = clean_string(establishment)

        # get report from database
        cursor.execute("SELECT id FROM report WHERE name=?", (report,))
        report_id = cursor.fetchone()[0]

        # get establishment from database
        try:
            cursor.execute("SELECT id FROM establishment WHERE name=?", (establishment,))
            establishment_id = cursor.fetchone()[0]
        except:
            print(f"Establishment not found: {establishment}")
            continue

        # insert data
        for index, row in df.iterrows():
            try:
                cursor.execute(
                    "INSERT INTO data (establishment_id, report_id, cohort, value, year) VALUES (?, ?, ?, ?, ?)", 
                    (establishment_id, report_id, row["Profesional"], row["Total_Ambos_sexos"], row["Año"]))
            except:
                print(f"Error inserting data: {establishment}, {report}, {row['Profesional']}, {row['Total_Ambos_sexos']}, {row['Año']}")
                exit()

        conn.commit()