from copy import copy
from viewkit.shortcut.validation import ShortcutKeyStringValidator, ShortcutKeyValidationError, VALIDATION_ERROR_EMPTY, VALIDATION_ERROR_FORBIDDEN, VALIDATION_ERROR_MODIFIER_ONLY, VALIDATION_ERROR_MULTI_NONMODIFIER, VALIDATION_ERROR_NEEDS_MODIFIER
from viewkit.shortcut.translation import strToShortcutKey, separateShortcutKeyString, ModifierKeyOnly, UnrecognizedKeyString, ShortcutKey


class RawEntry:
    def __init__(self, feature_identifier: str, shortcut_key_string: str):
        self.feature_identifier = feature_identifier
        self.shortcut_key_string = shortcut_key_string


class ParsedFileInput:
    """設定ファイルのパース結果を表すクラス"""

    def __init__(self, version: str, raw_entries: list[RawEntry]):
        self.version = version
        self.raw_entries = raw_entries


class Entry:
    def __init__(self, raw_entry: RawEntry):
        """ショートカットキーの設定を表すエントリ"""
        self.feature_identifier = raw_entry.feature_identifier
        temp_shortcut_keys = []
        # 文字列から ShortcutKey への返還を試みる
        if not self.shortcut_key_string:
            return
        separated = separateShortcutKeyString(self.shortcut_key_string)
        for key in separated:
            temp_shortcut_keys.append(strToShortcutKey(key))
        # 重複をチェックしながらリストに入れていく
        for key in temp_shortcut_keys:
            if not self._isDuplicateKeystroke(key):
                self.shortcut_keys.append(key)

    def _isDuplicateKeystroke(self, shortcutKey: ShortcutKey) -> bool:
        """同じショートカットキーが既に存在するかどうかをチェックする"""
        for existing_key in self.shortcut_keys:
            if existing_key.isSame(shortcutKey):
                return True
        return False

    def hasSameKeystroke(self, other: 'Entry') -> bool:
        """他のエントリと同じショートカットキーを持っているかどうかをチェックする"""
        if not isinstance(other, Entry):
            return False
        for key in self.shortcut_keys:
            if any(key.isSame(other_key) for other_key in other.shortcut_keys):
                return True


def _listDuplicateIdentifierEntryKeys(entries: list[Entry]) -> list[str]:
    """リスト内のエントリの中で、ショートカットキーが重複しているものを返す"""
    key_count = {}
    for entry in entries:
        if entry.shortcut_key_string not in key_count:
            key_count[entry.shortcut_key_string] = 0
        key_count[entry.shortcut_key_string] += 1
    return [key for key, count in key_count.items() if count > 1]


REMOVED_ENTRY_REASON_INVALID_NOTATION = "invalid_notation"
REMOVED_ENTRY_REASON_DUPLICATE_IDENTIFIER_IN_SETTINGS = "duplicate_identifier_in_settings"
REMOVED_ENTRY_REASON_DUPLICATE_SHORTCUT_IN_SETTINGS = "duplicate_shortcut_in_settings"
REMOVED_ENTRY_REASON_DUPLICATE_AFTER_APPLY = "duplicate_after_apply"


class RemovedEntry:
    """何らかのエラーで使用できず、削除されたエントリーを表すクラス。"""

    def __init__(self, reason: str, entry: Entry, additionalInfo: str = ""):
        self.reason = reason
        self.entry = entry
        self.additionalInfo = additionalInfo


class ShortcutKeySettings:
    def __init__(self, version: str, raw_entries: list[RawEntry]):
        """ショートカットキーの設定を表すクラス。"""
        self.version = version
        self.raw_entries = raw_entries

    def generateEntries(self):
        """RawEntryのリストから、Entryのリストを生成する。"""
        self.entries = [Entry(raw_entry) for raw_entry in self.raw_entries]

    def removeEntriesWithDuplicateIdentifiers(self) -> list[RemovedEntry]:
        """ショートカットキーが重複しているエントリを削除する。削除したエントリの識別子をリストにして返す。"""
        duplicate_identifiers = _listDuplicateIdentifierEntryKeys(self.entries)
        if not duplicate_identifiers:
            return []
        removed_entries = [entry for entry in self.entries if entry.feature_identifier in duplicate_identifiers]
        self.entries = [entry for entry in self.raw_entries if entry.feature_identifier not in duplicate_identifiers]
        return [RemovedEntry(REMOVED_ENTRY_REASON_DUPLICATE_IDENTIFIER_IN_SETTINGS, entry) for entry in removed_entries]

    def removeEntriesWithDuplicateKeystrokes(self) -> list[RemovedEntry]:
        """ショートカットキーが重複しているエントリを削除する。削除したエントリの識別子をリストにして返す。"""
        removed_entries = []
        for e in self.entries:
            for other in self.entries:
                if e is not other and e.hasSameKeystroke(other):
                    removed_entries.append(e)
                    break
        self.entries = [e for e in self.entries if e not in removed_entries]
        return [RemovedEntry(REMOVED_ENTRY_REASON_DUPLICATE_SHORTCUT_IN_SETTINGS, entry) for entry in removed_entries]

    def removeInvalidEntries(self, validator) -> list[RemovedEntry]:
        """ショートカットキーの文字列が無効なエントリを削除する。削除したエントリの識別子をリストにして返す。"""
        removed_entries = []
        valid_entries = []
        for entry in self.raw_entries:
            try:
                validator.validate(entry.shortcut_key_string)
                valid_entries.append(entry)
            except ShortcutKeyValidationError as e:
                removed_entries.append(RemovedEntry(REMOVED_ENTRY_REASON_INVALID_NOTATION, entry, str(e)))
        self.raw_entries = valid_entries
        return removed_entries
