import os
import json

files =os.listdir("responses/")

bad = 0
good = 0

for file in files:
    f = open("responses/"+file, "r")
    data = json.load(f)

    if data["results"][0]["status"] == "failure":
        bad += 1
    else:
        good += 1
    
print(bad)
print(good)
