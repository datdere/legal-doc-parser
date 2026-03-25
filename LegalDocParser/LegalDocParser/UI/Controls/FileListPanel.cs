using LegalDocParser.Models;

namespace LegalDocParser.UI.Controls;

/// <summary>
/// 좌측 파일 목록 패널 (드래그앤드롭 지원)
/// </summary>
public class FileListPanel : UserControl
{
    private readonly TreeView _treeView;
    private readonly Label _titleLabel;
    private readonly ToolStrip _toolbar;
    private readonly List<DocumentInfo> _documents = new();

    public event EventHandler<DocumentInfo>? DocumentSelected;
    public event EventHandler<IReadOnlyList<DocumentInfo>>? DocumentsAdded;

    public IReadOnlyList<DocumentInfo> Documents => _documents.AsReadOnly();

    public FileListPanel()
    {
        _titleLabel = new Label
        {
            Text = "문서 목록",
            Dock = DockStyle.Top,
            Height = 28,
            TextAlign = ContentAlignment.MiddleLeft,
            Font = new Font("맑은 고딕", 9f, FontStyle.Bold),
            Padding = new Padding(4, 0, 0, 0),
            BackColor = Color.FromArgb(240, 240, 240)
        };

        _toolbar = new ToolStrip { Dock = DockStyle.Top };
        var addButton = new ToolStripButton("파일 추가") { ToolTipText = "PDF 파일 추가 (Ctrl+O)" };
        var addFolderButton = new ToolStripButton("폴더 추가") { ToolTipText = "폴더 내 PDF 일괄 추가" };
        var removeButton = new ToolStripButton("제거") { ToolTipText = "선택 파일 제거" };
        var clearButton = new ToolStripButton("전체 삭제") { ToolTipText = "목록 비우기" };

        addButton.Click += OnAddFiles;
        addFolderButton.Click += OnAddFolder;
        removeButton.Click += OnRemoveSelected;
        clearButton.Click += OnClearAll;

        _toolbar.Items.AddRange(new ToolStripItem[] { addButton, addFolderButton, new ToolStripSeparator(), removeButton, clearButton });

        _treeView = new TreeView
        {
            Dock = DockStyle.Fill,
            AllowDrop = true,
            Font = new Font("맑은 고딕", 9f),
            ShowNodeToolTips = true,
            ImageList = CreateImageList()
        };

        _treeView.DragEnter += OnDragEnter;
        _treeView.DragDrop += OnDragDrop;
        _treeView.AfterSelect += OnNodeSelected;

        Controls.Add(_treeView);
        Controls.Add(_toolbar);
        Controls.Add(_titleLabel);
    }

    private ImageList CreateImageList()
    {
        var imageList = new ImageList { ImageSize = new Size(16, 16) };
        // 기본 아이콘 (실제 아이콘 파일 없이 색상 구분)
        var pdfBmp = new Bitmap(16, 16);
        using (var g = Graphics.FromImage(pdfBmp))
        {
            g.Clear(Color.Transparent);
            g.FillRectangle(Brushes.IndianRed, 2, 1, 12, 14);
            g.DrawString("P", new Font("Arial", 7, FontStyle.Bold), Brushes.White, 3, 2);
        }
        imageList.Images.Add("pdf", pdfBmp);

        var folderBmp = new Bitmap(16, 16);
        using (var g = Graphics.FromImage(folderBmp))
        {
            g.Clear(Color.Transparent);
            g.FillRectangle(Brushes.Goldenrod, 1, 4, 14, 11);
            g.FillRectangle(Brushes.Goldenrod, 1, 2, 7, 4);
        }
        imageList.Images.Add("folder", folderBmp);

        return imageList;
    }

    public void AddFiles(IEnumerable<string> filePaths)
    {
        var newDocs = new List<DocumentInfo>();

        foreach (var path in filePaths)
        {
            if (Directory.Exists(path))
            {
                var pdfFiles = Directory.GetFiles(path, "*.pdf", SearchOption.AllDirectories);
                foreach (var pdfFile in pdfFiles)
                {
                    AddDocument(pdfFile, newDocs);
                }
            }
            else if (path.EndsWith(".pdf", StringComparison.OrdinalIgnoreCase) && File.Exists(path))
            {
                AddDocument(path, newDocs);
            }
        }

        if (newDocs.Count > 0)
        {
            DocumentsAdded?.Invoke(this, newDocs);
        }
    }

    private void AddDocument(string filePath, List<DocumentInfo> newDocs)
    {
        if (_documents.Any(d => d.FilePath.Equals(filePath, StringComparison.OrdinalIgnoreCase)))
            return;

        var doc = DocumentInfo.FromFile(filePath);
        _documents.Add(doc);
        newDocs.Add(doc);

        var sizeKb = doc.FileSize / 1024.0;
        var sizeText = sizeKb > 1024 ? $"{sizeKb / 1024:F1} MB" : $"{sizeKb:F0} KB";

        var node = new TreeNode(doc.FileName)
        {
            Tag = doc,
            ImageKey = "pdf",
            SelectedImageKey = "pdf",
            ToolTipText = $"{doc.FilePath}\n크기: {sizeText}\n수정일: {doc.LastModified:yyyy-MM-dd HH:mm}"
        };

        _treeView.Nodes.Add(node);
    }

    public void UpdateNodeStatus(DocumentInfo doc, bool success)
    {
        foreach (TreeNode node in _treeView.Nodes)
        {
            if (node.Tag is DocumentInfo nodeDoc && nodeDoc.FilePath == doc.FilePath)
            {
                node.ForeColor = success ? Color.DarkGreen : Color.Red;
                node.Text = success ? $"{doc.FileName} [완료]" : $"{doc.FileName} [실패]";
                break;
            }
        }
    }

    private void OnAddFiles(object? sender, EventArgs e)
    {
        using var dialog = new OpenFileDialog
        {
            Filter = "PDF 파일 (*.pdf)|*.pdf|모든 파일 (*.*)|*.*",
            Multiselect = true,
            Title = "PDF 파일 선택"
        };

        if (dialog.ShowDialog() == DialogResult.OK)
        {
            AddFiles(dialog.FileNames);
        }
    }

    private void OnAddFolder(object? sender, EventArgs e)
    {
        using var dialog = new FolderBrowserDialog
        {
            Description = "PDF 파일이 포함된 폴더를 선택하세요"
        };

        if (dialog.ShowDialog() == DialogResult.OK)
        {
            AddFiles(new[] { dialog.SelectedPath });
        }
    }

    private void OnRemoveSelected(object? sender, EventArgs e)
    {
        if (_treeView.SelectedNode?.Tag is DocumentInfo doc)
        {
            _documents.Remove(doc);
            _treeView.Nodes.Remove(_treeView.SelectedNode);
        }
    }

    private void OnClearAll(object? sender, EventArgs e)
    {
        _documents.Clear();
        _treeView.Nodes.Clear();
    }

    private void OnDragEnter(object? sender, DragEventArgs e)
    {
        if (e.Data?.GetDataPresent(DataFormats.FileDrop) == true)
            e.Effect = DragDropEffects.Copy;
    }

    private void OnDragDrop(object? sender, DragEventArgs e)
    {
        if (e.Data?.GetData(DataFormats.FileDrop) is string[] files)
        {
            AddFiles(files);
        }
    }

    private void OnNodeSelected(object? sender, TreeViewEventArgs e)
    {
        if (e.Node?.Tag is DocumentInfo doc)
        {
            DocumentSelected?.Invoke(this, doc);
        }
    }
}
