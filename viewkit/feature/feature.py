from typing import Optional, Callable
from viewkit.shortcut import strToShortcutKey, separateShortcutKeyString, ShortcutKeyStringValidator
from viewkit.settings.shortcut import ShortcutKeySettings, RawEntry, RemovedEntry, ParsedFileInput
from copy import copy


class Feature:
    def __init__(self, identifier: str, display_name: str, shortcut_key: Optional[str], action: Optional[Callable] = None):
        self.identifier = identifier
        self.display_name = display_name
        self.action = action
        if shortcut_key is not None:
            separated_keys = separateShortcutKeyString(shortcut_key)
            self.shortcut_keys = [strToShortcutKey(key) for key in separated_keys]
        else:
            self.shortcut_keys = []

    def __str__(self):
        shortcut_keys_str = [str(key) for key in self.shortcut_keys] if self.shortcut_keys else []
        return f"Feature(identifier={self.identifier}, display_name={self.display_name}, shortcut_keys={shortcut_keys_str})"

    def copy(self):
        """Featureのコピーを返す"""
        return Feature(
            identifier=self.identifier,
            display_name=self.display_name,
            shortcut_key=str(self.shortcut_keys[0]) if self.shortcut_keys else None,
        )


class FeatureStore:
    def __init__(self):
        self.features = {}

    def register(self, feature: Feature):
        self.features[feature.identifier] = feature

    def all(self):
        return copy(self.features)

    def getByIdentifier(self, identifier: str) -> Optional[Feature]:
        return self.features.get(identifier, None)

    def applyShortcutKeySettings(self, input: ParsedFileInput) -> list[RemovedEntry]:
        """ショートカットキーの設定を適用し、無効なエントリを削除する。"""
        removed_entries = []
        settings = ShortcutKeySettings(input.version, input.raw_entries)
        settings.generateEntries()
        validator = ShortcutKeyStringValidator(has_char_input_on_screen=True)
        # 重複する識別子のエントリを削除
        removed_entries += settings.removeEntriesWithDuplicateIdentifiers()
        # 重複するショートカットキーのエントリを削除
        removed_entries += settings.removeEntriesWithDuplicateKeystrokes()
        # 無効なエントリを削除
        removed_entries = settings.removeInvalidEntries(validator)
        # featuresに上書きしていく
        for e in settings.entries:
            feature = self.getByIdentifier(e.feature_identifier)
            if feature is None:
                continue
            if e.shortcut_keys:
                feature.shortcut_keys = e.shortcut_keys
        return removed_entries

    def applyCustomShortcutSettings(self, shortcut_settings: dict) -> list[RemovedEntry]:
        """カスタムショートカット設定を適用し、競合解決を行う"""
        if not shortcut_settings:
            return []

        # 辞書形式から RawEntry リストに変換
        raw_entries = []
        for feature_id, shortcut_str in shortcut_settings.items():
            if isinstance(shortcut_str, str) and shortcut_str.strip():
                raw_entries.append(RawEntry(feature_id, shortcut_str))

        if not raw_entries:
            return []

        # 既存の applyShortcutKeySettings を利用
        input_data = ParsedFileInput("custom", raw_entries)
        return self.applyShortcutKeySettings(input_data)

    def applyShortcutSettingsWithCustomPriority(self, default_settings: ParsedFileInput = None, custom_settings: dict = None) -> list[RemovedEntry]:
        """デフォルト設定とカスタム設定を統合して適用し、カスタムを優先する"""
        all_removed_entries = []

        # まずデフォルト設定を適用
        if default_settings:
            all_removed_entries.extend(self.applyShortcutKeySettings(default_settings))

        # 次にカスタム設定を適用（カスタム設定が優先される）
        if custom_settings:
            all_removed_entries.extend(self.applyCustomShortcutSettings(custom_settings))

        return all_removed_entries

    def applyCustomShortcutSettingsWithConflictResolution(self, shortcut_settings: dict) -> list[RemovedEntry]:
        """カスタムショートカット設定を適用し、デフォルト設定との競合を解決する"""
        if not shortcut_settings:
            return []

        removed_entries = []

        # カスタム設定で使用されるショートカットキーを収集
        custom_shortcut_keys = set()
        for feature_id, shortcut_str in shortcut_settings.items():
            if isinstance(shortcut_str, str) and shortcut_str.strip():
                try:
                    from viewkit.shortcut import separateShortcutKeyString, strToShortcutKey
                    separated_keys = separateShortcutKeyString(shortcut_str)
                    for key_str in separated_keys:
                        shortcut_key = strToShortcutKey(key_str)
                        custom_shortcut_keys.add(str(shortcut_key).lower())
                except BaseException:
                    continue

        # デフォルト設定のFeatureで競合するものを特定し、ショートカットを削除
        for feature in self.features.values():
            if feature.identifier not in shortcut_settings:  # カスタム設定にないFeature
                if feature.shortcut_keys:
                    for shortcut_key in feature.shortcut_keys[:]:  # コピーを作成してイテレート
                        if str(shortcut_key).lower() in custom_shortcut_keys:
                            # 競合するデフォルトショートカットを削除
                            feature.shortcut_keys.remove(shortcut_key)

        # カスタム設定を適用
        removed_entries.extend(self.applyCustomShortcutSettings(shortcut_settings))

        return removed_entries
