# this script checks all the responses in the folder `responses2` to verify they are valid

import os
import json

# get all the files in the folder
files = os.listdir("responses2")

invalid = 0
valid = 0

# iterate over all the files
for file in files:
    path = "responses2/" + file
    with open(path, "r") as f:
        response = f.read()
        data = json.loads(response)

        try:
            if(len(data["data"]) == 0):
                invalid += 1
            else: 
                valid += 1
        except:
            invalid += 1

print("invalid responses: " + str(invalid))
print("valid responses: " + str(valid))