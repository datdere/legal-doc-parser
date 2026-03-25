using System.Text.RegularExpressions;

namespace LegalDocParser.Helpers;

/// <summary>
/// AI 안전 필터: 프롬프트 인젝션 및 민감 정보 탐지
/// </summary>
public static class AiSafetyFilter
{
    private static readonly Regex ResidentIdPattern = new(
        @"\d{6}\s*-\s*[1-4]\d{6}",
        RegexOptions.Compiled);

    private static readonly Regex PhonePattern = new(
        @"01[0-9]-?\d{3,4}-?\d{4}",
        RegexOptions.Compiled);

    private static readonly Regex HiddenTextPattern = new(
        @"<\s*div[^>]*style\s*=\s*""[^""]*(?:display\s*:\s*none|visibility\s*:\s*hidden|font-size\s*:\s*0)[^""]*""[^>]*>.*?</\s*div\s*>",
        RegexOptions.Compiled | RegexOptions.IgnoreCase | RegexOptions.Singleline);

    private static readonly string[] PromptInjectionKeywords = new[]
    {
        "ignore previous instructions",
        "ignore above instructions",
        "disregard all prior",
        "system prompt",
        "you are now",
        "new instructions:",
        "override:",
        "이전 지시를 무시",
        "시스템 프롬프트"
    };

    public static (string filteredContent, List<string> warnings) Filter(string content)
    {
        var warnings = new List<string>();
        var filtered = content;

        // 숨겨진 텍스트 제거
        var hiddenMatches = HiddenTextPattern.Matches(filtered);
        if (hiddenMatches.Count > 0)
        {
            warnings.Add($"숨겨진 텍스트 {hiddenMatches.Count}개 발견 및 제거됨");
            filtered = HiddenTextPattern.Replace(filtered, "[HIDDEN_TEXT_REMOVED]");
        }

        // 프롬프트 인젝션 탐지
        foreach (var keyword in PromptInjectionKeywords)
        {
            if (filtered.Contains(keyword, StringComparison.OrdinalIgnoreCase))
            {
                warnings.Add($"프롬프트 인젝션 의심 패턴 발견: '{keyword}'");
            }
        }

        // 주민등록번호 탐지
        var residentMatches = ResidentIdPattern.Matches(filtered);
        if (residentMatches.Count > 0)
        {
            warnings.Add($"주민등록번호 패턴 {residentMatches.Count}개 발견");
        }

        // 전화번호 탐지
        var phoneMatches = PhonePattern.Matches(filtered);
        if (phoneMatches.Count > 0)
        {
            warnings.Add($"전화번호 패턴 {phoneMatches.Count}개 발견");
        }

        return (filtered, warnings);
    }

    public static string RedactSensitiveInfo(string content)
    {
        var result = ResidentIdPattern.Replace(content, "******-*******");
        result = PhonePattern.Replace(result, "***-****-****");
        return result;
    }
}
