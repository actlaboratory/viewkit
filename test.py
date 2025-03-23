import wx
import viewkit


class TestWindow(viewkit.MainWindow):
    def __init__(self, ctx):
        viewkit.MainWindow.__init__(self, ctx)
        panel = wx.Panel(self, -1)
        exitButton = wx.Button(panel, -1, "Exit")
        exitButton.Bind(wx.EVT_BUTTON, self.OnExit)

    def define_menu_bar(self):
        menu = self.ctx.menu
        menu.add_top_menu("File", "F")
        menu.add_top_menu("Edit", "E")
        menu.add_top_menu("Help", "H")
        return menu.generate_menu_bar()

    def OnExit(self, event):
        self.Close()


ctx = viewkit.ApplicationContext("testtest")
viewkit.run(ctx, TestWindow)
