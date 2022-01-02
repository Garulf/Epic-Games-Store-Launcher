import webbrowser
from flox import Flox

import egs

class EpicGamesStoreLauncher(Flox):

    def query(self, query):
        games = egs.get_games()
        for game in games:
            self.add_item(
                title=game.display_name, 
                subtitle=str(game.full_exe_path()),
                icon=str(game.full_exe_path()),
                method=self.launch,
                parameters=[game.catalog_namespace, game.catalog_item_id, game.app_name]
                )

    def context_menu(self, data):
        pass

    def launch(self, namespace, catalog_id, app_name):
        uri = f'com.epicgames.launcher://apps/{namespace}%3A{catalog_id}%3A{app_name}?action=launch&silent=true'
        webbrowser.open(uri)

if __name__ == "__main__":
    EpicGamesStoreLauncher()
