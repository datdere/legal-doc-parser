import tkinter as tk
from tkinter import ttk
from typing import Callable, Optional

from models.search_result import SearchResult


class BottomTabPanel(ttk.Frame):
    def __init__(self, parent: tk.Widget, **kwargs):
        super().__init__(parent, **kwargs)
        self._on_search: Optional[Callable[[str, bool, bool], None]] = None
        self._on_result_select: Optional[Callable[[SearchResult], None]] = None
        self._search_results: list[SearchResult] = []
        self._build_ui()

    def set_on_search(self, callback: Callable[[str, bool, bool], None]) -> None:
        self._on_search = callback

    def set_on_result_select(self, callback: Callable[[SearchResult], None]) -> None:
        self._on_result_select = callback

    def _build_ui(self) -> None:
        self._notebook = ttk.Notebook(self)
        self._notebook.pack(fill=tk.BOTH, expand=True)

        # Log tab
        log_frame = ttk.Frame(self._notebook)
        self._notebook.add(log_frame, text="로그")

        self._log_text = tk.Text(log_frame, height=8, wrap=tk.WORD, state=tk.DISABLED, font=("Courier", 9))
        log_scroll = ttk.Scrollbar(log_frame, orient=tk.VERTICAL, command=self._log_text.yview)
        self._log_text.configure(yscrollcommand=log_scroll.set)
        self._log_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        log_scroll.pack(side=tk.RIGHT, fill=tk.Y)

        self._log_text.tag_configure("info", foreground="#333333")
        self._log_text.tag_configure("warning", foreground="#cc8800")
        self._log_text.tag_configure("error", foreground="#cc0000")
        self._log_text.tag_configure("success", foreground="#008800")

        # Search tab
        search_frame = ttk.Frame(self._notebook)
        self._notebook.add(search_frame, text="검색")

        search_toolbar = ttk.Frame(search_frame)
        search_toolbar.pack(fill=tk.X, padx=4, pady=4)

        self._search_entry = ttk.Entry(search_toolbar, width=40)
        self._search_entry.pack(side=tk.LEFT, padx=2)
        self._search_entry.bind("<Return>", lambda e: self._do_search())

        self._regex_var = tk.BooleanVar(value=False)
        ttk.Checkbutton(search_toolbar, text="정규식", variable=self._regex_var).pack(side=tk.LEFT, padx=4)

        self._case_var = tk.BooleanVar(value=False)
        ttk.Checkbutton(search_toolbar, text="대소문자 구분", variable=self._case_var).pack(side=tk.LEFT, padx=4)

        ttk.Button(search_toolbar, text="검색", command=self._do_search).pack(side=tk.LEFT, padx=4)

        self._results_tree = ttk.Treeview(
            search_frame,
            columns=("line", "column", "match", "context"),
            show="headings",
            height=6,
        )
        self._results_tree.heading("line", text="행")
        self._results_tree.heading("column", text="열")
        self._results_tree.heading("match", text="매칭 텍스트")
        self._results_tree.heading("context", text="문맥")
        self._results_tree.column("line", width=50, anchor=tk.CENTER)
        self._results_tree.column("column", width=50, anchor=tk.CENTER)
        self._results_tree.column("match", width=150)
        self._results_tree.column("context", width=400)

        results_scroll = ttk.Scrollbar(search_frame, orient=tk.VERTICAL, command=self._results_tree.yview)
        self._results_tree.configure(yscrollcommand=results_scroll.set)
        self._results_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=4, pady=2)
        results_scroll.pack(side=tk.RIGHT, fill=tk.Y, pady=2)

        self._results_tree.bind("<<TreeviewSelect>>", self._on_result_clicked)

    def log(self, message: str, level: str = "info") -> None:
        self._log_text.configure(state=tk.NORMAL)
        self._log_text.insert(tk.END, message + "\n", level)
        self._log_text.see(tk.END)
        self._log_text.configure(state=tk.DISABLED)

    def clear_log(self) -> None:
        self._log_text.configure(state=tk.NORMAL)
        self._log_text.delete("1.0", tk.END)
        self._log_text.configure(state=tk.DISABLED)

    def show_search_results(self, results: list[SearchResult]) -> None:
        self._search_results = results
        for item in self._results_tree.get_children():
            self._results_tree.delete(item)
        for r in results:
            self._results_tree.insert("", tk.END, values=(r.line_number, r.column_start, r.matched_text, r.context_line))

    def _do_search(self) -> None:
        pattern = self._search_entry.get().strip()
        if pattern and self._on_search:
            self._on_search(pattern, self._regex_var.get(), self._case_var.get())

    def _on_result_clicked(self, event: tk.Event) -> None:
        selected = self._results_tree.selection()
        if selected and self._on_result_select:
            idx = self._results_tree.index(selected[0])
            if idx < len(self._search_results):
                self._on_result_select(self._search_results[idx])
