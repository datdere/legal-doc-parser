namespace LegalDocParser.Models;

/// <summary>
/// 키워드 검색 결과
/// </summary>
public record SearchResult(
    string MatchedText,
    int LineNumber,
    int ColumnStart,
    int MatchLength,
    string ContextLine
);
