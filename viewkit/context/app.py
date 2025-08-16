from viewkit.settings import SettingsManager

class ApplicationContext:
    def __init__(
        self,
        *,
        applicationName: str,
        supportedLanguages: dict,
        language: str,
        settingFileName:str=""
    ):
        self.applicationName = applicationName
        self.supportedLanguages = supportedLanguages
        self.language = language
        self.settingFileName = settingFileName
        if self.settingFileName == "":
            self.settingFileName = "%s.json" % self.applicationName
        self.settings = SettingsManager(self.settingFileName)
