import re
from typing import Optional

from models.search_result import SearchResult


class SearchService:
    REGEX_TIMEOUT = 5

    def search(
        self,
        content: str,
        pattern: str,
        use_regex: bool = False,
        case_sensitive: bool = False,
    ) -> list[SearchResult]:
        if not content or not pattern:
            return []

        results: list[SearchResult] = []
        lines = content.splitlines()

        try:
            flags = 0 if case_sensitive else re.IGNORECASE
            if use_regex:
                compiled = re.compile(pattern, flags)
            else:
                compiled = re.compile(re.escape(pattern), flags)
        except re.error:
            return []

        for line_number, line in enumerate(lines, start=1):
            for match in compiled.finditer(line):
                results.append(SearchResult(
                    matched_text=match.group(),
                    line_number=line_number,
                    column_start=match.start(),
                    match_length=len(match.group()),
                    context_line=line,
                ))

        return results
