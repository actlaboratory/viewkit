from typing import Optional, Callable
from .shortcut import str_to_shortcut_key
from copy import copy


class Feature:
    def __init__(self, identifier: str, display_name: str, shortcut_key: Optional[str], action: Optional[Callable]):
        self.identifier = identifier
        self.display_name = display_name
        if shortcut_key is not None:
            self.shortcut_key = str_to_shortcut_key(shortcut_key)
        else:
            self.shortcut_key = None

class FeatureStore:
    def __init__(self):
        self.features = {}

    def register(self, feature: Feature):
        self.features[feature.identifier] = feature

    def all(self):
        return copy(self.features)
