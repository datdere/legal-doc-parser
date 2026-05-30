import os
import tkinter as tk
from tkinter import ttk
from typing import Callable, Optional

from models.document_info import DocumentInfo


class FileListPanel(ttk.Frame):
    def __init__(self, parent: tk.Widget, **kwargs):
        super().__init__(parent, **kwargs)
        self._documents: list[DocumentInfo] = []
        self._on_select: Optional[Callable[[DocumentInfo], None]] = None
        self._on_add: Optional[Callable[[list[DocumentInfo]], None]] = None
        self._build_ui()

    def set_on_select(self, callback: Callable[[DocumentInfo], None]) -> None:
        self._on_select = callback

    def set_on_add(self, callback: Callable[[list[DocumentInfo]], None]) -> None:
        self._on_add = callback

    @property
    def documents(self) -> list[DocumentInfo]:
        return list(self._documents)

    def add_files(self, paths: list[str]) -> None:
        existing = {doc.file_path for doc in self._documents}
        new_docs: list[DocumentInfo] = []
        for path in paths:
            if path.lower().endswith(".pdf") and path not in existing:
                doc = DocumentInfo(file_path=path)
                self._documents.append(doc)
                new_docs.append(doc)
                self._tree.insert("", tk.END, values=(doc.file_name, doc.file_size_display))
        if new_docs and self._on_add:
            self._on_add(new_docs)

    def remove_selected(self) -> None:
        selected = self._tree.selection()
        for item in reversed(selected):
            idx = self._tree.index(item)
            self._documents.pop(idx)
            self._tree.delete(item)

    def clear_all(self) -> None:
        self._documents.clear()
        for item in self._tree.get_children():
            self._tree.delete(item)

    def get_selected_document(self) -> Optional[DocumentInfo]:
        selected = self._tree.selection()
        if selected:
            idx = self._tree.index(selected[0])
            return self._documents[idx]
        return None

    def _build_ui(self) -> None:
        toolbar = ttk.Frame(self)
        toolbar.pack(fill=tk.X, padx=2, pady=2)

        ttk.Label(toolbar, text="파일 목록", font=("", 10, "bold")).pack(side=tk.LEFT, padx=4)

        btn_clear = ttk.Button(toolbar, text="전체 삭제", width=8, command=self.clear_all)
        btn_clear.pack(side=tk.RIGHT, padx=2)

        btn_remove = ttk.Button(toolbar, text="삭제", width=6, command=self.remove_selected)
        btn_remove.pack(side=tk.RIGHT, padx=2)

        tree_frame = ttk.Frame(self)
        tree_frame.pack(fill=tk.BOTH, expand=True, padx=2, pady=2)

        self._tree = ttk.Treeview(
            tree_frame, columns=("name", "size"), show="headings", selectmode="extended"
        )
        self._tree.heading("name", text="파일명")
        self._tree.heading("size", text="크기")
        self._tree.column("name", width=200)
        self._tree.column("size", width=80, anchor=tk.E)

        scrollbar = ttk.Scrollbar(tree_frame, orient=tk.VERTICAL, command=self._tree.yview)
        self._tree.configure(yscrollcommand=scrollbar.set)

        self._tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        self._tree.bind("<<TreeviewSelect>>", self._on_tree_select)

    def _on_tree_select(self, event: tk.Event) -> None:
        doc = self.get_selected_document()
        if doc and self._on_select:
            self._on_select(doc)
