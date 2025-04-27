import os
import unittest
import viewkit.shortcut


class TestShortcutValidator(unittest.TestCase):
    def test_initializeWithCharInputOff(self):
        viewkit.shortcut.ShortcutKeyStringValidator(False)

    def test_initializeWithCharInputOn(self):
        viewkit.shortcut.ShortcutKeyStringValidator(True)
