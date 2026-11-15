import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def manifest():
    return json.loads((ROOT / "data" / "plugin.json").read_text(encoding="utf-8"))


def test_plugin_identity_is_unchanged():
    data = manifest()
    assert data["ID"] == "02D91372A4C9429B93BA6365E38FBD4C"
    assert data["ActionKeyword"] == "eg"
    assert data["Language"] == "python_v2"


def test_website_points_at_the_repository():
    assert manifest()["Website"] == "https://github.com/Garulf/Epic-Games-Store-Launcher"
