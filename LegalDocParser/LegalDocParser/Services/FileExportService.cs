using LegalDocParser.Helpers;
using LegalDocParser.Models;
using LegalDocParser.Models.Enums;
using LegalDocParser.Services.Interfaces;

namespace LegalDocParser.Services;

/// <summary>
/// 변환 결과 파일 저장 및 클립보드 복사 서비스
/// </summary>
public class FileExportService : IFileExportService
{
    public async Task SaveAsync(ConversionResult result, string outputPath)
    {
        var dir = Path.GetDirectoryName(outputPath);
        if (!string.IsNullOrEmpty(dir) && !Directory.Exists(dir))
            Directory.CreateDirectory(dir);

        var content = result.Format == OutputFormat.Html
            ? MarkdownRenderer.RenderToHtml(result.Content)
            : result.Content;

        await File.WriteAllTextAsync(outputPath, content, System.Text.Encoding.UTF8);
    }

    public async Task SaveBatchAsync(IReadOnlyList<ConversionResult> results, string outputDir)
    {
        if (!Directory.Exists(outputDir))
            Directory.CreateDirectory(outputDir);

        foreach (var result in results)
        {
            if (!result.Success) continue;

            var extension = GetExtension(result.Format);
            var fileName = Path.GetFileNameWithoutExtension(result.Source.FileName) + extension;
            var outputPath = Path.Combine(outputDir, fileName);

            // 동일 이름 충돌 방지
            var counter = 1;
            while (File.Exists(outputPath))
            {
                fileName = $"{Path.GetFileNameWithoutExtension(result.Source.FileName)}_{counter}{extension}";
                outputPath = Path.Combine(outputDir, fileName);
                counter++;
            }

            await SaveAsync(result, outputPath);
        }
    }

    public void CopyToClipboard(string content)
    {
        if (string.IsNullOrEmpty(content)) return;
        Clipboard.SetText(content);
    }

    public static string GetExtension(OutputFormat format) => format switch
    {
        OutputFormat.Markdown => ".md",
        OutputFormat.Json => ".json",
        OutputFormat.Html => ".html",
        OutputFormat.Text => ".txt",
        _ => ".txt"
    };

    public static string GetFileFilter(OutputFormat format) => format switch
    {
        OutputFormat.Markdown => "Markdown 파일 (*.md)|*.md",
        OutputFormat.Json => "JSON 파일 (*.json)|*.json",
        OutputFormat.Html => "HTML 파일 (*.html)|*.html",
        OutputFormat.Text => "텍스트 파일 (*.txt)|*.txt",
        _ => "모든 파일 (*.*)|*.*"
    };
}
