
import pandas as pd
import simdjson
import sqlite3
from glob import glob
from clean import clean_string
import numpy as np

# silence pandas warnings about the pivot
pd.set_option('future.no_silent_downcasting', True)

# turn numpy int64 into int64 so that sqlite doesn't think its getting binary data
sqlite3.register_adapter(np.int64, int)

STRING_TABLE_INDEX = [
    "Controles remotos",
    "Glosa",
    "Diagnóstico/Factor de riesgo",
    "Diagnóstico/ Factor de riesgo",
    "Diagnóstico/Factor de Riesgo",
    "Tipo de taller",
    "Especialidad",
    "Mes",
    "Concepto",
    "Tipo",
    "Profesional",
    "Prestación",
    "Sustancia",
]

# all
files = glob("../0-scrapper/responses/Estación Central-Centro de Salud Familiar Las Mercedes*.json")
# files = glob("../0-scrapper/responses/Estación Central-Centro de Salud Familiar Las Mercedes-CovidKind.json")

# open sqlite database
conn = sqlite3.connect("../data/db.sqlite3")
cursor = conn.cursor()

cursor.execute('DELETE FROM data')

# counters
success = 0
no_data = 0
no_establishment = 0

# load each file 
for path in files:
    with open(path) as f:
        response = simdjson.load(f) # type: ignore

        # get column names
        variables = response["results"][0]["variables"]
        columns = []
        for variable in variables:
            columns.append(variable["label"])

        # get data
        try:
            data = response["results"][0]["data"]["valueList"]
        except:
            print("No data found")
            print(response)
            print(path)
            no_data += 1
            continue

        # cast everything to int
        for i in range(len(data)):
            for j in range(len(data[i])):
                try:
                    data[i][j] = int(data[i][j])
                except:
                    pass

        # organize data
        data = pd.DataFrame(data).T
        data.columns = columns

        # rename Año
        data.rename(columns={"Año": "year"}, inplace=True, errors="ignore")
        data.rename(columns={"Ano": "year"}, inplace=True, errors="ignore")

        # replace ~N with 0
        data.replace("~N", 0, inplace=True)
        data.replace(".", 0, inplace=True)

        # extract metadata from path
        # example: "Castro-Posta de Salud Rural Pid - Pid-AttendanceByAge.json"
        filename = path.split("/")[-1]
        commune = filename.split("-")[0]
        establishment = filename.split("-")[1]
        report = filename.split("-")[-1].split(".")[0]

        # get report from database
        try:
            cursor.execute("SELECT id FROM report WHERE name=?", (report,))
            report_id = cursor.fetchone()[0]
        except:
            print(f"Report not found!!!: {report}")
            print(filename)
            exit()

        # get commune from database
        try:
            commune = clean_string(commune)
            cursor.execute("SELECT id FROM commune WHERE name=?", (commune,))
            commune_id = cursor.fetchone()[0]
        except:
            print(f"Commune not found: {commune}")
            print(filename)
            exit()

        # get establishment, if not found ignore
        try:
            establishment = clean_string(establishment)
            cursor.execute("SELECT id FROM establishment WHERE name=?", (establishment,))
            establishment_id = cursor.fetchone()[0]
        except:
            print(f"Establishment not found: {establishment}")
            no_establishment += 1
            pass

        # get subset of STRING_TABLE_INDEX that are in the data
        # this has the list of columns that index the data
        index = list(set(STRING_TABLE_INDEX) & set(data.columns))

        # for reports with stringTables
        # this reports have a column with indexes that map to a stringTable
        # we need to map the indexes to the stringTable
        try:
            stringTable = response["results"][0]["stringTable"]["valueList"]

            # map indexes to stringTable
            data[index] = data[index].map(lambda x: stringTable[x])
        except:
            pass

        if("year" in data.columns):
            index_with_year = index + ["year"]
        else:
            index_with_year = index

        # melt dataframe for easy insertion
        data = pd.melt(data, id_vars=index_with_year, var_name="cohort", value_name="value")
        # fuse index columns
        data["cohort"] = data[index+["cohort"]].apply(lambda x: " - ".join(x), axis=1)
        # drop index columns, leave just cohort (and year)
        data.drop(index, axis=1, inplace=True)

        print(path)
        print(data)
        print()

        continue

        # insert data
        for index, row in data.iterrows():
            try:
                year = row["year"]
                cohort = row["cohort"]
                value = row["value"]
            except:
                print("Error extracting data")
                print(path)
                print(data)
                print(stringTable)
                exit()

            # insert data into db
            cursor.execute(
                "INSERT INTO data (establishment_id, report_id, commune_id, year, cohort, value) VALUES (?, ?, ?, ?, ?, ?)",
                (establishment_id, report_id, commune_id, year, cohort, value)
            )

        success += 1 

print(f"Success: {success}")
print(f"No data found: {no_data}")
print(f"No establishment found: {no_establishment}")

conn.commit()