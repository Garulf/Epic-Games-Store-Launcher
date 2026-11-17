from __future__ import annotations

import webbrowser
from typing import Any, Iterable, Iterator, Tuple

from pyflowlauncher import Plugin, Result
from pyflowlauncher.string_matcher import string_matcher

import egs

ICON = "icon.png"
DEFAULT_SCORE_THRESHOLD = 10

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


def as_bool(value: Any, default: bool) -> bool:
    if isinstance(value, bool):
        return value
    if isinstance(value, str):
        return value.strip().lower() in {"1", "true", "yes", "on"}
    return default


def score_threshold() -> int:
    try:
        return int(plugin.settings.get("score_threshold", DEFAULT_SCORE_THRESHOLD))
    except (TypeError, ValueError):
        return DEFAULT_SCORE_THRESHOLD


def show_on_empty_query() -> bool:
    return as_bool(plugin.settings.get("show_on_empty_query"), default=True)


def scored_games(query: str, games: Iterable[egs.Game]) -> Iterator[Tuple[egs.Game, int]]:
    if not query:
        if show_on_empty_query():
            yield from ((game, 0) for game in games)
        return
    threshold = score_threshold()
    for game in games:
        score = match_score(query, game)
        if score > threshold:
            yield game, score


@plugin.on_method
def query(query: str) -> Iterator[Result]:
    try:
        games = egs.get_games(egs.manifests_dir())
    except FileNotFoundError:
        yield Result(title="Unable to locate Epic Games Launcher", icon=plugin.launcher.icons.warning or ICON)
        return
    installed = [game for game in games if not game.incomplete_install]
    for game, score in scored_games(query.strip(), installed):
        yield game_result(game, score)
