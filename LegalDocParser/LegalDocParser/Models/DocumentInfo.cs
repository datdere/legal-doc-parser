namespace LegalDocParser.Models;

/// <summary>
/// PDF 문서 정보
/// </summary>
public class DocumentInfo
{
    public string FilePath { get; init; } = string.Empty;
    public string FileName => Path.GetFileName(FilePath);
    public long FileSize { get; init; }
    public DateTime LastModified { get; init; }
    public ConversionResult? LastConversion { get; set; }

    public static DocumentInfo FromFile(string filePath)
    {
        var fileInfo = new FileInfo(filePath);
        return new DocumentInfo
        {
            FilePath = filePath,
            FileSize = fileInfo.Exists ? fileInfo.Length : 0,
            LastModified = fileInfo.Exists ? fileInfo.LastWriteTime : DateTime.MinValue
        };
    }
}
