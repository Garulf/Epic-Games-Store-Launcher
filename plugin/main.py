import webbrowser
from difflib import SequenceMatcher as sm
from flox import Flox, ICON_WARNING

import egs

def match(query, game_name):
    return int(sm(lambda x: x==" " or x=="-", query.lower(), game_name.lower()).ratio() * 100)

class EpicGamesStoreLauncher(Flox):

    def query(self, query):
        try:
            games = egs.get_games()
            for game in games:
                score = match(query, game.display_name)
                if (score > 10 or query == '') and not game.b_is_incomplete_install:
                    self.add_item(
                        title=game.display_name, 
                        subtitle=str(game.full_exe_path()),
                        icon=str(game.full_exe_path()),
                        method=self.launch,
                        parameters=[game.catalog_namespace, game.catalog_item_id, game.app_name],
                        score=score
                        )
        except (FileNotFoundError):
            self.add_item(
                title='Unable to locate Epic Games Launcher',
                icon=ICON_WARNING
                )

    def context_menu(self, data):
        pass

    def launch(self, namespace, catalog_id, app_name):
        uri = f'com.epicgames.launcher://apps/{namespace}%3A{catalog_id}%3A{app_name}?action=launch&silent=true'
        webbrowser.open(uri)

if __name__ == "__main__":
    EpicGamesStoreLauncher()
