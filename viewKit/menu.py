from typing import Callable

class MenuItem:
    def __init__(self, identifier: str, displayName: str, shortcut: str | None, action: Callable | None):
        self.identifier = identifier
        self.displayName = displayName
        self.shortcut = shortcut
        self.action = action


class TopMenu:
    def __init__(self, displayName: str, shortcut: str):
        self.displayName = displayName
        self.shortcut = shortcut
        self.items = []

    def add_item(self, item: MenuItem):
        self.items.append(item)


class Menu:
    def __init__(self):
        self.top_menus = []
        self.refs = {}

    def add_top_menu(self, topMenu):
        self.top_menus.append(topMenu)

