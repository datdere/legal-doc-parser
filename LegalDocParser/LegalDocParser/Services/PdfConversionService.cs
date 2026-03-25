using System.Text.Json;
using LegalDocParser.Helpers;
using LegalDocParser.Models;
using LegalDocParser.Models.Enums;
using LegalDocParser.Services.Interfaces;

namespace LegalDocParser.Services;

/// <summary>
/// OpenDataLoader PDF Python SDK를 통한 PDF 변환 서비스
/// </summary>
public class PdfConversionService : IPdfConversionService
{
    private readonly AppSettings _settings;
    private readonly string _scriptPath;

    public PdfConversionService(AppSettings settings)
    {
        _settings = settings;
        _scriptPath = Path.Combine(AppDomain.CurrentDomain.BaseDirectory, "Scripts", "convert_pdf.py");
    }

    public async Task<ConversionResult> ConvertAsync(
        DocumentInfo document,
        ConversionOptions options,
        CancellationToken cancellationToken = default)
    {
        if (!File.Exists(document.FilePath))
        {
            return new ConversionResult
            {
                Source = document,
                Options = options,
                Format = options.Format,
                Success = false,
                Error = $"파일을 찾을 수 없습니다: {document.FilePath}"
            };
        }

        var args = BuildArguments(document.FilePath, options);
        var timeoutMs = _settings.ProcessTimeoutSeconds * 1000;

        var result = await ProcessHelper.RunAsync(
            _settings.PythonPath,
            args,
            timeoutMs,
            cancellationToken);

        return ParseResult(document, options, result);
    }

    public async Task<IReadOnlyList<ConversionResult>> ConvertBatchAsync(
        IReadOnlyList<DocumentInfo> documents,
        ConversionOptions options,
        IProgress<(int completed, int total, string currentFile)>? progress = null,
        CancellationToken cancellationToken = default)
    {
        var results = new List<ConversionResult>();
        var semaphore = new SemaphoreSlim(_settings.BatchConcurrency);
        var completed = 0;
        var total = documents.Count;

        var tasks = documents.Select(async doc =>
        {
            await semaphore.WaitAsync(cancellationToken);
            try
            {
                progress?.Report((Interlocked.Increment(ref completed) - 1, total, doc.FileName));
                var result = await ConvertAsync(doc, options, cancellationToken);
                progress?.Report((completed, total, doc.FileName));
                return result;
            }
            finally
            {
                semaphore.Release();
            }
        }).ToList();

        var batchResults = await Task.WhenAll(tasks);
        return batchResults.ToList();
    }

    public async Task<bool> ValidatePythonEnvironmentAsync()
    {
        var result = await ProcessHelper.RunAsync(
            _settings.PythonPath,
            "--version",
            10000);

        if (result.ExitCode != 0)
            return false;

        // opendataloader_pdf 모듈 존재 확인
        var moduleCheck = await ProcessHelper.RunAsync(
            _settings.PythonPath,
            "-c \"import opendataloader_pdf; print(opendataloader_pdf.__version__)\"",
            15000);

        return moduleCheck.ExitCode == 0;
    }

    private string BuildArguments(string inputPath, ConversionOptions options)
    {
        var args = new List<string>
        {
            $"\"{_scriptPath}\"",
            $"--input \"{inputPath}\"",
            $"--format {FormatToString(options.Format)}"
        };

        if (options.TableMode == TableExtractionMode.Hybrid)
            args.Add("--table-mode hybrid");
        else
            args.Add("--table-mode local");

        if (options.OcrLang != OcrLanguage.None)
        {
            args.Add($"--ocr-lang \"{OcrLangToString(options.OcrLang)}\"");
        }

        if (options.UseTaggedPdf)
            args.Add("--tagged-pdf");

        if (options.EnableAiSafetyFilter)
            args.Add("--ai-filter");

        if (!string.IsNullOrEmpty(options.PageRange))
            args.Add($"--pages \"{options.PageRange}\"");

        return string.Join(" ", args);
    }

    private ConversionResult ParseResult(
        DocumentInfo document,
        ConversionOptions options,
        ProcessHelper.ProcessResult processResult)
    {
        if (processResult.ExitCode != 0)
        {
            return new ConversionResult
            {
                Source = document,
                Options = options,
                Format = options.Format,
                Success = false,
                Error = string.IsNullOrWhiteSpace(processResult.StandardError)
                    ? $"변환 실패 (exit code: {processResult.ExitCode})"
                    : processResult.StandardError.Trim(),
                Duration = processResult.Duration
            };
        }

        try
        {
            var output = processResult.StandardOutput.Trim();
            var jsonResult = JsonSerializer.Deserialize<PythonConversionOutput>(output,
                new JsonSerializerOptions { PropertyNameCaseInsensitive = true });

            if (jsonResult == null)
            {
                return new ConversionResult
                {
                    Source = document,
                    Options = options,
                    Format = options.Format,
                    Success = false,
                    Error = "Python 출력 파싱 실패",
                    Duration = processResult.Duration
                };
            }

            var content = jsonResult.Content ?? string.Empty;
            List<string>? warnings = jsonResult.Warnings;

            // AI 안전 필터 적용
            if (options.EnableAiSafetyFilter)
            {
                var (filtered, filterWarnings) = AiSafetyFilter.Filter(content);
                content = filtered;
                warnings = (warnings ?? new List<string>()).Concat(filterWarnings).ToList();
            }

            return new ConversionResult
            {
                Source = document,
                Options = options,
                Format = options.Format,
                Success = jsonResult.Success,
                Content = content,
                Error = jsonResult.Error,
                Duration = processResult.Duration,
                AiFilterWarnings = warnings?.Count > 0 ? warnings : null
            };
        }
        catch (JsonException)
        {
            // JSON이 아닌 경우 직접 텍스트로 반환
            return new ConversionResult
            {
                Source = document,
                Options = options,
                Format = options.Format,
                Success = true,
                Content = processResult.StandardOutput.Trim(),
                Duration = processResult.Duration
            };
        }
    }

    private static string FormatToString(OutputFormat format) => format switch
    {
        OutputFormat.Markdown => "markdown",
        OutputFormat.Json => "json",
        OutputFormat.Html => "html",
        OutputFormat.Text => "text",
        _ => "markdown"
    };

    private static string OcrLangToString(OcrLanguage lang) => lang switch
    {
        OcrLanguage.Korean => "ko",
        OcrLanguage.English => "en",
        OcrLanguage.Both => "ko,en",
        _ => ""
    };

    private class PythonConversionOutput
    {
        public bool Success { get; set; }
        public string? Content { get; set; }
        public string? Error { get; set; }
        public List<string>? Warnings { get; set; }
    }
}
