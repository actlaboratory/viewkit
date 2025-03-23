from typing import Callable
from .shortcut import str_to_shortcut_key

class MenuItem:
    def __init__(self, identifier: str, display_name: str, shortcut_key: str | None, action: Callable | None):
        self.identifier = identifier
        self.display_name = display_name
        self.shortcut = str_to_shortcut_key(self.shortcut_key)
        self.action = action


class TopMenu:
    def __init__(self, displayName: str, accessorLetter: str):
        self.displayName = displayName
        self.accessorLetter = accessorLetter
        self.items = []

    def add_item(self, identifier: str, display_name: str, shortcut_key: str | None, action: Callable | None):
        self.items.append(MenuItem(identifier, display_name, shortcut_key, action))


class Menu:
    def __init__(self):
        self.top_menus = []

    def add_top_menu(self, displayName: str, accessorLetter: str):
        self.top_menus.append(TopMenu(displayName, accessorLetter))

