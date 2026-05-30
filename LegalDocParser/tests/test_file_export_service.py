import sys
import os
import tempfile

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from models.conversion_result import ConversionResult
from models.enums import OutputFormat
from services.file_export_service import FileExportService


def test_extension_mapping():
    assert FileExportService.get_extension(OutputFormat.MARKDOWN) == ".md"
    assert FileExportService.get_extension(OutputFormat.JSON) == ".json"
    assert FileExportService.get_extension(OutputFormat.HTML) == ".html"
    assert FileExportService.get_extension(OutputFormat.TEXT) == ".txt"


def test_save_success():
    svc = FileExportService()
    result = ConversionResult(success=True, content="# Test\nHello world")

    with tempfile.TemporaryDirectory() as tmp_dir:
        path = os.path.join(tmp_dir, "output.md")
        ok = svc.save(result, path, OutputFormat.MARKDOWN)
        assert ok
        assert os.path.exists(path)
        with open(path, "r") as f:
            assert "# Test" in f.read()


def test_save_failed_result():
    svc = FileExportService()
    result = ConversionResult(success=False, content="")

    with tempfile.TemporaryDirectory() as tmp_dir:
        path = os.path.join(tmp_dir, "output.md")
        ok = svc.save(result, path, OutputFormat.MARKDOWN)
        assert not ok


def test_batch_save():
    svc = FileExportService()
    items = [
        ("/fake/doc1.pdf", ConversionResult(success=True, content="content 1")),
        ("/fake/doc2.pdf", ConversionResult(success=True, content="content 2")),
        ("/fake/fail.pdf", ConversionResult(success=False, content="")),
    ]

    with tempfile.TemporaryDirectory() as tmp_dir:
        results = svc.save_batch(items, tmp_dir, OutputFormat.TEXT)
        assert len(results) == 3
        assert results[0][1] is True
        assert results[1][1] is True
        assert results[2][1] is False


def test_batch_save_collision_handling():
    svc = FileExportService()
    items = [
        ("/fake/doc.pdf", ConversionResult(success=True, content="content 1")),
        ("/fake2/doc.pdf", ConversionResult(success=True, content="content 2")),
    ]

    with tempfile.TemporaryDirectory() as tmp_dir:
        results = svc.save_batch(items, tmp_dir, OutputFormat.TEXT)
        files = os.listdir(tmp_dir)
        assert len(files) == 2
        assert "doc.txt" in files
        assert "doc_1.txt" in files
