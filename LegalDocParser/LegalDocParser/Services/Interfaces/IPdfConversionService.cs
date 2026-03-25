using LegalDocParser.Models;

namespace LegalDocParser.Services.Interfaces;

public interface IPdfConversionService
{
    Task<ConversionResult> ConvertAsync(
        DocumentInfo document,
        ConversionOptions options,
        CancellationToken cancellationToken = default);

    Task<IReadOnlyList<ConversionResult>> ConvertBatchAsync(
        IReadOnlyList<DocumentInfo> documents,
        ConversionOptions options,
        IProgress<(int completed, int total, string currentFile)>? progress = null,
        CancellationToken cancellationToken = default);

    Task<bool> ValidatePythonEnvironmentAsync();
}
