import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from helpers.process_helper import run_process


def test_successful_command():
    result = run_process(["python3", "-c", "print('hello')"])
    assert result.exit_code == 0
    assert "hello" in result.stdout


def test_invalid_command():
    result = run_process(["nonexistent_command_xyz"])
    assert result.exit_code == -1
    assert "명령을 찾을 수 없습니다" in result.stderr


def test_timeout():
    result = run_process(["python3", "-c", "import time; time.sleep(10)"], timeout_seconds=1)
    assert result.exit_code == -1
    assert "시간 초과" in result.stderr


def test_exit_code():
    result = run_process(["python3", "-c", "import sys; sys.exit(42)"])
    assert result.exit_code == 42


def test_duration_tracked():
    result = run_process(["python3", "-c", "print('fast')"])
    assert result.duration_seconds >= 0
