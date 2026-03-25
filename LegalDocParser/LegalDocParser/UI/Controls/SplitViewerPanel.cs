using LegalDocParser.Helpers;
using LegalDocParser.Models;
using LegalDocParser.Models.Enums;

namespace LegalDocParser.UI.Controls;

/// <summary>
/// 원본 PDF와 변환 결과를 좌우 분할로 보여주는 패널
/// </summary>
public class SplitViewerPanel : UserControl
{
    private readonly SplitContainer _splitContainer;
    private readonly WebBrowser _pdfViewer;
    private readonly WebBrowser _resultViewer;
    private readonly RichTextBox _textViewer;
    private readonly TabControl _resultTabControl;
    private readonly Label _pdfLabel;
    private readonly Label _resultLabel;
    private readonly Panel _leftPanel;
    private readonly Panel _rightPanel;

    private ConversionResult? _currentResult;

    public ConversionResult? CurrentResult => _currentResult;

    public SplitViewerPanel()
    {
        _leftPanel = new Panel { Dock = DockStyle.Fill };
        _rightPanel = new Panel { Dock = DockStyle.Fill };

        _pdfLabel = new Label
        {
            Text = "원본 PDF",
            Dock = DockStyle.Top,
            Height = 24,
            TextAlign = ContentAlignment.MiddleCenter,
            Font = new Font("맑은 고딕", 9f, FontStyle.Bold),
            BackColor = Color.FromArgb(230, 230, 240)
        };

        _resultLabel = new Label
        {
            Text = "변환 결과",
            Dock = DockStyle.Top,
            Height = 24,
            TextAlign = ContentAlignment.MiddleCenter,
            Font = new Font("맑은 고딕", 9f, FontStyle.Bold),
            BackColor = Color.FromArgb(230, 240, 230)
        };

        _pdfViewer = new WebBrowser
        {
            Dock = DockStyle.Fill,
            ScriptErrorsSuppressed = true
        };

        _resultViewer = new WebBrowser
        {
            Dock = DockStyle.Fill,
            ScriptErrorsSuppressed = true
        };

        _textViewer = new RichTextBox
        {
            Dock = DockStyle.Fill,
            ReadOnly = true,
            Font = new Font("Consolas", 10f),
            WordWrap = true,
            BackColor = Color.White
        };

        _resultTabControl = new TabControl { Dock = DockStyle.Fill };

        var htmlTab = new TabPage("렌더링 뷰") { Padding = new Padding(0) };
        htmlTab.Controls.Add(_resultViewer);

        var textTab = new TabPage("텍스트 뷰") { Padding = new Padding(0) };
        textTab.Controls.Add(_textViewer);

        _resultTabControl.TabPages.AddRange(new[] { htmlTab, textTab });

        _leftPanel.Controls.Add(_pdfViewer);
        _leftPanel.Controls.Add(_pdfLabel);

        _rightPanel.Controls.Add(_resultTabControl);
        _rightPanel.Controls.Add(_resultLabel);

        _splitContainer = new SplitContainer
        {
            Dock = DockStyle.Fill,
            Orientation = Orientation.Vertical,
            SplitterDistance = 400,
            Panel1MinSize = 200,
            Panel2MinSize = 200
        };

        _splitContainer.Panel1.Controls.Add(_leftPanel);
        _splitContainer.Panel2.Controls.Add(_rightPanel);

        Controls.Add(_splitContainer);

        ShowWelcomeMessage();
    }

    private void ShowWelcomeMessage()
    {
        var welcomeHtml = @"<!DOCTYPE html>
<html><head><meta charset='UTF-8'><style>
body { font-family: '맑은 고딕', sans-serif; display: flex; align-items: center;
  justify-content: center; height: 100vh; margin: 0; background: #f8f9fa; color: #666; }
.center { text-align: center; }
h2 { color: #333; margin-bottom: 10px; }
p { font-size: 14px; line-height: 1.6; }
</style></head><body>
<div class='center'>
<h2>LegalDocParser</h2>
<p>PDF 파일을 좌측 목록에 드래그하거나<br/>파일 메뉴에서 추가하세요.</p>
<p style='color:#999; font-size:12px;'>법률 문서 PDF 파싱 및 분석 도구</p>
</div>
</body></html>";

        _pdfViewer.DocumentText = welcomeHtml;
        _resultViewer.DocumentText = welcomeHtml;
    }

    public void ShowPdf(string filePath)
    {
        _pdfLabel.Text = $"원본 PDF - {Path.GetFileName(filePath)}";
        try
        {
            _pdfViewer.Navigate(filePath);
        }
        catch
        {
            _pdfViewer.DocumentText = $"<html><body><p>PDF를 표시할 수 없습니다: {Path.GetFileName(filePath)}</p></body></html>";
        }
    }

    public void ShowResult(ConversionResult result)
    {
        _currentResult = result;
        _resultLabel.Text = $"변환 결과 - {result.Source.FileName} [{result.Format}]";

        if (!result.Success)
        {
            var errorHtml = $@"<html><body style='font-family:맑은 고딕; padding:20px;'>
<h3 style='color:red;'>변환 실패</h3>
<p>{System.Net.WebUtility.HtmlEncode(result.Error ?? "알 수 없는 오류")}</p>
<p style='color:#999;'>소요 시간: {result.Duration.TotalSeconds:F1}초</p>
</body></html>";
            _resultViewer.DocumentText = errorHtml;
            _textViewer.Text = result.Error ?? "변환 실패";
            return;
        }

        // 텍스트 뷰에 원문 표시
        _textViewer.Text = result.Content;

        // 렌더링 뷰에 HTML 표시
        switch (result.Format)
        {
            case OutputFormat.Markdown:
                _resultViewer.DocumentText = MarkdownRenderer.RenderToHtml(result.Content);
                break;
            case OutputFormat.Html:
                _resultViewer.DocumentText = result.Content;
                break;
            case OutputFormat.Json:
            case OutputFormat.Text:
                _resultViewer.DocumentText = MarkdownRenderer.WrapPlainTextAsHtml(result.Content);
                break;
        }
    }

    public void Clear()
    {
        _currentResult = null;
        ShowWelcomeMessage();
        _textViewer.Clear();
        _pdfLabel.Text = "원본 PDF";
        _resultLabel.Text = "변환 결과";
    }
}
