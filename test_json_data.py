import json
from urllib.request import urlopen

# FUNCTION TO ADD TO JSON FILE
def write_json(data, filename="json_structure"):
    with open(filename, "w") as f:
        json.dump(data, f, indent=4)


data = json.load(urlopen("http://eu.battle.net/api/wow/realm/status"))

write_json(data)