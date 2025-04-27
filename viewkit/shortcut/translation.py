import wx
from . import str2key


class InvalidShortcutKeyError:
    pass


class ShortcutKey:
    def __init__(self, modifier_flags, key_code):
        self.modifier_flags = modifier_flags
        self.key_code = key_code


def str_to_shortcut_key(key: str) -> ShortcutKey:
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
        raise InvalidShortcutKeyError("shortcut key string must contain only one non-modifier key, and modifier-key-only string is not allowed.")
    codestr = codestr[len(codestr) - 1]
    if codestr not in str2key.str2key:  # 存在しないキーの指定はエラー
        raise InvalidShortcutKeyError("unrecognized key name: " + codestr)
    key_code = str2key.str2key[codestr]
    return ShortcutKey(flags, key_code)
