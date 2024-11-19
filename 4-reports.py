# inserts the reports into the database

import os
import json
import sqlite3

reports = os.listdir("payloads/")

conn = sqlite3.connect("db.sqlite3")
cursor = conn.cursor()

cursor.execute('DELETE FROM data')
cursor.execute('DELETE FROM report')

for report in reports:
    with open(f"payloads/{report}", "r") as f:
        payload = f.read()
        r = json.loads(payload)
        name = report.split(".")[0] # strip json

        description = r["_report"]
        category = r["_type"]
        try:
            misc = r["_extra"]
        except:
            misc = None

        cursor.execute(
            "INSERT INTO report (name, description, category, misc) VALUES (?, ?, ?, ?)", 
            (name, description, category, misc)
        )

conn.commit()