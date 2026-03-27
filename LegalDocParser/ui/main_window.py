import os
import threading
import tkinter as tk
from tkinter import ttk, filedialog, messagebox

from models.conversion_options import ConversionOptions
from models.conversion_result import ConversionResult
from models.document_info import DocumentInfo
from models.enums import OutputFormat, TableExtractionMode, OcrLanguage
from services.file_export_service import FileExportService
from services.pdf_conversion_service import PdfConversionService
from services.search_service import SearchService
from services.settings_service import SettingsService
from ui.controls.bottom_tab_panel import BottomTabPanel
from ui.controls.conversion_progress_panel import ConversionProgressPanel
from ui.controls.file_list_panel import FileListPanel
from ui.controls.split_viewer_panel import SplitViewerPanel
from ui.settings_dialog import SettingsDialog


class MainWindow:
    def __init__(self):
        self._root = tk.Tk()
        self._root.title("LegalDocParser - 법률 문서 파서")
        self._root.geometry("1200x800")
        self._root.minsize(800, 600)

        self._settings_service = SettingsService()
        self._settings_service.load()

        self._conversion_service = PdfConversionService(self._settings_service.settings)
        self._search_service = SearchService()
        self._export_service = FileExportService()

        self._current_document: DocumentInfo | None = None
        self._current_format = self._settings_service.settings.default_format

        self._build_menu()
        self._build_ui()
        self._connect_events()

        self._log("LegalDocParser가 시작되었습니다.", "success")

    def run(self) -> None:
        self._root.mainloop()

    def _build_menu(self) -> None:
        menubar = tk.Menu(self._root)
        self._root.config(menu=menubar)

        file_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="파일", menu=file_menu)
        file_menu.add_command(label="PDF 파일 열기...", command=self._open_files, accelerator="Ctrl+O")
        file_menu.add_command(label="폴더 열기...", command=self._open_folder)
        file_menu.add_separator()
        file_menu.add_command(label="결과 저장...", command=self._save_result, accelerator="Ctrl+S")
        file_menu.add_command(label="배치 저장...", command=self._batch_save)
        file_menu.add_separator()
        file_menu.add_command(label="클립보드에 복사", command=self._copy_to_clipboard, accelerator="Ctrl+C")
        file_menu.add_separator()
        file_menu.add_command(label="종료", command=self._root.quit)

        convert_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="변환", menu=convert_menu)
        convert_menu.add_command(label="선택 파일 변환", command=self._convert_selected, accelerator="F5")
        convert_menu.add_command(label="전체 배치 변환", command=self._convert_batch, accelerator="F6")
        convert_menu.add_separator()

        self._format_var = tk.StringVar(value=self._settings_service.settings.default_format.value)
        format_menu = tk.Menu(convert_menu, tearoff=0)
        convert_menu.add_cascade(label="출력 형식", menu=format_menu)
        for fmt in OutputFormat:
            format_menu.add_radiobutton(
                label=fmt.value.capitalize(), value=fmt.value, variable=self._format_var,
                command=self._on_format_changed,
            )

        self._table_var = tk.StringVar(value=self._settings_service.settings.default_table_mode.value)
        table_menu = tk.Menu(convert_menu, tearoff=0)
        convert_menu.add_cascade(label="테이블 추출 모드", menu=table_menu)
        for mode in TableExtractionMode:
            table_menu.add_radiobutton(label=mode.value.capitalize(), value=mode.value, variable=self._table_var)

        self._ocr_var = tk.StringVar(value=self._settings_service.settings.default_ocr_lang.value)
        ocr_menu = tk.Menu(convert_menu, tearoff=0)
        convert_menu.add_cascade(label="OCR 언어", menu=ocr_menu)
        ocr_labels = {"none": "없음", "ko": "한국어", "en": "영어", "ko,en": "한국어+영어"}
        for lang in OcrLanguage:
            ocr_menu.add_radiobutton(label=ocr_labels[lang.value], value=lang.value, variable=self._ocr_var)

        settings_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="설정", menu=settings_menu)
        settings_menu.add_command(label="환경 설정...", command=self._open_settings)
        settings_menu.add_command(label="Python 환경 확인", command=self._validate_python)
        settings_menu.add_separator()
        settings_menu.add_command(label="정보", command=self._show_about)

        self._root.bind("<Control-o>", lambda e: self._open_files())
        self._root.bind("<Control-s>", lambda e: self._save_result())
        self._root.bind("<F5>", lambda e: self._convert_selected())
        self._root.bind("<F6>", lambda e: self._convert_batch())

    def _build_ui(self) -> None:
        main_paned = ttk.PanedWindow(self._root, orient=tk.HORIZONTAL)
        main_paned.pack(fill=tk.BOTH, expand=True, padx=4, pady=4)

        self._file_list = FileListPanel(main_paned)
        main_paned.add(self._file_list, weight=1)

        right_paned = ttk.PanedWindow(main_paned, orient=tk.VERTICAL)
        main_paned.add(right_paned, weight=3)

        self._viewer = SplitViewerPanel(right_paned)
        right_paned.add(self._viewer, weight=3)

        self._bottom_panel = BottomTabPanel(right_paned)
        right_paned.add(self._bottom_panel, weight=1)

        self._progress_panel = ConversionProgressPanel(self._root)

        self._status_var = tk.StringVar(value="준비")
        status_bar = ttk.Label(self._root, textvariable=self._status_var, relief=tk.SUNKEN, anchor=tk.W)
        status_bar.pack(fill=tk.X, side=tk.BOTTOM, padx=4, pady=2)

    def _connect_events(self) -> None:
        self._file_list.set_on_select(self._on_document_selected)
        self._bottom_panel.set_on_search(self._on_search)
        self._bottom_panel.set_on_result_select(self._on_search_result_select)
        self._progress_panel.set_on_cancel(lambda: None)

    def _log(self, message: str, level: str = "info") -> None:
        self._bottom_panel.log(message, level)

    def _set_status(self, text: str) -> None:
        self._status_var.set(text)

    def _open_files(self) -> None:
        paths = filedialog.askopenfilenames(
            title="PDF 파일 선택",
            filetypes=[("PDF 파일", "*.pdf"), ("모든 파일", "*.*")],
        )
        if paths:
            self._file_list.add_files(list(paths))
            self._log(f"{len(paths)}개 파일이 추가되었습니다.")

    def _open_folder(self) -> None:
        folder = filedialog.askdirectory(title="PDF 폴더 선택")
        if folder:
            pdf_files = [
                os.path.join(folder, f)
                for f in os.listdir(folder)
                if f.lower().endswith(".pdf")
            ]
            if pdf_files:
                self._file_list.add_files(pdf_files)
                self._log(f"폴더에서 {len(pdf_files)}개 PDF 파일이 추가되었습니다.")
            else:
                self._log("폴더에 PDF 파일이 없습니다.", "warning")

    def _save_result(self) -> None:
        if not self._current_document or not self._current_document.last_conversion:
            messagebox.showwarning("저장", "저장할 변환 결과가 없습니다.")
            return

        fmt = OutputFormat(self._format_var.get())
        default_name = os.path.splitext(self._current_document.file_name)[0] + fmt.extension

        path = filedialog.asksaveasfilename(
            title="결과 저장",
            initialfile=default_name,
            defaultextension=fmt.extension,
        )
        if path:
            success = self._export_service.save(self._current_document.last_conversion, path, fmt)
            if success:
                self._log(f"저장 완료: {path}", "success")
            else:
                self._log("저장 실패", "error")

    def _batch_save(self) -> None:
        docs = self._file_list.documents
        items = [(d.file_path, d.last_conversion) for d in docs if d.last_conversion and d.last_conversion.success]
        if not items:
            messagebox.showwarning("배치 저장", "저장할 변환 결과가 없습니다.")
            return

        folder = filedialog.askdirectory(title="배치 저장 폴더 선택")
        if folder:
            fmt = OutputFormat(self._format_var.get())
            results = self._export_service.save_batch(items, folder, fmt)
            ok_count = sum(1 for _, ok in results if ok)
            self._log(f"배치 저장 완료: {ok_count}/{len(results)} 성공", "success")

    def _copy_to_clipboard(self) -> None:
        content = self._viewer.get_raw_content()
        if content:
            self._root.clipboard_clear()
            self._root.clipboard_append(content)
            self._log("클립보드에 복사되었습니다.", "success")

    def _get_conversion_options(self) -> ConversionOptions:
        settings = self._settings_service.settings
        return ConversionOptions(
            format=OutputFormat(self._format_var.get()),
            table_mode=TableExtractionMode(self._table_var.get()),
            ocr_lang=OcrLanguage(self._ocr_var.get()),
            enable_ai_safety_filter=settings.default_ai_safety_filter,
        )

    def _convert_selected(self) -> None:
        doc = self._file_list.get_selected_document()
        if not doc:
            messagebox.showwarning("변환", "변환할 파일을 선택하세요.")
            return

        self._set_status(f"변환 중: {doc.file_name}")
        self._log(f"변환 시작: {doc.file_name}")
        options = self._get_conversion_options()

        def do_convert():
            result = self._conversion_service.convert(doc.file_path, options)
            self._root.after(0, lambda: self._on_conversion_done(doc, result))

        threading.Thread(target=do_convert, daemon=True).start()

    def _on_conversion_done(self, doc: DocumentInfo, result: ConversionResult) -> None:
        doc.last_conversion = result
        if result.success:
            fmt = OutputFormat(self._format_var.get())
            self._viewer.show_result(result.content, fmt)
            self._log(f"변환 완료: {doc.file_name} ({result.duration_seconds:.1f}초)", "success")
            for w in result.warnings:
                self._log(f"  경고: {w}", "warning")
            for w in result.ai_filter_warnings:
                self._log(f"  안전 필터: {w}", "warning")
        else:
            self._log(f"변환 실패: {doc.file_name} - {result.error_message}", "error")
        self._set_status("준비")

    def _convert_batch(self) -> None:
        docs = self._file_list.documents
        if not docs:
            messagebox.showwarning("배치 변환", "변환할 파일이 없습니다.")
            return

        paths = [d.file_path for d in docs]
        options = self._get_conversion_options()
        total = len(paths)

        self._progress_panel.show(total)
        self._log(f"배치 변환 시작: {total}개 파일")

        def do_batch():
            results = self._conversion_service.convert_batch(
                paths, options,
                on_progress=lambda c, t, f: self._root.after(
                    0, lambda: self._progress_panel.update_progress(c, t, f)
                ),
                cancel_check=lambda: self._progress_panel.is_cancelled,
            )
            self._root.after(0, lambda: self._on_batch_done(docs, results))

        threading.Thread(target=do_batch, daemon=True).start()

    def _on_batch_done(self, docs: list[DocumentInfo], results: list[tuple[str, ConversionResult]]) -> None:
        result_map = {path: result for path, result in results}
        ok_count = 0
        for doc in docs:
            if doc.file_path in result_map:
                doc.last_conversion = result_map[doc.file_path]
                if result_map[doc.file_path].success:
                    ok_count += 1

        self._progress_panel.hide()
        self._log(f"배치 변환 완료: {ok_count}/{len(results)} 성공", "success")
        self._set_status("준비")

    def _on_document_selected(self, doc: DocumentInfo) -> None:
        self._current_document = doc
        info_lines = [
            f"파일명: {doc.file_name}",
            f"경로: {doc.file_path}",
            f"크기: {doc.file_size_display}",
        ]
        if doc.last_modified:
            info_lines.append(f"수정일: {doc.last_modified.strftime('%Y-%m-%d %H:%M:%S')}")

        self._viewer.show_pdf_info("\n".join(info_lines))

        if doc.last_conversion and doc.last_conversion.success:
            fmt = OutputFormat(self._format_var.get())
            self._viewer.show_result(doc.last_conversion.content, fmt)
        else:
            self._viewer.clear()
            self._viewer.show_pdf_info("\n".join(info_lines))

    def _on_search(self, pattern: str, use_regex: bool, case_sensitive: bool) -> None:
        content = self._viewer.get_raw_content()
        if not content:
            self._log("검색할 내용이 없습니다.", "warning")
            return

        results = self._search_service.search(content, pattern, use_regex, case_sensitive)
        self._bottom_panel.show_search_results(results)
        self._log(f"검색 결과: '{pattern}' - {len(results)}건 발견")

    def _on_search_result_select(self, result) -> None:
        self._log(f"행 {result.line_number}: {result.context_line.strip()}")

    def _on_format_changed(self) -> None:
        self._current_format = OutputFormat(self._format_var.get())
        if self._current_document and self._current_document.last_conversion:
            if self._current_document.last_conversion.success:
                self._viewer.show_result(
                    self._current_document.last_conversion.content,
                    self._current_format,
                )

    def _open_settings(self) -> None:
        dialog = SettingsDialog(self._root, self._settings_service.settings)
        self._root.wait_window(dialog)
        if dialog.result:
            self._settings_service.save(dialog.result)
            self._conversion_service.update_settings(dialog.result)
            self._log("설정이 저장되었습니다.", "success")

    def _validate_python(self) -> None:
        ok, msg = self._conversion_service.validate_python()
        if ok:
            messagebox.showinfo("Python 환경", msg)
            self._log(msg, "success")
        else:
            messagebox.showerror("Python 환경", msg)
            self._log(msg, "error")

    def _show_about(self) -> None:
        messagebox.showinfo(
            "정보",
            "LegalDocParser v1.0\n\n"
            "법률 문서 PDF 파싱 도구\n"
            "Python + tkinter\n\n"
            "PDF 변환: opendataloader-pdf\n"
            "AI API 미사용 - 로컬 처리 전용",
        )
