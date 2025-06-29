import os
import unittest
import viewkit.shortcut


class TestShortcutValidator(unittest.TestCase):
    def _testcase(self, validator, name, key_string, success, error_reason=None):
        try:
            validator.validate(key_string)
        except viewkit.shortcut.ShortcutKeyValidationError as e:
            if success:
                self.fail(f"Test case {name} failed: expected success but got error: {e}")
            else:
                self.assertEqual(error_reason, e.reason, f"Test case {name} failed: {e.reason}")

    def test_initializeWithCharInputOff(self):
        viewkit.shortcut.ShortcutKeyStringValidator(False)

    def test_initializeWithCharInputOn(self):
        viewkit.shortcut.ShortcutKeyStringValidator(True)

    def test_empty(self):
        validator = viewkit.shortcut.ShortcutKeyStringValidator(False)
        self._testcase(validator, "empty", "", False, viewkit.shortcut.VALIDATION_ERROR_EMPTY)

    def test_singleKey(self):
        validator = viewkit.shortcut.ShortcutKeyStringValidator(False)
        self._singleKeyCommonCase(validator)

        self._testcase(validator, "input control key", "BACK", False)
        self._testcase(validator, "input control key", "END", False)
        self._testcase(validator, "input control key", "PAGEUP", False)

    def test_singleKeyOnCharInputScreen(self):
        validator = viewkit.shortcut.ShortcutKeyStringValidator(False)
        self._singleKeyCommonCase(validator)

        self._testcase(validator, "input control key", "BACK", False)
        self._testcase(validator, "input control key", "END", False)
        self._testcase(validator, "input control key", "PAGEUP", False)

    def _singleKeyCommonCase(self, validator):
        self._testcase(validator, "unknown key", "CAT", False, viewkit.shortcut.VALIDATION_ERROR_FORBIDDEN)
        self._testcase(validator, "mouse button", "LBUTTON", False, viewkit.shortcut.VALIDATION_ERROR_FORBIDDEN)

        self._testcase(validator, "modifier key", "CTRL", False, viewkit.shortcut.VALIDATION_ERROR_MODIFIER_ONLY)
        self._testcase(validator, "modifier key", "ALT", False, viewkit.shortcut.VALIDATION_ERROR_MODIFIER_ONLY)
        self._testcase(validator, "modifier key", "SHIFT", False, viewkit.shortcut.VALIDATION_ERROR_MODIFIER_ONLY)
        self._testcase(validator, "modifier key", "WINDOWS", False, viewkit.shortcut.VALIDATION_ERROR_MODIFIER_ONLY)

        self._testcase(validator, "function key", "F1", True)
        self._testcase(validator, "function key", "F24", True)

        self._testcase(validator, "system key", "TAB", False)
        self._testcase(validator, "system key", "TAB", False)
        self._testcase(validator, "system key", "RETURN", False)
        self._testcase(validator, "system key", "ESCAPE", False)
        self._testcase(validator, "system key", "APPLICATIONS", False)
        self._testcase(validator, "system key", "PRINTSCREEN", False)
        self._testcase(validator, "system key", "LEFTARROW", False)
        self._testcase(validator, "system key", "CLEAR", False)

        self._testcase(validator, "NUMPAD", "NUMPAD_DECIMAL", True)
        self._testcase(validator, "NUMPAD", "NUMPAD_EQUAL", True)

        self._testcase(validator, "media key", "VOLUME_UP", True)
        self._testcase(validator, "special key", "SPECIAL20", True)

        self._testcase(validator, "alphabet key", "A", False, viewkit.shortcut.VALIDATION_ERROR_NEEDS_MODIFIER)
        self._testcase(validator, "alphabet key", "Z", False, viewkit.shortcut.VALIDATION_ERROR_NEEDS_MODIFIER)
        self._testcase(validator, "number key", "0", False, viewkit.shortcut.VALIDATION_ERROR_NEEDS_MODIFIER)
        self._testcase(validator, "number key", "9", False, viewkit.shortcut.VALIDATION_ERROR_NEEDS_MODIFIER)
        self._testcase(validator, "symbol key", ":", False, viewkit.shortcut.VALIDATION_ERROR_NEEDS_MODIFIER)
        self._testcase(validator, "symbol key", "@", False, viewkit.shortcut.VALIDATION_ERROR_NEEDS_MODIFIER)
        self._testcase(validator, "symbol key", "/", False, viewkit.shortcut.VALIDATION_ERROR_NEEDS_MODIFIER)

        self._testcase(validator, "numpad number key", "NUMPAD0", False, viewkit.shortcut.VALIDATION_ERROR_NEEDS_MODIFIER)
        self._testcase(validator, "numpad number key", "NUMPAD9", False, viewkit.shortcut.VALIDATION_ERROR_NEEDS_MODIFIER)

    def test_multiKeyValidCombinations(self):
        validator = viewkit.shortcut.ShortcutKeyStringValidator(False)
        # 修飾キーと通常キーの組み合わせ
        self._testcase(validator, "ctrl+function key", "CTRL+F1", True)
        self._testcase(validator, "alt+function key", "ALT+F5", True)
        self._testcase(validator, "shift+function key", "SHIFT+F12", True)
        self._testcase(validator, "ctrl+alt+function key", "CTRL+ALT+F8", True)

        # 修飾キーと特殊キーの組み合わせ
        self._testcase(validator, "ctrl+special key", "CTRL+SPECIAL10", True)
        self._testcase(validator, "alt+media key", "ALT+VOLUME_UP", True)
        self._testcase(validator, "shift+numpad key", "SHIFT+NUMPAD_DECIMAL", True)

    def test_multiKeyInvalidCombinations(self):
        validator = viewkit.shortcut.ShortcutKeyStringValidator(False)
        # 修飾キーのみ
        self._testcase(validator, "ctrl only", "CTRL", False, viewkit.shortcut.VALIDATION_ERROR_MODIFIER_ONLY)
        self._testcase(validator, "alt+shift only", "ALT+SHIFT", False, viewkit.shortcut.VALIDATION_ERROR_MODIFIER_ONLY)

        # 複数の非修飾キー
        self._testcase(validator, "two function keys", "F1+F2", False, viewkit.shortcut.VALIDATION_ERROR_MULTI_NONMODIFIER)
        self._testcase(validator, "function key + special key", "F1+SPECIAL1", False, viewkit.shortcut.VALIDATION_ERROR_MULTI_NONMODIFIER)

        # 修飾キー必須のキーが単独で使われている
        self._testcase(validator, "needs modifier", "A", False, viewkit.shortcut.VALIDATION_ERROR_NEEDS_MODIFIER)
        self._testcase(validator, "needs modifier", "0", False, viewkit.shortcut.VALIDATION_ERROR_NEEDS_MODIFIER)

    def test_forbiddenCombinations(self):
        validator = viewkit.shortcut.ShortcutKeyStringValidator(False)
        # 常に禁止されている組み合わせ
        self._testcase(validator, "ctrl+escape", "CTRL+ESCAPE", False, viewkit.shortcut.VALIDATION_ERROR_FORBIDDEN)
        self._testcase(validator, "alt+tab", "ALT+TAB", False, viewkit.shortcut.VALIDATION_ERROR_FORBIDDEN)
        self._testcase(validator, "alt+f4", "ALT+F4", False, viewkit.shortcut.VALIDATION_ERROR_FORBIDDEN)
        self._testcase(validator, "applications key", "APPLICATIONS", False, viewkit.shortcut.VALIDATION_ERROR_FORBIDDEN)
        self._testcase(validator, "escape key", "ESCAPE", False, viewkit.shortcut.VALIDATION_ERROR_FORBIDDEN)
        self._testcase(validator, "f10 key", "F10", False, viewkit.shortcut.VALIDATION_ERROR_FORBIDDEN)

    def test_charInputValidation(self):
        # 文字入力画面での検証
        validator_with_char_input = viewkit.shortcut.ShortcutKeyStringValidator(True)

        # 文字入力画面で追加で禁止される組み合わせ
        self._testcase(validator_with_char_input, "ctrl+c", "CTRL+C", False, viewkit.shortcut.VALIDATION_ERROR_FORBIDDEN)
        self._testcase(validator_with_char_input, "ctrl+v", "CTRL+V", False, viewkit.shortcut.VALIDATION_ERROR_FORBIDDEN)
        self._testcase(validator_with_char_input, "ctrl+x", "CTRL+X", False, viewkit.shortcut.VALIDATION_ERROR_FORBIDDEN)
        self._testcase(validator_with_char_input, "ctrl+z", "CTRL+Z", False, viewkit.shortcut.VALIDATION_ERROR_FORBIDDEN)
        self._testcase(validator_with_char_input, "ctrl+a", "CTRL+A", False, viewkit.shortcut.VALIDATION_ERROR_FORBIDDEN)

        # 入力制御キーは修飾キー必須
        self._testcase(validator_with_char_input, "back needs modifier", "BACK", False, viewkit.shortcut.VALIDATION_ERROR_NEEDS_MODIFIER)
        self._testcase(validator_with_char_input, "end needs modifier", "END", False, viewkit.shortcut.VALIDATION_ERROR_NEEDS_MODIFIER)
        self._testcase(validator_with_char_input, "pageup needs modifier", "PAGEUP", False, viewkit.shortcut.VALIDATION_ERROR_NEEDS_MODIFIER)

        # 修飾キーと組み合わせれば使用可能
        self._testcase(validator_with_char_input, "ctrl+back", "CTRL+BACK", True)
        self._testcase(validator_with_char_input, "alt+end", "ALT+END", True)

    def test_caseInsensitive(self):
        validator = viewkit.shortcut.ShortcutKeyStringValidator(False)
        # 大文字小文字を区別しない
        self._testcase(validator, "lowercase function key", "f1", True)
        self._testcase(validator, "mixed case", "Ctrl+f5", True)
        self._testcase(validator, "all lowercase", "alt+volume_up", True)

    def test_edgeCases(self):
        validator = viewkit.shortcut.ShortcutKeyStringValidator(False)
        # 不正なキー名
        self._testcase(validator, "unknown key", "UNKNOWN_KEY", False, viewkit.shortcut.VALIDATION_ERROR_FORBIDDEN)
        # マウスボタン
        self._testcase(validator, "mouse button", "LBUTTON", False, viewkit.shortcut.VALIDATION_ERROR_FORBIDDEN)
        # Windowsキー（修飾キーだが許可されていない）
        self._testcase(validator, "windows key", "WINDOWS", False, viewkit.shortcut.VALIDATION_ERROR_MODIFIER_ONLY)
