import winreg as reg
from winreg import HKEY_CURRENT_USER
import json
from pathlib import Path
import webbrowser

DEFAULT_EGS_KEY = r'SOFTWARE\Epic Games\EOS'

def camel_to_snake(s):
    return ''.join(['_'+c.lower() if c.isupper() else c for c in s]).lstrip('_')

def epic_games_manifests():
    with reg.OpenKey(HKEY_CURRENT_USER, DEFAULT_EGS_KEY) as key:
        return reg.QueryValueEx(key, "ModSdkMetadataDir")[0]

def get_games():
    games = []
    for manifest in Path(epic_games_manifests()).glob('**/*.item'):
        with open(manifest) as f:
            games.append(Game(json.load(f)))
    return games

class Game(object):

    def __init__(self, manifest):
        self.manifest = manifest
        for key, value in manifest.items():
            setattr(self, camel_to_snake(key), value)

    def full_exe_path(self):
        return Path(self.install_location).joinpath(self.launch_executable)

    def uri(self):
        return 'com.epicgames.launcher://apps/{self.catalog_namespace}:{self.catalog_item_id}:{self.app_name}?action=launch&silent=true'.replace(':', '%3A')

    def launch(self):
        webbrowser.open(self.uri)


# games = get_games()
# print(games[0].full_exe_path())