import unittest
from unittest.mock import Mock
from viewkit.feature.feature import Feature, FeatureStore
from viewkit.settings.shortcut import ParsedFileInput, RawEntry
from viewkit.shortcut import ShortcutKey


class TestFeature(unittest.TestCase):
    """Featureクラスのテスト"""

    def test_init_with_shortcut_key(self):
        """ショートカットキー付きの初期化テスト"""
        feature = Feature("test_id", "Test Feature", "ctrl+a")

        self.assertEqual(feature.identifier, "test_id")
        self.assertEqual(feature.display_name, "Test Feature")
        self.assertEqual(len(feature.shortcut_keys), 1)
        self.assertIsInstance(feature.shortcut_keys[0], ShortcutKey)

    def test_init_without_shortcut_key(self):
        """ショートカットキーなしの初期化テスト"""
        feature = Feature("test_id", "Test Feature", None)

        self.assertEqual(feature.identifier, "test_id")
        self.assertEqual(feature.display_name, "Test Feature")
        self.assertEqual(feature.shortcut_keys, [])

    def test_init_with_multiple_shortcut_keys(self):
        """複数ショートカットキーでの初期化テスト"""
        feature = Feature("test_id", "Test Feature", "ctrl+a/ctrl+b")

        self.assertEqual(len(feature.shortcut_keys), 2)

    def test_str_representation(self):
        """文字列表現のテスト"""
        feature = Feature("test_id", "Test Feature", "ctrl+a")

        str_repr = str(feature)
        self.assertIn("test_id", str_repr)
        self.assertIn("Test Feature", str_repr)

    def test_str_representation_no_shortcut(self):
        """ショートカットキーなしの文字列表現テスト"""
        feature = Feature("test_id", "Test Feature", None)

        str_repr = str(feature)
        self.assertIn("test_id", str_repr)
        self.assertIn("Test Feature", str_repr)
        self.assertIn("[]", str_repr)

    def test_copy_with_shortcut_key(self):
        """ショートカットキー付きコピーのテスト"""
        original = Feature("test_id", "Test Feature", "ctrl+a")
        copied = original.copy()

        self.assertEqual(copied.identifier, original.identifier)
        self.assertEqual(copied.display_name, original.display_name)
        self.assertIsNot(copied, original)

    def test_copy_without_shortcut_key(self):
        """ショートカットキーなしコピーのテスト"""
        original = Feature("test_id", "Test Feature", None)
        copied = original.copy()

        self.assertEqual(copied.identifier, original.identifier)
        self.assertEqual(copied.display_name, original.display_name)
        self.assertEqual(copied.shortcut_keys, [])
        self.assertIsNot(copied, original)


class TestFeatureStore(unittest.TestCase):
    """FeatureStoreクラスのテスト"""

    def setUp(self):
        """テスト用のセットアップ"""
        self.store = FeatureStore()
        self.feature1 = Feature("feature1", "Feature 1", "ctrl+a")
        self.feature2 = Feature("feature2", "Feature 2", "ctrl+b")

    def test_init(self):
        """初期化のテスト"""
        store = FeatureStore()
        self.assertEqual(store.features, {})

    def test_register(self):
        """機能登録のテスト"""
        self.store.register(self.feature1)

        self.assertIn("feature1", self.store.features)
        self.assertEqual(self.store.features["feature1"], self.feature1)

    def test_register_multiple(self):
        """複数機能登録のテスト"""
        self.store.register(self.feature1)
        self.store.register(self.feature2)

        self.assertEqual(len(self.store.features), 2)
        self.assertIn("feature1", self.store.features)
        self.assertIn("feature2", self.store.features)

    def test_all(self):
        """全機能取得のテスト"""
        self.store.register(self.feature1)
        self.store.register(self.feature2)

        all_features = self.store.all()
        self.assertEqual(len(all_features), 2)
        self.assertIn("feature1", all_features)
        self.assertIn("feature2", all_features)
        self.assertIsNot(all_features, self.store.features)

    def test_getByIdentifier_existing(self):
        """存在する識別子での取得テスト"""
        self.store.register(self.feature1)

        retrieved = self.store.getByIdentifier("feature1")
        self.assertEqual(retrieved, self.feature1)

    def test_getByIdentifier_non_existing(self):
        """存在しない識別子での取得テスト"""
        retrieved = self.store.getByIdentifier("non_existing")
        self.assertIsNone(retrieved)

    def test_applyShortcutKeySettings(self):
        """ショートカットキー設定適用のテスト"""
        self.store.register(self.feature1)
        self.store.register(self.feature2)

        raw_entries = [
            RawEntry("feature1", "ctrl+x"),
            RawEntry("feature2", "ctrl+y")
        ]
        input_data = ParsedFileInput(version=1, raw_entries=raw_entries)

        removed_entries = self.store.applyShortcutKeySettings(input_data)

        self.assertIsInstance(removed_entries, list)


if __name__ == '__main__':
    unittest.main()
