import wx
from . import str2key


class ModifierKeyOnly(Exception):
    """ショートカットキーの文字列が修飾キーのみで構成されている場合に発生するエラー"""
    pass


class UnrecognizedKeyString(Exception):
    """ショートカットキーの文字列が認識できない場合に発生するエラー"""
    pass


class ShortcutKey:
    def __init__(self, modifier_flags, key_code):
        self.modifier_flags = modifier_flags
        self.key_code = key_code

    def isSame(self, other: 'ShortcutKey') -> bool:
        """他のショートカットキーと同じかどうかを比較する"""
        return (self.modifier_flags == other.modifier_flags and
                self.key_code == other.key_code)


def strToShortcutKey(key: str) -> ShortcutKey:
    """人間が読めるショートカットキー文字列から、ShortcutKeyのインスタンスに変換する"""
    key = key.upper()  # 大文字に統一して処理
    modifier_keys = {
        "CTRL": wx.ACCEL_CTRL,
        "ALT": wx.ACCEL_ALT,
        "SHIFT": wx.ACCEL_SHIFT
    }
    flags = 0
    flag_count = 0
    for name, value in modifier_keys.items():
        if name + "+" in key:
            flags |= value
            flag_count += 1
    # 修飾キーのみのもの、修飾キーでないキーが複数含まれるものはダメ
    codestr = key.split("+")
    if not len(codestr) - flag_count == 1:
        raise ModifierKeyOnly("shortcut key string must contain only one non-modifier key, and modifier-key-only string is not allowed.")
    codestr = codestr[len(codestr) - 1]
    if codestr not in str2key.str2key:  # 存在しないキーの指定はエラー
        raise UnrecognizedKeyString(f"'{codestr}' is not recognized as a valid key string.")
    key_code = str2key.str2key[codestr]
    return ShortcutKey(flags, key_code)


SHORTCUT_KEY_SEPARATOR = "/"


def separateShortcutKeyString(key_string: str) -> list[str]:
    """ショートカットキーの文字列を分割する。"""
    if not key_string:
        return []
    return key_string.split(SHORTCUT_KEY_SEPARATOR)
