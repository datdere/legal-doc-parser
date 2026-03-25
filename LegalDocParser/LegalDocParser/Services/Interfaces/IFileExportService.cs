using LegalDocParser.Models;

namespace LegalDocParser.Services.Interfaces;

public interface IFileExportService
{
    Task SaveAsync(ConversionResult result, string outputPath);
    Task SaveBatchAsync(IReadOnlyList<ConversionResult> results, string outputDir);
    void CopyToClipboard(string content);
}
