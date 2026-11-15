import egs
import search
from conftest import manifest


def titles(results):
    return [result.title for result in results]


def test_empty_query_lists_installed_games(manifests, settings):
    assert titles(search.query("")) == ["Hades", "Just Cause 4", "Subnautica", "Transistor"]


def test_matching_game_scores_highest(manifests, settings):
    results = sorted(search.query("hades"), key=lambda result: result.score, reverse=True)

    assert results[0].title == "Hades"
    assert results[0].score > 0


def test_result_launches_through_the_epic_uri(manifests, settings, monkeypatch):
    (result,) = [result for result in search.query("hades") if result.title == "Hades"]
    opened = []
    monkeypatch.setattr(search.webbrowser, "open", opened.append)

    assert result.subtitle == "C:\\Program Files\\Epic Games\\Hades\\Hades.exe"
    assert result.icon == result.subtitle
    assert result.json_rpc_action == {
        "Method": "launch",
        "Parameters": ["hades-namespace", "hades-item", "Hades"],
        "DontHideAfterAction": False,
    }
    search.launch(*result.json_rpc_action["Parameters"])
    assert opened == ["com.epicgames.launcher://apps/hades-namespace%3Ahades-item%3AHades?action=launch&silent=true"]


def test_incomplete_installs_are_hidden(manifests, settings):
    manifests(manifest("Celeste", "Celeste", bIsIncompleteInstall=True))

    assert "Celeste" not in titles(search.query(""))


def test_missing_launcher_shows_a_warning(settings, monkeypatch):
    def missing():
        raise FileNotFoundError("SOFTWARE\\Epic Games\\EOS")

    monkeypatch.setattr(egs, "manifests_dir", missing)

    assert titles(search.query("")) == ["Unable to locate Epic Games Launcher"]


def test_query_is_registered_as_a_plugin_method(manifests, settings):
    import asyncio

    response = asyncio.run(search.plugin._event_handler.trigger_event("query", "hades"))

    assert "Hades" in [result["Title"] for result in response["Result"]]


def test_unrelated_games_are_hidden(manifests, settings):
    assert titles(search.query("just caus")) == ["Just Cause 4"]


def test_score_threshold_setting_hides_weak_matches(manifests, settings):
    weak = max(result.score for result in search.query("tr"))
    settings["score_threshold"] = str(weak)

    assert titles(search.query("tr")) == []


def test_default_threshold_keeps_good_matches(manifests, settings):
    assert titles(search.query("hades")) == ["Hades"]


def test_empty_query_can_show_nothing(manifests, settings):
    settings["show_on_empty_query"] = False

    assert titles(search.query("")) == []
