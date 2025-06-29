# language select dialog

import _winxptheme
import wx

from logging import getLogger

from viewkit.creator import ViewCreator


class LangDialog:
    def __init__(self, supported_languages: dict):
        self.lang_code = list(supported_languages.keys())
        self.lang_name = list(supported_languages.values())
        self.identifier = "LanguageSelectDialog"
        self.log = getLogger("%s.%s" % ("viewkit", self.identifier))
        self.value = None

    def Initialize(self):
        self.log.debug("created")
        self.wnd = wx.Dialog(None, -1, "language select")
        _winxptheme.SetWindowTheme(self.wnd.GetHandle(), "", "")
        self.wnd.SetEscapeId(wx.ID_NONE)

        self.panel = wx.Panel(self.wnd, wx.ID_ANY)
        self.sizer = wx.BoxSizer(wx.VERTICAL)
        self.panel.SetSizer(self.sizer)

        self.InstallControls()

    def InstallControls(self):
        """いろんなwidgetを設置する。"""
        self.creator = ViewCreator(0, self.panel, self.sizer, wx.VERTICAL, 20)
        # 翻訳
        self.langSelect, static = self.creator.combobox("select language", self.lang_name, None, state=0)
        self.ok = self.creator.okbutton("OK", None)

    def Destroy(self, events=None):
        self.log.debug("destroy")
        self.wnd.Destroy()

    def GetData(self):
        select = self.langSelect.GetSelection()
        return self.lang_code[select]

    # ウィンドウを中央に配置してモーダル表示する
    # ウィンドウ内の部品を全て描画してから呼び出す
    def Show(self, modal=True):
        self.panel.Layout()
        self.sizer.Fit(self.wnd)
        self.wnd.Centre()
        if modal:
            result = self.wnd.ShowModal()
            if result != wx.ID_CANCEL:
                self.value = self.GetData()
            self.wnd.Destroy()
        else:
            result = self.wnd.Show()
        self.log.debug("show(modal=%s) result=%s" % (str(modal), str(result)))
        return result

    def GetValue(self):
        self.log.debug("Value:%s" % str(self.value))
        return self.value
