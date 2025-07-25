import wx
import viewkit


class TestWindow(viewkit.MainWindow):
    def __init__(self, ctx):
        viewkit.MainWindow.__init__(self, ctx)
        exitButton = self.creator.button("Exit", self.OnExit)

    def define_features(self):
        return [
            viewkit.Feature("file_exit", "Exit", "Ctrl+Q", self.OnExit),
            viewkit.Feature("file_open_audio", "Open audio file", None, self.OnExit),
            viewkit.Feature("file_open_video", "Open video file", None, self.OnExit),
            viewkit.Feature("help_about", "Show about dialog", None, self.OnExit)
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

    def OnExit(self, event):
        self.Close()


ctx = viewkit.ApplicationContext(
    applicationName="testtest",
    supportedLanguages={"ja-JP": "日本語", "en-US": "English"},
    language="ja-JP",
)
viewkit.run(ctx, TestWindow)
