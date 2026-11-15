from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path, PureWindowsPath
from typing import Any, Dict, List

EOS_KEY = r"SOFTWARE\Epic Games\EOS"
MANIFESTS_VALUE = "ModSdkMetadataDir"
LAUNCH_URI = "com.epicgames.launcher://apps/{namespace}%3A{catalog_id}%3A{app_name}?action=launch&silent=true"


def manifests_dir() -> Path:
    import winreg

    with winreg.OpenKey(winreg.HKEY_CURRENT_USER, EOS_KEY) as key:
        return Path(winreg.QueryValueEx(key, MANIFESTS_VALUE)[0])


def launch_uri(namespace: str, catalog_id: str, app_name: str) -> str:
    return LAUNCH_URI.format(namespace=namespace, catalog_id=catalog_id, app_name=app_name)


@dataclass(frozen=True)
class Game:
    display_name: str
    install_location: str
    launch_executable: str
    catalog_namespace: str
    catalog_item_id: str
    app_name: str
    incomplete_install: bool = False

    @classmethod
    def from_manifest(cls, manifest: Dict[str, Any]) -> Game:
        return cls(
            display_name=manifest["DisplayName"],
            install_location=manifest["InstallLocation"],
            launch_executable=manifest["LaunchExecutable"],
            catalog_namespace=manifest["CatalogNamespace"],
            catalog_item_id=manifest["CatalogItemId"],
            app_name=manifest["AppName"],
            incomplete_install=bool(manifest.get("bIsIncompleteInstall", False)),
        )

    @property
    def exe_path(self) -> str:
        return str(PureWindowsPath(self.install_location, self.launch_executable))

    @property
    def launch_uri(self) -> str:
        return launch_uri(self.catalog_namespace, self.catalog_item_id, self.app_name)


def get_games(directory: Path) -> List[Game]:
    return [Game.from_manifest(json.loads(path.read_bytes())) for path in sorted(directory.glob("**/*.item"))]
