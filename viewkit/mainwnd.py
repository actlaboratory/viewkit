import wx
from typing import List
from viewkit.context.app import ApplicationContext
from viewkit.context.window import WindowContext
from viewkit.feature import Feature
from viewkit.menu import MenuDefinition, MenuItem, MenuItemWithSubmenu, separator
from viewkit.creator import ViewCreator


class MainWindow(wx.Frame):
    def __init__(self, app_ctx: ApplicationContext):
        wx.Frame.__init__(self, None, -1, app_ctx.applicationName)
        self.app_ctx = app_ctx
        self.ctx = WindowContext()
        self.Bind(wx.EVT_MENU, self._receiveMenuCommand)
        self.clear()

    def clear(self, space=0):
        self.DestroyChildren()
        panel = wx.Panel(self, wx.ID_ANY, size=(-1, -1))
        self.creator = ViewCreator(0, panel, None, wx.VERTICAL, style=wx.ALL, space=space)
        self.Layout()

    def define_features(self) -> List[Feature]:
        """このメソッドをオーバーライドして、アプリケーションが持つ機能を定義します。viewkit.Feature のリストを返す必要があります。"""
        raise RuntimeError("Please override define_features method to describe the application features")

    def define_menu(self, ctx: WindowContext):
        """このメソッドをオーバーライドして、メインウインドウのメニューを設定します。 viewkit.MenuDefinition の機能を使って、メニューを定義してください。メニューバーを持たないアプリケーションの場合は、 return None で終了してください。"""
        raise RuntimeError("Please override define_menu method to setup the application menu")

    def _register_features(self, features):
        for feature in features:
            self.ctx.feature_store.register(feature)

    def _apply_custom_shortcuts(self):
        """カスタムショートカット設定を適用する"""
        shortcuts_settings = self.app_ctx.settings.getShortcutSettings()
        if shortcuts_settings:
            self.ctx.feature_store.applyCustomShortcutSettings(shortcuts_settings)

    def _assign_refs(self):
        for feature in self.ctx.feature_store.all().values():
            self.ctx.ref_store.getRef(feature.identifier)

    def _setup_menu_bar(self):
        if not self.ctx.menu.need_menu_bar():
            return
        bar = wx.MenuBar()
        for top_menu in self.ctx.menu.top_menus:
            menu = wx.Menu()
            for item in top_menu.items:
                if item is separator:
                    menu.AppendSeparator()
                    continue
                ref = self.ctx.ref_store.getRef(item.identifier)
                menu_item = self._generate_menu_item(menu, ref, item)
                menu.Append(menu_item)
            bar.Append(menu, "%s(&%s)" % (top_menu.display_name, top_menu.accessor_letter))
        self.SetMenuBar(bar)

    def _generate_menu_item(self, menu: wx.Menu, ref: int, item: MenuItem | MenuItemWithSubmenu):
        if isinstance(item, MenuItem):
            display_name = item.display_name
            feature = self.ctx.feature_store.getByIdentifier(item.identifier)
            if feature.shortcut_keys:
                display_name += "\t" + str(feature.shortcut_keys[0])
            return wx.MenuItem(menu, ref, display_name)
        elif isinstance(item, MenuItemWithSubmenu):
            submenu = wx.Menu()
            for sub_item in item.sub_menu_items:
                ref = self.ctx.ref_store.getRef(sub_item.identifier)
                menu_item = self._generate_menu_item(submenu, ref, sub_item)
                submenu.Append(menu_item)
            return wx.MenuItem(menu, ref, item.display_name, subMenu=submenu)

    def _apply_accelerator_table(self):
        if not self.ctx.menu.need_menu_bar():
            return
        self.SetAcceleratorTable(self.ctx.generateAcceleratorTable())

    def _receiveMenuCommand(self, event):
        identifier = self.ctx.ref_store.getIdentifier(event.GetId())
        if identifier is None:
            return
        feature = self.ctx.feature_store.getByIdentifier(identifier)
        if feature is None:
            return
        if feature.action is not None:
            feature.action(event)
