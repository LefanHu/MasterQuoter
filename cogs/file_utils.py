from discord.ext import commands
import json
import os
from dotenv import load_dotenv


class File(commands.Cog):
    def __init__(self, client):
        self.client = client
        self.save_location = os.getenv("SAVE_LOCATION")
        load_dotenv()

    def file_remove(self, path_to_file=None):
        if path_to_file is None:
            path_to_file = self.save_location

    def file_exists(self, path_to_file=None):
        if path_to_file is None:
            path_to_file = self.save_location
        return (
            os.path.isfile(self.save_location)
            and os.path.getsize(self.save_location) > 0
        )

    def write_json(self, data, filename):
        with open(filename, "w") as f:
            json.dump(data, f, indent=4)

    def get_env(self, variable_name):
        return os.getenv(f"{variable_name}")


def setup(client):
    client.add_cog(File(client))
    print(f"Cog 'file_utils' has been loaded")