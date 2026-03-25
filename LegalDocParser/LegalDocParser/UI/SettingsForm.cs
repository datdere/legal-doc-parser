using LegalDocParser.Models;
using LegalDocParser.Models.Enums;

namespace LegalDocParser.UI;

/// <summary>
/// 환경 설정 폼
/// </summary>
public class SettingsForm : Form
{
    private readonly TextBox _pythonPathBox;
    private readonly TextBox _outputDirBox;
    private readonly ComboBox _defaultFormatCombo;
    private readonly ComboBox _defaultTableModeCombo;
    private readonly ComboBox _defaultOcrCombo;
    private readonly CheckBox _aiSafetyFilterCheck;
    private readonly NumericUpDown _concurrencyUpDown;
    private readonly NumericUpDown _timeoutUpDown;
    private readonly TextBox _claudeApiKeyBox;
    private readonly TextBox _hybridServerUrlBox;

    public AppSettings UpdatedSettings { get; private set; }

    public SettingsForm(AppSettings currentSettings)
    {
        UpdatedSettings = currentSettings;

        Text = "환경 설정";
        Size = new Size(550, 520);
        FormBorderStyle = FormBorderStyle.FixedDialog;
        MaximizeBox = false;
        MinimizeBox = false;
        StartPosition = FormStartPosition.CenterParent;
        Font = new Font("맑은 고딕", 9f);

        var mainPanel = new Panel { Dock = DockStyle.Fill, AutoScroll = true, Padding = new Padding(16) };
        int y = 16;

        // === Python 경로 ===
        mainPanel.Controls.Add(CreateLabel("Python 실행 경로:", 16, y));
        y += 22;
        _pythonPathBox = CreateTextBox(currentSettings.PythonPath, 16, y, 380);
        var browseBtn = new Button { Text = "찾기", Location = new Point(405, y - 2), Width = 60, Height = 26 };
        browseBtn.Click += (_, _) =>
        {
            using var dialog = new OpenFileDialog
            {
                Filter = "Python (python.exe)|python.exe|모든 파일 (*.*)|*.*",
                Title = "Python 실행 파일 선택"
            };
            if (dialog.ShowDialog() == DialogResult.OK)
                _pythonPathBox.Text = dialog.FileName;
        };
        mainPanel.Controls.Add(_pythonPathBox);
        mainPanel.Controls.Add(browseBtn);
        y += 34;

        // === 기본 출력 디렉토리 ===
        mainPanel.Controls.Add(CreateLabel("기본 출력 디렉토리:", 16, y));
        y += 22;
        _outputDirBox = CreateTextBox(currentSettings.DefaultOutputDir, 16, y, 380);
        var browseDirBtn = new Button { Text = "찾기", Location = new Point(405, y - 2), Width = 60, Height = 26 };
        browseDirBtn.Click += (_, _) =>
        {
            using var dialog = new FolderBrowserDialog();
            if (dialog.ShowDialog() == DialogResult.OK)
                _outputDirBox.Text = dialog.SelectedPath;
        };
        mainPanel.Controls.Add(_outputDirBox);
        mainPanel.Controls.Add(browseDirBtn);
        y += 40;

        // === 기본 포맷 ===
        mainPanel.Controls.Add(CreateLabel("기본 출력 포맷:", 16, y));
        _defaultFormatCombo = new ComboBox
        {
            DropDownStyle = ComboBoxStyle.DropDownList,
            Location = new Point(200, y - 2),
            Width = 150
        };
        _defaultFormatCombo.Items.AddRange(new object[] { "Markdown", "JSON", "HTML", "Text" });
        _defaultFormatCombo.SelectedIndex = (int)currentSettings.DefaultFormat;
        mainPanel.Controls.Add(_defaultFormatCombo);
        y += 34;

        // === 기본 표 추출 모드 ===
        mainPanel.Controls.Add(CreateLabel("기본 표 추출 모드:", 16, y));
        _defaultTableModeCombo = new ComboBox
        {
            DropDownStyle = ComboBoxStyle.DropDownList,
            Location = new Point(200, y - 2),
            Width = 150
        };
        _defaultTableModeCombo.Items.AddRange(new object[] { "로컬 (빠름)", "하이브리드 (정확)" });
        _defaultTableModeCombo.SelectedIndex = (int)currentSettings.DefaultTableMode;
        mainPanel.Controls.Add(_defaultTableModeCombo);
        y += 34;

        // === 기본 OCR ===
        mainPanel.Controls.Add(CreateLabel("기본 OCR 언어:", 16, y));
        _defaultOcrCombo = new ComboBox
        {
            DropDownStyle = ComboBoxStyle.DropDownList,
            Location = new Point(200, y - 2),
            Width = 150
        };
        _defaultOcrCombo.Items.AddRange(new object[] { "OCR 없음", "한국어", "영어", "한국어+영어" });
        _defaultOcrCombo.SelectedIndex = (int)currentSettings.DefaultOcrLang;
        mainPanel.Controls.Add(_defaultOcrCombo);
        y += 34;

        // === AI 안전 필터 ===
        _aiSafetyFilterCheck = new CheckBox
        {
            Text = "AI 안전 필터 활성화 (프롬프트 인젝션, 민감정보 탐지)",
            Location = new Point(16, y),
            AutoSize = true,
            Checked = currentSettings.DefaultAiSafetyFilter
        };
        mainPanel.Controls.Add(_aiSafetyFilterCheck);
        y += 34;

        // === 배치 동시 처리 수 ===
        mainPanel.Controls.Add(CreateLabel("배치 동시 처리 수:", 16, y));
        _concurrencyUpDown = new NumericUpDown
        {
            Location = new Point(200, y - 2),
            Width = 80,
            Minimum = 1,
            Maximum = 10,
            Value = currentSettings.BatchConcurrency
        };
        mainPanel.Controls.Add(_concurrencyUpDown);
        y += 34;

        // === 프로세스 타임아웃 ===
        mainPanel.Controls.Add(CreateLabel("프로세스 타임아웃 (초):", 16, y));
        _timeoutUpDown = new NumericUpDown
        {
            Location = new Point(200, y - 2),
            Width = 80,
            Minimum = 30,
            Maximum = 3600,
            Value = currentSettings.ProcessTimeoutSeconds
        };
        mainPanel.Controls.Add(_timeoutUpDown);
        y += 40;

        // === Hybrid Server URL ===
        mainPanel.Controls.Add(CreateLabel("하이브리드 서버 URL:", 16, y));
        y += 22;
        _hybridServerUrlBox = CreateTextBox(currentSettings.HybridServerUrl ?? "", 16, y, 450);
        mainPanel.Controls.Add(_hybridServerUrlBox);
        y += 34;

        // === Claude API Key ===
        mainPanel.Controls.Add(CreateLabel("Claude API Key (선택):", 16, y));
        y += 22;
        _claudeApiKeyBox = CreateTextBox(currentSettings.ClaudeApiKey ?? "", 16, y, 450);
        _claudeApiKeyBox.PasswordChar = '*';
        mainPanel.Controls.Add(_claudeApiKeyBox);

        // === 버튼 ===
        var buttonPanel = new Panel { Dock = DockStyle.Bottom, Height = 50 };
        var okButton = new Button
        {
            Text = "확인",
            DialogResult = DialogResult.OK,
            Location = new Point(340, 12),
            Width = 80,
            Height = 30
        };
        var cancelButton = new Button
        {
            Text = "취소",
            DialogResult = DialogResult.Cancel,
            Location = new Point(430, 12),
            Width = 80,
            Height = 30
        };

        okButton.Click += (_, _) => SaveSettings();

        buttonPanel.Controls.AddRange(new Control[] { okButton, cancelButton });

        Controls.Add(mainPanel);
        Controls.Add(buttonPanel);

        AcceptButton = okButton;
        CancelButton = cancelButton;
    }

    private void SaveSettings()
    {
        UpdatedSettings = new AppSettings
        {
            PythonPath = _pythonPathBox.Text.Trim(),
            DefaultOutputDir = _outputDirBox.Text.Trim(),
            DefaultFormat = (OutputFormat)_defaultFormatCombo.SelectedIndex,
            DefaultTableMode = (TableExtractionMode)_defaultTableModeCombo.SelectedIndex,
            DefaultOcrLang = (OcrLanguage)_defaultOcrCombo.SelectedIndex,
            DefaultAiSafetyFilter = _aiSafetyFilterCheck.Checked,
            BatchConcurrency = (int)_concurrencyUpDown.Value,
            ProcessTimeoutSeconds = (int)_timeoutUpDown.Value,
            HybridServerUrl = _hybridServerUrlBox.Text.Trim(),
            ClaudeApiKey = string.IsNullOrWhiteSpace(_claudeApiKeyBox.Text) ? null : _claudeApiKeyBox.Text.Trim()
        };
    }

    private static Label CreateLabel(string text, int x, int y)
    {
        return new Label
        {
            Text = text,
            Location = new Point(x, y),
            AutoSize = true
        };
    }

    private static TextBox CreateTextBox(string text, int x, int y, int width)
    {
        return new TextBox
        {
            Text = text,
            Location = new Point(x, y),
            Width = width
        };
    }
}
