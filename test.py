import wx
import viewkit


class TestWindow(viewkit.MainWindow):
    def __init__(self, ctx):
        viewkit.MainWindow.__init__(self, ctx)
        panel = wx.Panel(self, -1)
        exitButton = wx.Button(panel, -1, "Exit")
        exitButton.Bind(wx.EVT_BUTTON, self.OnExit)

    def define_features(self):
        return [
            viewkit.Feature("file_exit", "Exit", "Ctrl+Q", self.OnExit)
        ]

    def define_menu(self, ctx):
        menu = ctx.menu
        filemenu = menu.add_top_menu("File", "F")
        filemenu.add_item("file_exit", "&Exit")
        editmenu = menu.add_top_menu("Edit", "E")
        helpmenu = menu.add_top_menu("Help", "H")

    def OnExit(self, event):
        self.Close()


ctx = viewkit.ApplicationContext("testtest")
viewkit.run(ctx, TestWindow)
