using LegalDocParser.Services;
using Xunit;

namespace LegalDocParser.Tests.Services;

public class SearchServiceTests
{
    private readonly SearchService _service = new();

    [Fact]
    public async Task SearchAsync_FindsSimpleMatch()
    {
        var content = "제1조 (목적)\n이 계약은 목적을 정한다.\n제2조 (정의)";
        var results = await _service.SearchAsync(content, "목적");

        Assert.Equal(2, results.Count);
        Assert.Equal(1, results[0].LineNumber);
        Assert.Equal(2, results[1].LineNumber);
    }

    [Fact]
    public async Task SearchAsync_CaseInsensitive_Default()
    {
        var content = "Article 1\narticle 2\nARTICLE 3";
        var results = await _service.SearchAsync(content, "article");

        Assert.Equal(3, results.Count);
    }

    [Fact]
    public async Task SearchAsync_CaseSensitive()
    {
        var content = "Article 1\narticle 2\nARTICLE 3";
        var results = await _service.SearchAsync(content, "Article", caseSensitive: true);

        Assert.Single(results);
        Assert.Equal(1, results[0].LineNumber);
    }

    [Fact]
    public async Task SearchAsync_Regex()
    {
        var content = "제1조 (목적)\n제2조 (정의)\n제10조 (해지)";
        var results = await _service.SearchAsync(content, @"제\d+조", useRegex: true);

        Assert.Equal(3, results.Count);
    }

    [Fact]
    public async Task SearchAsync_EmptyContent_ReturnsEmpty()
    {
        var results = await _service.SearchAsync("", "test");
        Assert.Empty(results);
    }

    [Fact]
    public async Task SearchAsync_EmptyPattern_ReturnsEmpty()
    {
        var results = await _service.SearchAsync("some content", "");
        Assert.Empty(results);
    }

    [Fact]
    public async Task SearchAsync_InvalidRegex_ReturnsEmpty()
    {
        var results = await _service.SearchAsync("content", "[invalid", useRegex: true);
        Assert.Empty(results);
    }

    [Fact]
    public async Task SearchAsync_ReturnsCorrectColumns()
    {
        var content = "앞부분 키워드 뒷부분";
        var results = await _service.SearchAsync(content, "키워드");

        Assert.Single(results);
        Assert.Equal(4, results[0].ColumnStart);
        Assert.Equal(3, results[0].MatchLength);
    }

    [Fact]
    public async Task SearchAsync_MultipleMatchesInOneLine()
    {
        var content = "가나다 가나다 가나다";
        var results = await _service.SearchAsync(content, "가나다");

        Assert.Equal(3, results.Count);
        Assert.All(results, r => Assert.Equal(1, r.LineNumber));
    }
}
