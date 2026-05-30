import os
from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional

from .conversion_result import ConversionResult


@dataclass
class DocumentInfo:
    file_path: str = ""
    last_conversion: Optional[ConversionResult] = None

    @property
    def file_name(self) -> str:
        return os.path.basename(self.file_path)

    @property
    def file_size(self) -> int:
        try:
            return os.path.getsize(self.file_path)
        except OSError:
            return 0

    @property
    def last_modified(self) -> Optional[datetime]:
        try:
            return datetime.fromtimestamp(os.path.getmtime(self.file_path))
        except OSError:
            return None

    @property
    def file_size_display(self) -> str:
        size = self.file_size
        if size < 1024:
            return f"{size} B"
        elif size < 1024 * 1024:
            return f"{size / 1024:.1f} KB"
        else:
            return f"{size / (1024 * 1024):.1f} MB"
