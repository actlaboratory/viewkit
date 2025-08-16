import unittest
import tempfile
import os
from viewkit.feature.feature import Feature, FeatureStore
from viewkit.settings.shortcut import ParsedFileInput, RawEntry
from viewkit.context.app import ApplicationContext


class TestCustomShortcuts(unittest.TestCase):
    """カスタムショートカット機能のテスト"""

    def setUp(self):
        """各テストの前準備"""
        self.temp_dir = tempfile.mkdtemp()
        self.test_file = os.path.join(self.temp_dir, "test_app.json")
        
        # FeatureStoreを作成し、テスト用Featureを登録
        self.store = FeatureStore()
        self.feature1 = Feature("feature1", "Feature 1", "ctrl+a")
        self.feature2 = Feature("feature2", "Feature 2", "ctrl+b")
        self.feature3 = Feature("feature3", "Feature 3", None)  # ショートカットなし
        
        self.store.register(self.feature1)
        self.store.register(self.feature2)
        self.store.register(self.feature3)

    def tearDown(self):
        """各テストの後片付け"""
        if os.path.exists(self.test_file):
            os.remove(self.test_file)
        os.rmdir(self.temp_dir)

    def test_settings_manager_get_shortcut_settings_empty(self):
        """SettingsManagerのgetShortcutSettings()メソッドのテスト（空の場合）"""
        app_context = ApplicationContext(
            applicationName="TestApp",
            supportedLanguages={"ja": "Japanese"},
            language="ja",
            settingFileName=self.test_file
        )
        
        shortcuts = app_context.settings.getShortcutSettings()
        self.assertEqual(shortcuts, {})

    def test_settings_manager_get_shortcut_settings_with_data(self):
        """SettingsManagerのgetShortcutSettings()メソッドのテスト（データありの場合）"""
        app_context = ApplicationContext(
            applicationName="TestApp",
            supportedLanguages={"ja": "Japanese"},
            language="ja",
            settingFileName=self.test_file
        )
        
        # カスタムショートカット設定を保存
        custom_shortcuts = {
            "feature1": "ctrl+shift+a",
            "feature2": "f5"
        }
        app_context.settings.changeSetting('shortcuts', custom_shortcuts)
        
        # 取得テスト
        shortcuts = app_context.settings.getShortcutSettings()
        self.assertEqual(shortcuts, custom_shortcuts)

    def test_apply_custom_shortcut_settings_empty(self):
        """空のカスタムショートカット設定の適用テスト"""
        removed_entries = self.store.applyCustomShortcutSettings({})
        
        # 空の設定では何も削除されない
        self.assertEqual(len(removed_entries), 0)
        
        # 元のショートカットキーが保持される
        f1 = self.store.getByIdentifier("feature1")
        f2 = self.store.getByIdentifier("feature2")
        self.assertEqual(str(f1.shortcut_keys[0]), "ctrl+a")
        self.assertEqual(str(f2.shortcut_keys[0]), "ctrl+b")

    def test_apply_custom_shortcut_settings_valid(self):
        """有効なカスタムショートカット設定の適用テスト"""
        custom_shortcuts = {
            "feature1": "ctrl+shift+a",
            "feature2": "f5"
        }
        
        removed_entries = self.store.applyCustomShortcutSettings(custom_shortcuts)
        
        # 有効な設定なので削除エントリはない
        self.assertEqual(len(removed_entries), 0)
        
        # ショートカットキーが変更されている
        f1 = self.store.getByIdentifier("feature1")
        f2 = self.store.getByIdentifier("feature2")
        self.assertEqual(str(f1.shortcut_keys[0]), "ctrl+shift+a")
        self.assertEqual(str(f2.shortcut_keys[0]), "f5")

    def test_apply_custom_shortcut_settings_nonexistent_feature(self):
        """存在しないfeatureのカスタムショートカット設定テスト"""
        custom_shortcuts = {
            "nonexistent_feature": "ctrl+x",
            "feature1": "ctrl+shift+a"
        }
        
        removed_entries = self.store.applyCustomShortcutSettings(custom_shortcuts)
        
        # removed_entriesの内容を確認（存在しないfeatureの場合の動作）
        # ショートカットキーの処理でバリデーションエラーが発生する可能性があるため、
        # removed_entriesの数は実装に依存する
        self.assertIsInstance(removed_entries, list)
        
        # 存在するfeatureのショートカットは正しく変更される
        f1 = self.store.getByIdentifier("feature1")
        self.assertEqual(str(f1.shortcut_keys[0]), "ctrl+shift+a")

    def test_apply_custom_shortcut_settings_invalid_keys(self):
        """無効なショートカットキーのカスタム設定テスト"""
        custom_shortcuts = {
            "feature1": "",  # 空文字列
            "feature2": "   ",  # 空白のみ
            "feature3": "ctrl+shift+f1"  # 有効なキー
        }
        
        removed_entries = self.store.applyCustomShortcutSettings(custom_shortcuts)
        
        # 空文字列や空白のみのエントリは無視される
        # ただし、removed_entriesには含まれない（RawEntryに変換されない）
        self.assertEqual(len(removed_entries), 0)
        
        # 有効なキーのみ適用される
        f1 = self.store.getByIdentifier("feature1")
        f2 = self.store.getByIdentifier("feature2")
        f3 = self.store.getByIdentifier("feature3")
        
        # feature1, feature2は元のまま（無効な設定は無視）
        self.assertEqual(str(f1.shortcut_keys[0]), "ctrl+a")
        self.assertEqual(str(f2.shortcut_keys[0]), "ctrl+b")
        
        # feature3は新しく設定される
        self.assertEqual(str(f3.shortcut_keys[0]), "ctrl+shift+f1")

    def test_apply_custom_shortcut_settings_with_none_values(self):
        """None値を含むカスタム設定テスト"""
        custom_shortcuts = {
            "feature1": None,
            "feature2": "f5"
        }
        
        # None値は文字列でないため無視される
        removed_entries = self.store.applyCustomShortcutSettings(custom_shortcuts)
        self.assertEqual(len(removed_entries), 0)
        
        # feature1は元のまま、feature2は変更される
        f1 = self.store.getByIdentifier("feature1")
        f2 = self.store.getByIdentifier("feature2")
        self.assertEqual(str(f1.shortcut_keys[0]), "ctrl+a")
        self.assertEqual(str(f2.shortcut_keys[0]), "f5")

    def test_apply_shortcut_settings_with_custom_priority_default_only(self):
        """デフォルト設定のみの統合適用テスト"""
        default_raw_entries = [
            RawEntry("feature1", "f1"),
            RawEntry("feature2", "f2")
        ]
        default_settings = ParsedFileInput("1.0", default_raw_entries)
        
        removed_entries = self.store.applyShortcutSettingsWithCustomPriority(
            default_settings=default_settings,
            custom_settings=None
        )
        
        self.assertEqual(len(removed_entries), 0)
        
        # デフォルト設定が適用される
        f1 = self.store.getByIdentifier("feature1")
        f2 = self.store.getByIdentifier("feature2")
        self.assertEqual(str(f1.shortcut_keys[0]), "f1")
        self.assertEqual(str(f2.shortcut_keys[0]), "f2")

    def test_apply_shortcut_settings_with_custom_priority_custom_only(self):
        """カスタム設定のみの統合適用テスト"""
        custom_settings = {
            "feature1": "ctrl+shift+a",
            "feature2": "f5"
        }
        
        removed_entries = self.store.applyShortcutSettingsWithCustomPriority(
            default_settings=None,
            custom_settings=custom_settings
        )
        
        self.assertEqual(len(removed_entries), 0)
        
        # カスタム設定が適用される
        f1 = self.store.getByIdentifier("feature1")
        f2 = self.store.getByIdentifier("feature2")
        self.assertEqual(str(f1.shortcut_keys[0]), "ctrl+shift+a")
        self.assertEqual(str(f2.shortcut_keys[0]), "f5")

    def test_apply_shortcut_settings_with_custom_priority_both(self):
        """デフォルトとカスタム両方の統合適用テスト（カスタム優先）"""
        # デフォルト設定
        default_raw_entries = [
            RawEntry("feature1", "f1"),
            RawEntry("feature2", "f2"),
            RawEntry("feature3", "f3")
        ]
        default_settings = ParsedFileInput("1.0", default_raw_entries)
        
        # カスタム設定（feature1のみ上書き）
        custom_settings = {
            "feature1": "ctrl+shift+f1"
        }
        
        removed_entries = self.store.applyShortcutSettingsWithCustomPriority(
            default_settings=default_settings,
            custom_settings=custom_settings
        )
        
        self.assertEqual(len(removed_entries), 0)
        
        # 結果確認
        f1 = self.store.getByIdentifier("feature1")
        f2 = self.store.getByIdentifier("feature2")
        f3 = self.store.getByIdentifier("feature3")
        
        # feature1はカスタム設定が優先される
        self.assertEqual(str(f1.shortcut_keys[0]), "ctrl+shift+f1")
        # feature2, feature3はデフォルト設定が適用される
        self.assertEqual(str(f2.shortcut_keys[0]), "f2")
        self.assertEqual(str(f3.shortcut_keys[0]), "f3")

    def test_apply_shortcut_settings_with_custom_priority_override_same_key(self):
        """同じショートカットキーでのカスタム優先テスト"""
        # デフォルト設定
        default_raw_entries = [
            RawEntry("feature1", "f1"),
            RawEntry("feature2", "f2")
        ]
        default_settings = ParsedFileInput("1.0", default_raw_entries)
        
        # カスタム設定（同じキーをfeature1に再設定）
        custom_settings = {
            "feature1": "f1"  # デフォルトと同じだが、カスタムが後で適用される
        }
        
        removed_entries = self.store.applyShortcutSettingsWithCustomPriority(
            default_settings=default_settings,
            custom_settings=custom_settings
        )
        
        # 同じキーでもカスタム設定が適用される
        f1 = self.store.getByIdentifier("feature1")
        f2 = self.store.getByIdentifier("feature2")
        self.assertEqual(str(f1.shortcut_keys[0]), "f1")
        self.assertEqual(str(f2.shortcut_keys[0]), "f2")

    def test_integration_with_application_context(self):
        """ApplicationContextとの統合テスト"""
        app_context = ApplicationContext(
            applicationName="TestApp",
            supportedLanguages={"ja": "Japanese"},
            language="ja",
            settingFileName=self.test_file
        )
        
        # カスタムショートカット設定
        custom_shortcuts = {
            "feature1": "ctrl+shift+a",
            "feature2": "f5",
            "feature3": "ctrl+t"
        }
        app_context.settings.changeSetting('shortcuts', custom_shortcuts)
        
        # FeatureStoreに適用
        shortcuts_settings = app_context.settings.getShortcutSettings()
        removed_entries = self.store.applyCustomShortcutSettings(shortcuts_settings)
        
        self.assertEqual(len(removed_entries), 0)
        
        # 全てのfeatureにカスタムショートカットが適用される
        f1 = self.store.getByIdentifier("feature1")
        f2 = self.store.getByIdentifier("feature2")
        f3 = self.store.getByIdentifier("feature3")
        
        self.assertEqual(str(f1.shortcut_keys[0]), "ctrl+shift+a")
        self.assertEqual(str(f2.shortcut_keys[0]), "f5")
        self.assertEqual(str(f3.shortcut_keys[0]), "ctrl+t")

    def test_integration_settings_persistence(self):
        """設定の永続化統合テスト"""
        # 最初のApplicationContextでカスタム設定を保存
        app_context1 = ApplicationContext(
            applicationName="TestApp",
            supportedLanguages={"ja": "Japanese"},
            language="ja",
            settingFileName=self.test_file
        )
        
        custom_shortcuts = {"feature1": "ctrl+shift+a"}
        app_context1.settings.changeSetting('shortcuts', custom_shortcuts)
        app_context1.settings.save()
        
        # 新しいApplicationContextで読み込み
        app_context2 = ApplicationContext(
            applicationName="TestApp",
            supportedLanguages={"ja": "Japanese"},
            language="ja",
            settingFileName=self.test_file
        )
        
        # 設定が正しく読み込まれることを確認
        loaded_shortcuts = app_context2.settings.getShortcutSettings()
        self.assertEqual(loaded_shortcuts, custom_shortcuts)
        
        # FeatureStoreに適用して動作確認
        removed_entries = self.store.applyCustomShortcutSettings(loaded_shortcuts)
        self.assertEqual(len(removed_entries), 0)
        
        f1 = self.store.getByIdentifier("feature1")
        self.assertEqual(str(f1.shortcut_keys[0]), "ctrl+shift+a")

    def test_conflict_resolution_default_removed(self):
        """デフォルト設定がカスタム設定と競合して削除されるテスト"""
        # デフォルト設定でFeatureを作成
        store = FeatureStore()
        feature1 = Feature("feature1", "Feature 1", "F1")  # デフォルト: F1
        feature2 = Feature("feature2", "Feature 2", "F2")  # デフォルト: F2
        store.register(feature1)
        store.register(feature2)
        
        # カスタム設定: feature2にF1を設定（feature1のデフォルトと競合）
        custom_settings = {
            "feature2": "F1"
        }
        
        # 競合解決ありの適用
        removed_entries = store.applyCustomShortcutSettingsWithConflictResolution(custom_settings)
        
        # 結果確認
        f1 = store.getByIdentifier("feature1")
        f2 = store.getByIdentifier("feature2")
        
        # feature1のF1は削除される（カスタム設定のfeature2と競合）
        self.assertEqual(len(f1.shortcut_keys), 0)
        
        # feature2はカスタム設定のF1が適用される
        self.assertEqual(len(f2.shortcut_keys), 1)
        self.assertEqual(str(f2.shortcut_keys[0]), "f1")

    def test_conflict_resolution_multiple_conflicts(self):
        """複数の競合解決テスト"""
        store = FeatureStore()
        feature1 = Feature("feature1", "Feature 1", "F1")
        feature2 = Feature("feature2", "Feature 2", "F2")
        feature3 = Feature("feature3", "Feature 3", "F3")
        store.register(feature1)
        store.register(feature2)
        store.register(feature3)
        
        # カスタム設定で複数の競合を作成
        custom_settings = {
            "feature2": "F1",  # feature1と競合
            "feature3": "F2"   # feature2と競合（ただしfeature2はF1に変更されるため実質的にfeature2元のF2は無効）
        }
        
        removed_entries = store.applyCustomShortcutSettingsWithConflictResolution(custom_settings)
        
        f1 = store.getByIdentifier("feature1")
        f2 = store.getByIdentifier("feature2")
        f3 = store.getByIdentifier("feature3")
        
        # feature1: F1が削除（feature2カスタムと競合）
        self.assertEqual(len(f1.shortcut_keys), 0)
        
        # feature2: カスタムF1が適用
        self.assertEqual(str(f2.shortcut_keys[0]), "f1")
        
        # feature3: カスタムF2が適用
        self.assertEqual(str(f3.shortcut_keys[0]), "f2")

    def test_conflict_resolution_no_conflicts(self):
        """競合がない場合のテスト"""
        store = FeatureStore()
        feature1 = Feature("feature1", "Feature 1", "F1")
        feature2 = Feature("feature2", "Feature 2", "F2")
        store.register(feature1)
        store.register(feature2)
        
        # 競合しないカスタム設定
        custom_settings = {
            "feature1": "F3"  # 新しいキー、競合なし
        }
        
        removed_entries = store.applyCustomShortcutSettingsWithConflictResolution(custom_settings)
        
        f1 = store.getByIdentifier("feature1")
        f2 = store.getByIdentifier("feature2")
        
        # feature1: カスタムF3が適用
        self.assertEqual(str(f1.shortcut_keys[0]), "f3")
        
        # feature2: デフォルトF2が保持
        self.assertEqual(str(f2.shortcut_keys[0]), "f2")


if __name__ == '__main__':
    unittest.main()