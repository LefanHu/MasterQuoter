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

    def fetch_quote(self, server_id, quote_id):
        """Message id of quote is passed to function, which then returns the quote dict"""
        data = self.read_json()

        server = self.get_server(server_id, data)
        for member in server["members"]:
            for quote in member["quotes"]:
                if quote["message_id"] == quote_id:
                    return quote
        return None

    def from_user(self, user_id: Member.id, server_id=None):
        data = self.read_json()

        quotes = []
        if not server_id:  # fetch quotes from all servers
            for server in data["guilds"]:
                member = self.get_member(user_id, server)
                quotes += member["quotes"]
            return quotes
        else:  # fetch from specific server
            server = self.get_server(server_id, data)
            if not server:
                return []
            member = self.get_member(user_id, server)
            if not member:
                return []

            return member["quotes"]

    def from_server(self, server_id):
        data = self.read_json()

        quotes = []
        server = self.get_server(server_id, data)

        if not server:
            return []

        for member in server["members"]:
            quotes += member["quotes"]

        return quotes

    # returns server from quotes.json
    def get_server(self, guild_id: int, data):
        guild_id = int(guild_id)
        if data == None:
            print(f"Adding server {guild_id}")
            return None
        for server in data["guilds"]:
            if server["guild_id"] == guild_id:
                return server
        return None

    # returns member from quotes.json when passed server from quotes.json
    def get_member(self, user_id: int, server_data):
        user_id = int(user_id)
        if server_data == None:
            return None
        for member in server_data["members"]:
            if member["user_id"] == user_id:
                return member
        return None

    def getenv(self, variable_name):
        return os.getenv(f"{variable_name}")

    def is_image(self, filename):
        if any(filename.lower().endswith(image) for image in self.image_types):
            return True

    def file_name(self, file):
        return os.path.basename(file)