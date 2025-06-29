import json
import os
from typing import Dict, Any, Optional
from cerberus import Validator


class SettingsManager:
    def __init__(self, filename: str):
        self.filename = filename
        self.custom_fields = {}
        self.schema = {
            'test_str': {'type': 'string', 'default': ''},
            'test_number': {'type': 'number', 'default': 0},
            'test_range': {'type': 'number', 'min': 1, 'max': 100, 'default': 50},
            'custom': {'type': 'dict', 'default': {}}
        }
        self.data = {}
        self._load_or_create_default()

    def register_custom_field(self, field_name: str, schema: Optional[Dict[str, Any]] = None):
        """カスタムフィールドを登録する"""
        if schema is None:
            schema = {}
        self.custom_fields[field_name] = schema

    def _load_or_create_default(self):
        """ファイルがなければデフォルトの設定でファイルを書き込む"""
        if not os.path.exists(self.filename):
            self._create_default_settings()
        else:
            self._load_settings()

    def _create_default_settings(self):
        """デフォルト設定を作成"""
        validator = Validator(self.schema)
        self.data = validator.normalized({})
        self._save_settings()

    def _load_settings(self):
        """設定ファイルを読み込む"""
        try:
            with open(self.filename, 'r', encoding='utf-8') as f:
                data = json.load(f)

            # バリデーション
            validator = Validator(self.schema)
            if validator.validate(data):
                self.data = validator.normalized(data)
            else:
                raise ValueError(f"設定ファイルの検証に失敗: {validator.errors}")

            # カスタムフィールドのバリデーション
            if 'custom' in self.data:
                for field_name, field_data in self.data['custom'].items():
                    if field_name in self.custom_fields and self.custom_fields[field_name]:
                        field_validator = Validator(self.custom_fields[field_name], allow_unknown=True)
                        if not field_validator.validate(field_data):
                            raise ValueError(f"カスタムフィールド '{field_name}' の検証に失敗: {field_validator.errors}")

        except (json.JSONDecodeError, FileNotFoundError, ValueError) as e:
            print(f"設定ファイルの読み込みエラー: {e}")
            self._create_default_settings()

    def get_setting(self, key: str, default: Any = None) -> Any:
        """設定値にアクセスする"""
        return self.data.get(key, default)

    def get_custom_setting(self, field_name: str, key: str = None, default: Any = None) -> Any:
        """カスタム設定値にアクセスする"""
        custom_data = self.data.get('custom', {})
        if field_name not in custom_data:
            return default

        if key is None:
            return custom_data[field_name]

        return custom_data[field_name].get(key, default)

    def set_setting(self, key: str, value: Any):
        """設定値を変更する"""
        if key == 'custom':
            raise ValueError("カスタム設定は set_custom_setting を使用してください")

        # バリデーション
        temp_data = self.data.copy()
        temp_data[key] = value
        validator = Validator(self.schema)

        if validator.validate(temp_data):
            self.data[key] = value
        else:
            raise ValueError(f"設定値の検証に失敗: {validator.errors}")

    def set_custom_setting(self, field_name: str, value: Any):
        """カスタム設定値を変更する"""
        if field_name not in self.custom_fields:
            raise ValueError(f"カスタムフィールド '{field_name}' が登録されていません")

        # バリデーション（スキーマが空でない場合のみ）
        if self.custom_fields[field_name]:
            field_validator = Validator(self.custom_fields[field_name], allow_unknown=True)
            if not field_validator.validate(value):
                raise ValueError(f"カスタムフィールド '{field_name}' の検証に失敗: {field_validator.errors}")

        if 'custom' not in self.data:
            self.data['custom'] = {}

        self.data['custom'][field_name] = value

    def save(self):
        """ファイルを保存する"""
        self._save_settings()

    def _save_settings(self):
        """設定をファイルに保存"""
        os.makedirs(os.path.dirname(self.filename), exist_ok=True)
        with open(self.filename, 'w', encoding='utf-8') as f:
            json.dump(self.data, f, ensure_ascii=False, indent=2)
