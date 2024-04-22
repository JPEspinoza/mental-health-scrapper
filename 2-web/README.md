# Mental health WebUI

This is a demo Flask webapp that shows the different interactive maps

The Flask app is dockerized and runs on port 9000

It automatically installs the requirements and loads the required data from the sqlite database at `../data`

## Running
Requirements:
- docker

From this folder, in a unix shell
```
docker compose up
```

Then open a browser and go to `http://localhost:9000`