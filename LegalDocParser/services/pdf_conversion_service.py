import json
import os
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import Callable, Optional

from helpers import ai_safety_filter
from helpers.process_helper import run_process
from models.app_settings import AppSettings
from models.conversion_options import ConversionOptions
from models.conversion_result import ConversionResult
from models.enums import OcrLanguage


SCRIPT_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), "scripts", "convert_pdf.py")


class PdfConversionService:
    def __init__(self, settings: AppSettings):
        self._settings = settings

    def update_settings(self, settings: AppSettings) -> None:
        self._settings = settings

    def convert(
        self,
        pdf_path: str,
        options: ConversionOptions,
        cancel_check: Optional[Callable[[], bool]] = None,
    ) -> ConversionResult:
        if not os.path.isfile(pdf_path):
            return ConversionResult(
                success=False,
                error_message=f"파일을 찾을 수 없습니다: {pdf_path}",
            )

        args = self._build_arguments(pdf_path, options)
        start = time.monotonic()

        proc = run_process(
            [self._settings.python_path] + args,
            timeout_seconds=self._settings.process_timeout_seconds,
            cancel_check=cancel_check,
        )
        duration = time.monotonic() - start

        if proc.exit_code == -2:
            return ConversionResult(
                success=False,
                error_message="사용자에 의해 취소되었습니다.",
                duration_seconds=duration,
            )

        if proc.exit_code != 0:
            return ConversionResult(
                success=False,
                error_message=proc.stderr or f"변환 실패 (exit code: {proc.exit_code})",
                duration_seconds=duration,
            )

        try:
            output = json.loads(proc.stdout)
        except (json.JSONDecodeError, TypeError):
            return ConversionResult(
                success=False,
                error_message="Python 스크립트의 출력을 파싱할 수 없습니다.",
                duration_seconds=duration,
            )

        if not isinstance(output, dict):
            return ConversionResult(
                success=False,
                error_message="변환 출력이 올바른 JSON 객체가 아닙니다.",
                duration_seconds=duration,
            )

        if not output.get("success", False):
            return ConversionResult(
                success=False,
                error_message=output.get("error", "알 수 없는 오류"),
                duration_seconds=duration,
            )

        content = output.get("content")
        if not isinstance(content, str):
            return ConversionResult(
                success=False,
                error_message="변환 결과에 유효한 content 필드가 없습니다.",
                duration_seconds=duration,
            )

        raw_warnings = output.get("warnings", [])
        warnings = [str(w) for w in raw_warnings] if isinstance(raw_warnings, list) else []
        ai_warnings: list[str] = []

        if options.enable_ai_safety_filter:
            content, ai_warnings = ai_safety_filter.filter_content(content)

        return ConversionResult(
            success=True,
            content=content,
            duration_seconds=duration,
            warnings=warnings,
            ai_filter_warnings=ai_warnings,
        )

    def convert_batch(
        self,
        pdf_paths: list[str],
        options: ConversionOptions,
        on_progress: Optional[Callable[[int, int, str], None]] = None,
        cancel_check: Optional[Callable[[], bool]] = None,
    ) -> list[tuple[str, ConversionResult]]:
        if not pdf_paths:
            return []

        results: list[tuple[str, ConversionResult]] = []
        total = len(pdf_paths)

        with ThreadPoolExecutor(max_workers=self._settings.batch_concurrency) as executor:
            futures = {
                executor.submit(self.convert, path, options, cancel_check): path
                for path in pdf_paths
            }
            completed = 0
            for future in as_completed(futures):
                path = futures[future]
                if cancel_check and cancel_check():
                    for f in futures:
                        f.cancel()
                    break
                try:
                    result = future.result()
                except Exception as e:
                    result = ConversionResult(success=False, error_message=str(e))
                results.append((path, result))
                completed += 1
                if on_progress:
                    on_progress(completed, total, os.path.basename(path))

        return results

    def validate_python(self) -> tuple[bool, str]:
        # 1. Python 실행 가능 여부
        proc = run_process(
            [self._settings.python_path, "--version"],
            timeout_seconds=10,
        )
        if proc.exit_code != 0:
            return False, f"Python을 실행할 수 없습니다: {proc.stderr}"
        python_version = (proc.stdout or proc.stderr).strip()

        # 2. opendataloader_pdf 모듈 import + 버전 확인
        proc = run_process(
            [self._settings.python_path, "-c",
             "import opendataloader_pdf; print(getattr(opendataloader_pdf, '__version__', 'unknown'))"],
            timeout_seconds=15,
        )
        if proc.exit_code != 0:
            return False, f"opendataloader_pdf 모듈을 찾을 수 없습니다.\npip install opendataloader-pdf 를 실행하세요.\n\n{proc.stderr}"
        module_version = proc.stdout.strip()

        # 3. 변환 스크립트 파일 존재 확인
        if not os.path.isfile(SCRIPT_PATH):
            return False, f"변환 스크립트를 찾을 수 없습니다: {SCRIPT_PATH}"

        # 4. 변환 스크립트 구문 검사
        proc = run_process(
            [self._settings.python_path, "-c",
             f"import py_compile; py_compile.compile(r'{SCRIPT_PATH}', doraise=True); print('OK')"],
            timeout_seconds=10,
        )
        if proc.exit_code != 0:
            return False, f"변환 스크립트에 구문 오류가 있습니다:\n{proc.stderr}"

        return True, (
            f"Python 환경이 정상입니다.\n"
            f"  Python: {python_version}\n"
            f"  opendataloader_pdf: {module_version}\n"
            f"  변환 스크립트: {SCRIPT_PATH}"
        )

    def _build_arguments(self, pdf_path: str, options: ConversionOptions) -> list[str]:
        args = [
            SCRIPT_PATH,
            "--input", pdf_path,
            "--format", options.format.value,
            "--table-mode", options.table_mode.value,
        ]
        if options.ocr_lang != OcrLanguage.NONE:
            args.extend(["--ocr-lang", options.ocr_lang.value])
        if options.use_tagged_pdf:
            args.append("--tagged-pdf")
        # AI 안전 필터는 서비스 계층(ai_safety_filter.filter_content)에서 적용.
        # 스크립트의 --ai-filter는 중복이므로 전달하지 않음.
        if options.page_range:
            args.extend(["--pages", options.page_range])
        return args
