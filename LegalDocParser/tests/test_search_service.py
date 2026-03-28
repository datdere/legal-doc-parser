import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from services.search_service import SearchService


def setup_service():
    return SearchService()


def test_simple_search():
    svc = setup_service()
    content = "hello world\nfoo bar\nhello again"
    results = svc.search(content, "hello")
    assert len(results) == 2
    assert results[0].line_number == 1
    assert results[1].line_number == 3


def test_case_insensitive():
    svc = setup_service()
    content = "Hello World\nhello world"
    results = svc.search(content, "hello", case_sensitive=False)
    assert len(results) == 2


def test_case_sensitive():
    svc = setup_service()
    content = "Hello World\nhello world"
    results = svc.search(content, "Hello", case_sensitive=True)
    assert len(results) == 1
    assert results[0].line_number == 1


def test_regex_search():
    svc = setup_service()
    content = "abc 123 def\nghi 456 jkl"
    results = svc.search(content, r"\d+", use_regex=True)
    assert len(results) == 2
    assert results[0].matched_text == "123"
    assert results[1].matched_text == "456"


def test_column_position():
    svc = setup_service()
    content = "hello world"
    results = svc.search(content, "world")
    assert len(results) == 1
    assert results[0].column_start == 6


def test_empty_content():
    svc = setup_service()
    results = svc.search("", "test")
    assert len(results) == 0


def test_empty_pattern():
    svc = setup_service()
    results = svc.search("test content", "")
    assert len(results) == 0


def test_invalid_regex():
    svc = setup_service()
    results = svc.search("test content", "[invalid", use_regex=True)
    assert len(results) == 0


def test_multiple_matches_per_line():
    svc = setup_service()
    content = "aaa bbb aaa"
    results = svc.search(content, "aaa")
    assert len(results) == 2
    assert results[0].column_start == 0
    assert results[1].column_start == 8


def test_regex_timeout_returns_partial():
    """Catastrophic regex backtracking should not hang indefinitely."""
    import services.search_service as mod
    original = mod._REGEX_TIMEOUT_SECONDS
    mod._REGEX_TIMEOUT_SECONDS = 1
    try:
        svc = setup_service()
        # This pattern + input can cause exponential backtracking
        evil_input = "a" * 30 + "!"
        results = svc.search(evil_input, r"(a+)+b", use_regex=True)
        # Should return (possibly empty) without hanging
        assert isinstance(results, list)
    finally:
        mod._REGEX_TIMEOUT_SECONDS = original
