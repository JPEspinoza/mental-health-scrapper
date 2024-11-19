import requests
from lib.communes import communes
import os
# import simdjson as json
import json 
import uuid

xCsrfToken = "83b680f9-e183-479f-a91f-9d1926afd64f"
jSessionID = "13357EE8A03CA527651A262611440326.report-data-192-168-173-202"

# load the payloads
print("loading payloads")
class Report:
    def __init__(self, name: str, payload: str):
        self.name = name
        self.payload = payload

        # rescue the metadata stored inside the payload
        temp = json.loads(payload)
        self.family = temp["_type"]
        self.report = temp["_report"]
        try:
            self.misc = temp["_extra"]
        except:
            self.misc = None

reports: list[Report] = []
files = os.listdir("payloads/")
for file in files:
    path = "payloads/" + file
    with open(path, "r") as f:
        print(f"loading payload {file}")
        payload = f.read()
        reports.append(Report(file, payload))

# get an executor id
print("getting executor id")
url = "https://informesdeis.minsal.cl/reportData/executors"
response = requests.post(
    url, 
    headers = {
        "Content-Type": "application/vnd.sas.report.query+json",
        "x-csrf-token": xCsrfToken,
        "Cookie": "JSESSIONID=" + jSessionID
    },
)
executorID: str = response.json()["id"]

# main scrape
print("scraping")
sequence = 0
unscraped = 0

for commune in communes:
    for establishment in commune.establishments:
        for report in reports:

            # verify if the report already exists
            path = "responses/" + str(commune.name) + "-" + str(establishment) + "-" + report.name
            if os.path.exists(path):
                continue

            sequence += 1

            # replace the {1} in the payload with the establishment
            payload = report.payload.replace("{1}", establishment)

            # format the payload
            payload = json.loads(payload)

            # build url
            url = f"https://informesdeis.minsal.cl/reportData/jobs?indexStrings=true&embeddedData=true&wait=30" 
            url += "&executorId=" + executorID
            url += "&jobId=" + str(uuid.uuid4())
            url += "&sequence=" + str(sequence)

            # ask for the report
            response = requests.post(
                url,
                headers={
                    "content-type": "application/vnd.sas.report.query+json",
                    "x-csrf-token": xCsrfToken,
                },
                cookies={
                    "JSESSIONID": jSessionID
                },
                json = payload,
            )

            content = json.loads(response.text)["results"]["content"]

            content = json.loads(content)
            content["establishment"] = establishment
            content["commune"] = commune.name
            content["report"] = report.report
            content["family"] = report.family
            content["misc"] = report.misc

            content = json.dumps(content, ensure_ascii=False, indent=4)

            # save the report
            with open(path, "w") as f:
                f.write(content)
            
            print(f"{path} saved successfully")

print("scrapping done")
print("unscraped reports: " + str(unscraped))
print("scrapped reports: " + str(sequence - unscraped))