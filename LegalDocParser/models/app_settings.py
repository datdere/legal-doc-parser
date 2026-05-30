from dataclasses import dataclass, field

from .enums import OutputFormat, TableExtractionMode, OcrLanguage


@dataclass
class AppSettings:
    python_path: str = "python"
    default_output_dir: str = ""
    default_format: OutputFormat = OutputFormat.MARKDOWN
    default_table_mode: TableExtractionMode = TableExtractionMode.LOCAL
    default_ocr_lang: OcrLanguage = OcrLanguage.NONE
    default_ai_safety_filter: bool = True
    batch_concurrency: int = 3
    process_timeout_seconds: int = 300
    hybrid_server_url: str = "http://localhost:5002"

    def to_dict(self) -> dict:
        return {
            "python_path": self.python_path,
            "default_output_dir": self.default_output_dir,
            "default_format": self.default_format.value,
            "default_table_mode": self.default_table_mode.value,
            "default_ocr_lang": self.default_ocr_lang.value,
            "default_ai_safety_filter": self.default_ai_safety_filter,
            "batch_concurrency": self.batch_concurrency,
            "process_timeout_seconds": self.process_timeout_seconds,
            "hybrid_server_url": self.hybrid_server_url,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "AppSettings":
        return cls(
            python_path=data.get("python_path", "python"),
            default_output_dir=data.get("default_output_dir", ""),
            default_format=OutputFormat(data.get("default_format", "markdown")),
            default_table_mode=TableExtractionMode(data.get("default_table_mode", "local")),
            default_ocr_lang=OcrLanguage(data.get("default_ocr_lang", "none")),
            default_ai_safety_filter=data.get("default_ai_safety_filter", True),
            batch_concurrency=data.get("batch_concurrency", 3),
            process_timeout_seconds=data.get("process_timeout_seconds", 300),
            hybrid_server_url=data.get("hybrid_server_url", "http://localhost:5002"),
        )
