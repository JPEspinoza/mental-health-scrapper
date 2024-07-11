import requests
from communes import communes
import os
import json
import uuid

xCsrfToken = "123d6363-a63c-48be-b60f-31265cf865ff"
jSessionID = "91ED5BDD21C844EC147BA7B816F911F5.report-data-172-16-1-254"

# load the payloads
print("loading payloads")
class Report:
    def __init__(self, name: str, payload: str):
        self.name = name
        self.payload = payload
reports: list[Report] = []
files = os.listdir("payloads/")
for file in files:
    path = "payloads/" + file
    with open(path, "r") as f:
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

            try:
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

                # atrociously formatted nested json hell
                content = json.loads(response.text)["results"]["content"]
                results = json.loads(content)["results"][0]
            except Exception as e:
                unscraped += 1
                print(f"failed to scrape {path}: {e}")
                continue

            # extract
            try:
                data = results["data"]["valueList"]
            except Exception as e:
                unscraped += 1
                print(f"failed to scrape {path}: {e}")
                continue

            try:
                stringTable = results["stringTable"]["valueList"]
            except:
                stringTable = None

            report = {
                "commune": commune.name,
                "establishment": establishment,
                "report": report.name,
                "data": data,
                "stringTable": stringTable
            }

            # save the report
            with open(path, "w") as f:
                f.write(json.dumps(report, ensure_ascii=False))

            print(f"{path} saved successfully")

print("scrapping done")
print("unscraped reports: " + str(unscraped))
print("scrapped reports: " + str(sequence - unscraped))