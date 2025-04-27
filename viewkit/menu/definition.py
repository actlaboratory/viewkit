from typing import List


class MenuItemDefinition:
    def __init__(self, identifier: str, display_name: str, accessor_letter: str, sub_menu_items: List["MenuItemDefinition"] = None):
        self.identifier = identifier
        self.display_name = display_name
        self.accessor_letter = accessor_letter
        self.sub_menu_items = sub_menu_items

    def getDisplayString(self) -> str:
        result = self.display_name
        if self.accessor_letter:
            # アクセラレーターきーの処理
            if self.accessor_letter in self.display_name.upper():
                # 該当の文字の直前に&をつける
                idx = self.display_name.upper().find(self.accessor_letter)
                result = self.display_name[0:idx] + "&" + self.display_name[idx:]
            else:
                # 末尾に(&O)のようにしてくっつける
                result = self.display_name + "(&" + self.accessor_letter + ")"
        return result

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
