using LegalDocParser.Models;

namespace LegalDocParser.Services.Interfaces;

public interface ISettingsService
{
    AppSettings Load();
    void Save(AppSettings settings);
}
