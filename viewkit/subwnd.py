import wx
import _winxptheme
from viewkit.creator import ViewCreator, ViewModeCalculator


class ModalResult:
    def __init__(self, code, user_object):
        self.code = code
        self.user_object = user_object

    def __str__(self):
        return "ModalResult(code=%s, user_object=%s)" % (self.code, self.user_object)


class SubWindow(wx.Dialog):
    """viewkit では、メインウィンドウ以外のウィンドウをサブウィンドウと呼びます。現状では、これらは全て wx.Dialogのサブクラスとして実装されます。"""

    def __init__(self, parent, ctx, title, style=wx.CAPTION | wx.SYSTEM_MENU | wx.BORDER_DEFAULT):
        self.app_ctx = ctx
        self.reload_requested = False
        wx.Dialog.__init__(self, parent, wx.ID_ANY, title, style=style)
        _winxptheme.SetWindowTheme(self.GetHandle(), "", "")
        self.SetEscapeId(wx.ID_NONE)
        self.Bind(wx.EVT_CLOSE, self.OnClose)
        self.panel = wx.Panel(self, wx.ID_ANY)
        self.creator = ViewCreator(
            ViewModeCalculator(self.app_ctx.settings.getSetting('view.is_dark'), self.app_ctx.settings.getSetting('view.is_word_wrap')).getMode(),
            self.app_ctx.font.getFont(),
            self.panel,
            None,
            wx.VERTICAL,
            style=wx.ALL,
            space=0
        )

    def ShowModal(self):
        self.creator.getPanel().Layout()
        self.creator.getSizer().Fit(self)
        super().ShowModal()

    def Show(self):
        self.creator.getPanel().Layout()
        self.creator.getSizer().Fit(self)
        super().Show()

    def result(self):
        return None

    # closeイベントで呼ばれる。Alt+F4対策
    def OnClose(self, event):
        if self.GetWindowStyleFlag() & wx.CLOSE_BOX == wx.CLOSE_BOX:
            event.Skip()
        else:
            event.Veto()

    def reload(self, event=None):  # 直接イベントハンドラとして使ってもいいように
        self.reload_requested = True
        self.EndModal(wx.ID_NONE)
