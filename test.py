import wx
import viewkit


class TestWindow(viewkit.MainWindow):
    def __init__(self, ctx):
        viewkit.MainWindow.__init__(self, ctx)
        panel = wx.Panel(self, -1)
        exitButton = wx.Button(panel, -1, "Exit")
        exitButton.Bind(wx.EVT_BUTTON, self.OnExit)

    def OnExit(self, event):
        self.Close()


ctx = viewkit.ApplicationContext("testtest")
viewkit.run(ctx, TestWindow)
