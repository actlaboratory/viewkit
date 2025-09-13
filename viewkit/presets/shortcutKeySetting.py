import wx
from viewkit import Feature
from viewkit import MainWindow, SubWindow
from .keyValueSetting import *


class ShortcutKeyEditWindow(SubWindow):
    def __init__(self, parent, ctx, title, parameters: KeyValueSettingEditEvent):
        super().__init__(parent, ctx, title, parameters)
        settable_shortcut_keys = 5
        self._shortcut_key_strings = []
        for i in range(settable_shortcut_keys):
            self._shortcut_key_strings.append("")
        if parameters.original_value_row is not None:
            self._shortcut_key_strings = parameters.original_value_row["shortcut_keys"].split("/")
        self._shortcut_key_inputs = []
        for i in range(settable_shortcut_keys):
            default_value = ""
            if i < len(self._shortcut_key_strings):
                default_value = self._shortcut_key_strings[i]
            input, _ = self.creator.inputbox("shortcut %d" % (i + 1), default_value=default_value)
            self._shortcut_key_inputs.append(input)
        self.creator.okbutton("OK")
        self.creator.cancelbutton("Cancel")

    def result(self):
        shortcut_keys = []
        for input in self._shortcut_key_inputs:
            v = input.GetValue().strip()
            if v != "":
                shortcut_keys.append(v)
        return {
            "feature": self.parameters.original_value_row["feature"],
            "shortcut_keys": "/".join(shortcut_keys)
        }


def showShortcutKeySettingWindow(parent: MainWindow, features: list[Feature]):
    keys = [
        KeyValueSettingKey("feature", "feature", wx.LIST_FORMAT_LEFT, 200),
        KeyValueSettingKey("shortcut_keys", "shortcut keys", wx.LIST_FORMAT_LEFT, 200)
    ]
    rows = []
    for f in features:
        rows.append({
            "feature": f.display_name,
            "shortcut_keys": "/".join([str(k) for k in f.shortcut_keys]) if f.shortcut_keys is not None else ""
        })
    config = KeyValueSettingConfig(
        listview_label="features",
        keys=keys,
        values=rows,
        allow_edit_rows=False,
        editor_window_class=ShortcutKeyEditWindow,
    )
    return parent.showSubWindow(KeyValueSettingWindow, "shortcut key settings", config, modal=True)
