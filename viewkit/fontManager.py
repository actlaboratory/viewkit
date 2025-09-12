import wx
from logging import getLogger


# フォントサイズの設定可能サイズ範囲
MIN_FONT_SIZE = 5
MAX_FONT_SIZE = 35
DEFAULT_FONT = "bold 'ＭＳ ゴシック' 22"


class FontManager():
    def __init__(self):
        self.log = getLogger(__name__)
        self.log.debug("created")

        # 設定ファイルの情報を基にfontを生成
        self.font = wx.Font()
        self.font.SetNativeFontInfoUserDesc(DEFAULT_FONT)

    def setFontFromString(self, setting_string: str):
        if not self.font.SetNativeFontInfoUserDesc(setting_string):
            self.log.warning("fontString error. SetNativeFontInfoUserDesc(" + setting_string + ") returned false.")
            self.font.SetNativeFontInfoUserDesc(DEFAULT_FONT)
            return False
        return True

    # フォント設定ダイアログを表示
    # 引数に親ウィンドウを指定
    def showSettingDialog(self, parent):
        # FontDataを生成し、設定を行う
        fontData = wx.FontData()
        fontData.EnableEffects(False)  # 取り消し線などは設定できない
        fontData.SetAllowSymbols(False)  # シンボルフォントの設定は認めない
        fontData.SetRange(MIN_FONT_SIZE, MAX_FONT_SIZE)
        fontData.SetInitialFont(self.font)

        fontchooser = wx.FontDialog(parent, fontData)
        if (fontchooser.ShowModal() == wx.ID_OK):
            font = fontchooser.GetFontData().GetChosenFont()
        else:
            self.log.info("font change was canceled.")
        # アサーションエラーの対策
        if not font.IsOk():
            self.log.warning("font change error. IsOK() returned False.")
            return false
        self.font = font
        return True

    def getFont(self):
        return self.font

    def getName(self):
        return self.font.GetFaceName()

    def getSize(self):
        return self.font.GetPointSize()

    def getInfo(self):
        return self.font.GetNativeFontInfoUserDesc()
