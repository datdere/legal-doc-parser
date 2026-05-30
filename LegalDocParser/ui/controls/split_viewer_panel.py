import tkinter as tk
from tkinter import ttk
from typing import Optional

from models.enums import OutputFormat
from services.file_export_service import FileExportService


class SplitViewerPanel(ttk.Frame):
    def __init__(self, parent: tk.Widget, **kwargs):
        super().__init__(parent, **kwargs)
        self._build_ui()

    def _build_ui(self) -> None:
        paned = ttk.PanedWindow(self, orient=tk.HORIZONTAL)
        paned.pack(fill=tk.BOTH, expand=True)

        left_frame = ttk.LabelFrame(paned, text="원본 PDF 정보")
        paned.add(left_frame, weight=1)

        self._pdf_info = tk.Text(left_frame, wrap=tk.WORD, state=tk.DISABLED, bg="#f9f9f9")
        self._pdf_info.pack(fill=tk.BOTH, expand=True, padx=4, pady=4)

        right_frame = ttk.Frame(paned)
        paned.add(right_frame, weight=2)

        self._notebook = ttk.Notebook(right_frame)
        self._notebook.pack(fill=tk.BOTH, expand=True)

        render_frame = ttk.Frame(self._notebook)
        self._notebook.add(render_frame, text="렌더링")

        self._render_text = tk.Text(render_frame, wrap=tk.WORD, state=tk.DISABLED)
        render_scroll = ttk.Scrollbar(render_frame, orient=tk.VERTICAL, command=self._render_text.yview)
        self._render_text.configure(yscrollcommand=render_scroll.set)
        self._render_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        render_scroll.pack(side=tk.RIGHT, fill=tk.Y)

        text_frame = ttk.Frame(self._notebook)
        self._notebook.add(text_frame, text="텍스트")

        self._raw_text = tk.Text(text_frame, wrap=tk.WORD, state=tk.DISABLED, font=("Courier", 10))
        text_scroll = ttk.Scrollbar(text_frame, orient=tk.VERTICAL, command=self._raw_text.yview)
        self._raw_text.configure(yscrollcommand=text_scroll.set)
        self._raw_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        text_scroll.pack(side=tk.RIGHT, fill=tk.Y)

    def show_pdf_info(self, info_text: str) -> None:
        self._pdf_info.configure(state=tk.NORMAL)
        self._pdf_info.delete("1.0", tk.END)
        self._pdf_info.insert(tk.END, info_text)
        self._pdf_info.configure(state=tk.DISABLED)

    def show_result(self, content: str, fmt: OutputFormat) -> None:
        rendered = FileExportService.render_for_display(content, fmt)

        self._render_text.configure(state=tk.NORMAL)
        self._render_text.delete("1.0", tk.END)
        self._render_text.insert(tk.END, rendered)
        self._render_text.configure(state=tk.DISABLED)

        self._raw_text.configure(state=tk.NORMAL)
        self._raw_text.delete("1.0", tk.END)
        self._raw_text.insert(tk.END, content)
        self._raw_text.configure(state=tk.DISABLED)

    def clear(self) -> None:
        self._pdf_info.configure(state=tk.NORMAL)
        self._pdf_info.delete("1.0", tk.END)
        self._pdf_info.configure(state=tk.DISABLED)

        self._render_text.configure(state=tk.NORMAL)
        self._render_text.delete("1.0", tk.END)
        self._render_text.configure(state=tk.DISABLED)

        self._raw_text.configure(state=tk.NORMAL)
        self._raw_text.delete("1.0", tk.END)
        self._raw_text.configure(state=tk.DISABLED)

    def get_raw_content(self) -> str:
        return self._raw_text.get("1.0", tk.END).strip()
