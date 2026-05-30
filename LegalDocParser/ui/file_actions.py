import os
import tkinter as tk
from tkinter import filedialog, messagebox
from typing import Callable

from models.document_info import DocumentInfo
from models.enums import OutputFormat
from services.file_export_service import FileExportService


class FileActions:
    def __init__(
        self,
        root: tk.Tk,
        export_service: FileExportService,
        log: Callable[[str, str], None],
        get_documents: Callable[[], list[DocumentInfo]],
        get_current_doc: Callable[[], DocumentInfo | None],
        get_raw_content: Callable[[], str],
        get_format: Callable[[], OutputFormat],
    ):
        self._root = root
        self._export = export_service
        self._log = log
        self._get_documents = get_documents
        self._get_current_doc = get_current_doc
        self._get_raw_content = get_raw_content
        self._get_format = get_format

    def open_files(self, add_files: Callable[[list[str]], None]) -> None:
        paths = filedialog.askopenfilenames(
            title="PDF 파일 선택",
            filetypes=[("PDF 파일", "*.pdf"), ("모든 파일", "*.*")],
        )
        if paths:
            add_files(list(paths))
            self._log(f"{len(paths)}개 파일이 추가되었습니다.", "info")

    def open_folder(self, add_files: Callable[[list[str]], None]) -> None:
        folder = filedialog.askdirectory(title="PDF 폴더 선택")
        if folder:
            pdf_files = [
                os.path.join(folder, f)
                for f in os.listdir(folder)
                if f.lower().endswith(".pdf")
            ]
            if pdf_files:
                add_files(pdf_files)
                self._log(f"폴더에서 {len(pdf_files)}개 PDF 파일이 추가되었습니다.", "info")
            else:
                self._log("폴더에 PDF 파일이 없습니다.", "warning")

    def save_result(self) -> None:
        doc = self._get_current_doc()
        if not doc or not doc.last_conversion:
            messagebox.showwarning("저장", "저장할 변환 결과가 없습니다.")
            return

        fmt = self._get_format()
        default_name = os.path.splitext(doc.file_name)[0] + fmt.extension

        path = filedialog.asksaveasfilename(
            title="결과 저장",
            initialfile=default_name,
            defaultextension=fmt.extension,
        )
        if path:
            success = self._export.save(doc.last_conversion, path, fmt)
            if success:
                self._log(f"저장 완료: {path}", "success")
            else:
                self._log("저장 실패", "error")

    def batch_save(self) -> None:
        docs = self._get_documents()
        items = [
            (d.file_path, d.last_conversion)
            for d in docs
            if d.last_conversion and d.last_conversion.success
        ]
        if not items:
            messagebox.showwarning("배치 저장", "저장할 변환 결과가 없습니다.")
            return

        folder = filedialog.askdirectory(title="배치 저장 폴더 선택")
        if folder:
            fmt = self._get_format()
            results = self._export.save_batch(items, folder, fmt)
            ok_count = sum(1 for _, ok in results if ok)
            self._log(f"배치 저장 완료: {ok_count}/{len(results)} 성공", "success")

    def copy_to_clipboard(self) -> None:
        content = self._get_raw_content()
        if content:
            self._root.clipboard_clear()
            self._root.clipboard_append(content)
            self._log("클립보드에 복사되었습니다.", "success")
