import sys
import traceback
import wx
import _winxptheme

from logging import getLogger
from typing import List

from viewkit.context.app import ApplicationContext
from viewkit.context.window import WindowContext
from viewkit.feature import Feature
from viewkit.menu import MenuDefinition, MenuItem, MenuItemWithSubmenu, separator
from viewkit.creator import ViewCreator, ViewModeCalculator
from viewkit.subwnd import ModalResult
from viewkit.context.message import MAIN_WINDOW_RELOADED
from viewkit.context.messageParameters import MainWindowReloaded
from viewkit.reload import reload_recursive
from viewkit.presets.exceptionDialog import ExceptionDialog


class MainWindow(wx.Frame):
    def __init__(self, app_ctx: ApplicationContext, *, size_x=-1, size_y=-1):
        wx.Frame.__init__(
            self,
            None,
            wx.ID_ANY,
            app_ctx.application_name,
            size=(
                size_x if size_x > 0 else app_ctx.settings.getSetting('main_window.size_x'),
                size_y if size_y > 0 else app_ctx.settings.getSetting('main_window.size_y')),
            pos=(
                app_ctx.settings.getSetting('main_window.x'),
                app_ctx.settings.getSetting('main_window.y')))
        if app_ctx.settings.getSetting('main_window.maximized'):
            self.Maximize()
        self.app_ctx = app_ctx
        self.logger = getLogger(__name__)
        self.window_ctx = WindowContext()
        self.Bind(wx.EVT_MENU, self._receiveMenuCommand)
        self.Bind(wx.EVT_MOVE_END, self._windowMove)
        self.Bind(wx.EVT_SIZE, self._windowResize)
        self.Bind(wx.EVT_MAXIMIZE, self._windowResize)
        _winxptheme.SetWindowTheme(self.GetHandle(), "", "")
        self.logger.info("initialized")
        self.clear()

    def clear(self, space=0):
        self.DestroyChildren()
        panel = wx.Panel(self, wx.ID_ANY, size=(-1, -1))
        self.creator = ViewCreator(
            ViewModeCalculator(self.app_ctx.settings.getSetting('view.is_dark'), self.app_ctx.settings.getSetting('view.is_word_wrap')).getMode(),
            self.app_ctx.font.getFont(),
            panel,
            None,
            wx.VERTICAL,
            style=wx.ALL,
            space=space
        )
        self.Layout()

    def define_features(self) -> List[Feature]:
        """このメソッドをオーバーライドして、アプリケーションが持つ機能を定義します。viewkit.Feature のリストを返す必要があります。"""
        raise RuntimeError("Please override define_features method to describe the application features")

    def define_menu(self, ctx: WindowContext):
        """このメソッドをオーバーライドして、メインウインドウのメニューを設定します。 viewkit.MenuDefinition の機能を使って、メニューを定義してください。メニューバーを持たないアプリケーションの場合は、 return None で終了してください。"""
        raise RuntimeError("Please override define_menu method to setup the application menu")

    def onOpen(self):
        """ウィンドウ生成時に呼ばれる処理"""
        pass

    def Show(self):
        self.creator.getPanel().Layout()
        super().Show()

    def showSubWindow(self, window_class, title, parameters=None, modal=True):
        """サブウィンドウを表示します。window_class は viewkit.SubWindow のサブクラスである必要があります。ウィンドウ上での作業結果を表すオブジェクトを返します。"""
        while (True):
            try:
                wnd = window_class(self, self.app_ctx, title, parameters)
                wnd.Center()
                code = None
                if modal:
                    code = wnd.ShowModal()
                else:
                    code = wnd.Show()
                result = ModalResult(code, wnd.result())
                if wnd.reload_requested:
                    module = sys.modules.get(window_class.__module__)
                    if e := self._reloadWindow(window_class) is None:
                        window_class = getattr(module, window_class.__name__)
                        self.logger.debug("re-opening the sub window")
                        continue
                    else:
                        raise e
                # end reload
                wnd.Destroy()
                break
            except Exception as e:
                if hasattr(sys, "frozen"):
                    # 解発ちゅう以外は上に投げる
                    raise e
                msg = list(traceback.TracebackException.from_exception(e).format())
                self.logger.error("".join(msg))
                wnd = ExceptionDialog(self, self.app_ctx, _("リロードエラー"), "".join(msg))
                wnd.Center()
                code = wnd.ShowModal()
                if code == wx.ID_CANCEL:
                    print("cancel")
                    return e

                module = sys.modules.get(window_class.__module__)
                if e := self._reloadWindow(window_class) is None:
                    window_class = getattr(module, window_class.__name__)
                    self.logger.debug("re-opening the sub window")
                else:
                    raise e
        # end until user interaction except window reloading
        return result

    def _reloadWindow(self, window_class):
        while (True):
            module = sys.modules.get(window_class.__module__)
            self.logger.info("Reloading sub window: %s" % module)
            try:
                reload_recursive(module)
                return None
            except BaseException as e:
                if hasattr(sys, "frozen"):
                    # 解発ちゅう以外は上に投げる
                    raise e
                msg = list(traceback.TracebackException.from_exception(e).format())
                self.logger.error("".join(msg))
                wnd = ExceptionDialog(self, self.app_ctx, _("リロードエラー"), "".join(msg))
                wnd.Center()
                code = wnd.ShowModal()
                if code == wx.ID_CANCEL:
                    print("cancel")
                    return e

    def reload(self, evt=None):  # 直接イベントハンドラとして使ってもいいように
        # トップレベルウインドウの処理は app でやらないといけないが、 app -> mainWindow の依存方向を守りたいのでメッセージング機構を使って逆転させる
        self.app_ctx.sendContextMessage(MAIN_WINDOW_RELOADED, MainWindowReloaded(self))

    def _registerFeatures(self, features):
        for feature in features:
            self.window_ctx.feature_store.register(feature)

    def _applyCustomShortcuts(self):
        """カスタムショートカット設定を適用する"""
        shortcuts_settings = self.app_ctx.settings.getShortcutSettings()
        if shortcuts_settings:
            self.window_ctx.feature_store.applyCustomShortcutSettingsWithConflictResolution(shortcuts_settings)

    def _assignRefs(self):
        for feature in self.window_ctx.feature_store.all().values():
            self.window_ctx.ref_store.getRef(feature.identifier)

    def _setupMenuBar(self):
        if not self.window_ctx.menu.need_menu_bar():
            return
        bar = wx.MenuBar()
        for top_menu in self.window_ctx.menu.top_menus:
            menu = wx.Menu()
            for item in top_menu.items:
                if item is separator:
                    menu.AppendSeparator()
                    continue
                ref = self.window_ctx.ref_store.getRef(item.identifier)
                menu_item = self._generateMenuItem(menu, ref, item)
                menu.Append(menu_item)
            bar.Append(menu, "%s(&%s)" % (top_menu.display_name, top_menu.accessor_letter))
        self.SetMenuBar(bar)

    def _generateMenuItem(self, menu: wx.Menu, ref: int, item: MenuItem | MenuItemWithSubmenu):
        if isinstance(item, MenuItem):
            display_name = item.display_name
            feature = self.window_ctx.feature_store.getByIdentifier(item.identifier)
            if feature.shortcut_keys:
                display_name += "\t" + str(feature.shortcut_keys[0])
            return wx.MenuItem(menu, ref, display_name)
        elif isinstance(item, MenuItemWithSubmenu):
            submenu = wx.Menu()
            for sub_item in item.sub_menu_items:
                ref = self.window_ctx.ref_store.getRef(sub_item.identifier)
                menu_item = self._generateMenuItem(submenu, ref, sub_item)
                submenu.Append(menu_item)
            return wx.MenuItem(menu, ref, item.display_name, subMenu=submenu)

    def _applyAcceleratorTable(self):
        if not self.window_ctx.menu.need_menu_bar():
            return
        self.SetAcceleratorTable(self.window_ctx.generateAcceleratorTable())

    def _receiveMenuCommand(self, event):
        identifier = self.window_ctx.ref_store.getIdentifier(event.GetId())
        if identifier is None:
            return
        feature = self.window_ctx.feature_store.getByIdentifier(identifier)
        if feature is None:
            return
        if feature.action is not None:
            feature.action(event)

    def _windowMove(self, event):
        # wx.EVT_MOVE_END→wx.MoveEvent
        # 設定ファイルに位置を保存
        self.app_ctx.settings.changeSetting('main_window.x', self.GetPosition().x)
        self.app_ctx.settings.changeSetting('main_window.y', self.GetPosition().y)
        self.app_ctx.settings.save()
        event.Skip()

    def _windowResize(self, event):
        # wx.EVT_SIZE→wx.SizeEvent
        if not self.IsActive():
            # ウィンドウがアクティブでない時(ウィンドウ生成時など)のイベントは無視
            event.Skip()
            return

        self.app_ctx.settings.changeSetting('main_window.maximized', int(self.IsMaximized()))
        if not self.IsMaximized():
            self.app_ctx.settings.changeSetting('main_window.size_x', event.GetSize().x)
            self.app_ctx.settings.changeSetting('main_window.size_y', event.GetSize().y)
        self.app_ctx.settings.save()
        # sizerを正しく機能させるため、Skipの呼出が必須
        event.Skip()
