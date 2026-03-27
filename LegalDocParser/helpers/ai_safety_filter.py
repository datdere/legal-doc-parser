import re


PROMPT_INJECTION_KEYWORDS = [
    "ignore previous instructions",
    "ignore above instructions",
    "disregard all prior",
    "system prompt",
    "you are now",
    "new instructions:",
    "override:",
    "이전 지시를 무시",
    "시스템 프롬프트",
]

RESIDENT_ID_PATTERN = re.compile(r"\d{6}\s*-\s*[1-4]\d{6}")
PHONE_PATTERN = re.compile(r"01[0-9]-?\d{3,4}-?\d{4}")
HIDDEN_HTML_PATTERN = re.compile(
    r"<div[^>]*(?:display\s*:\s*none|visibility\s*:\s*hidden|font-size\s*:\s*0)[^>]*>.*?</div>",
    re.DOTALL | re.IGNORECASE,
)


def filter_content(content: str) -> tuple[str, list[str]]:
    warnings: list[str] = []

    content_lower = content.lower()
    for keyword in PROMPT_INJECTION_KEYWORDS:
        if keyword.lower() in content_lower:
            warnings.append(f"프롬프트 인젝션 키워드 감지: '{keyword}'")

    if RESIDENT_ID_PATTERN.search(content):
        warnings.append("주민등록번호 패턴이 감지되었습니다.")

    if PHONE_PATTERN.search(content):
        warnings.append("전화번호 패턴이 감지되었습니다.")

    filtered = HIDDEN_HTML_PATTERN.sub("[HIDDEN_TEXT_REMOVED]", content)
    if filtered != content:
        warnings.append("숨겨진 HTML 텍스트가 제거되었습니다.")

    return filtered, warnings


def redact_sensitive_info(content: str) -> str:
    content = RESIDENT_ID_PATTERN.sub("******-*******", content)
    content = PHONE_PATTERN.sub("***-****-****", content)
    return content
