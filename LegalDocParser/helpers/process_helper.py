import subprocess
import threading
import time
from dataclasses import dataclass
from typing import Callable, Optional


@dataclass
class ProcessResult:
    exit_code: int
    stdout: str
    stderr: str
    duration_seconds: float


def run_process(
    command: list[str],
    timeout_seconds: int = 300,
    cwd: Optional[str] = None,
    cancel_check: Optional[Callable[[], bool]] = None,
) -> ProcessResult:
    start = time.monotonic()

    if cancel_check is None:
        return _run_simple(command, timeout_seconds, cwd, start)

    return _run_cancellable(command, timeout_seconds, cwd, start, cancel_check)


def _run_simple(
    command: list[str],
    timeout_seconds: int,
    cwd: Optional[str],
    start: float,
) -> ProcessResult:
    try:
        result = subprocess.run(
            command,
            capture_output=True,
            text=True,
            timeout=timeout_seconds,
            cwd=cwd,
        )
        duration = time.monotonic() - start
        return ProcessResult(
            exit_code=result.returncode,
            stdout=result.stdout,
            stderr=result.stderr,
            duration_seconds=duration,
        )
    except subprocess.TimeoutExpired as e:
        duration = time.monotonic() - start
        if isinstance(e.stdout, str):
            stdout = e.stdout or ""
        elif isinstance(e.stdout, bytes):
            stdout = e.stdout.decode(errors="replace")
        else:
            stdout = ""
        return ProcessResult(
            exit_code=-1,
            stdout=stdout,
            stderr=f"프로세스 시간 초과 ({timeout_seconds}초)",
            duration_seconds=duration,
        )
    except FileNotFoundError:
        duration = time.monotonic() - start
        return ProcessResult(
            exit_code=-1,
            stdout="",
            stderr=f"명령을 찾을 수 없습니다: {command[0]}",
            duration_seconds=duration,
        )


def _run_cancellable(
    command: list[str],
    timeout_seconds: int,
    cwd: Optional[str],
    start: float,
    cancel_check: Callable[[], bool],
) -> ProcessResult:
    try:
        proc = subprocess.Popen(
            command,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            cwd=cwd,
        )
    except FileNotFoundError:
        duration = time.monotonic() - start
        return ProcessResult(
            exit_code=-1,
            stdout="",
            stderr=f"명령을 찾을 수 없습니다: {command[0]}",
            duration_seconds=duration,
        )

    poll_interval = 0.3
    elapsed = 0.0
    while proc.poll() is None:
        if cancel_check():
            proc.terminate()
            try:
                proc.wait(timeout=3)
            except subprocess.TimeoutExpired:
                proc.kill()
                proc.wait()
            duration = time.monotonic() - start
            return ProcessResult(
                exit_code=-2,
                stdout="",
                stderr="사용자에 의해 취소되었습니다.",
                duration_seconds=duration,
            )
        if elapsed >= timeout_seconds:
            proc.kill()
            proc.wait()
            duration = time.monotonic() - start
            return ProcessResult(
                exit_code=-1,
                stdout="",
                stderr=f"프로세스 시간 초과 ({timeout_seconds}초)",
                duration_seconds=duration,
            )
        time.sleep(poll_interval)
        elapsed += poll_interval

    stdout, stderr = proc.communicate()
    duration = time.monotonic() - start
    return ProcessResult(
        exit_code=proc.returncode,
        stdout=stdout or "",
        stderr=stderr or "",
        duration_seconds=duration,
    )
