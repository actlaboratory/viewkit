import wx
from typing import Callable
from .shortcut import str_to_shortcut_key


class MenuItem:
    def __init__(self, identifier: str, display_name: str, shortcut_key: str | None, action: Callable | None):
        self.identifier = identifier
        self.display_name = display_name
        self.shortcut = str_to_shortcut_key(self.shortcut_key)
        self.action = action


class TopMenu:
    def __init__(self, display_name: str, accessor_letter: str):
        self.display_name = display_name
        self.accessor_letter = accessor_letter
        self.items = []

    def add_item(self, identifier: str, display_name: str, shortcut_key: str | None, action: Callable | None):
        self.items.append(MenuItem(identifier, display_name, shortcut_key, action))


class Menu:
    def __init__(self):
        self.top_menus = []

    def add_top_menu(self, display_name: str, accessor_letter: str):
        self.top_menus.append(TopMenu(display_name, accessor_letter))

    def generate_menu_bar(self):
        bar = wx.MenuBar()
        for top_menu in self.top_menus:
            menu = wx.Menu()
            bar.Append(menu, "%s(&%s)" % (top_menu.display_name, top_menu.accessor_letter))
        # サブメニューアイテムはあとでやる
        return bar
