import gettext
import locale
import os
import sys
import wx

import viewkit.views.langDialog

from viewkit.context.app import ApplicationContext
from viewkit.views.langDialog import LangDialog


class App(wx.App):
    def __init__(self, ctx: ApplicationContext, initial_window):
        """アプリケーション初期化"""
        self.ctx = ctx
        self._initial_window = initial_window
        wx.App.__init__(self)

    def run(self):
        """ウインドウを表示して、アプリケーションを開始。アプリケーションが終了するまで制御を返さない"""
        self._addPath()
        self._init_translation()
        wnd = self._initial_window(self.ctx)
        wnd._register_features(wnd.define_features())
        wnd._assign_refs()
        wnd.ctx.menu.setup(wnd.define_menu())
        wnd._setup_menu_bar()
        wnd._apply_accelerator_table()
        wnd.Show()
        self.MainLoop()

    def _addPath(self):
        """sys.pathと、3.8以降の場合のdll読み込み対象パスにアプリケーション直下を追加"""
        if sys.version_info.major >= 3 and sys.version_info.minor >= 8:
            os.add_dll_directory(os.path.dirname(self.getAppPath()))
        sys.path.append(os.path.dirname(self.getAppPath()))

    def _init_translation(self):
        """翻訳を初期化する。"""
        localeLang = locale.getdefaultlocale()[0].replace("_", "-")
        if self.ctx.language in list(self.ctx.supportedLanguages.keys()):
            lang = self.ctx.language
        elif localeLang in list(self.ctx.supportedLanguages.keys()):
            lang = localeLang
        else:
            # 言語選択を表示
            langSelect = LangDialog(self.ctx.supportedLanguages)
            langSelect.Initialize()
            langSelect.Show()
            lang = langSelect.GetValue()
        self.ctx.language = lang
        self.translator = gettext.translation("messages", "locale", languages=[lang], fallback=True)
        self.translator.install()

    def getAppPath(self):
        """アプリの絶対パスを返す"""
        if hasattr(sys, "frozen"):
            # exeファイルで実行されている
            return sys.executable
        else:
            # pyファイルで実行されている
            return os.path.abspath(sys.argv[0])
