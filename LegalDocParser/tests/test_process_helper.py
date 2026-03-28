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


def test_cancel_kills_process():
    """cancel_check=True should terminate a long-running process."""
    import threading

    cancelled = threading.Event()

    def trigger_cancel():
        import time
        time.sleep(0.5)
        cancelled.set()

    threading.Thread(target=trigger_cancel, daemon=True).start()

    result = run_process(
        ["python3", "-c", "import time; time.sleep(30)"],
        timeout_seconds=60,
        cancel_check=lambda: cancelled.is_set(),
    )
    assert result.exit_code == -2
    assert "취소" in result.stderr
    assert result.duration_seconds < 5


def test_cancel_check_not_triggered():
    """cancel_check that never returns True should let process complete normally."""
    result = run_process(
        ["python3", "-c", "print('done')"],
        timeout_seconds=10,
        cancel_check=lambda: False,
    )
    assert result.exit_code == 0
    assert "done" in result.stdout
