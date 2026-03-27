from dataclasses import dataclass


@dataclass
class SearchResult:
    matched_text: str
    line_number: int
    column_start: int
    match_length: int
    context_line: str
