import wx
from viewkit.context.app import ApplicationContext
from viewkit.context.window import WindowContext


class MainWindow(wx.Frame):
    def __init__(self, app_ctx: ApplicationContext):
        wx.Frame.__init__(self, None, -1, app_ctx.applicationName)
        self.ctx = WindowContext()
