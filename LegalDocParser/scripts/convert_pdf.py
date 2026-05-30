#!/usr/bin/env python3
"""PDF 변환 스크립트 - opendataloader_pdf를 사용하여 PDF를 텍스트로 변환합니다."""

import argparse
import json
import os
import sys
import tempfile
import re


INJECTION_KEYWORDS = [
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


def detect_prompt_injection(text: str) -> list[str]:
    warnings = []
    text_lower = text.lower()
    for keyword in INJECTION_KEYWORDS:
        if keyword.lower() in text_lower:
            warnings.append(f"Prompt injection keyword detected: '{keyword}'")
    return warnings


def convert_pdf(
    input_path: str,
    output_format: str = "markdown",
    table_mode: str = "local",
    ocr_lang: str | None = None,
    tagged_pdf: bool = False,
    ai_filter: bool = False,
    pages: str | None = None,
) -> dict:
    try:
        import opendataloader_pdf
    except ImportError:
        return {
            "success": False,
            "error": "opendataloader_pdf 모듈이 설치되지 않았습니다. pip install opendataloader-pdf 를 실행하세요.",
        }

    if not os.path.isfile(input_path):
        return {"success": False, "error": f"파일을 찾을 수 없습니다: {input_path}"}

    try:
        with tempfile.TemporaryDirectory() as tmp_dir:
            kwargs = {
                "input_path": input_path,
                "output_dir": tmp_dir,
                "format": output_format,
            }

            if table_mode == "hybrid":
                kwargs["hybrid"] = "docling-fast"

            if tagged_pdf:
                kwargs["use_struct_tree"] = True

            if ocr_lang:
                kwargs["force_ocr"] = True
                kwargs["ocr_lang"] = ocr_lang

            if pages:
                kwargs["pages"] = pages

            opendataloader_pdf.convert(**kwargs)

            result_files = [f for f in os.listdir(tmp_dir) if not f.startswith(".")]
            if not result_files:
                return {"success": False, "error": "변환 결과 파일이 생성되지 않았습니다."}

            result_path = os.path.join(tmp_dir, result_files[0])
            with open(result_path, "r", encoding="utf-8") as f:
                content = f.read()

        warnings = []
        if ai_filter:
            warnings = detect_prompt_injection(content)

        return {
            "success": True,
            "content": content,
            "warnings": warnings,
        }

    except Exception as e:
        return {"success": False, "error": str(e)}


def main():
    parser = argparse.ArgumentParser(description="PDF 변환 스크립트")
    parser.add_argument("--input", required=True, help="입력 PDF 파일 경로")
    parser.add_argument("--format", default="markdown", choices=["markdown", "json", "html", "text"])
    parser.add_argument("--table-mode", default="local", choices=["local", "hybrid"])
    parser.add_argument("--ocr-lang", default=None, help="OCR 언어 (ko, en, ko,en)")
    parser.add_argument("--tagged-pdf", action="store_true")
    parser.add_argument("--ai-filter", action="store_true")
    parser.add_argument("--pages", default=None, help="페이지 범위 (예: 1-5,8)")

    args = parser.parse_args()

    result = convert_pdf(
        input_path=args.input,
        output_format=args.format,
        table_mode=args.table_mode,
        ocr_lang=args.ocr_lang,
        tagged_pdf=args.tagged_pdf,
        ai_filter=args.ai_filter,
        pages=args.pages,
    )

    print(json.dumps(result, ensure_ascii=False))


if __name__ == "__main__":
    main()
