#!/usr/bin/env python3
"""LegalDocParser - 법률 문서 PDF 파싱 도구

AI API를 사용하지 않는 로컬 전용 PDF 변환/검색/내보내기 도구입니다.
"""

import sys
import os

sys.path.insert(0, os.path.dirname(__file__))

from ui.main_window import MainWindow


def main():
    app = MainWindow()
    app.run()


if __name__ == "__main__":
    main()
