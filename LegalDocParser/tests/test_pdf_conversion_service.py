import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from models.app_settings import AppSettings
from models.conversion_options import ConversionOptions
from services.pdf_conversion_service import PdfConversionService


def test_nonexistent_file():
    settings = AppSettings()
    svc = PdfConversionService(settings)
    result = svc.convert("/nonexistent/file.pdf", ConversionOptions())
    assert not result.success
    assert "찾을 수 없습니다" in result.error_message


def test_empty_batch():
    settings = AppSettings()
    svc = PdfConversionService(settings)
    results = svc.convert_batch([], ConversionOptions())
    assert len(results) == 0


def test_batch_progress_reporting():
    settings = AppSettings()
    svc = PdfConversionService(settings)
    progress_calls = []

    def on_progress(completed, total, filename):
        progress_calls.append((completed, total, filename))

    svc.convert_batch(
        ["/nonexistent/a.pdf", "/nonexistent/b.pdf"],
        ConversionOptions(),
        on_progress=on_progress,
    )
    assert len(progress_calls) == 2
