import json
import os
from dotenv import load_dotenv


class File:
    def __init__(self):
        load_dotenv()

    def remove(self, path_to_file=None):
        if path_to_file is None:
            path_to_file = self.save_location

    def exists(self, path_to_file=None):
        if path_to_file is None:
            path_to_file = self.save_location
        return os.path.isfile(path_to_file) and os.path.getsize(path_to_file) > 0

    def write_json(self, data, filename):
        with open(filename, "w") as f:
            json.dump(data, f, indent=4)

    def read_json(self, filename=None):
        if filename == None:
            filename = os.getenv("SAVE_LOCATION")
        else:
            # print(f"{filename} exists = {self.file_exists(filename)}")
            if not self.exists(filename):
                with open(filename, "w") as f:
                    json.dump({}, f, indent=4)
                return {}
            with open(filename, "r") as f:
                data = json.load(f)
        return data

    def getenv(self, variable_name):
        return os.getenv(f"{variable_name}")

    def file_name(self, file):
        return os.path.basename(file)