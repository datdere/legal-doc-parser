using LegalDocParser.Models.Enums;

namespace LegalDocParser.Models;

/// <summary>
/// PDF 변환 옵션
/// </summary>
public record ConversionOptions
{
    public OutputFormat Format { get; init; } = OutputFormat.Markdown;
    public TableExtractionMode TableMode { get; init; } = TableExtractionMode.Local;
    public OcrLanguage OcrLang { get; init; } = OcrLanguage.None;
    public bool UseTaggedPdf { get; init; } = false;
    public bool EnableAiSafetyFilter { get; init; } = true;
    public string? PageRange { get; init; } = null;
}
