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
                self.assertEqual(e.reason, error_reason, f"Test case {name} failed: {e.reason}")

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
        self._testcase(validator, "unknown key", "CAT", False)
        self._testcase(validator, "mouse button", "LBUTTON", False)

        self._testcase(validator, "modifire key", "CTRL", False)
        self._testcase(validator, "modifire key", "ALT", False)
        self._testcase(validator, "modifire key", "SHIFT", False)
        self._testcase(validator, "modifire key", "WINDOWS", False)

        self._testcase(validator, "function key", "F1", True)
        self._testcase(validator, "function key", "F24", True)

        self._testcase(validator, "system key", "TAB",False)
        self._testcase(validator, "system key", "TAB",False)
        self._testcase(validator, "system key", "RETURN",False)
        self._testcase(validator, "system key", "ESCAPE",False)
        self._testcase(validator, "system key", "APPLICATIONS",False)
        self._testcase(validator, "system key", "PRINTSCREEN",False)
        self._testcase(validator, "system key", "LEFTARROW",False)
        self._testcase(validator, "system key", "CLEAR",False)

        self._testcase(validator, "NUMPAD", "NUMPAD_DECIMAL",True)
        self._testcase(validator, "NUMPAD", "NUMPAD_EQUAL",True)

        self._testcase(validator, "media key", "VOLUME_UP",True)
        self._testcase(validator, "special key", "SPECIAL20",True)

        self._testcase(validator, "alphabet key", "A",False)
        self._testcase(validator, "alphabet key", "Z",False)
        self._testcase(validator, "number key", "0",False)
        self._testcase(validator, "number key", "9",False)
        self._testcase(validator, "symbol key", ":",False)
        self._testcase(validator, "symbol key", "@",False)
        self._testcase(validator, "symbol key", "/",False)

        self._testcase(validator, "numpad number key", "NUMPAD0",False)
        self._testcase(validator, "numpad number key", "NUMPAD9",False)






