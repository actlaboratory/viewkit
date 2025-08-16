from typing import Optional, Callable
from viewkit.shortcut import strToShortcutKey, separateShortcutKeyString, ShortcutKeyStringValidator
from viewkit.settings.shortcut import ShortcutKeySettings, RawEntry, RemovedEntry, ParsedFileInput
from copy import copy


class Feature:
    def __init__(self, identifier: str, display_name: str, shortcut_key: Optional[str], action: Optional[Callable]=None):
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
