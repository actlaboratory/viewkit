import wx
from viewkit.context.app import ApplicationContext
from viewkit.context.window import WindowContext


class MainWindow(wx.Frame):
    def __init__(self, app_ctx: ApplicationContext):
        wx.Frame.__init__(self, None, -1, app_ctx.applicationName)
        self.ctx = WindowContext()

    def define_menu_bar(self) -> wx.MenuBar:
        """このメソッドをオーバーライドして、メインウインドウのメニューを設定します。最終的に適用する wx.MenuBar のインスタンスを返すようにします。メニューバーを作らないアプリケーションであっても、 return None するメソッドで上書きしてください。"""
        raise RuntimeError("Please override define_menu_bar method to setup the application menu")
