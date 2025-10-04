import wx
from viewkit import Feature
from viewkit import MainWindow, SubWindow
from .keyValueSetting import *
from viewkit.shortcut.str2key import str2key


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
            btn = self.creator.button("Change", self._onChangeButton(i))
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

    def _onChangeButton(self, index):
        def handler(event):
            self.showSubWindow(ShortcutKeyDetectionWindow, "Change shortcut key")
        return handler

class ShortcutKeyDetectionWindow(SubWindow):
    def __init__(self, parent, ctx, title, parameters=None):
        super().__init__(parent, ctx, title)
        self.creator.staticText(_("設定するには、使用したいキーの組み合わせを押します。\n設定を解除するには、Escキーを押します。"))
        self._key_name_text=self.creator.staticText("",sizer_flag=wx.ALIGN_CENTER | wx.ALL,margin=20)
        self.error_text=self.creator.staticText("",sizer_flag=wx.ALIGN_CENTER)
        self._cancel_button = self.creator.cancelbutton(_("設定解除"))
        self.Bind(wx.EVT_TIMER, self._handleTimer)
        self._timer=wx.Timer(self)
        self.TIMER_INTERVAL=100
        self._all_detected_keys = [] # キーが全部リリースされるまで記録し続ける
        self._last_detected_keys = [] # 最後のタイマーフレームで検出されたキー

    def onOpen(self):
        self._timer.StartOnce(self.TIMER_INTERVAL)

    def _handleTimer(self, event):
        self._timer.Stop()
        hits = []
        key_names = str2key.keys()
        for name in key_names:
            code=str2key[name]
            if code<=4: # マウスを使われると困る
                continue
            #カテゴリキーは取得不可、NumLockとCapsLockは押し下げ状態ではなく現在のON/OFFを返してしまうので
            if type(code)==wx.KeyCategoryFlags or name=="NUMLOCK" or name=="SCROLL":
                continue
            if wx.GetKeyState(code):
                hits.append(name)
            # end ヒット
        # end 全部のキー
        if hits:
            self._cancel_button.Disable() #こうしないとEnterで反応してEnterがショートカットに使えない
            self.last_detected_keys = []
            for i,key in enumerate(hits):
                self.last_detected_keys.append(key)
                if len(self._all_detected_keys)<len(self.last_detected_keys):
                    self._all_detected_keys.append(key)
                    key_str = "+".join(self._all_detected_keys)
                    self._key_name_text.SetLabel(key_str)
                    self._key_name_text.SetLabel(key_str)
                    self.panel.Layout()
                else:									#キーが放されたら前の入力を検証する
                    self._cancel_button.Enable()
                    # とりあえずバリデーションはすっ飛ばす
                    self.EndModal(wx.ID_OK)		#正しい入力なのでダイアログを閉じる
        self._timer.Start(self.TIMER_INTERVAL)

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
