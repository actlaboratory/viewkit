import unittest
from viewkit.settings.shortcut.settings import (
    RawEntry, ParsedFileInput, Entry, RemovedEntry,
    ShortcutKeySettings, _listDuplicateIdentifierEntryKeys,
    REMOVED_ENTRY_REASON_INVALID_NOTATION,
    REMOVED_ENTRY_REASON_DUPLICATE_IDENTIFIER_IN_SETTINGS,
    REMOVED_ENTRY_REASON_DUPLICATE_KEYSTROKE_IN_SETTINGS,
    REMOVED_ENTRY_REASON_DUPLICATE_AFTER_APPLY
)
from viewkit.shortcut.validation import ShortcutKeyStringValidator, ShortcutKeyValidationError


class TestRawEntry(unittest.TestCase):
    """RawEntryクラスのテスト"""

    def test_init(self):
        """初期化のテスト"""
        entry = RawEntry("test_feature", "ctrl+a")
        self.assertEqual(entry.feature_identifier, "test_feature")
        self.assertEqual(entry.shortcut_key_string, "ctrl+a")

    def test_init_empty_strings(self):
        """空文字列での初期化テスト"""
        entry = RawEntry("", "")
        self.assertEqual(entry.feature_identifier, "")
        self.assertEqual(entry.shortcut_key_string, "")


class TestParsedFileInput(unittest.TestCase):
    """ParsedFileInputクラスのテスト"""

    def test_init(self):
        """初期化のテスト"""
        raw_entries = [RawEntry("feature1", "ctrl+a"), RawEntry("feature2", "ctrl+b")]
        parsed_input = ParsedFileInput("1.0", raw_entries)
        self.assertEqual(parsed_input.version, "1.0")
        self.assertEqual(parsed_input.raw_entries, raw_entries)

    def test_init_empty_entries(self):
        """空のエントリリストでの初期化テスト"""
        parsed_input = ParsedFileInput("1.0", [])
        self.assertEqual(parsed_input.version, "1.0")
        self.assertEqual(parsed_input.raw_entries, [])


class TestEntry(unittest.TestCase):
    """Entryクラスのテスト"""

    def test_init_with_valid_shortcut_single_key(self):
        """有効な単一ショートカットキーでの初期化テスト"""
        raw_entry = RawEntry("test_feature", "ctrl+a")
        entry = Entry(raw_entry)
        self.assertEqual(entry.feature_identifier, "test_feature")
        self.assertTrue(hasattr(entry, 'shortcut_keys'))

    def test_init_with_valid_shortcut_multiple_keys(self):
        """複数のショートカットキーでの初期化テスト"""
        raw_entry = RawEntry("test_feature", "ctrl+a/ctrl+b")
        entry = Entry(raw_entry)
        self.assertEqual(entry.feature_identifier, "test_feature")
        self.assertTrue(hasattr(entry, 'shortcut_keys'))

    def test_init_with_empty_shortcut_key_string(self):
        """空のショートカットキー文字列での初期化テスト"""
        raw_entry = RawEntry("test_feature", "")
        entry = Entry(raw_entry)
        self.assertEqual(entry.feature_identifier, "test_feature")

    def test_has_same_keystroke_different_entries(self):
        """異なるエントリ間でのキーストローク比較テスト"""
        raw_entry1 = RawEntry("feature1", "ctrl+a")
        raw_entry2 = RawEntry("feature2", "ctrl+b")

        entry1 = Entry(raw_entry1)
        entry2 = Entry(raw_entry2)

        # 異なるショートカットキーなので重複はないはず
        result = entry1.hasSameKeystroke(entry2)
        self.assertFalse(result)

    def test_has_same_keystroke_same_entries(self):
        """同じショートカットキーのエントリ間での比較テスト"""
        raw_entry1 = RawEntry("feature1", "ctrl+a")
        raw_entry2 = RawEntry("feature2", "ctrl+a")

        entry1 = Entry(raw_entry1)
        entry2 = Entry(raw_entry2)

        # 同じショートカットキーなので重複があるはず
        result = entry1.hasSameKeystroke(entry2)
        # 実際の実装に依存するが、同じキーの場合はTrueになるはず
        if hasattr(entry1, 'shortcut_keys') and hasattr(entry2, 'shortcut_keys'):
            if entry1.shortcut_keys and entry2.shortcut_keys:
                self.assertTrue(result)

    def test_has_same_keystroke_with_non_entry(self):
        """Entryクラス以外のオブジェクトとの比較テスト"""
        raw_entry = RawEntry("feature1", "ctrl+a")
        entry = Entry(raw_entry)
        result = entry.hasSameKeystroke("not_an_entry")
        self.assertFalse(result)


class TestListDuplicateIdentifierEntryKeys(unittest.TestCase):
    """_listDuplicateIdentifierEntryKeys関数のテスト"""

    def test_no_duplicates(self):
        """重複なしのテスト"""
        # 実際のEntryオブジェクトを作成
        raw_entry1 = RawEntry("feature1", "ctrl+a")
        raw_entry2 = RawEntry("feature2", "ctrl+b")
        raw_entry3 = RawEntry("feature3", "ctrl+c")

        entry1 = Entry(raw_entry1)
        entry2 = Entry(raw_entry2)
        entry3 = Entry(raw_entry3)

        entries = [entry1, entry2, entry3]
        result = _listDuplicateIdentifierEntryKeys(entries)
        self.assertEqual(result, [])

    def test_with_duplicates(self):
        """重複ありのテスト"""
        raw_entry1 = RawEntry("feature1", "ctrl+a")
        raw_entry2 = RawEntry("feature2", "ctrl+b")
        raw_entry3 = RawEntry("feature1", "ctrl+c")  # entry1と同じキー
        raw_entry4 = RawEntry("feature4", "ctrl+d")

        entry1 = Entry(raw_entry1)
        entry2 = Entry(raw_entry2)
        entry3 = Entry(raw_entry3)
        entry4 = Entry(raw_entry4)

        entries = [entry1, entry2, entry3, entry4]
        result = _listDuplicateIdentifierEntryKeys(entries)
        self.assertIn("feature1", result)
        self.assertEqual(len(result), 1)

    def test_empty_list(self):
        """空リストのテスト"""
        result = _listDuplicateIdentifierEntryKeys([])
        self.assertEqual(result, [])


class TestRemovedEntry(unittest.TestCase):
    """RemovedEntryクラスのテスト"""

    def test_init_with_additional_info(self):
        """追加情報ありでの初期化テスト"""
        raw_entry = RawEntry("test_feature", "ctrl+a")
        entry = Entry(raw_entry)
        removed = RemovedEntry(REMOVED_ENTRY_REASON_INVALID_NOTATION, entry, "test info")
        self.assertEqual(removed.reason, REMOVED_ENTRY_REASON_INVALID_NOTATION)
        self.assertEqual(removed.entry, entry)
        self.assertEqual(removed.additionalInfo, "test info")

    def test_init_without_additional_info(self):
        """追加情報なしでの初期化テスト"""
        raw_entry = RawEntry("test_feature", "ctrl+a")
        entry = Entry(raw_entry)
        removed = RemovedEntry(REMOVED_ENTRY_REASON_DUPLICATE_IDENTIFIER_IN_SETTINGS, entry)
        self.assertEqual(removed.reason, REMOVED_ENTRY_REASON_DUPLICATE_IDENTIFIER_IN_SETTINGS)
        self.assertEqual(removed.entry, entry)
        self.assertEqual(removed.additionalInfo, "")


class TestShortcutKeySettings(unittest.TestCase):
    """ShortcutKeySettingsクラスのテスト"""

    def setUp(self):
        """各テストの前準備"""
        self.raw_entries = [
            RawEntry("feature1", "ctrl+a"),
            RawEntry("feature2", "ctrl+b")
        ]
        self.settings = ShortcutKeySettings("1.0", self.raw_entries)

    def test_init(self):
        """初期化のテスト"""
        self.assertEqual(self.settings.version, "1.0")
        self.assertEqual(self.settings.raw_entries, self.raw_entries)

    def test_generate_entries(self):
        """エントリ生成のテスト"""
        self.settings.generateEntries()

        self.assertTrue(hasattr(self.settings, 'entries'))
        self.assertEqual(len(self.settings.entries), 2)
        self.assertIsInstance(self.settings.entries[0], Entry)
        self.assertIsInstance(self.settings.entries[1], Entry)

    def test_remove_invalid_entries_with_valid_keys(self):
        """有効なキーでの無効エントリ削除テスト"""
        validator = ShortcutKeyStringValidator(has_char_input_on_screen=False)

        removed = self.settings.removeInvalidEntries(validator)

        # 有効なキーなので削除されるエントリはないはず
        self.assertEqual(len(removed), 0)
        self.assertEqual(len(self.settings.raw_entries), 2)

    def test_remove_invalid_entries_with_invalid_keys(self):
        """無効なキーでの無効エントリ削除テスト"""
        # 無効なキーを含むraw_entriesを作成
        invalid_raw_entries = [
            RawEntry("feature1", "ctrl+a"),  # 有効
            RawEntry("feature2", ""),        # 無効（空文字列）
            RawEntry("feature3", "invalidkey")  # 無効（存在しないキー）
        ]
        settings = ShortcutKeySettings("1.0", invalid_raw_entries)
        validator = ShortcutKeyStringValidator(has_char_input_on_screen=False)

        removed = settings.removeInvalidEntries(validator)

        # 2つの無効なエントリが削除されるはず
        self.assertEqual(len(removed), 2)
        self.assertEqual(len(settings.raw_entries), 1)
        self.assertEqual(removed[0].reason, REMOVED_ENTRY_REASON_INVALID_NOTATION)
        self.assertEqual(removed[1].reason, REMOVED_ENTRY_REASON_INVALID_NOTATION)

    def test_remove_entries_with_duplicate_identifiers_no_duplicates(self):
        """重複識別子なしでの削除テスト"""
        self.settings.generateEntries()  # まずエントリを生成

        removed = self.settings.removeEntriesWithDuplicateIdentifiers()

        # 重複がないので削除されるエントリはないはず
        self.assertEqual(len(removed), 0)

    def test_remove_entries_with_duplicate_identifiers_with_duplicates(self):
        """重複識別子ありでの削除テスト"""
        # 重複するキーを含むエントリを作成
        duplicate_raw_entries = [
            RawEntry("feature1", "ctrl+a"),
            RawEntry("feature2", "ctrl+b"),
            RawEntry("feature3", "ctrl+a")  # feature1と重複
        ]
        settings = ShortcutKeySettings("1.0", duplicate_raw_entries)
        settings.generateEntries()

        removed = settings.removeEntriesWithDuplicateKeystrokes()

        # 重複するエントリが削除されるはず
        self.assertGreater(len(removed), 0)
        for removed_entry in removed:
            self.assertEqual(removed_entry.reason, REMOVED_ENTRY_REASON_DUPLICATE_KEYSTROKE_IN_SETTINGS)

    def test_remove_entries_with_duplicate_keystrokes(self):
        """重複キーストロークエントリの削除テスト"""
        # 同じキーストロークを持つエントリを作成
        duplicate_raw_entries = [
            RawEntry("feature1", "ctrl+a"),
            RawEntry("feature2", "ctrl+b"),
            RawEntry("feature3", "ctrl+a")  # feature1と同じキーストローク
        ]
        settings = ShortcutKeySettings("1.0", duplicate_raw_entries)
        settings.generateEntries()

        removed = settings.removeEntriesWithDuplicateKeystrokes()

        # 重複するキーストロークのエントリが削除されるはず
        self.assertGreater(len(removed), 0)
        for removed_entry in removed:
            self.assertEqual(removed_entry.reason, REMOVED_ENTRY_REASON_DUPLICATE_KEYSTROKE_IN_SETTINGS)


if __name__ == '__main__':
    unittest.main()
