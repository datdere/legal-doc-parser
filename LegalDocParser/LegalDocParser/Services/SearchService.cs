using System.Text.RegularExpressions;
using LegalDocParser.Models;
using LegalDocParser.Services.Interfaces;

namespace LegalDocParser.Services;

/// <summary>
/// 변환된 문서 내 키워드 검색 서비스
/// </summary>
public class SearchService : ISearchService
{
    private static readonly TimeSpan RegexTimeout = TimeSpan.FromSeconds(5);

    public Task<IReadOnlyList<SearchResult>> SearchAsync(
        string content,
        string pattern,
        bool useRegex = false,
        bool caseSensitive = false)
    {
        return Task.Run(() => Search(content, pattern, useRegex, caseSensitive));
    }

    private static IReadOnlyList<SearchResult> Search(
        string content,
        string pattern,
        bool useRegex,
        bool caseSensitive)
    {
        if (string.IsNullOrEmpty(content) || string.IsNullOrEmpty(pattern))
            return Array.Empty<SearchResult>();

        var results = new List<SearchResult>();
        var lines = content.Split('\n');

        var regexOptions = RegexOptions.Compiled;
        if (!caseSensitive)
            regexOptions |= RegexOptions.IgnoreCase;

        Regex regex;
        try
        {
            var regexPattern = useRegex ? pattern : Regex.Escape(pattern);
            regex = new Regex(regexPattern, regexOptions, RegexTimeout);
        }
        catch (ArgumentException)
        {
            return Array.Empty<SearchResult>();
        }

        for (int i = 0; i < lines.Length; i++)
        {
            var line = lines[i];
            MatchCollection matches;

            try
            {
                matches = regex.Matches(line);
            }
            catch (RegexMatchTimeoutException)
            {
                continue;
            }

            foreach (Match match in matches)
            {
                results.Add(new SearchResult(
                    MatchedText: match.Value,
                    LineNumber: i + 1,
                    ColumnStart: match.Index,
                    MatchLength: match.Length,
                    ContextLine: line.Trim()
                ));
            }
        }

        return results;
    }
}
