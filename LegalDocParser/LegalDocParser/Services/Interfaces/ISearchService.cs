using LegalDocParser.Models;

namespace LegalDocParser.Services.Interfaces;

public interface ISearchService
{
    Task<IReadOnlyList<SearchResult>> SearchAsync(
        string content,
        string pattern,
        bool useRegex = false,
        bool caseSensitive = false);
}
