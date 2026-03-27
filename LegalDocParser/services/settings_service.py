import json
import os

from models.app_settings import AppSettings

DEFAULT_SETTINGS_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), "settings.json")


class SettingsService:
    def __init__(self, settings_path: str = DEFAULT_SETTINGS_PATH):
        self._settings_path = settings_path
        self._settings: AppSettings = AppSettings()

    @property
    def settings(self) -> AppSettings:
        return self._settings

    def load(self) -> AppSettings:
        if os.path.exists(self._settings_path):
            with open(self._settings_path, "r", encoding="utf-8") as f:
                data = json.load(f)
            self._settings = AppSettings.from_dict(data)
        else:
            self._settings = AppSettings()
        return self._settings

    def save(self, settings: AppSettings | None = None) -> None:
        if settings is not None:
            self._settings = settings
        with open(self._settings_path, "w", encoding="utf-8") as f:
            json.dump(self._settings.to_dict(), f, indent=4, ensure_ascii=False)
