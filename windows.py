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
                keyValueSetting.KeyValueSettingKey("name", "名前", wx.LIST_FORMAT_LEFT, 200),
                keyValueSetting.KeyValueSettingKey("age", "年齢", wx.LIST_FORMAT_RIGHT, 100),
                keyValueSetting.KeyValueSettingKey("job", "職業", wx.LIST_FORMAT_LEFT, 200),
            ],
            values=[
                {
                    "name": "nekochan",
                    "age": "27",
                    "job": "猫"
                },
                {
                    "name": "usachan",
                    "age": "24",
                    "job": "うっさ",
                },
            ],
            allow_edit_rows=True,
            custom_buttons=[
                keyValueSetting.KeyValueSettingCustomButton("説明", "explain")
            ],
        )
        self.showSubWindow(MyKvWindow, "Key Value Setting", config, modal=True)


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

class MyKvWindow(keyValueSetting.KeyValueSettingWindow):
    def explain(self, event):
        if event is None:
            return
        v = event.selected_value_row
        viewkit.dialog.simple(self, "説明", "%s %s歳 職業は%sだよ。よろしくね" % (v["name"], v["age"], v["job"]))
