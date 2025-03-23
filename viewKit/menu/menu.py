import wx
from typing import Callable
from .definition import MenuDefinition


class MenuItem:
    def __init__(self, identifier: str, display_name: str):
        self.identifier = identifier
        self.display_name = display_name


class TopMenu:
    def __init__(self, display_name: str, accessor_letter: str):
        self.display_name = display_name
        self.accessor_letter = accessor_letter
        self.items = []

    def add_item(self, identifier: str, display_name: str):
        self.items.append(MenuItem(identifier, display_name))


class Menu:
    def __init__(self):
        self.top_menus = []

    def setup(self, definition: MenuDefinition):
        for top_menu_def in definition.top_menus:
            top_menu = self._add_top_menu(top_menu_def.display_name, top_menu_def.accessor_letter)
            for item_def in top_menu_def.items:
                top_menu.add_item(item_def.identifier, item_def.display_name)

    def _add_top_menu(self, display_name: str, accessor_letter: str) -> TopMenu:
        topmenu = TopMenu(display_name, accessor_letter)
        self.top_menus.append(topmenu)
        return topmenu

    def need_menu_bar(self):
        return len(self.top_menus) > 0
