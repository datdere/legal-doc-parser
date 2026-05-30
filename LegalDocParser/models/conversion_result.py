from dataclasses import dataclass, field
from typing import Optional


@dataclass
class ConversionResult:
    success: bool = False
    content: str = ""
    error_message: str = ""
    duration_seconds: float = 0.0
    warnings: list[str] = field(default_factory=list)
    ai_filter_warnings: list[str] = field(default_factory=list)
