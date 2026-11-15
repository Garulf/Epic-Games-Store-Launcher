import json

import pytest

import egs
import search


def manifest(name, app_name, **overrides):
    data = {
        "DisplayName": name,
        "InstallLocation": f"C:\\Program Files\\Epic Games\\{app_name}",
        "LaunchExecutable": f"{app_name}.exe",
        "CatalogNamespace": f"{app_name.lower()}-namespace",
        "CatalogItemId": f"{app_name.lower()}-item",
        "AppName": app_name,
        "bIsIncompleteInstall": False,
    }
    data.update(overrides)
    return data


GAMES = [
    manifest("Hades", "Hades"),
    manifest("Just Cause 4", "JustCause4"),
    manifest("Subnautica", "Subnautica"),
    manifest("Transistor", "Transistor"),
]


@pytest.fixture
def manifests(tmp_path, monkeypatch):
    def write(*games):
        for index, game in enumerate(games):
            (tmp_path / f"{index:02d}.item").write_text(json.dumps(game), encoding="utf-8")
        return tmp_path

    monkeypatch.setattr(egs, "manifests_dir", lambda: tmp_path)
    write(*GAMES)
    return write


@pytest.fixture
def settings():
    launcher = search.plugin.launcher
    launcher._settings = {}
    yield launcher._settings
    launcher._settings = {}
