import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from helpers.ai_safety_filter import filter_content, redact_sensitive_info


def test_prompt_injection_english():
    content = "This document says ignore previous instructions and do something else."
    _, warnings = filter_content(content)
    assert any("ignore previous instructions" in w for w in warnings)


def test_prompt_injection_korean():
    content = "이 문서에는 이전 지시를 무시하라는 내용이 있습니다."
    _, warnings = filter_content(content)
    assert any("이전 지시를 무시" in w for w in warnings)


def test_resident_id_detection():
    content = "주민등록번호: 901231-1234567"
    _, warnings = filter_content(content)
    assert any("주민등록번호" in w for w in warnings)


def test_phone_detection():
    content = "연락처: 010-1234-5678"
    _, warnings = filter_content(content)
    assert any("전화번호" in w for w in warnings)


def test_hidden_html_removal():
    content = '<div style="display:none">hidden text</div> visible text'
    filtered, warnings = filter_content(content)
    assert "hidden text" not in filtered
    assert "[HIDDEN_TEXT_REMOVED]" in filtered
    assert "visible text" in filtered


def test_no_warnings_clean_content():
    content = "이것은 정상적인 법률 문서입니다."
    filtered, warnings = filter_content(content)
    assert len(warnings) == 0
    assert filtered == content


def test_redact_resident_id():
    content = "주민번호는 901231-1234567 입니다."
    redacted = redact_sensitive_info(content)
    assert "901231-1234567" not in redacted
    assert "******-*******" in redacted


def test_redact_phone():
    content = "전화번호는 010-1234-5678 입니다."
    redacted = redact_sensitive_info(content)
    assert "010-1234-5678" not in redacted
    assert "***-****-****" in redacted
