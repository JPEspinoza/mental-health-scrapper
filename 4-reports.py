# inserts the reports into the database

import os
import json
import sqlite3

reports = os.listdir("../0-scrapper/payloads/")

conn = sqlite3.connect("../data/db.sqlite3")
cursor = conn.cursor()

cursor.execute('DELETE FROM data')
cursor.execute('DELETE FROM report')

for report in reports:
    with open(f"../0-scrapper/payloads/{report}", "r") as f:
        payload = f.read()
        r = json.loads(payload)
        name = report.split(".")[0] # strip json
        try:
            description = r["_comment0"]
        except:
            description = None
        cursor.execute("INSERT INTO report (name, description) VALUES (?, ?)", (name, description))

conn.commit()