import wx
from viewkit.subwnd import SubWindow
from viewkit.version import getVersion


class VersionInfoDialog(SubWindow):
    def __init__(self, parent, ctx, title, parameters):
        SubWindow.__init__(self, parent, ctx, title)
        textList = []
        textList.append("%s (%s)" % (self.app_ctx.application_name, self.app_ctx.short_name))
        textList.append("%s: %s" % (_("ソフトウェアバージョン"), self.app_ctx.application_version))
        textList.append("%s: %s" % (_("viewkit バージョン"), getVersion()))
        # textList.append(_("ライセンス") + ": " + constants.APP_LICENSE)
        # textList.append(_("開発元") + ": %s - %s" %(constants.APP_DEVELOPERS, constants.APP_DEVELOPERS_URL))
        # textList.append(_("ソフトウェア詳細情報") + ": " + constants.APP_DETAILS_URL)
        # textList.append("")
        textList.append(_("ライセンス/著作権情報については、同梱の license.txt を参照してください。"))
        textList.append("")

        self.info, dummy = self.creator.inputbox("", default_value="\r\n".join(textList), style=wx.TE_MULTILINE |
                                                 wx.TE_READONLY | wx.TE_NO_VSCROLL | wx.BORDER_RAISED, sizer_flag=wx.EXPAND, x=750, text_layout=None)
        f = self.info.GetFont()
        f.SetPointSize((int)(f.GetPointSize() * (2 / 3)))
        self.info.SetFont(f)
        self.info.SetMinSize(wx.Size(750, 240))

        # フッター
        footerCreator = self.creator.makeChild(style=wx.ALIGN_RIGHT | wx.ALL, margin=20)
        self.closeBtn = footerCreator.closebutton(_("閉じる"))
        self.closeBtn.SetDefault()
