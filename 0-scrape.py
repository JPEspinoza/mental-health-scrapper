import requests
from lib.communes import communes
import os
import json 
import uuid

xCsrfToken = "194d7bff-3cf2-451c-aec8-014b76bf585b"
jSessionID = "00F57A9627E2B7BC28A5F15A6001CA2C.report-data-192-168-173-202"

# load the payloads
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

print("loading reports")
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

existing_responses = os.listdir("responses/")

for commune in communes:
    for establishment in commune.establishments:
        for report in reports:

            # verify if the report already exists
            filename = str(commune.name) + "-" + str(establishment) + "-" + report.name
            path = "responses/" + filename

            # if we already scrapped this check if it failed
            if(filename in existing_responses):
                f = open(path)
                data = json.load(f)

                if data["results"][0]["status"] == "failure":
                    # go ahead and download again
                    pass
                else:
                    # if it downloaded correctly skip it
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

            if(content["results"][0]["status"] == "failure"):
                raise Exception("failed to download " + path)

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