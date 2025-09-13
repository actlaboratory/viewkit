import wx
import viewkit
import viewkit.presets.keyValueSetting as keyValueSetting


class TestWindow(viewkit.MainWindow):
    def __init__(self, ctx):
        viewkit.MainWindow.__init__(self, ctx)
        exitButton = self.creator.button("Exit", self.onExit)

    def define_features(self):
        return [
            viewkit.Feature("file_exit", "Exit", "Ctrl+Q", self.onExit),
            viewkit.Feature("file_open_audio", "Open audio file", None),
            viewkit.Feature("file_open_video", "Open video file", None),
            viewkit.Feature("file_show_sub_window", "Show sub window", "ctrl+t", self.testSubWindow),
            viewkit.Feature("file_reload_main_window", "Reload main window", "ctrl+r/f5", self.reload),
            viewkit.Feature("file_show_kv_window", "show key value settings", "ctrl+k", self.showKvWindow),
            viewkit.Feature("help_about", "Show about dialog", None, self.showAboutDialog)
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
                    viewkit.MenuItemDefinition("file_show_sub_window", "Show sub window", "T"),
                    viewkit.MenuItemDefinition("file_reload_main_window", "Reload main window", "R"),
                    viewkit.MenuItemDefinition("file_show_kv_window", "Show key value settings", "K"),
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
        raise RuntimeError("test")
        # self.Close()

    def testSubWindow(self, event):
        result = self.showSubWindow(TestSubWindow, "Test Sub Window", modal=True)
        viewkit.dialog.simple(self, "Result from sub window", f"Result: {result}")

    def showAboutDialog(self, event):
        self.showSubWindow(viewkit.presets.VersionInfoDialog, "About", modal=True)

    def showKvWindow(self, event):
        config = keyValueSetting.KeyValueSettingConfig(
            listview_label="プロフィール項目",
            keys=[
                keyValueSetting.KeyValueSettingKey("名前", wx.LIST_FORMAT_LEFT, 200),
                keyValueSetting.KeyValueSettingKey("年齢", wx.LIST_FORMAT_RIGHT, 100),
                keyValueSetting.KeyValueSettingKey("職業", wx.LIST_FORMAT_LEFT, 200),
            ],
            values = [
                {
                    "名前": "nekochan",
                    "年齢": "27",
                    "職業": "猫"
                },
                {
                    "名前": "usachan",
                    "年齢": "24",
                    "職業": "うっさ",
                },
            ],
            allow_edit_keys=True,
            custom_buttons=[
                keyValueSetting.KeyValueSettingCustomButton("説明", self.onExplainButtonClicked)
            ],
        )
        self.showSubWindow(keyValueSetting.KeyValueSettingWindow, "Key Value Setting", config, modal=True)

    def onExplainButtonClicked(self, event):
        viewkit.dialog.simple("説明", "これはキーと値のペアを編集するためのウィンドウです。")

class TestSubWindow(viewkit.SubWindow):
    def __init__(self, parent, ctx, title):
        viewkit.SubWindow.__init__(self, parent, ctx, title)
        self.value = None
        self.creator.staticText("This is a sub window")
        self.creator.inputbox("hogehogehogehoge", default_value="にゃーにゃーにゃー")
        self.creator.button("Reload from code", self.reload)
        self.creator.okbutton("OK", self.onOK)
        self.creator.cancelbutton("Cancel", self.onCancel)

    def onOK(self, event):
        self.value = "OK"
        event.Skip()

    def onCancel(self, event):
        self.value = "Cancel"
        event.Skip()

    def result(self):
        return self.value
