using System.Text.Json;
using LegalDocParser.Models;
using LegalDocParser.Services.Interfaces;

namespace LegalDocParser.Services;

/// <summary>
/// 애플리케이션 설정 로드/저장 서비스
/// </summary>
public class SettingsService : ISettingsService
{
    private static readonly string SettingsPath = Path.Combine(
        AppDomain.CurrentDomain.BaseDirectory, "appsettings.json");

    private static readonly JsonSerializerOptions JsonOptions = new()
    {
        WriteIndented = true,
        PropertyNameCaseInsensitive = true
    };

    public AppSettings Load()
    {
        try
        {
            if (File.Exists(SettingsPath))
            {
                var json = File.ReadAllText(SettingsPath);
                return JsonSerializer.Deserialize<AppSettings>(json, JsonOptions)
                       ?? new AppSettings();
            }
        }
        catch
        {
            // 설정 파일 로드 실패 시 기본값 반환
        }

        return new AppSettings();
    }

    public void Save(AppSettings settings)
    {
        var json = JsonSerializer.Serialize(settings, JsonOptions);
        File.WriteAllText(SettingsPath, json);
    }
}
