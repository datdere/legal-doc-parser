using LegalDocParser.Models.Enums;

namespace LegalDocParser.Models;

/// <summary>
/// PDF 변환 결과
/// </summary>
public class ConversionResult
{
    public DocumentInfo Source { get; init; } = null!;
    public ConversionOptions Options { get; init; } = null!;
    public string Content { get; init; } = string.Empty;
    public OutputFormat Format { get; init; }
    public bool Success { get; init; }
    public string? Error { get; init; }
    public TimeSpan Duration { get; init; }
    public List<string>? AiFilterWarnings { get; init; }
}
