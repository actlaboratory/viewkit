import wx
from typing import Callable, List, Optional
from .definition import MenuDefinition, separator


class MenuItem:
    def __init__(self, identifier: str, display_name: str):
        self.identifier = identifier
        self.display_name = display_name


class MenuItemWithSubmenu:
    def __init__(self, identifier, display_name: str, sub_menu_items: List[MenuItem]):
        self.identifier = identifier
        self.display_name = display_name
        self.sub_menu_items = sub_menu_items


class TopMenu:
    def __init__(self, display_name: str, accessor_letter: str):
        self.display_name = display_name
        self.accessor_letter = accessor_letter
        self.items = []

    def add_item(self, identifier: str, display_string: str):
        self.items.append(MenuItem(identifier, display_string))

    def add_item_with_submenu(self, item: MenuItemWithSubmenu):
        self.items.append(item)

    def addSeparator(self):
        self.items.append(separator)


class Menu:
    def __init__(self):
        self.top_menus = []

    def setup(self, definition: Optional[MenuDefinition]):
        if definition is None:
            self.top_menus = []
            return
        for top_menu_def in definition.top_menus:
            top_menu = self._add_top_menu(top_menu_def.display_name, top_menu_def.accessor_letter)
            for item_def in top_menu_def.items:
                if item_def is separator:
                    top_menu.addSeparator()
                    continue
                if item_def.sub_menu_items:
                    top_menu.add_item_with_submenu(_submenu_def_to_instance(item_def))
                else:
                    top_menu.add_item(item_def.identifier, item_def.getDisplayString())

    def _add_top_menu(self, display_name: str, accessor_letter: str) -> TopMenu:
        topmenu = TopMenu(display_name, accessor_letter)
        self.top_menus.append(topmenu)
        return topmenu

    def need_menu_bar(self):
        return len(self.top_menus) > 0


def _submenu_def_to_instance(submenu_def: MenuItemWithSubmenu) -> MenuItemWithSubmenu:
    sub_menu_items = []
    for item in submenu_def.sub_menu_items:
        sub_menu_items.append(MenuItem(item.identifier, item.getDisplayString()))
    return MenuItemWithSubmenu(submenu_def.identifier, submenu_def.getDisplayString(), sub_menu_items)
