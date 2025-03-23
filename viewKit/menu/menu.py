import wx
from typing import Callable


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

    def add_top_menu(self, display_name: str, accessor_letter: str) -> TopMenu:
        topmenu = TopMenu(display_name, accessor_letter)
        self.top_menus.append(topmenu)
        return topmenu

    def need_menu_bar(self):
        return len(self.top_menus) > 0
