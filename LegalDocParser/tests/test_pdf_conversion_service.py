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


def test_batch_cancel_stops_remaining():
    """Cancelling mid-batch should not process all files."""
    settings = AppSettings(batch_concurrency=1)
    svc = PdfConversionService(settings)
    completed_count = []

    def on_progress(completed, total, filename):
        completed_count.append(completed)

    cancel_after_first = {"count": 0}

    def cancel_check():
        return cancel_after_first["count"] >= 1

    def on_progress_and_track(completed, total, filename):
        cancel_after_first["count"] = completed
        completed_count.append(completed)

    results = svc.convert_batch(
        ["/nonexistent/a.pdf", "/nonexistent/b.pdf", "/nonexistent/c.pdf"],
        ConversionOptions(),
        on_progress=on_progress_and_track,
        cancel_check=cancel_check,
    )
    # Should have fewer results than total files
    assert len(results) < 3


def test_validate_python_checks_multiple():
    """validate_python should check Python, module, and script."""
    settings = AppSettings()
    svc = PdfConversionService(settings)
    ok, msg = svc.validate_python()
    # opendataloader_pdf is likely not installed, so it should fail
    # but it should at least get past the Python version check
    if not ok:
        assert "opendataloader_pdf" in msg or "Python" in msg or "스크립트" in msg
    else:
        assert "Python" in msg
        assert "opendataloader_pdf" in msg
        assert "변환 스크립트" in msg
