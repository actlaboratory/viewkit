import wx
import viewkit
import viewkit.presets.keyValueSetting as keyValueSetting
from viewkit.presets.shortcutKeySetting import showShortcutKeySettingWindow
from viewkit.subwnd import SubWindow


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
            viewkit.Feature("file_show_kv_window", "show key value settings", None, self.showKvWindow),
            viewkit.Feature("file_show_shortcut_window", "show shortcut key settings", "ctrl+k", self.showShortcutWindow),
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
                    viewkit.MenuItemDefinition("file_show_shortcut_window", "Show shortcut key settings", "S"),
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
            allow_edit_rows=False,
            editor_window_class=KvEditWindow,
            custom_buttons=[
                keyValueSetting.KeyValueSettingCustomButton("説明", "explain")
            ],
        )
        self.showSubWindow(MyKvWindow, "Key Value Setting", config, modal=True)

    def showShortcutWindow(self, event):
        features = self.window_ctx.feature_store.all().values()
        ret = showShortcutKeySettingWindow(self, features)
        for r in ret:
            print(r)


class TestSubWindow(viewkit.SubWindow):
    def __init__(self, parent, ctx, title, parameters):
        viewkit.SubWindow.__init__(self, parent, ctx, title)
        self.value = None

        self.creator.staticText("This is a sub window")
        i, dummy = self.creator.inputbox("some input", default_value="にゃーにゃーにゃー")
        i.hideScrollBar(wx.HORIZONTAL)

        self.creator.button("Reload from code", self.reload)

        footerCreator = self.creator.makeChild(style=wx.ALIGN_RIGHT | wx.ALL, margin=20)
        footerCreator.okbutton("OK", self.onOK)
        footerCreator.cancelbutton("Cancel")

    def onOK(self, event):
        self.value = "OK"
        event.Skip()

    def result(self):
        return self.value


class MyKvWindow(keyValueSetting.KeyValueSettingWindow):
    def explain(self, event):
        if event is None:
            return
        v = event.selected_value_row
        viewkit.dialog.simple(self, "説明", "%s %s歳 職業は%sだよ。よろしくね" % (v["name"], v["age"], v["job"]))


class KvEditWindow(SubWindow):
    def __init__(self, parent, ctx, title, event):
        super().__init__(parent, ctx, title)
        self.event = event
        self._name, _ = self.creator.inputbox("名前", default_value=event.original_value_row.get("name", "") if event.original_value_row else "")
        self._age, _ = self.creator.inputbox("年齢", default_value=event.original_value_row.get("age", "") if event.original_value_row else "")
        self._job, _ = self.creator.inputbox("職業", default_value=event.original_value_row.get("job", "") if event.original_value_row else "")
        self.creator.okbutton("OK", self._handleOk)
        self.creator.cancelbutton("Cancel")

    def result(self):
        return {
            "name": self._name.GetValue(),
            "age": self._age.GetValue(),
            "job": self._job.GetValue()
        }

    def _handleOk(self, event):
        if self._name.GetValue().strip() == "":
            viewkit.dialog.win("error", "名前は必須です")
            return
        if not self._age.GetValue().isdigit():
            viewkit.dialog.win("error", "年齢は整数で入力してください")
            return
        if self._job.GetValue().strip() == "":
            viewkit.dialog.win("error", "職業は必須です")
            return
        if self._name.GetValue() in [v["name"] for i, v in enumerate(self.event.all_value_rows) if i != self.event.editing_index]:
            viewkit.dialog.win("error", "その名前は既に使われています")
            return
        event.Skip()
