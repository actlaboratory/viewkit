import wx
from viewkit.subwnd import SubWindow


class ExceptionDialog(SubWindow):
    def __init__(self, parent, ctx, title, msg):
        SubWindow.__init__(self, parent, ctx, title)

        info, dummy = self.creator.inputbox("", default_value=msg, style=wx.TE_MULTILINE |
                                            wx.TE_READONLY | wx.BORDER_RAISED, sizer_flag=wx.EXPAND, x=750, text_layout=None)
        f = info.GetFont()
        f.SetPointSize((int)(f.GetPointSize() * (2 / 3)))
        info.SetFont(f)
        info.SetMinSize(wx.Size(750, 240))
        info.hideScrollBar(wx.HORIZONTAL)

        # フッター
        footerCreator = self.creator.makeChild(style=wx.ALIGN_RIGHT | wx.ALL, margin=20)
        footerCreator.okbutton(_("再試行"))
        footerCreator.cancelbutton(_("キャンセル"))
