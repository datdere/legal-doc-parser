import json
import os
import logging

from models.app_settings import AppSettings

DEFAULT_SETTINGS_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), "settings.json")
logger = logging.getLogger(__name__)


class SettingsService:
    def __init__(self, settings_path: str = DEFAULT_SETTINGS_PATH):
        self._settings_path = settings_path
        self._settings: AppSettings = AppSettings()

    @property
    def settings(self) -> AppSettings:
        return self._settings

    def load(self) -> AppSettings:
        if not os.path.exists(self._settings_path):
            self._settings = AppSettings()
            return self._settings

        try:
            with open(self._settings_path, "r", encoding="utf-8") as f:
                data = json.load(f)
            self._settings = AppSettings.from_dict(data)
        except (json.JSONDecodeError, UnicodeDecodeError) as e:
            logger.warning("설정 파일이 손상되어 기본값을 사용합니다: %s", e)
            self._settings = AppSettings()
        except (ValueError, TypeError, KeyError) as e:
            logger.warning("설정 값이 유효하지 않아 기본값을 사용합니다: %s", e)
            self._settings = AppSettings()
        except OSError as e:
            logger.warning("설정 파일을 읽을 수 없어 기본값을 사용합니다: %s", e)
            self._settings = AppSettings()

        return self._settings

    def save(self, settings: AppSettings | None = None) -> bool:
        if settings is not None:
            self._settings = settings
        try:
            os.makedirs(os.path.dirname(self._settings_path), exist_ok=True)
            with open(self._settings_path, "w", encoding="utf-8") as f:
                json.dump(self._settings.to_dict(), f, indent=4, ensure_ascii=False)
            return True
        except OSError as e:
            logger.error("설정 파일 저장 실패: %s", e)
            return False
