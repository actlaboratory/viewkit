import unittest
import os
import json
import tempfile
from viewkit.settings import SettingsManager


class TestSettingsManager(unittest.TestCase):
    """SettingsManagerクラスのテスト"""

    def setUp(self):
        """各テストの前準備"""
        self.temp_dir = tempfile.mkdtemp()
        self.test_file = os.path.join(self.temp_dir, "test_settings.json")
        self.settings = SettingsManager(self.test_file)

    def tearDown(self):
        """各テストの後片付け"""
        if os.path.exists(self.test_file):
            os.remove(self.test_file)
        os.rmdir(self.temp_dir)

    def test_init_creates_default_file(self):
        """初期化時にデフォルトファイルが作成されることを確認"""
        self.assertTrue(os.path.exists(self.test_file))
        
        with open(self.test_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        self.assertEqual(data['test_str'], '')
        self.assertEqual(data['test_number'], 0)
        self.assertEqual(data['test_range'], 50)
        self.assertEqual(data['custom'], {})

    def test_get_setting_default_values(self):
        """デフォルト値の取得テスト"""
        self.assertEqual(self.settings.get_setting('test_str'), '')
        self.assertEqual(self.settings.get_setting('test_number'), 0)
        self.assertEqual(self.settings.get_setting('test_range'), 50)
        self.assertEqual(self.settings.get_setting('custom'), {})

    def test_get_setting_with_default(self):
        """存在しないキーでのデフォルト値取得テスト"""
        result = self.settings.get_setting('nonexistent', 'default_value')
        self.assertEqual(result, 'default_value')

    def test_set_setting_valid_values(self):
        """有効な値の設定テスト"""
        self.settings.set_setting('test_str', 'hello')
        self.settings.set_setting('test_number', 42)
        self.settings.set_setting('test_range', 75)
        
        self.assertEqual(self.settings.get_setting('test_str'), 'hello')
        self.assertEqual(self.settings.get_setting('test_number'), 42)
        self.assertEqual(self.settings.get_setting('test_range'), 75)

    def test_set_setting_invalid_range(self):
        """範囲外の値の設定テスト"""
        with self.assertRaises(ValueError):
            self.settings.set_setting('test_range', 0)  # 1未満
        
        with self.assertRaises(ValueError):
            self.settings.set_setting('test_range', 101)  # 100超過

    def test_set_setting_invalid_type(self):
        """無効な型の設定テスト"""
        with self.assertRaises(ValueError):
            self.settings.set_setting('test_str', 123)  # 文字列に数値
        
        with self.assertRaises(ValueError):
            self.settings.set_setting('test_number', 'not_a_number')  # 数値に文字列

    def test_set_setting_custom_field_error(self):
        """customフィールドを直接設定しようとするとエラーになることを確認"""
        with self.assertRaises(ValueError):
            self.settings.set_setting('custom', {'field': 'value'})

    def test_register_custom_field_without_schema(self):
        """スキーマなしでのカスタムフィールド登録テスト"""
        self.settings.register_custom_field('my_field')
        self.assertIn('my_field', self.settings.custom_fields)
        self.assertEqual(self.settings.custom_fields['my_field'], {})

    def test_register_custom_field_with_schema(self):
        """スキーマありでのカスタムフィールド登録テスト"""
        schema = {
            'enabled': {'type': 'boolean', 'default': True},
            'name': {'type': 'string', 'default': 'default_name'}
        }
        self.settings.register_custom_field('feature', schema)
        self.assertIn('feature', self.settings.custom_fields)
        self.assertEqual(self.settings.custom_fields['feature'], schema)

    def test_set_custom_setting_unregistered_field(self):
        """未登録のカスタムフィールドへの設定テスト"""
        with self.assertRaises(ValueError):
            self.settings.set_custom_setting('unregistered', {'value': 'test'})

    def test_set_custom_setting_valid(self):
        """有効なカスタム設定のテスト"""
        schema = {
            'enabled': {'type': 'boolean', 'default': True},
            'count': {'type': 'number', 'default': 0}
        }
        self.settings.register_custom_field('feature', schema)
        
        custom_data = {'enabled': False, 'count': 10}
        self.settings.set_custom_setting('feature', custom_data)
        
        result = self.settings.get_custom_setting('feature')
        self.assertEqual(result, custom_data)

    def test_set_custom_setting_invalid_schema(self):
        """無効なスキーマでのカスタム設定テスト"""
        schema = {
            'enabled': {'type': 'boolean', 'default': True}
        }
        self.settings.register_custom_field('feature', schema)
        
        with self.assertRaises(ValueError):
            self.settings.set_custom_setting('feature', {'enabled': 'not_boolean'})

    def test_get_custom_setting_nonexistent_field(self):
        """存在しないカスタムフィールドの取得テスト"""
        result = self.settings.get_custom_setting('nonexistent', default='default')
        self.assertEqual(result, 'default')

    def test_get_custom_setting_with_key(self):
        """キー指定でのカスタム設定取得テスト"""
        self.settings.register_custom_field('feature')
        custom_data = {'key1': 'value1', 'key2': 'value2'}
        self.settings.set_custom_setting('feature', custom_data)
        
        result = self.settings.get_custom_setting('feature', 'key1')
        self.assertEqual(result, 'value1')
        
        result = self.settings.get_custom_setting('feature', 'nonexistent', 'default')
        self.assertEqual(result, 'default')

    def test_save_and_load(self):
        """保存と読み込みのテスト"""
        # 設定を変更
        self.settings.set_setting('test_str', 'saved_value')
        self.settings.set_setting('test_number', 99)
        
        # カスタム設定を追加
        self.settings.register_custom_field('feature')
        self.settings.set_custom_setting('feature', {'option': 'custom_value'})
        
        # 保存
        self.settings.save()
        
        # 新しいインスタンスで読み込み
        new_settings = SettingsManager(self.test_file)
        
        # 値が保存されていることを確認
        self.assertEqual(new_settings.get_setting('test_str'), 'saved_value')
        self.assertEqual(new_settings.get_setting('test_number'), 99)
        
        # カスタム設定は登録が必要
        new_settings.register_custom_field('feature')
        result = new_settings.get_custom_setting('feature')
        self.assertEqual(result, {'option': 'custom_value'})

    def test_load_invalid_json_creates_default(self):
        """無効なJSONファイルの場合にデフォルト設定が作成されることを確認"""
        # 無効なJSONを書き込み
        with open(self.test_file, 'w', encoding='utf-8') as f:
            f.write("invalid json content")
        
        # 新しいインスタンスを作成（内部でデフォルト設定が作成される）
        settings = SettingsManager(self.test_file)
        
        # デフォルト値になっていることを確認
        self.assertEqual(settings.get_setting('test_str'), '')
        self.assertEqual(settings.get_setting('test_number'), 0)
        self.assertEqual(settings.get_setting('test_range'), 50)

    def test_load_file_with_missing_fields(self):
        """フィールドが不足したJSONファイルの読み込みテスト"""
        # 一部のフィールドが不足したJSONを作成
        incomplete_data = {
            'test_str': 'partial_data'
            # test_number, test_range, customが不足
        }
        
        with open(self.test_file, 'w', encoding='utf-8') as f:
            json.dump(incomplete_data, f, ensure_ascii=False, indent=2)
        
        # 新しいインスタンスで読み込み
        settings = SettingsManager(self.test_file)
        
        # デフォルト値で補完されることを確認
        self.assertEqual(settings.get_setting('test_str'), 'partial_data')
        self.assertEqual(settings.get_setting('test_number'), 0)  # デフォルト値
        self.assertEqual(settings.get_setting('test_range'), 50)  # デフォルト値
        self.assertEqual(settings.get_setting('custom'), {})  # デフォルト値

    def test_utf8_encoding(self):
        """UTF-8エンコーディングのテスト"""
        japanese_text = '日本語のテスト'
        self.settings.set_setting('test_str', japanese_text)
        self.settings.save()
        
        # ファイルを直接読み込んでUTF-8であることを確認
        with open(self.test_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        self.assertEqual(data['test_str'], japanese_text)
        
        # 新しいインスタンスで正しく読み込めることを確認
        new_settings = SettingsManager(self.test_file)
        self.assertEqual(new_settings.get_setting('test_str'), japanese_text)


if __name__ == '__main__':
    unittest.main()