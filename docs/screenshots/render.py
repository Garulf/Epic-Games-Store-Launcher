"""Render the README screenshots and hero image with flow-render.

Usage (from the repo root):

    uvx --from flow-render==0.15.0 --with pillow --with pip python docs/screenshots/render.py

Each ``<shot>.json`` is a flow-render config whose results describe a game
icon as a ``tile`` (short text on a coloured square) instead of an image
``icon``. Flow Launcher shows the icon of each game's executable, which only
exists on Windows, so the tiles stand in for them.
"""
import json
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parents[2]
SHOTS_DIR = ROOT / "docs" / "screenshots"
ASSETS_DIR = ROOT / ".github" / "assets"
THEMES = ("light", "dark")
HERO = {"shot": "hero", "css": ["win11-dark.css", "docs/screenshots/hero.css"]}
TILE_SIZE = 128


def tile_png(text: str, color: str, out_dir: Path) -> Path:
    path = out_dir / f"tile-{text}-{color.lstrip('#')}.png"
    if not path.exists():
        image = Image.new("RGBA", (TILE_SIZE, TILE_SIZE), (0, 0, 0, 0))
        draw = ImageDraw.Draw(image)
        draw.rounded_rectangle((4, 4, TILE_SIZE - 4, TILE_SIZE - 4), radius=22, fill=color)
        font = ImageFont.load_default(size=56)
        draw.text((TILE_SIZE / 2, TILE_SIZE / 2), text, font=font, fill="#FFFFFF", anchor="mm")
        image.save(path)
    return path


def flow_render(args, out_path: Path) -> None:
    with tempfile.TemporaryDirectory() as out_dir:
        subprocess.run(["flow-render", *args, "-o", out_dir], check=True, cwd=ROOT)
        (rendered,) = Path(out_dir).glob("*.png")
        shutil.move(str(rendered), out_path)
    print(f"Wrote {out_path}")


def render_config(shot: str, css, out_path: Path, work: Path) -> None:
    config = json.loads((SHOTS_DIR / f"{shot}.json").read_text(encoding="utf-8"))
    config["icon"] = str((SHOTS_DIR / config["icon"]).resolve())
    for result in config["results"]:
        tile = result.pop("tile")
        result["icon"] = str(tile_png(tile["text"], tile["color"], work))
    config["css"] = css
    config_path = work / f"{shot}.json"
    config_path.write_text(json.dumps(config), encoding="utf-8")
    flow_render(["-c", str(config_path)], out_path)


def main() -> None:
    shots = sorted(path.stem for path in SHOTS_DIR.glob("*.json") if path.stem != HERO["shot"])
    ASSETS_DIR.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory() as tmp:
        work = Path(tmp)
        for shot in shots:
            for theme in THEMES:
                render_config(shot, f"win11-{theme}.css", ASSETS_DIR / f"{shot}-{theme}.png", work)
        render_config(HERO["shot"], HERO["css"], ASSETS_DIR / "hero.png", work)

        package = subprocess.run(
            [str(ROOT / "scripts" / "package.sh"), str(work / "dist")], check=True, capture_output=True, text=True
        )
        plugin_zip = package.stdout.strip().splitlines()[-1]
        for theme in THEMES:
            flow_render(["-u", plugin_zip, "-i", "-s", f"win11-{theme}", "--hide-caret"], ASSETS_DIR / f"install-{theme}.png")


if __name__ == "__main__":
    sys.exit(main())
