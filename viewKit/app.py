import wx


class App(wx.App):
    def __init__(self, initial_window):
        """アプリケーション初期化"""
        self._initial_window = initial_window
        wx.App.__init__(self)

    def run(self):
        """ウインドウを表示して、アプリケーションを開始。アプリケーションが終了するまで制御を返さない"""
        self._initial_window().Show()
        self.MainLoop()
