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
