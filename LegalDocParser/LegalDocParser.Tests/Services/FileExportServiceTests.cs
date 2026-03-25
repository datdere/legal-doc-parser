using LegalDocParser.Models;
using LegalDocParser.Models.Enums;
using LegalDocParser.Services;
using Xunit;

namespace LegalDocParser.Tests.Services;

public class FileExportServiceTests
{
    [Theory]
    [InlineData(OutputFormat.Markdown, ".md")]
    [InlineData(OutputFormat.Json, ".json")]
    [InlineData(OutputFormat.Html, ".html")]
    [InlineData(OutputFormat.Text, ".txt")]
    public void GetExtension_ReturnsCorrectExtension(OutputFormat format, string expected)
    {
        Assert.Equal(expected, FileExportService.GetExtension(format));
    }

    [Fact]
    public async Task SaveAsync_CreatesFile()
    {
        var service = new FileExportService();
        var tempDir = Path.Combine(Path.GetTempPath(), Guid.NewGuid().ToString());
        var outputPath = Path.Combine(tempDir, "test.md");

        var result = new ConversionResult
        {
            Source = new DocumentInfo { FilePath = "test.pdf" },
            Options = new ConversionOptions(),
            Format = OutputFormat.Markdown,
            Success = true,
            Content = "# Test\n\nHello World"
        };

        try
        {
            await service.SaveAsync(result, outputPath);
            Assert.True(File.Exists(outputPath));

            var content = await File.ReadAllTextAsync(outputPath);
            Assert.Equal("# Test\n\nHello World", content);
        }
        finally
        {
            if (Directory.Exists(tempDir))
                Directory.Delete(tempDir, true);
        }
    }

    [Fact]
    public async Task SaveBatchAsync_CreatesMultipleFiles()
    {
        var service = new FileExportService();
        var tempDir = Path.Combine(Path.GetTempPath(), Guid.NewGuid().ToString());

        var results = new List<ConversionResult>
        {
            new()
            {
                Source = new DocumentInfo { FilePath = "doc1.pdf" },
                Options = new ConversionOptions(),
                Format = OutputFormat.Markdown,
                Success = true,
                Content = "# Doc 1"
            },
            new()
            {
                Source = new DocumentInfo { FilePath = "doc2.pdf" },
                Options = new ConversionOptions(),
                Format = OutputFormat.Markdown,
                Success = true,
                Content = "# Doc 2"
            },
            new()
            {
                Source = new DocumentInfo { FilePath = "failed.pdf" },
                Options = new ConversionOptions(),
                Format = OutputFormat.Markdown,
                Success = false,
                Content = "",
                Error = "Some error"
            }
        };

        try
        {
            await service.SaveBatchAsync(results, tempDir);

            Assert.True(File.Exists(Path.Combine(tempDir, "doc1.md")));
            Assert.True(File.Exists(Path.Combine(tempDir, "doc2.md")));
            Assert.False(File.Exists(Path.Combine(tempDir, "failed.md"))); // 실패한 것은 저장 안됨
        }
        finally
        {
            if (Directory.Exists(tempDir))
                Directory.Delete(tempDir, true);
        }
    }
}
