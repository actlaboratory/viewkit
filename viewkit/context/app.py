import logging
import logging.handlers
from viewkit.settings import SettingsManager, CustomSettingField
from viewkit.fontManager import FontManager, DEFAULT_FONT
from .message import ContextMessageHandler, ContextMessageReceiver


class ApplicationContext:
    def __init__(
        self,
        application_name: str,
        application_version: str,
        short_name: str,
        *,
        supported_languages: dict,
        language: str,
        setting_file_name: str = "",
        custom_setting_fields: list[CustomSettingField] = [],
        log_handler: logging.Handler = None,
    ):
        self._message_handler = ContextMessageHandler()
        self.application_name = application_name
        self.short_name = short_name
        self.application_version = application_version
        self.short_name = short_name
        self.supported_languages = supported_languages
        self.language = language
        self.setting_file_name = setting_file_name
        self._initLogger(log_handler)
        self.logger.debug(
            "ApplicationContext initialized with application_name=%s, application_version=%s, short_name=%s, language=%s, setting_file_name=%s",
            application_name,
            application_version,
            short_name,
            language,
            self.setting_file_name)
        if self.setting_file_name == "":
            self.setting_file_name = "%s.json" % self.application_name
            self.logger.debug("ApplicationContext using default setting_file_name=%s", self.setting_file_name)
        self.settings = SettingsManager(self.setting_file_name)
        self.font = FontManager()
        for field in custom_setting_fields:
            self.settings.registerCustomField(field)
        self.settings.loadOrCreateDefault()
        print(self.settings.getSetting("view.font"))
        if not self.font.setFontFromString(self.settings.getSetting("view.font")):
            self.settings.changeSetting("view.font", DEFAULT_FONT)

    def registerContextMessageReceiver(self, key, callable):
        self._message_handler.registerReceiver(key, ContextMessageReceiver(callable))

    def sendContextMessage(self, key, params=None):
        self._message_handler.send(key, params)

    def _initLogger(self, log_handler):
        self._root_logger = logging.getLogger("viewkit")
        self._root_logger.setLevel(logging.DEBUG)
        if log_handler:
            self._root_logger.addHandler(log_handler)
        else:
            h = logging.handlers.RotatingFileHandler(
                "%s.log" %
                self.short_name,
                mode="w",
                encoding="UTF-8",
                maxBytes=2**20 *
                256,
                backupCount=5)  # 256MB
            f = logging.Formatter("%(name)s - %(levelname)s - %(message)s (%(asctime)s)")
            h.setFormatter(f)
            self._root_logger.addHandler(h)
        self.logger = logging.getLogger(__name__)
