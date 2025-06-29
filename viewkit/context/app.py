class ApplicationContext:
    def __init__(
    self,
     *,
    applicationName: str,
    supportedLanguages : dict,
    language: str,
):
        self.applicationName = applicationName
        self.supportedLanguages= supportedLanguages
        self.language = language