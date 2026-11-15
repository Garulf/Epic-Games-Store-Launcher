from __future__ import annotations

import webbrowser
from typing import Iterator

from pyflowlauncher import Plugin, Result
from pyflowlauncher.string_matcher import string_matcher

import egs

ICON = "icon.png"

plugin = Plugin()


@plugin.on_method
def launch(namespace: str, catalog_id: str, app_name: str) -> None:
    webbrowser.open(egs.launch_uri(namespace, catalog_id, app_name))


def game_result(game: egs.Game, score: int) -> Result:
    return Result(
        title=game.display_name,
        subtitle=game.exe_path,
        icon=game.exe_path,
        score=score,
    ).add_action(launch, [game.catalog_namespace, game.catalog_item_id, game.app_name])


def match_score(query: str, game: egs.Game) -> int:
    match = string_matcher(query, game.display_name)
    return int(match.score) if match.matched else 0


@plugin.on_method
def query(query: str) -> Iterator[Result]:
    try:
        games = egs.get_games(egs.manifests_dir())
    except FileNotFoundError:
        yield Result(title="Unable to locate Epic Games Launcher", icon=plugin.launcher.icons.warning or ICON)
        return
    for game in games:
        if not game.incomplete_install:
            yield game_result(game, match_score(query, game))
