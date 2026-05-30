from enum import Enum


class OutputFormat(str, Enum):
    MARKDOWN = "markdown"
    JSON = "json"
    HTML = "html"
    TEXT = "text"

    @property
    def extension(self) -> str:
        return {
            OutputFormat.MARKDOWN: ".md",
            OutputFormat.JSON: ".json",
            OutputFormat.HTML: ".html",
            OutputFormat.TEXT: ".txt",
        }[self]


class TableExtractionMode(str, Enum):
    LOCAL = "local"
    HYBRID = "hybrid"


class OcrLanguage(str, Enum):
    NONE = "none"
    KOREAN = "ko"
    ENGLISH = "en"
    BOTH = "ko,en"
