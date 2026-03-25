using LegalDocParser.Models.Enums;

namespace LegalDocParser.Models;

/// <summary>
/// 애플리케이션 설정
/// </summary>
public class AppSettings
{
    public string PythonPath { get; set; } = "python";
    public string DefaultOutputDir { get; set; } = "";
    public OutputFormat DefaultFormat { get; set; } = OutputFormat.Markdown;
    public TableExtractionMode DefaultTableMode { get; set; } = TableExtractionMode.Local;
    public OcrLanguage DefaultOcrLang { get; set; } = OcrLanguage.None;
    public bool DefaultAiSafetyFilter { get; set; } = true;
    public int BatchConcurrency { get; set; } = 3;
    public int ProcessTimeoutSeconds { get; set; } = 300;
    public string? ClaudeApiKey { get; set; }
    public string? HybridServerUrl { get; set; } = "http://localhost:5002";
}
