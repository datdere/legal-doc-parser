using LegalDocParser.Helpers;
using LegalDocParser.Models;
using LegalDocParser.Models.Enums;
using LegalDocParser.Services;
using LegalDocParser.Services.Interfaces;
using LegalDocParser.UI.Controls;

namespace LegalDocParser.UI;

/// <summary>
/// LegalDocParser 메인 폼
/// </summary>
public class MainForm : Form
{
    // Services
    private readonly ISettingsService _settingsService;
    private readonly IPdfConversionService _conversionService;
    private readonly ISearchService _searchService;
    private readonly IFileExportService _exportService;
    private AppSettings _settings;

    // UI Controls
    private readonly MenuStrip _menuStrip;
    private readonly SplitContainer _mainSplitContainer;
    private readonly SplitContainer _centerSplitContainer;
    private readonly FileListPanel _fileListPanel;
    private readonly SplitViewerPanel _splitViewerPanel;
    private readonly BottomTabPanel _bottomTabPanel;
    private readonly ConversionProgressPanel _progressPanel;
    private readonly StatusStrip _statusStrip;
    private readonly ToolStripStatusLabel _statusLabel;

    // Conversion options UI
    private ToolStripComboBox? _formatCombo;
    private ToolStripComboBox? _tableModeCombo;
    private ToolStripComboBox? _ocrCombo;

    public MainForm()
    {
        // Initialize services
        _settingsService = new SettingsService();
        _settings = _settingsService.Load();
        _conversionService = new PdfConversionService(_settings);
        _searchService = new SearchService();
        _exportService = new FileExportService();

        // Form setup
        Text = "LegalDocParser - 법률 문서 PDF 파싱 및 분석 도구";
        Size = new Size(1400, 900);
        MinimumSize = new Size(800, 600);
        StartPosition = FormStartPosition.CenterScreen;
        Font = new Font("맑은 고딕", 9f);
        AllowDrop = true;

        // Create controls
        _menuStrip = CreateMenuStrip();
        _fileListPanel = new FileListPanel();
        _splitViewerPanel = new SplitViewerPanel();
        _bottomTabPanel = new BottomTabPanel();
        _progressPanel = new ConversionProgressPanel();

        _statusStrip = new StatusStrip();
        _statusLabel = new ToolStripStatusLabel("준비 완료");
        _statusStrip.Items.Add(_statusLabel);

        // Layout
        _centerSplitContainer = new SplitContainer
        {
            Dock = DockStyle.Fill,
            Orientation = Orientation.Horizontal,
            SplitterDistance = 550,
            Panel2MinSize = 120
        };
        _centerSplitContainer.Panel1.Controls.Add(_splitViewerPanel);
        _centerSplitContainer.Panel2.Controls.Add(_bottomTabPanel);

        _mainSplitContainer = new SplitContainer
        {
            Dock = DockStyle.Fill,
            Orientation = Orientation.Vertical,
            SplitterDistance = 250,
            Panel1MinSize = 180
        };
        _mainSplitContainer.Panel1.Controls.Add(_fileListPanel);
        _mainSplitContainer.Panel2.Controls.Add(_centerSplitContainer);

        _progressPanel.Dock = DockStyle.Bottom;
        _splitViewerPanel.Dock = DockStyle.Fill;
        _bottomTabPanel.Dock = DockStyle.Fill;
        _fileListPanel.Dock = DockStyle.Fill;

        Controls.Add(_mainSplitContainer);
        Controls.Add(_progressPanel);
        Controls.Add(_menuStrip);
        Controls.Add(_statusStrip);

        MainMenuStrip = _menuStrip;

        // Event wiring
        _fileListPanel.DocumentSelected += OnDocumentSelected;
        _fileListPanel.DocumentsAdded += OnDocumentsAdded;
        _bottomTabPanel.SearchRequested += OnSearchRequested;
        _bottomTabPanel.SearchResultSelected += OnSearchResultSelected;
        _progressPanel.CancelRequested += (_, _) => _bottomTabPanel.Log("사용자가 변환을 취소했습니다.", BottomTabPanel.LogLevel.Warning);

        // Drag-drop on main form
        DragEnter += (_, e) =>
        {
            if (e.Data?.GetDataPresent(DataFormats.FileDrop) == true)
                e.Effect = DragDropEffects.Copy;
        };
        DragDrop += (_, e) =>
        {
            if (e.Data?.GetData(DataFormats.FileDrop) is string[] files)
                _fileListPanel.AddFiles(files);
        };

        // Keyboard shortcuts
        KeyPreview = true;
        KeyDown += OnKeyDown;

        _bottomTabPanel.Log("LegalDocParser가 시작되었습니다.", BottomTabPanel.LogLevel.Success);
    }

    private MenuStrip CreateMenuStrip()
    {
        var menuStrip = new MenuStrip();

        // === 파일 메뉴 ===
        var fileMenu = new ToolStripMenuItem("파일(&F)");
        fileMenu.DropDownItems.AddRange(new ToolStripItem[]
        {
            new ToolStripMenuItem("PDF 파일 추가(&O)", null, (_, _) => OpenFiles()) { ShortcutKeys = Keys.Control | Keys.O },
            new ToolStripMenuItem("폴더 추가(&D)", null, (_, _) => OpenFolder()),
            new ToolStripSeparator(),
            new ToolStripMenuItem("결과 저장(&S)", null, (_, _) => SaveResult()) { ShortcutKeys = Keys.Control | Keys.S },
            new ToolStripMenuItem("배치 결과 저장", null, (_, _) => SaveBatchResults()),
            new ToolStripSeparator(),
            new ToolStripMenuItem("클립보드에 복사(&C)", null, (_, _) => CopyToClipboard()) { ShortcutKeys = Keys.Control | Keys.Shift | Keys.C },
            new ToolStripSeparator(),
            new ToolStripMenuItem("종료(&X)", null, (_, _) => Close()) { ShortcutKeys = Keys.Alt | Keys.F4 }
        });

        // === 변환 메뉴 ===
        var convertMenu = new ToolStripMenuItem("변환(&C)");

        _formatCombo = new ToolStripComboBox("formatCombo")
        {
            DropDownStyle = ComboBoxStyle.DropDownList,
            ToolTipText = "출력 포맷",
            Width = 100
        };
        _formatCombo.Items.AddRange(new object[] { "Markdown", "JSON", "HTML", "Text" });
        _formatCombo.SelectedIndex = (int)_settings.DefaultFormat;

        _tableModeCombo = new ToolStripComboBox("tableModeCombo")
        {
            DropDownStyle = ComboBoxStyle.DropDownList,
            ToolTipText = "표 추출 모드",
            Width = 90
        };
        _tableModeCombo.Items.AddRange(new object[] { "로컬 (빠름)", "하이브리드 (정확)" });
        _tableModeCombo.SelectedIndex = (int)_settings.DefaultTableMode;

        _ocrCombo = new ToolStripComboBox("ocrCombo")
        {
            DropDownStyle = ComboBoxStyle.DropDownList,
            ToolTipText = "OCR 언어",
            Width = 110
        };
        _ocrCombo.Items.AddRange(new object[] { "OCR 없음", "한국어", "영어", "한국어+영어" });
        _ocrCombo.SelectedIndex = (int)_settings.DefaultOcrLang;

        convertMenu.DropDownItems.AddRange(new ToolStripItem[]
        {
            new ToolStripMenuItem("선택 파일 변환(&C)", null, async (_, _) => await ConvertSelected()) { ShortcutKeys = Keys.F5 },
            new ToolStripMenuItem("전체 일괄 변환(&B)", null, async (_, _) => await ConvertBatch()) { ShortcutKeys = Keys.Shift | Keys.F5 },
            new ToolStripSeparator(),
            new ToolStripLabel("출력 포맷:"),
            _formatCombo,
            new ToolStripLabel("표 추출:"),
            _tableModeCombo,
            new ToolStripLabel("OCR:"),
            _ocrCombo
        });

        // === 비교 메뉴 (Phase 2) ===
        var compareMenu = new ToolStripMenuItem("비교(&D)");
        compareMenu.DropDownItems.Add(new ToolStripMenuItem("PDF 비교 (Phase 2)", null) { Enabled = false });

        // === AI 분석 메뉴 (Phase 2) ===
        var aiMenu = new ToolStripMenuItem("AI 분석(&A)");
        aiMenu.DropDownItems.Add(new ToolStripMenuItem("Claude 분석 (Phase 2)", null) { Enabled = false });

        // === 설정 메뉴 ===
        var settingsMenu = new ToolStripMenuItem("설정(&S)");
        settingsMenu.DropDownItems.AddRange(new ToolStripItem[]
        {
            new ToolStripMenuItem("환경 설정(&P)", null, (_, _) => ShowSettings()),
            new ToolStripMenuItem("Python 환경 확인", null, async (_, _) => await ValidatePython()),
            new ToolStripSeparator(),
            new ToolStripMenuItem("LegalDocParser 정보", null, (_, _) => ShowAbout())
        });

        menuStrip.Items.AddRange(new ToolStripItem[] { fileMenu, convertMenu, compareMenu, aiMenu, settingsMenu });
        return menuStrip;
    }

    private ConversionOptions GetCurrentOptions()
    {
        return new ConversionOptions
        {
            Format = (OutputFormat)(_formatCombo?.SelectedIndex ?? 0),
            TableMode = (TableExtractionMode)(_tableModeCombo?.SelectedIndex ?? 0),
            OcrLang = (OcrLanguage)(_ocrCombo?.SelectedIndex ?? 0),
            UseTaggedPdf = false,
            EnableAiSafetyFilter = _settings.DefaultAiSafetyFilter
        };
    }

    // === Event Handlers ===

    private void OnDocumentSelected(object? sender, DocumentInfo doc)
    {
        _splitViewerPanel.ShowPdf(doc.FilePath);
        _statusLabel.Text = $"선택: {doc.FileName} ({doc.FileSize / 1024.0:F0} KB)";

        if (doc.LastConversion != null)
        {
            _splitViewerPanel.ShowResult(doc.LastConversion);
        }
    }

    private void OnDocumentsAdded(object? sender, IReadOnlyList<DocumentInfo> docs)
    {
        _bottomTabPanel.Log($"{docs.Count}개 파일이 추가되었습니다.", BottomTabPanel.LogLevel.Info);
        _statusLabel.Text = $"총 {_fileListPanel.Documents.Count}개 파일";
    }

    private async void OnSearchRequested(object? sender, (string pattern, bool useRegex, bool caseSensitive) args)
    {
        var result = _splitViewerPanel.CurrentResult;
        if (result == null || !result.Success)
        {
            _bottomTabPanel.Log("검색할 변환 결과가 없습니다.", BottomTabPanel.LogLevel.Warning);
            return;
        }

        try
        {
            var results = await _searchService.SearchAsync(
                result.Content, args.pattern, args.useRegex, args.caseSensitive);
            _bottomTabPanel.ShowSearchResults(results);
        }
        catch (Exception ex)
        {
            _bottomTabPanel.Log($"검색 오류: {ex.Message}", BottomTabPanel.LogLevel.Error);
        }
    }

    private void OnSearchResultSelected(object? sender, SearchResult result)
    {
        _bottomTabPanel.Log($"줄 {result.LineNumber}: {result.ContextLine}");
    }

    private void OnKeyDown(object? sender, KeyEventArgs e)
    {
        if (e.Control && e.KeyCode == Keys.F)
        {
            _bottomTabPanel.FocusSearch();
            e.Handled = true;
        }
    }

    // === Actions ===

    private void OpenFiles()
    {
        using var dialog = new OpenFileDialog
        {
            Filter = "PDF 파일 (*.pdf)|*.pdf|모든 파일 (*.*)|*.*",
            Multiselect = true,
            Title = "PDF 파일 선택"
        };

        if (dialog.ShowDialog() == DialogResult.OK)
        {
            _fileListPanel.AddFiles(dialog.FileNames);
        }
    }

    private void OpenFolder()
    {
        using var dialog = new FolderBrowserDialog
        {
            Description = "PDF 파일이 포함된 폴더를 선택하세요"
        };

        if (dialog.ShowDialog() == DialogResult.OK)
        {
            _fileListPanel.AddFiles(new[] { dialog.SelectedPath });
        }
    }

    private async Task ConvertSelected()
    {
        var docs = _fileListPanel.Documents;
        // TreeView에서 선택된 문서가 있으면 해당 문서만, 없으면 전체
        var selectedDocs = docs.Where(d => d.LastConversion == null).Take(1).ToList();

        if (selectedDocs.Count == 0 && docs.Count > 0)
        {
            selectedDocs = new List<DocumentInfo> { docs[0] };
        }

        if (selectedDocs.Count == 0)
        {
            MessageBox.Show("변환할 PDF 파일을 추가하세요.", "알림", MessageBoxButtons.OK, MessageBoxIcon.Information);
            return;
        }

        var doc = selectedDocs[0];
        var options = GetCurrentOptions();

        _bottomTabPanel.Log($"변환 시작: {doc.FileName} [{options.Format}]");
        _statusLabel.Text = $"변환 중: {doc.FileName}...";

        try
        {
            var result = await _conversionService.ConvertAsync(doc, options);
            doc.LastConversion = result;

            if (result.Success)
            {
                _splitViewerPanel.ShowResult(result);
                _fileListPanel.UpdateNodeStatus(doc, true);
                _bottomTabPanel.Log(
                    $"변환 완료: {doc.FileName} ({result.Duration.TotalSeconds:F1}초)",
                    BottomTabPanel.LogLevel.Success);

                if (result.AiFilterWarnings?.Count > 0)
                {
                    foreach (var warning in result.AiFilterWarnings)
                    {
                        _bottomTabPanel.Log($"  [필터] {warning}", BottomTabPanel.LogLevel.Warning);
                    }
                }
            }
            else
            {
                _splitViewerPanel.ShowResult(result);
                _fileListPanel.UpdateNodeStatus(doc, false);
                _bottomTabPanel.Log($"변환 실패: {doc.FileName} - {result.Error}", BottomTabPanel.LogLevel.Error);
            }
        }
        catch (OperationCanceledException)
        {
            _bottomTabPanel.Log("변환이 취소되었습니다.", BottomTabPanel.LogLevel.Warning);
        }
        catch (Exception ex)
        {
            _bottomTabPanel.Log($"오류: {ex.Message}", BottomTabPanel.LogLevel.Error);
        }

        _statusLabel.Text = "준비 완료";
    }

    private async Task ConvertBatch()
    {
        var docs = _fileListPanel.Documents;
        if (docs.Count == 0)
        {
            MessageBox.Show("변환할 PDF 파일을 추가하세요.", "알림", MessageBoxButtons.OK, MessageBoxIcon.Information);
            return;
        }

        var options = GetCurrentOptions();
        var ct = _progressPanel.Start(docs.Count);
        var progress = new Progress<(int completed, int total, string currentFile)>(
            p => _progressPanel.UpdateProgress(p.completed, p.total, p.currentFile));

        _bottomTabPanel.Log($"배치 변환 시작: {docs.Count}개 파일 [{options.Format}]");
        _statusLabel.Text = $"배치 변환 중...";

        try
        {
            var results = await _conversionService.ConvertBatchAsync(docs, options, progress, ct);

            var successCount = results.Count(r => r.Success);
            var failCount = results.Count(r => !r.Success);
            _progressPanel.Complete(successCount, failCount);

            foreach (var result in results)
            {
                var doc = result.Source;
                doc.LastConversion = result;
                _fileListPanel.UpdateNodeStatus(doc, result.Success);

                if (result.Success)
                {
                    _bottomTabPanel.Log($"  완료: {doc.FileName} ({result.Duration.TotalSeconds:F1}초)", BottomTabPanel.LogLevel.Success);
                }
                else
                {
                    _bottomTabPanel.Log($"  실패: {doc.FileName} - {result.Error}", BottomTabPanel.LogLevel.Error);
                }
            }

            _bottomTabPanel.Log(
                $"배치 변환 완료: 성공 {successCount}, 실패 {failCount}",
                failCount > 0 ? BottomTabPanel.LogLevel.Warning : BottomTabPanel.LogLevel.Success);

            // 첫 번째 성공 결과 표시
            var firstSuccess = results.FirstOrDefault(r => r.Success);
            if (firstSuccess != null)
            {
                _splitViewerPanel.ShowPdf(firstSuccess.Source.FilePath);
                _splitViewerPanel.ShowResult(firstSuccess);
            }
        }
        catch (OperationCanceledException)
        {
            _bottomTabPanel.Log("배치 변환이 취소되었습니다.", BottomTabPanel.LogLevel.Warning);
        }
        catch (Exception ex)
        {
            _bottomTabPanel.Log($"배치 오류: {ex.Message}", BottomTabPanel.LogLevel.Error);
        }

        _statusLabel.Text = "준비 완료";
    }

    private void SaveResult()
    {
        var result = _splitViewerPanel.CurrentResult;
        if (result == null || !result.Success)
        {
            MessageBox.Show("저장할 변환 결과가 없습니다.", "알림", MessageBoxButtons.OK, MessageBoxIcon.Information);
            return;
        }

        var ext = FileExportService.GetExtension(result.Format);
        var defaultName = Path.GetFileNameWithoutExtension(result.Source.FileName) + ext;

        using var dialog = new SaveFileDialog
        {
            Filter = FileExportService.GetFileFilter(result.Format) + "|모든 파일 (*.*)|*.*",
            FileName = defaultName,
            Title = "변환 결과 저장"
        };

        if (dialog.ShowDialog() == DialogResult.OK)
        {
            _ = Task.Run(async () =>
            {
                try
                {
                    await _exportService.SaveAsync(result, dialog.FileName);
                    Invoke(() => _bottomTabPanel.Log($"저장 완료: {dialog.FileName}", BottomTabPanel.LogLevel.Success));
                }
                catch (Exception ex)
                {
                    Invoke(() => _bottomTabPanel.Log($"저장 실패: {ex.Message}", BottomTabPanel.LogLevel.Error));
                }
            });
        }
    }

    private void SaveBatchResults()
    {
        var results = _fileListPanel.Documents
            .Where(d => d.LastConversion is { Success: true })
            .Select(d => d.LastConversion!)
            .ToList();

        if (results.Count == 0)
        {
            MessageBox.Show("저장할 변환 결과가 없습니다.", "알림", MessageBoxButtons.OK, MessageBoxIcon.Information);
            return;
        }

        using var dialog = new FolderBrowserDialog
        {
            Description = "변환 결과를 저장할 폴더를 선택하세요"
        };

        if (dialog.ShowDialog() == DialogResult.OK)
        {
            _ = Task.Run(async () =>
            {
                try
                {
                    await _exportService.SaveBatchAsync(results, dialog.SelectedPath);
                    Invoke(() => _bottomTabPanel.Log(
                        $"배치 저장 완료: {results.Count}개 파일 → {dialog.SelectedPath}",
                        BottomTabPanel.LogLevel.Success));
                }
                catch (Exception ex)
                {
                    Invoke(() => _bottomTabPanel.Log($"배치 저장 실패: {ex.Message}", BottomTabPanel.LogLevel.Error));
                }
            });
        }
    }

    private void CopyToClipboard()
    {
        var result = _splitViewerPanel.CurrentResult;
        if (result == null || !result.Success)
        {
            MessageBox.Show("복사할 변환 결과가 없습니다.", "알림", MessageBoxButtons.OK, MessageBoxIcon.Information);
            return;
        }

        _exportService.CopyToClipboard(result.Content);
        _bottomTabPanel.Log("클립보드에 복사되었습니다.", BottomTabPanel.LogLevel.Success);
        _statusLabel.Text = "클립보드에 복사됨";
    }

    private void ShowSettings()
    {
        using var settingsForm = new SettingsForm(_settings);
        if (settingsForm.ShowDialog() == DialogResult.OK)
        {
            _settings = settingsForm.UpdatedSettings;
            _settingsService.Save(_settings);
            _bottomTabPanel.Log("설정이 저장되었습니다.", BottomTabPanel.LogLevel.Success);
        }
    }

    private async Task ValidatePython()
    {
        _bottomTabPanel.Log("Python 환경을 확인 중...");
        _statusLabel.Text = "Python 환경 확인 중...";

        var isValid = await _conversionService.ValidatePythonEnvironmentAsync();

        if (isValid)
        {
            _bottomTabPanel.Log("Python 환경이 정상입니다. (opendataloader_pdf 모듈 확인됨)", BottomTabPanel.LogLevel.Success);
            MessageBox.Show("Python 환경이 정상입니다.\nopendataloader_pdf 모듈이 설치되어 있습니다.",
                "환경 확인", MessageBoxButtons.OK, MessageBoxIcon.Information);
        }
        else
        {
            _bottomTabPanel.Log("Python 환경 오류: opendataloader_pdf를 찾을 수 없습니다.", BottomTabPanel.LogLevel.Error);
            MessageBox.Show(
                "Python 또는 opendataloader_pdf 모듈을 찾을 수 없습니다.\n\n" +
                "1. Python이 설치되어 있는지 확인하세요.\n" +
                "2. pip install opendataloader-pdf 명령으로 모듈을 설치하세요.\n" +
                "3. 설정에서 Python 경로를 확인하세요.",
                "환경 오류", MessageBoxButtons.OK, MessageBoxIcon.Warning);
        }

        _statusLabel.Text = "준비 완료";
    }

    private void ShowAbout()
    {
        MessageBox.Show(
            "LegalDocParser v1.0\n\n" +
            "법률 문서 PDF 파싱 및 분석 도구\n\n" +
            "기반 기술: OpenDataLoader PDF (Apache 2.0)\n" +
            "개발: 법무법인 세움\n\n" +
            "PDF 문서를 Markdown, JSON, HTML, Text로 변환하고\n" +
            "키워드 검색, AI 분석에 활용할 수 있습니다.",
            "LegalDocParser 정보",
            MessageBoxButtons.OK,
            MessageBoxIcon.Information);
    }
}
