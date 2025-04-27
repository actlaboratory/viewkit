from typing import boolean
from .str2key import *

# 単独のキーの組み合わせのバリデーション
validation_dict = {
    # 絶対に設定できないキーの組み合わせ
    "always_forbidden": set([
        "CTRL+ESCAPE", # スタートメニュー
        "CTRL+SHIFT+ESCAPE" # タスクマネージャ
        "CTRL+WINDOWS+RETURN", # ナレーターの起動と終了
        "ALT+SHIFT+PRINTSCREEN", # ハイコントラストの切り替え
        "ALT+ESCAPE", # 最前面ウィンドウの最小化
        "ALT+TAB", # ウィンドウ間の移動
        "ALT+SHIFT+TAB", # ウィンドウ間の移動
        "APPLICATIONS", # コンテキストメニューの表示
        "SHIFT+F10", # コンテキストメニューの表示
        "F10", # ALTキーの代わり
        "ESCAPE", # 操作の取り消し
        "ALT+F4", # アプリケーションの終了
        "SPACE", # ボタンの押下
        "ALT+SPACE", # リストビュー等で全ての選択を解除
    ]),
    # ウインドウ内で文字入力をする場合には設定できないキーの組み合わせ
    "forbidden_if_char_input_allowed": set([
        "CTRL+INSERT", # コピー
        "SHIFT+INSERT", # 貼り付け
        "CTRL+Z", # 元に戻す
        "CTRL+X", # 切り取り
        "CTRL+C", # コピー
        "CTRL+V", # 貼り付け
        "CTRL+A", # すべて選択
        "CTRL+Y", # やり直し
        "CTRL+F7", # 単語登録(日本語変換時のみ)
        "CTRL+F10", # IMEメニュー表示(日本語変換時のみ)
    ]),
}

VALIDATION_ERROR_EMPTY = "empty"
VALIDATION_ERROR_FORBIDDEN = "forbidden"
VALIDATION_ERROR_MODIFIER_ONLY = "modifier_only"
VALIDATION_ERROR_MULTI_NONMODIFIER = "multi_nonmodifier"
VALIDATION_ERROR_NEEDS_MODIFIER = "needs_modifier"

class ShortcutKeyValidationError(Exception):
    """ショートカットキーの組み合わせが無効な場合に発生するエラー"""
    def __init__(self, key: str, reason:str):
        super().__init__(f"Invalid shortcut key combination: {key}, reason: {reason}")
        self.key = key
        self.reason = reason

class ShortcutKeyStringValidator:
    """ショートカットキーを表す文字列を解析して、利用可能な諸音かっとキーかどうかをチェックする。"""
    def __init__(self, has_char_input_on_screen:boolean):
        self.modifier_keys = set([
            "CTRL",
            "ALT",
            "SHIFT",
        ])
        self.allowed_standalone = set()
        self.allowed_with_modifier = set()
        self.forbidden_combinations = []
        # 初期設定
        self.allowed_standalone |= set(str2FunctionKey.keys() + str2SpecialKey.keys())
        if has_char_input_on_screen:
            #単独で文字入力の制御に利用されるので修飾キー必須
            self.allowed_with_modifier |= str2InputControlKey.keys()
        else:
            #単独で文字入力の制御に利用されるが、それがないため単独利用可能
            self.allowed_standalone |= str2InputControlKey.keys()
        # 禁止されているパターンを全部追加
        for elem in validation_dict["always_forbidden"]:
            self._add_forbidden_combination(elem)
        # ウインドウ内で文字入力をする場合には、さらに編集関連のキーを禁止にする必要があるので追加する
        if has_char_input_on_screen:
            for elem in validation_dict["forbidden_if_char_input_allowed"]:
                self._add_forbidden_combination(elem)
            # end add
        # end for
        return self

    def _add_forbidden_combination(self, combination_string):
        combinations = combination_string.split("+")
        for c in combinations:
            c = c.upper()
            if not c in str2key:
                raise ValueError("%s is not recognized" % c)
            # end key is not recognized
        # end for each key name
        # ctrl + shift とか shift+ control と順番が入れ替わってもいいように set で管理する
        self.forbidden_combinations.append(set(combinations))

    def validate(self, key_string:str):
        if not key_string:
            raise ShortcutKeyEmptyError("Shortcut key string is empty")
        keys = key_string.upper().split("+")
        is_modifier=False
        is_shift=False
        standalone_count=0
        with_modifier_count=0
        for key in keys:
            if key in self.modifier_keys:
                if key=="SHIFT":
                    is_shift=True
                else:
                    is_modifier=True
                continue
            if key in self.allowed_standalone:
                standalone_count+=1
                continue
            if key in self.allowed_with_modifier:
                with_modifier_count+=1
                continue
            #ここまでcontinueされなかったらエラー
            raise ShortcutKeyValidationError(                key_string, VALIDATION_ERROR_FORBIDDEN)
        #組み合わせの妥当性確認
        if len(keys)==1: # 単独のショートカットキー
            if standalone_count>0: # 単独で利用可能なショートカットが単独で書かれている == OK
                return True
            else: # 1個だけ書かれているけど、単独で利用可能なキーには入ってない
                if is_modifier>0 or is_shift>0: # それが就職キーの場合はエラー
                    raise ShortcutKeyValidationError(key_string, VALIDATION_ERROR_MODIFIER_ONLY)
                else: # 就職キーとの組み合わせでなければ使えないキーが単独で書かれている == NG
                    raise ShortcutKeyValidationError(key_string, VALIDATION_ERROR_NEEDS_MODIFIER)
        #２つ以上が指定されている場合
        if standalone_count+with_modifier_count >1:
            raise ShortcutKeyValidationError(key_string, VALIDATION_ERROR_MULTI_NONMODIFIER)
        elif standalone_count==0 and with_modifier_count==0:
            raise ShortcutKeyValidationError(key_string, VALIDATION_ERROR_MODIFIER_ONLY)
        if set(keys) in self.disablePattern:
            raise ShortcutKeyValidationError(key_string, VALIDATION_ERROR_FORBIDDEN)
        return True

