using LegalDocParser.Helpers;
using Xunit;

namespace LegalDocParser.Tests.Helpers;

public class ProcessHelperTests
{
    [Fact]
    public async Task RunAsync_InvalidCommand_ReturnsError()
    {
        var result = await ProcessHelper.RunAsync(
            "nonexistent_command_xyz",
            "--version",
            5000);

        Assert.Equal(-1, result.ExitCode);
        Assert.Contains("Failed to start process", result.StandardError);
    }

    [Fact]
    public async Task RunAsync_Timeout_ReturnsTimeoutError()
    {
        // 긴 실행 명령에 매우 짧은 타임아웃
        var result = await ProcessHelper.RunAsync(
            "sleep",
            "60",
            100); // 100ms 타임아웃

        Assert.Equal(-1, result.ExitCode);
        Assert.Contains("timed out", result.StandardError);
    }

    [Fact]
    public async Task RunAsync_CancellationToken_StopsProcess()
    {
        using var cts = new CancellationTokenSource();
        cts.CancelAfter(100);

        await Assert.ThrowsAsync<OperationCanceledException>(async () =>
        {
            await ProcessHelper.RunAsync(
                "sleep",
                "60",
                60000,
                cts.Token);
        });
    }
}
