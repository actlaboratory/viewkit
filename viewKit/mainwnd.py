import wx

class MainWindow(wx.Frame):
    def __init__(self, ctx):
        wx.Frame.__init__(self, None, -1, ctx.applicationName)
        self.ctx = ctx
