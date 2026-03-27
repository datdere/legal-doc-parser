import tkinter as tk
from tkinter import ttk
from typing import Callable, Optional


class ConversionProgressPanel(ttk.Frame):
    def __init__(self, parent: tk.Widget, **kwargs):
        super().__init__(parent, **kwargs)
        self._cancelled = False
        self._on_cancel: Optional[Callable[[], None]] = None
        self._build_ui()
        self.hide()

    def set_on_cancel(self, callback: Callable[[], None]) -> None:
        self._on_cancel = callback

    @property
    def is_cancelled(self) -> bool:
        return self._cancelled

    def _build_ui(self) -> None:
        self._status_label = ttk.Label(self, text="대기 중...")
        self._status_label.pack(side=tk.LEFT, padx=8)

        self._progress = ttk.Progressbar(self, mode="determinate", length=300)
        self._progress.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=8)

        self._count_label = ttk.Label(self, text="0/0")
        self._count_label.pack(side=tk.LEFT, padx=8)

        self._cancel_btn = ttk.Button(self, text="취소", command=self._do_cancel)
        self._cancel_btn.pack(side=tk.RIGHT, padx=8)

    def show(self, total: int) -> None:
        self._cancelled = False
        self._progress["maximum"] = total
        self._progress["value"] = 0
        self._count_label.configure(text=f"0/{total}")
        self._status_label.configure(text="변환 중...")
        self._cancel_btn.configure(state=tk.NORMAL)
        self.pack(fill=tk.X, padx=4, pady=4)

    def hide(self) -> None:
        self.pack_forget()

    def update_progress(self, completed: int, total: int, current_file: str) -> None:
        self._progress["value"] = completed
        self._count_label.configure(text=f"{completed}/{total}")
        self._status_label.configure(text=f"변환 중: {current_file}")

    def _do_cancel(self) -> None:
        self._cancelled = True
        self._cancel_btn.configure(state=tk.DISABLED)
        self._status_label.configure(text="취소 중...")
        if self._on_cancel:
            self._on_cancel()
