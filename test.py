import wx
import viewkit


class TestWindow(viewkit.MainWindow):
    def __init__(self, ctx):
        viewkit.MainWindow.__init__(self, ctx)
        exitButton = self.creator.button("Exit", self.onExit)

    def define_features(self):
        return [
            viewkit.Feature("file_exit", "Exit", "Ctrl+Q", self.onExit),
            viewkit.Feature("file_open_audio", "Open audio file", None),
            viewkit.Feature("file_open_video", "Open video file", None),
            viewkit.Feature("help_about", "Show about dialog", None)
        ]

    def define_menu(self):
        return viewkit.MenuDefinition(
            viewkit.TopMenuDefinition(
                "File", "F", [
                    viewkit.MenuItemDefinition(None, "Open", "O", [
                        viewkit.MenuItemDefinition("file_open_audio", "Audio", "A"),
                        viewkit.MenuItemDefinition("file_open_video", "Video", "V")
                    ]),
                    viewkit.separator,
                    viewkit.MenuItemDefinition("file_exit", "Exit", "E")
                ]
            ),
            viewkit.TopMenuDefinition(
                "Help", "H", [
                    viewkit.MenuItemDefinition("help_about", "About", "A")
                ]
            )
        )

    def onExit(self, event):
        self.Close()

user_name_field = viewkit.CustomSettingField(
    "user_name",
    {
        "type": "string",
        "default": "nekochan",
    }
)

user_age_field = viewkit.CustomSettingField(
    "user_age",
    {
        "type": "number",
        "default": 27,
    }
)

ctx = viewkit.ApplicationContext(
    applicationName="viewkitExample",
    supportedLanguages={"ja-JP": "日本語", "en-US": "English"},
    language="ja-JP",
    settingFileName="settings.json",
    customSettingFields=[user_name_field, user_age_field],
)
viewkit.run(ctx, TestWindow)
