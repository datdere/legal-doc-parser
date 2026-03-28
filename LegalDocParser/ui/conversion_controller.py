import os
import threading
from typing import Callable, Optional

from models.conversion_options import ConversionOptions
from models.conversion_result import ConversionResult
from models.document_info import DocumentInfo
from models.enums import OutputFormat, TableExtractionMode, OcrLanguage
from services.pdf_conversion_service import PdfConversionService


class ConversionController:
    def __init__(
        self,
        conversion_service: PdfConversionService,
        schedule_on_main: Callable,
        log: Callable[[str, str], None],
    ):
        self._service = conversion_service
        self._schedule = schedule_on_main
        self._log = log

    def convert_single(
        self,
        doc: DocumentInfo,
        options: ConversionOptions,
        on_done: Callable[[DocumentInfo, ConversionResult], None],
    ) -> None:
        self._log(f"변환 시작: {doc.file_name}", "info")

        def _worker():
            result = self._service.convert(doc.file_path, options)
            self._schedule(lambda: on_done(doc, result))

        threading.Thread(target=_worker, daemon=True).start()

    def convert_batch(
        self,
        docs: list[DocumentInfo],
        options: ConversionOptions,
        on_progress: Callable[[int, int, str], None],
        on_done: Callable[[list[DocumentInfo], list[tuple[str, ConversionResult]]], None],
        cancel_check: Callable[[], bool],
    ) -> None:
        paths = [d.file_path for d in docs]
        total = len(paths)
        self._log(f"배치 변환 시작: {total}개 파일", "info")

        def _worker():
            results = self._service.convert_batch(
                paths, options,
                on_progress=lambda c, t, f: self._schedule(lambda: on_progress(c, t, f)),
                cancel_check=cancel_check,
            )
            self._schedule(lambda: on_done(docs, results))

        threading.Thread(target=_worker, daemon=True).start()

    def validate_python(self) -> tuple[bool, str]:
        return self._service.validate_python()
