import json

import egs
from conftest import manifest


def test_reads_every_manifest_below_the_directory(tmp_path):
    (tmp_path / "nested").mkdir()
    (tmp_path / "a.item").write_text(json.dumps(manifest("Hades", "Hades")), encoding="utf-8")
    (tmp_path / "nested" / "b.item").write_text(json.dumps(manifest("Celeste", "Celeste")), encoding="utf-8")
    (tmp_path / "notes.txt").write_text("not a manifest", encoding="utf-8")

    assert [game.display_name for game in egs.get_games(tmp_path)] == ["Hades", "Celeste"]


def test_reads_utf8_names(tmp_path):
    (tmp_path / "a.item").write_bytes(json.dumps(manifest("Ōkami HD", "Okami"), ensure_ascii=False).encode("utf-8"))

    assert egs.get_games(tmp_path)[0].display_name == "Ōkami HD"


def test_exe_path_joins_install_location_and_executable():
    game = egs.Game.from_manifest(manifest("Hades", "Hades", LaunchExecutable="x64/Hades.exe"))

    assert game.exe_path == "C:\\Program Files\\Epic Games\\Hades\\x64\\Hades.exe"


def test_launch_uri():
    game = egs.Game.from_manifest(manifest("Hades", "Hades"))

    assert game.launch_uri == (
        "com.epicgames.launcher://apps/hades-namespace%3Ahades-item%3AHades?action=launch&silent=true"
    )


def test_incomplete_install_flag():
    assert egs.Game.from_manifest(manifest("Hades", "Hades", bIsIncompleteInstall=True)).incomplete_install
    assert not egs.Game.from_manifest({**manifest("Hades", "Hades"), "bIsIncompleteInstall": None}).incomplete_install


def test_missing_registry_key_raises_file_not_found(monkeypatch):
    import sys
    import types

    def open_key(root, path):
        raise FileNotFoundError(path)

    fake = types.SimpleNamespace(HKEY_CURRENT_USER=object(), OpenKey=open_key)
    monkeypatch.setitem(sys.modules, "winreg", fake)

    try:
        egs.manifests_dir()
    except FileNotFoundError:
        return
    raise AssertionError("expected FileNotFoundError")


def test_manifests_dir_comes_from_the_registry(monkeypatch):
    import contextlib
    import sys
    import types

    hkcu = object()
    opened = []

    @contextlib.contextmanager
    def open_key(root, path):
        opened.append((root, path))
        yield "key"

    def query_value(key, name):
        assert (key, name) == ("key", "ModSdkMetadataDir")
        return ("C:/ProgramData/Epic/EpicGamesLauncher/Data/Manifests", 1)

    fake = types.SimpleNamespace(HKEY_CURRENT_USER=hkcu, OpenKey=open_key, QueryValueEx=query_value)
    monkeypatch.setitem(sys.modules, "winreg", fake)

    assert egs.manifests_dir().as_posix() == "C:/ProgramData/Epic/EpicGamesLauncher/Data/Manifests"
    assert opened == [(hkcu, r"SOFTWARE\Epic Games\EOS")]
