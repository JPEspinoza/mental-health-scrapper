# mental health organizer

This projects takes the raw date scraped from DEIS by the scraper, an up-to-date list of the establishments, and inserts everything into a sqlite database

Tested under Python 3.12

All the scripts must be run sequentially in the order they are numbered

In particular, the report scripts are delicate. If one fails, all of them must be rerun.

## Running
From this folder, in a unix shell
```
# create a virtual environment
python3 -m venv venv 

# load the virtual environment
source venv/bin/activate

# install the requirements
pip install -r requirements.txt

# run the scripts
python 0-communes.py
python 1-establishments.py
python 2-reports-by-gender-or-age.py
python 3-reports-by-month.py
python 4-reports-by-professional.py
```