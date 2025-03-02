import wx
import viewKit

class TestFrame(wx.Frame):
    def __init__(self):
        wx.Frame.__init__(self, None, -1, "Test Frame")
        panel = wx.Panel(self, -1)
        exitButton = wx.Button(panel, -1, "Exit")
        exitButton.Bind(wx.EVT_BUTTON, self.OnExit)

    def OnExit(self, event):
        self.Close()

viewKit.run(TestFrame)
