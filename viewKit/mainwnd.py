import wx

class MainWindow(wx.Frame):
    def __init__(self, title):
        wx.Frame.__init__(self, None, -1, title)
