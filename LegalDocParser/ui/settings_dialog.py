import tkinter as tk
from tkinter import ttk, filedialog
from typing import Optional

from models.app_settings import AppSettings
from models.enums import OutputFormat, TableExtractionMode, OcrLanguage


class SettingsDialog(tk.Toplevel):
    def __init__(self, parent: tk.Widget, settings: AppSettings):
        super().__init__(parent)
        self.title("설정")
        self.geometry("500x450")
        self.resizable(False, False)
        self.transient(parent)
        self.grab_set()

        self._settings = settings
        self._result: Optional[AppSettings] = None
        self._build_ui()
        self._load_values()

    @property
    def result(self) -> Optional[AppSettings]:
        return self._result

    def _build_ui(self) -> None:
        main = ttk.Frame(self, padding=16)
        main.pack(fill=tk.BOTH, expand=True)

        row = 0
        ttk.Label(main, text="Python 경로:").grid(row=row, column=0, sticky=tk.W, pady=4)
        python_frame = ttk.Frame(main)
        python_frame.grid(row=row, column=1, sticky=tk.EW, pady=4)
        self._python_entry = ttk.Entry(python_frame, width=35)
        self._python_entry.pack(side=tk.LEFT, fill=tk.X, expand=True)
        ttk.Button(python_frame, text="찾기", width=5,
                   command=self._browse_python).pack(side=tk.RIGHT, padx=(4, 0))

        row += 1
        ttk.Label(main, text="출력 디렉토리:").grid(row=row, column=0, sticky=tk.W, pady=4)
        dir_frame = ttk.Frame(main)
        dir_frame.grid(row=row, column=1, sticky=tk.EW, pady=4)
        self._dir_entry = ttk.Entry(dir_frame, width=35)
        self._dir_entry.pack(side=tk.LEFT, fill=tk.X, expand=True)
        ttk.Button(dir_frame, text="찾기", width=5,
                   command=self._browse_dir).pack(side=tk.RIGHT, padx=(4, 0))

        row += 1
        ttk.Label(main, text="기본 출력 형식:").grid(row=row, column=0, sticky=tk.W, pady=4)
        self._format_var = tk.StringVar()
        fmt_combo = ttk.Combobox(main, textvariable=self._format_var, state="readonly", width=15)
        fmt_combo["values"] = [f.value for f in OutputFormat]
        fmt_combo.grid(row=row, column=1, sticky=tk.W, pady=4)

        row += 1
        ttk.Label(main, text="기본 테이블 모드:").grid(row=row, column=0, sticky=tk.W, pady=4)
        self._table_var = tk.StringVar()
        table_combo = ttk.Combobox(main, textvariable=self._table_var, state="readonly", width=15)
        table_combo["values"] = [t.value for t in TableExtractionMode]
        table_combo.grid(row=row, column=1, sticky=tk.W, pady=4)

        row += 1
        ttk.Label(main, text="기본 OCR 언어:").grid(row=row, column=0, sticky=tk.W, pady=4)
        self._ocr_var = tk.StringVar()
        ocr_combo = ttk.Combobox(main, textvariable=self._ocr_var, state="readonly", width=15)
        ocr_combo["values"] = [o.value for o in OcrLanguage]
        ocr_combo.grid(row=row, column=1, sticky=tk.W, pady=4)

        row += 1
        self._filter_var = tk.BooleanVar()
        ttk.Checkbutton(main, text="AI 안전 필터 활성화", variable=self._filter_var).grid(
            row=row, column=0, columnspan=2, sticky=tk.W, pady=4)

        row += 1
        ttk.Label(main, text="배치 동시 처리 수:").grid(row=row, column=0, sticky=tk.W, pady=4)
        self._concurrency_spin = ttk.Spinbox(main, from_=1, to=10, width=5)
        self._concurrency_spin.grid(row=row, column=1, sticky=tk.W, pady=4)

        row += 1
        ttk.Label(main, text="프로세스 시간 제한 (초):").grid(row=row, column=0, sticky=tk.W, pady=4)
        self._timeout_spin = ttk.Spinbox(main, from_=30, to=3600, width=8)
        self._timeout_spin.grid(row=row, column=1, sticky=tk.W, pady=4)

        row += 1
        ttk.Label(main, text="하이브리드 서버 URL:").grid(row=row, column=0, sticky=tk.W, pady=4)
        self._server_entry = ttk.Entry(main, width=30)
        self._server_entry.grid(row=row, column=1, sticky=tk.W, pady=4)

        main.columnconfigure(1, weight=1)

        btn_frame = ttk.Frame(self, padding=(16, 0, 16, 16))
        btn_frame.pack(fill=tk.X)

        ttk.Button(btn_frame, text="취소", command=self.destroy).pack(side=tk.RIGHT, padx=4)
        ttk.Button(btn_frame, text="저장", command=self._save).pack(side=tk.RIGHT, padx=4)

    def _load_values(self) -> None:
        s = self._settings
        self._python_entry.insert(0, s.python_path)
        self._dir_entry.insert(0, s.default_output_dir)
        self._format_var.set(s.default_format.value)
        self._table_var.set(s.default_table_mode.value)
        self._ocr_var.set(s.default_ocr_lang.value)
        self._filter_var.set(s.default_ai_safety_filter)
        self._concurrency_spin.set(s.batch_concurrency)
        self._timeout_spin.set(s.process_timeout_seconds)
        self._server_entry.insert(0, s.hybrid_server_url)

    def _browse_python(self) -> None:
        path = filedialog.askopenfilename(title="Python 실행 파일 선택")
        if path:
            self._python_entry.delete(0, tk.END)
            self._python_entry.insert(0, path)

    def _browse_dir(self) -> None:
        path = filedialog.askdirectory(title="출력 디렉토리 선택")
        if path:
            self._dir_entry.delete(0, tk.END)
            self._dir_entry.insert(0, path)

    def _save(self) -> None:
        self._result = AppSettings(
            python_path=self._python_entry.get().strip() or "python",
            default_output_dir=self._dir_entry.get().strip(),
            default_format=OutputFormat(self._format_var.get()),
            default_table_mode=TableExtractionMode(self._table_var.get()),
            default_ocr_lang=OcrLanguage(self._ocr_var.get()),
            default_ai_safety_filter=self._filter_var.get(),
            batch_concurrency=int(self._concurrency_spin.get()),
            process_timeout_seconds=int(self._timeout_spin.get()),
            hybrid_server_url=self._server_entry.get().strip(),
        )
        self.destroy()
