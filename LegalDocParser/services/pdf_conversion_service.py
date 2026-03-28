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
from models.enums import OcrLanguage, TableExtractionMode


SCRIPT_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), "scripts", "convert_pdf.py")


class PdfConversionService:
    def __init__(self, settings: AppSettings):
        self._settings = settings

    def update_settings(self, settings: AppSettings) -> None:
        self._settings = settings

    def convert(self, pdf_path: str, options: ConversionOptions) -> ConversionResult:
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
        )
        duration = time.monotonic() - start

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
                executor.submit(self.convert, path, options): path
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
        proc = run_process(
            [self._settings.python_path, "-c", "import opendataloader_pdf; print('OK')"],
            timeout_seconds=30,
        )
        if proc.exit_code == 0 and "OK" in proc.stdout:
            return True, "Python 환경이 정상입니다."
        return False, proc.stderr or "opendataloader_pdf 모듈을 찾을 수 없습니다."

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
        if options.enable_ai_safety_filter:
            args.append("--ai-filter")
        if options.page_range:
            args.extend(["--pages", options.page_range])
        return args
