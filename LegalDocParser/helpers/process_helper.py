import subprocess
import time
from dataclasses import dataclass
from typing import Optional


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
) -> ProcessResult:
    start = time.monotonic()
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
        return ProcessResult(
            exit_code=-1,
            stdout=e.stdout or "" if isinstance(e.stdout, str) else (e.stdout or b"").decode(errors="replace"),
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
