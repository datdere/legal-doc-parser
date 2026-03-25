using System.Diagnostics;

namespace LegalDocParser.Helpers;

/// <summary>
/// 외부 프로세스(Python 등)를 비동기로 호출하는 헬퍼
/// </summary>
public class ProcessHelper
{
    public record ProcessResult(
        int ExitCode,
        string StandardOutput,
        string StandardError,
        TimeSpan Duration);

    public static async Task<ProcessResult> RunAsync(
        string fileName,
        string arguments,
        int timeoutMs = 300000,
        CancellationToken cancellationToken = default)
    {
        var stopwatch = Stopwatch.StartNew();

        using var process = new Process();
        process.StartInfo = new ProcessStartInfo
        {
            FileName = fileName,
            Arguments = arguments,
            RedirectStandardOutput = true,
            RedirectStandardError = true,
            UseShellExecute = false,
            CreateNoWindow = true,
            StandardOutputEncoding = System.Text.Encoding.UTF8,
            StandardErrorEncoding = System.Text.Encoding.UTF8
        };

        var stdoutBuilder = new System.Text.StringBuilder();
        var stderrBuilder = new System.Text.StringBuilder();

        process.OutputDataReceived += (_, e) =>
        {
            if (e.Data != null)
                stdoutBuilder.AppendLine(e.Data);
        };

        process.ErrorDataReceived += (_, e) =>
        {
            if (e.Data != null)
                stderrBuilder.AppendLine(e.Data);
        };

        try
        {
            process.Start();
            process.BeginOutputReadLine();
            process.BeginErrorReadLine();

            using var timeoutCts = new CancellationTokenSource(timeoutMs);
            using var linkedCts = CancellationTokenSource.CreateLinkedTokenSource(
                cancellationToken, timeoutCts.Token);

            try
            {
                await process.WaitForExitAsync(linkedCts.Token);
            }
            catch (OperationCanceledException)
            {
                KillProcessTree(process);

                if (cancellationToken.IsCancellationRequested)
                    throw;

                stopwatch.Stop();
                return new ProcessResult(
                    -1,
                    stdoutBuilder.ToString(),
                    $"Process timed out after {timeoutMs}ms",
                    stopwatch.Elapsed);
            }

            stopwatch.Stop();
            return new ProcessResult(
                process.ExitCode,
                stdoutBuilder.ToString(),
                stderrBuilder.ToString(),
                stopwatch.Elapsed);
        }
        catch (Exception ex) when (ex is not OperationCanceledException)
        {
            stopwatch.Stop();
            return new ProcessResult(
                -1,
                string.Empty,
                $"Failed to start process: {ex.Message}",
                stopwatch.Elapsed);
        }
    }

    private static void KillProcessTree(Process process)
    {
        try
        {
            process.Kill(entireProcessTree: true);
        }
        catch
        {
            // 프로세스가 이미 종료된 경우 무시
        }
    }
}
