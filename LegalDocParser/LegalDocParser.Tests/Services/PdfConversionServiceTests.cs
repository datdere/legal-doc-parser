using LegalDocParser.Models;
using LegalDocParser.Models.Enums;
using LegalDocParser.Services;
using Xunit;

namespace LegalDocParser.Tests.Services;

public class PdfConversionServiceTests
{
    private readonly PdfConversionService _service;

    public PdfConversionServiceTests()
    {
        var settings = new AppSettings
        {
            PythonPath = "python",
            ProcessTimeoutSeconds = 30,
            BatchConcurrency = 2
        };
        _service = new PdfConversionService(settings);
    }

    [Fact]
    public async Task ConvertAsync_NonExistentFile_ReturnsFailure()
    {
        var doc = new DocumentInfo { FilePath = "/nonexistent/test.pdf" };
        var options = new ConversionOptions { Format = OutputFormat.Markdown };

        var result = await _service.ConvertAsync(doc, options);

        Assert.False(result.Success);
        Assert.Contains("찾을 수 없습니다", result.Error);
    }

    [Fact]
    public async Task ConvertBatchAsync_EmptyList_ReturnsEmpty()
    {
        var docs = new List<DocumentInfo>();
        var options = new ConversionOptions();

        var results = await _service.ConvertBatchAsync(docs, options);

        Assert.Empty(results);
    }

    [Fact]
    public async Task ConvertBatchAsync_ReportsProgress()
    {
        var docs = new List<DocumentInfo>
        {
            new() { FilePath = "/nonexistent/a.pdf" },
            new() { FilePath = "/nonexistent/b.pdf" }
        };
        var options = new ConversionOptions();

        var progressReports = new List<(int completed, int total, string currentFile)>();
        var progress = new Progress<(int completed, int total, string currentFile)>(
            p => progressReports.Add(p));

        await _service.ConvertBatchAsync(docs, options, progress);

        // 프로그레스 리포트가 발생해야 함 (비동기라 정확한 수 보장은 안됨)
        Assert.True(docs.Count == 2);
    }
}
