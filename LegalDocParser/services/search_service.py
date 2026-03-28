import re
import signal
import threading

from models.search_result import SearchResult

_REGEX_TIMEOUT_SECONDS = 5


class _RegexTimeoutError(Exception):
    pass


class SearchService:
    def search(
        self,
        content: str,
        pattern: str,
        use_regex: bool = False,
        case_sensitive: bool = False,
    ) -> list[SearchResult]:
        if not content or not pattern:
            return []

        try:
            flags = 0 if case_sensitive else re.IGNORECASE
            if use_regex:
                compiled = re.compile(pattern, flags)
            else:
                compiled = re.compile(re.escape(pattern), flags)
        except re.error:
            return []

        results: list[SearchResult] = []
        lines = content.splitlines()

        try:
            results = self._search_with_timeout(compiled, lines)
        except _RegexTimeoutError:
            return results

        return results

    def _search_with_timeout(
        self, compiled: re.Pattern, lines: list[str]
    ) -> list[SearchResult]:
        results: list[SearchResult] = []
        container: dict = {"done": False, "error": None}

        def _do_search():
            try:
                for line_number, line in enumerate(lines, start=1):
                    for match in compiled.finditer(line):
                        results.append(SearchResult(
                            matched_text=match.group(),
                            line_number=line_number,
                            column_start=match.start(),
                            match_length=len(match.group()),
                            context_line=line,
                        ))
                container["done"] = True
            except Exception as e:
                container["error"] = e

        thread = threading.Thread(target=_do_search, daemon=True)
        thread.start()
        thread.join(timeout=_REGEX_TIMEOUT_SECONDS)

        if not container["done"] and container["error"] is None:
            raise _RegexTimeoutError(
                f"정규식 검색이 {_REGEX_TIMEOUT_SECONDS}초 제한을 초과했습니다."
            )
        if container["error"] is not None:
            raise _RegexTimeoutError(str(container["error"]))

        return results
