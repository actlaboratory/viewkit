from viewkit.settings import SettingsManager, CustomSettingField

class ApplicationContext:
    def __init__(
        self,
        application_name: str,
        supported_languages: dict,
        language: str,
        setting_file_name:str="",
        custom_setting_fields: list[CustomSettingField] = []
    ):
        self.application_name = application_name
        self.supported_languages = supported_languages
        self.language = language
        self.setting_file_name = setting_file_name
        if self.setting_file_name == "":
            self.setting_file_name = "%s.json" % self.application_name
        self.settings = SettingsManager(self.setting_file_name)

        for field in custom_setting_fields:
            self.settings.registerCustomField(field)
        self.settings.loadOrCreateDefault()
