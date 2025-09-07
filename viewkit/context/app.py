import logging
from viewkit.settings import SettingsManager, CustomSettingField

class ApplicationContext:
    def __init__(
        self,
        application_name: str,
        short_name: str,
        *,
        supported_languages: dict,
        language: str,
        setting_file_name:str="",
        custom_setting_fields: list[CustomSettingField] = [],
        log_handler: logging.Handler = None,
    ):
        self._initLogger(log_handler)
        self.application_name = application_name
        self.short_name = short_name
        self.supported_languages = supported_languages
        self.language = language
        self.setting_file_name = setting_file_name
        self.logger.debug("ApplicationContext initialized with application_name=%s, short_name=%s, language=%s, setting_file_name=%s", application_name, short_name, language, self.setting_file_name)
        if self.setting_file_name == "":
            self.setting_file_name = "%s.json" % self.application_name
            self.logger.debug("ApplicationContext using default setting_file_name=%s", self.setting_file_name)
        self.settings = SettingsManager(self.setting_file_name)

        for field in custom_setting_fields:
            self.settings.registerCustomField(field)
        self.settings.loadOrCreateDefault()

    def _initLogger(self, log_handler):
        self._root_logger = logging.getLogger("viewkit")
        self._root_logger.setLevel(logging.DEBUG)
        if log_handler:
            self._root_logger.addHandler(log_handler)
        else:
            h = logging.FileHandler('viewkit.log', encoding='utf-8', mode='w')
            f = logging.Formatter("%(name)s - %(levelname)s - %(message)s (%(asctime)s)")
            h.setFormatter(f)
            self._root_logger.addHandler(h)
        self.logger = logging.getLogger(__name__)
