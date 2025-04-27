from typing import List


class MenuItemDefinition:
    def __init__(self, identifier: str, display_name: str, sub_menu_items: List["MenuItemDefinition"] = None):
        self.identifier = identifier
        self.display_name = display_name
        self.sub_menu_items = sub_menu_items


class TopMenuDefinition:
    def __init__(self, display_name: str, accessor_letter: str, items: List[MenuItemDefinition]):
        self.display_name = display_name
        self.accessor_letter = accessor_letter
        self.items = items


class MenuDefinition:
    def __init__(self, *args: List[TopMenuDefinition]):
        for arg in args:
            if not isinstance(arg, TopMenuDefinition):
                raise ValueError("MenuDefinition must be initialized with TopMenuDefinition instances")
        self.top_menus = args
