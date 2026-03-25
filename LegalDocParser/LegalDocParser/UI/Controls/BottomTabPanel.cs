using LegalDocParser.Models;

namespace LegalDocParser.UI.Controls;

/// <summary>
/// 하단 탭 패널: 로그, 검색 결과, AI 분석 결과
/// </summary>
public class BottomTabPanel : UserControl
{
    private readonly TabControl _tabControl;
    private readonly RichTextBox _logBox;
    private readonly Panel _searchPanel;
    private readonly TextBox _searchInput;
    private readonly Button _searchButton;
    private readonly CheckBox _regexCheck;
    private readonly CheckBox _caseSensitiveCheck;
    private readonly DataGridView _searchResultsGrid;
    private readonly RichTextBox _aiResultBox;

    public event EventHandler<(string pattern, bool useRegex, bool caseSensitive)>? SearchRequested;
    public event EventHandler<SearchResult>? SearchResultSelected;

    public BottomTabPanel()
    {
        _tabControl = new TabControl { Dock = DockStyle.Fill };

        // === 로그 탭 ===
        var logTab = new TabPage("로그");
        _logBox = new RichTextBox
        {
            Dock = DockStyle.Fill,
            ReadOnly = true,
            Font = new Font("Consolas", 9f),
            BackColor = Color.FromArgb(30, 30, 30),
            ForeColor = Color.LightGray,
            WordWrap = true
        };
        logTab.Controls.Add(_logBox);

        // === 검색 탭 ===
        var searchTab = new TabPage("검색");
        _searchPanel = new Panel { Dock = DockStyle.Top, Height = 36, Padding = new Padding(4) };

        _searchInput = new TextBox
        {
            Width = 300,
            Location = new Point(4, 6),
            Font = new Font("맑은 고딕", 9f),
            PlaceholderText = "검색어 입력 (Ctrl+F)"
        };

        _searchButton = new Button
        {
            Text = "검색",
            Location = new Point(310, 5),
            Width = 60,
            Height = 26
        };
        _searchButton.Click += OnSearchClick;

        _regexCheck = new CheckBox
        {
            Text = "정규식",
            Location = new Point(380, 8),
            AutoSize = true,
            Font = new Font("맑은 고딕", 8.5f)
        };

        _caseSensitiveCheck = new CheckBox
        {
            Text = "대소문자 구분",
            Location = new Point(445, 8),
            AutoSize = true,
            Font = new Font("맑은 고딕", 8.5f)
        };

        _searchPanel.Controls.AddRange(new Control[] { _searchInput, _searchButton, _regexCheck, _caseSensitiveCheck });

        _searchResultsGrid = new DataGridView
        {
            Dock = DockStyle.Fill,
            ReadOnly = true,
            AllowUserToAddRows = false,
            AllowUserToDeleteRows = false,
            SelectionMode = DataGridViewSelectionMode.FullRowSelect,
            AutoSizeColumnsMode = DataGridViewAutoSizeColumnsMode.Fill,
            Font = new Font("맑은 고딕", 9f),
            RowHeadersVisible = false,
            BackgroundColor = Color.White
        };

        _searchResultsGrid.Columns.AddRange(new DataGridViewColumn[]
        {
            new DataGridViewTextBoxColumn { Name = "Line", HeaderText = "줄", Width = 50, FillWeight = 10 },
            new DataGridViewTextBoxColumn { Name = "Match", HeaderText = "매칭", Width = 120, FillWeight = 20 },
            new DataGridViewTextBoxColumn { Name = "Context", HeaderText = "내용", FillWeight = 70 }
        });

        _searchResultsGrid.CellDoubleClick += OnSearchResultDoubleClick;

        _searchInput.KeyDown += (s, e) =>
        {
            if (e.KeyCode == Keys.Enter)
            {
                OnSearchClick(s, e);
                e.Handled = true;
                e.SuppressKeyPress = true;
            }
        };

        searchTab.Controls.Add(_searchResultsGrid);
        searchTab.Controls.Add(_searchPanel);

        // === AI 분석 탭 ===
        var aiTab = new TabPage("AI 분석");
        _aiResultBox = new RichTextBox
        {
            Dock = DockStyle.Fill,
            ReadOnly = true,
            Font = new Font("맑은 고딕", 10f),
            BackColor = Color.White
        };
        aiTab.Controls.Add(_aiResultBox);

        _tabControl.TabPages.AddRange(new[] { logTab, searchTab, aiTab });
        Controls.Add(_tabControl);
    }

    public void Log(string message, LogLevel level = LogLevel.Info)
    {
        if (InvokeRequired)
        {
            Invoke(() => Log(message, level));
            return;
        }

        var timestamp = DateTime.Now.ToString("HH:mm:ss");
        var prefix = level switch
        {
            LogLevel.Error => "[ERROR]",
            LogLevel.Warning => "[WARN] ",
            LogLevel.Success => "[OK]   ",
            _ => "[INFO] "
        };

        var color = level switch
        {
            LogLevel.Error => Color.Salmon,
            LogLevel.Warning => Color.Yellow,
            LogLevel.Success => Color.LightGreen,
            _ => Color.LightGray
        };

        _logBox.SelectionStart = _logBox.TextLength;
        _logBox.SelectionColor = color;
        _logBox.AppendText($"[{timestamp}] {prefix} {message}\n");
        _logBox.ScrollToCaret();
    }

    public void ShowSearchResults(IReadOnlyList<SearchResult> results)
    {
        _searchResultsGrid.Rows.Clear();

        foreach (var result in results)
        {
            _searchResultsGrid.Rows.Add(
                result.LineNumber.ToString(),
                result.MatchedText,
                result.ContextLine
            );
            _searchResultsGrid.Rows[^1].Tag = result;
        }

        _tabControl.SelectedIndex = 1; // 검색 탭으로 전환
        Log($"검색 완료: {results.Count}건 발견");
    }

    public void ShowAiResult(string result)
    {
        _aiResultBox.Text = result;
        _tabControl.SelectedIndex = 2; // AI 분석 탭으로 전환
    }

    public void FocusSearch()
    {
        _tabControl.SelectedIndex = 1;
        _searchInput.Focus();
        _searchInput.SelectAll();
    }

    private void OnSearchClick(object? sender, EventArgs e)
    {
        var pattern = _searchInput.Text.Trim();
        if (string.IsNullOrEmpty(pattern)) return;

        SearchRequested?.Invoke(this, (pattern, _regexCheck.Checked, _caseSensitiveCheck.Checked));
    }

    private void OnSearchResultDoubleClick(object? sender, DataGridViewCellEventArgs e)
    {
        if (e.RowIndex < 0) return;
        if (_searchResultsGrid.Rows[e.RowIndex].Tag is SearchResult result)
        {
            SearchResultSelected?.Invoke(this, result);
        }
    }

    public enum LogLevel
    {
        Info,
        Warning,
        Error,
        Success
    }
}
