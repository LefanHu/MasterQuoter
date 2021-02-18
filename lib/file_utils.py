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

    def fetch_quote(self, serverid, quoteid):
        """Message id of quote is passed to function, which then returns the quote dict"""
        pass

    def from_user(self, user_id: Member.id, server=None):
        data = self.read_json()

        quotes = []
        if not server:  # fetch quotes from all servers
            for server in data:
                for user in data[str(server)]:
                    if user == user_id:
                        quotes += data[str(server)][str(user_id)]["quotes"]
            return quotes
        else:
            try:  # fetch from specific server
                return data[str(server)][str(user_id)]["quotes"]
            except KeyError:
                return quotes

    def from_server(self, server_id):
        data = self.read_json()

        quotes = []
        for user in data[str(server_id)]:
            quotes += data[str(server_id)][str(user)]["quotes"]
        return quotes

    def getenv(self, variable_name):
        return os.getenv(f"{variable_name}")

    def is_image(self, filename):
        if any(filename.lower().endswith(image) for image in self.image_types):
            return True

    def file_name(self, file):
        return os.path.basename(file)