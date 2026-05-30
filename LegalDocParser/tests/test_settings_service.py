import sys
import os
import json
import tempfile

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from models.app_settings import AppSettings
from services.settings_service import SettingsService


def test_load_default_when_no_file():
    svc = SettingsService(settings_path="/nonexistent/settings.json")
    result = svc.load()
    assert result.python_path == "python"


def test_save_and_load():
    with tempfile.TemporaryDirectory() as tmp:
        path = os.path.join(tmp, "settings.json")
        svc = SettingsService(settings_path=path)

        settings = AppSettings(python_path="/usr/bin/python3")
        svc.save(settings)

        svc2 = SettingsService(settings_path=path)
        loaded = svc2.load()
        assert loaded.python_path == "/usr/bin/python3"


def test_load_corrupted_json():
    with tempfile.TemporaryDirectory() as tmp:
        path = os.path.join(tmp, "settings.json")
        with open(path, "w") as f:
            f.write("{invalid json!!!")

        svc = SettingsService(settings_path=path)
        result = svc.load()
        assert result.python_path == "python"


def test_load_invalid_values():
    with tempfile.TemporaryDirectory() as tmp:
        path = os.path.join(tmp, "settings.json")
        with open(path, "w") as f:
            json.dump({"default_format": "nonexistent_format"}, f)

        svc = SettingsService(settings_path=path)
        result = svc.load()
        assert result.python_path == "python"


def test_save_returns_bool():
    with tempfile.TemporaryDirectory() as tmp:
        path = os.path.join(tmp, "settings.json")
        svc = SettingsService(settings_path=path)
        assert svc.save() is True


def test_save_failure_returns_false():
    svc = SettingsService(settings_path="/nonexistent/deeply/nested/settings.json")
    result = svc.save()
    # makedirs should create nested dirs, so this should succeed
    # Test with truly unwritable path instead
    svc2 = SettingsService(settings_path="/proc/settings.json")
    result = svc2.save()
    assert result is False
