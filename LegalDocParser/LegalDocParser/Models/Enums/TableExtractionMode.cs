namespace LegalDocParser.Models.Enums;

/// <summary>
/// 표 추출 모드
/// </summary>
public enum TableExtractionMode
{
    /// <summary>로컬 모드 (빠름, Java 기반)</summary>
    Local,

    /// <summary>하이브리드 모드 (정확, Python 서버 기반)</summary>
    Hybrid
}
