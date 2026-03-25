namespace LegalDocParser.UI.Controls;

/// <summary>
/// 배치 변환 진행률 표시 패널
/// </summary>
public class ConversionProgressPanel : UserControl
{
    private readonly ProgressBar _overallProgress;
    private readonly Label _statusLabel;
    private readonly Label _detailLabel;
    private readonly Button _cancelButton;
    private CancellationTokenSource? _cts;

    public event EventHandler? CancelRequested;

    public ConversionProgressPanel()
    {
        Height = 80;
        Dock = DockStyle.Bottom;
        Visible = false;
        Padding = new Padding(8);
        BackColor = Color.FromArgb(245, 245, 250);
        BorderStyle = BorderStyle.FixedSingle;

        _statusLabel = new Label
        {
            Text = "변환 준비 중...",
            Location = new Point(8, 8),
            AutoSize = true,
            Font = new Font("맑은 고딕", 9f, FontStyle.Bold)
        };

        _overallProgress = new ProgressBar
        {
            Location = new Point(8, 30),
            Height = 20,
            Style = ProgressBarStyle.Continuous
        };

        _detailLabel = new Label
        {
            Text = "",
            Location = new Point(8, 55),
            AutoSize = true,
            Font = new Font("맑은 고딕", 8.5f),
            ForeColor = Color.Gray
        };

        _cancelButton = new Button
        {
            Text = "취소",
            Width = 60,
            Height = 26,
            Location = new Point(8, 30)
        };
        _cancelButton.Click += (_, _) =>
        {
            _cts?.Cancel();
            CancelRequested?.Invoke(this, EventArgs.Empty);
        };

        Controls.AddRange(new Control[] { _statusLabel, _overallProgress, _detailLabel, _cancelButton });

        Resize += (_, _) => AdjustLayout();
    }

    private void AdjustLayout()
    {
        _overallProgress.Width = Width - _cancelButton.Width - 30;
        _cancelButton.Location = new Point(Width - _cancelButton.Width - 12, 30);
    }

    public CancellationToken Start(int totalFiles)
    {
        _cts?.Dispose();
        _cts = new CancellationTokenSource();

        _overallProgress.Minimum = 0;
        _overallProgress.Maximum = totalFiles;
        _overallProgress.Value = 0;
        _statusLabel.Text = $"변환 진행 중... (0/{totalFiles})";
        _detailLabel.Text = "";

        Visible = true;
        AdjustLayout();

        return _cts.Token;
    }

    public void UpdateProgress(int completed, int total, string currentFile)
    {
        if (InvokeRequired)
        {
            Invoke(() => UpdateProgress(completed, total, currentFile));
            return;
        }

        _overallProgress.Maximum = total;
        _overallProgress.Value = Math.Min(completed, total);
        _statusLabel.Text = $"변환 진행 중... ({completed}/{total})";
        _detailLabel.Text = $"처리 중: {currentFile}";
    }

    public void Complete(int successCount, int failCount)
    {
        if (InvokeRequired)
        {
            Invoke(() => Complete(successCount, failCount));
            return;
        }

        _overallProgress.Value = _overallProgress.Maximum;
        _statusLabel.Text = $"변환 완료 - 성공: {successCount}, 실패: {failCount}";
        _detailLabel.Text = "완료되었습니다.";
    }

    public void Hide()
    {
        Visible = false;
        _cts?.Dispose();
        _cts = null;
    }

    protected override void Dispose(bool disposing)
    {
        if (disposing)
        {
            _cts?.Dispose();
        }
        base.Dispose(disposing);
    }
}
