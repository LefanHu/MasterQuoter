import json
import os
from dotenv import load_dotenv

from discord import Member


class File:
    def __init__(self):
        self.save_location = os.getenv("SAVE_LOCATION")
        self.image_types = ["png", "jpeg", "gif", "jpg"]
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
            filename = self.save_location
        else:
            if not self.exists(filename):
                with open(filename, "w") as f:
                    json.dump({}, f, indent=4)
                return {}

        with open(filename, "r") as f:
            data = json.load(f)

        return data

    def getenv(self, variable_name):
        return os.getenv(f"{variable_name}")

    def is_image(self, filename):
        if any(filename.lower().endswith(image) for image in self.image_types):
            return True

    def file_name(self, file):
        return os.path.basename(file)