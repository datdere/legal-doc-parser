#!/usr/bin/env python3
"""
LegalDocParser - PDF 변환 브릿지 스크립트
OpenDataLoader PDF Python SDK를 호출하여 PDF를 변환합니다.

Usage:
    python convert_pdf.py --input <path> --format <markdown|json|html|text>
        [--table-mode local|hybrid] [--ocr-lang ko|en|ko,en]
        [--tagged-pdf] [--ai-filter] [--pages "1-5,8"]
"""

import argparse
import json
import os
import sys
import time


def parse_args():
    parser = argparse.ArgumentParser(description="LegalDocParser PDF 변환")
    parser.add_argument("--input", required=True, help="입력 PDF 파일 경로")
    parser.add_argument("--format", required=True,
                        choices=["markdown", "json", "html", "text"],
                        help="출력 포맷")
    parser.add_argument("--table-mode", default="local",
                        choices=["local", "hybrid"],
                        help="표 추출 모드 (default: local)")
    parser.add_argument("--ocr-lang", default=None,
                        help="OCR 언어 (ko, en, ko,en)")
    parser.add_argument("--tagged-pdf", action="store_true",
                        help="Tagged PDF 구조 태그 활용")
    parser.add_argument("--ai-filter", action="store_true",
                        help="AI 안전 필터 적용")
    parser.add_argument("--pages", default=None,
                        help="페이지 범위 (예: 1-5,8)")
    return parser.parse_args()


def convert_pdf(args):
    """OpenDataLoader PDF를 사용하여 PDF를 변환합니다."""
    import tempfile

    input_path = os.path.abspath(args.input)

    if not os.path.exists(input_path):
        return {"success": False, "error": f"파일을 찾을 수 없습니다: {input_path}"}

    try:
        import opendataloader_pdf
    except ImportError:
        return {
            "success": False,
            "error": "opendataloader_pdf 모듈이 설치되지 않았습니다. "
                     "'pip install opendataloader-pdf' 명령으로 설치하세요."
        }

    try:
        # 임시 출력 디렉토리 생성
        with tempfile.TemporaryDirectory() as output_dir:
            # 변환 옵션 구성
            convert_kwargs = {
                "input_path": [input_path],
                "output_dir": output_dir,
                "format": args.format,
            }

            # 하이브리드 모드
            if args.table_mode == "hybrid":
                convert_kwargs["hybrid"] = "docling-fast"

            # Tagged PDF
            if args.tagged_pdf:
                convert_kwargs["use_struct_tree"] = True

            # OCR 설정
            if args.ocr_lang:
                convert_kwargs["force_ocr"] = True
                convert_kwargs["ocr_lang"] = args.ocr_lang

            # 페이지 범위
            if args.pages:
                convert_kwargs["pages"] = args.pages

            # 변환 실행
            opendataloader_pdf.convert(**convert_kwargs)

            # 결과 파일 읽기
            format_ext = {
                "markdown": ".md",
                "json": ".json",
                "html": ".html",
                "text": ".txt"
            }

            ext = format_ext.get(args.format, ".md")
            base_name = os.path.splitext(os.path.basename(input_path))[0]
            output_file = os.path.join(output_dir, base_name + ext)

            if not os.path.exists(output_file):
                # 디렉토리에서 해당 확장자 파일 찾기
                for f in os.listdir(output_dir):
                    if f.endswith(ext):
                        output_file = os.path.join(output_dir, f)
                        break

            if os.path.exists(output_file):
                with open(output_file, "r", encoding="utf-8") as f:
                    content = f.read()

                warnings = []

                # AI 안전 필터 (기본적인 프롬프트 인젝션 탐지)
                if args.ai_filter:
                    injection_keywords = [
                        "ignore previous instructions",
                        "ignore above instructions",
                        "disregard all prior",
                        "이전 지시를 무시",
                    ]
                    for keyword in injection_keywords:
                        if keyword.lower() in content.lower():
                            warnings.append(
                                f"프롬프트 인젝션 의심 패턴: '{keyword}'"
                            )

                return {
                    "success": True,
                    "content": content,
                    "warnings": warnings if warnings else None
                }
            else:
                return {
                    "success": False,
                    "error": "변환 결과 파일을 찾을 수 없습니다."
                }

    except Exception as e:
        return {"success": False, "error": str(e)}


def main():
    args = parse_args()
    start_time = time.time()

    result = convert_pdf(args)

    elapsed = time.time() - start_time
    result["elapsed_seconds"] = round(elapsed, 2)

    # JSON 결과를 stdout으로 출력
    print(json.dumps(result, ensure_ascii=False))


if __name__ == "__main__":
    main()
