import json
import os
from typing import Dict, Any, Optional
from cerberus import Validator

class CustomSettingField:
    def __init__(self, name:str, schema: Dict[str, Any]):
        self.name = name
        self.schema = schema

class SettingsManager:
    SETTING_SEPARATOR = '.'

    def __init__(self, filename: str):
        self.filename = os.path.abspath(filename)
        self.custom_fields = {}
        self.schema = {
            # 'test_str': {'type': 'string', 'default': ''},
            # 'test_number': {'type': 'number', 'default': 0},
            # 'test_range': {'type': 'number', 'min': 1, 'max': 100, 'default': 50},
            'app_version': {'type': 'string', 'default': ''},
            'schema_version': {'type': 'string', 'default': '20250816.0'},
            'shortcuts': {'type': 'dict', 'default': {}},
            'custom': {'type': 'dict', 'default': {}}
        }
        self.data = {}

    def registerCustomField(self, field: CustomSettingField):
        """カスタムフィールドを登録する"""
        self.custom_fields[field.name] = field.schema

    def getShortcutSettings(self):
        """ショートカット設定を取得する"""
        return self.getSetting('shortcuts', default={})

    def loadOrCreateDefault(self):
        """ファイルがなければデフォルトの設定でファイルを書き込む"""
        if not os.path.exists(self.filename):
            self._createDefaultSettings()
        else:
            self._loadSettings()

    def _createDefaultSettings(self):
        """デフォルト設定を作成"""
        # カスタムフィールドも含めてデフォルト設定を埋めたいので、カスタムフィールドと通常のスキーマを一時的にマージする
        merged_schema = {**self.schema}
        if self.custom_fields:
            merged_schema["custom"]["schema"] = self.custom_fields
        validator = Validator(merged_schema)
        self.data = validator.normalized({})
        self._saveSettings()

    def _loadSettings(self):
        """設定ファイルを読み込む"""
        try:
            with open(self.filename, 'r', encoding='utf-8') as f:
                data = json.load(f)

            # バリデーション
            validator = Validator(self.schema)
            if validator.validate(data):
                self.data = validator.normalized(data)
            else:
                raise ValueError(f"Settings file validation failed: {validator.errors}")

            # カスタムフィールドのバリデーション
            if 'custom' in self.data:
                for field_name, field_data in self.data['custom'].items():
                    if field_name in self.custom_fields and self.custom_fields[field_name]:
                        field_validator = Validator(self.custom_fields[field_name], allow_unknown=True)
                        if not field_validator.validate(field_data):
                            raise ValueError(f"Custom field '{field_name}' validation failed: {field_validator.errors}")

        except (json.JSONDecodeError, FileNotFoundError, ValueError) as e:
            print(f"設定ファイルの読み込みエラー: {e}")
            self._createDefaultSettings()

    def getSetting(self, key: str, default: Any = None) -> Any:
        """設定値にアクセスする（ネストパス対応）"""
        if self.SETTING_SEPARATOR in key:
            keys = key.split(self.SETTING_SEPARATOR)
            current = self.data

            for k in keys:
                if isinstance(current, dict) and k in current:
                    current = current[k]
                else:
                    return default

            return current
        else:
            return self.data.get(key, default)

    def getCustomSetting(self, field_name: str, key: str = None, default: Any = None) -> Any:
        """カスタム設定値にアクセスする"""
        custom_data = self.data.get('custom', {})
        if field_name not in custom_data:
            return default

        if key is None:
            return custom_data[field_name]

        return custom_data[field_name].get(key, default)

    def getNestedSetting(self, path: str, default: Any = None) -> Any:
        """区切り文字で区切られたパスで設定値を探索して取得する"""
        keys = path.split(self.SETTING_SEPARATOR)
        current = self.data

        for key in keys:
            if isinstance(current, dict) and key in current:
                current = current[key]
            else:
                return default

        return current

    def changeNestedSetting(self, path: str, value: Any):
        """区切り文字で区切られたパスで設定値を変更する（バリデーション付き）"""
        keys = path.split(self.SETTING_SEPARATOR)

        # バリデーション用に一時的にデータを作成
        temp_data = self.data.copy()
        current = temp_data

        # パスをたどって設定値を変更
        for i, key in enumerate(keys[:-1]):
            if key not in current:
                current[key] = {}
            elif not isinstance(current[key], dict):
                raise ValueError(f"Path '{self.SETTING_SEPARATOR.join(keys[:i + 1])}' is not a dictionary")
            current = current[key]

        # 最終キーに値を設定
        final_key = keys[-1]
        current[final_key] = value

        # バリデーション実行
        validator = Validator(self.schema)
        if not validator.validate(temp_data):
            raise ValueError(f"Setting validation failed: {validator.errors}")

        # バリデーション成功時のみ実際のデータを更新
        self.data = validator.normalized(temp_data)

    def changeSetting(self, key: str, value: Any):
        """設定値を変更する（ネストパス・カスタム設定対応）"""
        if self.SETTING_SEPARATOR in key:
            keys = key.split(self.SETTING_SEPARATOR)

            # カスタム設定の場合は専用のバリデーションロジック
            if keys[0] == 'custom' and len(keys) >= 2:
                field_name = keys[1]
                if field_name not in self.custom_fields:
                    raise ValueError(f"Custom field '{field_name}' is not registered")

                # カスタムフィールドの値全体を設定する場合
                if len(keys) == 2:
                    # バリデーション（スキーマが空でない場合のみ）
                    if self.custom_fields[field_name]:
                        field_validator = Validator(self.custom_fields[field_name], allow_unknown=True)
                        if not field_validator.validate(value):
                            raise ValueError(f"Custom field '{field_name}' validation failed: {field_validator.errors}")

                    if 'custom' not in self.data:
                        self.data['custom'] = {}
                    self.data['custom'][field_name] = value
                    return

            # 通常のネストパス処理
            # バリデーション用に一時的にデータを作成
            temp_data = self.data.copy()
            current = temp_data

            # パスをたどって設定値を変更
            for i, k in enumerate(keys[:-1]):
                if k not in current:
                    current[k] = {}
                elif not isinstance(current[k], dict):
                    raise ValueError(f"Path '{self.SETTING_SEPARATOR.join(keys[:i + 1])}' is not a dictionary")
                current = current[k]

            # 最終キーに値を設定
            final_key = keys[-1]
            current[final_key] = value

            # バリデーション実行
            validator = Validator(self.schema)
            if not validator.validate(temp_data):
                raise ValueError(f"Setting validation failed: {validator.errors}")

            # バリデーション成功時のみ実際のデータを更新
            self.data = validator.normalized(temp_data)
        else:
            if key == 'custom':
                raise ValueError("Use custom.field_name format for custom settings")

            # バリデーション
            temp_data = self.data.copy()
            temp_data[key] = value
            validator = Validator(self.schema)

            if validator.validate(temp_data):
                self.data[key] = value
            else:
                raise ValueError(f"Setting validation failed: {validator.errors}")

    def setCustomSetting(self, field_name: str, value: Any):
        """カスタム設定値を変更する"""
        if field_name not in self.custom_fields:
            raise ValueError(f"Custom field '{field_name}' is not registered")

        # バリデーション（スキーマが空でない場合のみ）
        if self.custom_fields[field_name]:
            field_validator = Validator(self.custom_fields[field_name], allow_unknown=True)
            if not field_validator.validate(value):
                raise ValueError(f"Custom field '{field_name}' validation failed: {field_validator.errors}")

        if 'custom' not in self.data:
            self.data['custom'] = {}

        self.data['custom'][field_name] = value

    def save(self):
        """ファイルを保存する"""
        self._saveSettings()

    def _saveSettings(self):
        """設定をファイルに保存"""
        os.makedirs(os.path.dirname(self.filename), exist_ok=True)
        with open(self.filename, 'w', encoding='utf-8') as f:
            json.dump(self.data, f, ensure_ascii=False, indent=2)
