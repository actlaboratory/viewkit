from typing import Optional, Callable
from viewkit.shortcut import strToShortcutKey, ShortcutKeyStringValidator
from viewkit.settings.shortcut import ShortcutKeySettings, RawEntry, RemovedEntry, ParsedFileInput
from copy import copy


class Feature:
    def __init__(self, identifier: str, display_name: str, shortcut_key: Optional[str], action: Optional[Callable]):
        self.identifier = identifier
        self.display_name = display_name
        if shortcut_key is not None:
            self.shortcut_key = strToShortcutKey(shortcut_key)
            self.shortcut_key_str = shortcut_key
        else:
            self.shortcut_key = None
            self.shortcut_key_str = None

    def __str__(self):
        return f"Feature(identifier={self.identifier}, display_name={self.display_name}, shortcut_key={self.shortcut_key_str})"

    def copy(self):
        """Featureのコピーを返す"""
        return Feature(
            identifier=self.identifier,
            display_name=self.display_name,
            shortcut_key=self.shortcut_key_str,
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

    def applyShortcutKeySettings(self, input:ParsedFileInput) -> list[RemovedEntry]:
        """ショートカットキーの設定を適用し、無効なエントリを削除する。"""
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
        # todo: 複数に対応する。とりあえず [0] を使う
        for e in settings.entries:
            feature = self.getByIdentifier(e.feature_identifier)
            if feature is None: continue
            if e.shortcut_key_string is not None:
                feature.shortcut_key_str = e.shortcut_key_string
            if e.shortcut_keys:
                feature.shortcut_key = e.shortcut_keys[0]
