from dataclasses import dataclass, field

from .enums import OutputFormat, TableExtractionMode, OcrLanguage


@dataclass
class ConversionOptions:
    format: OutputFormat = OutputFormat.MARKDOWN
    table_mode: TableExtractionMode = TableExtractionMode.LOCAL
    ocr_lang: OcrLanguage = OcrLanguage.NONE
    use_tagged_pdf: bool = False
    enable_ai_safety_filter: bool = True
    page_range: str = ""
