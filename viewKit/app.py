import wx
from viewkit.context.app import ApplicationContext


class App(wx.App):
    def __init__(self, ctx: ApplicationContext, initial_window):
        """アプリケーション初期化"""
        self.ctx = ctx
        self._initial_window = initial_window
        wx.App.__init__(self)

    def run(self):
        """ウインドウを表示して、アプリケーションを開始。アプリケーションが終了するまで制御を返さない"""
        wnd = self._initial_window(self.ctx)
        bar = wnd.define_menu_bar()
        if bar:
            wnd.SetMenuBar(bar)
        wnd.Show()
        self.MainLoop()
