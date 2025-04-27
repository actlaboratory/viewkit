import wx
import viewkit


class TestWindow(viewkit.MainWindow):
    def __init__(self, ctx):
        viewkit.MainWindow.__init__(self, ctx)
        panel = wx.Panel(self, -1)
        exitButton = wx.Button(panel, -1, "Exit")
        exitButton.Bind(wx.EVT_BUTTON, self.OnExit)

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


ctx = viewkit.ApplicationContext("testtest")
viewkit.run(ctx, TestWindow)
