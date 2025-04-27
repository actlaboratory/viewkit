import wx
from viewkit.menu import Menu
from viewkit.ref import RefStore
from viewkit.feature import FeatureStore


class WindowContext:
    def __init__(self):
        self.menu = Menu()
        self.ref_store = RefStore()
        self.feature_store = FeatureStore()

    def generateAcceleratorTable(self):
        """すべての feature の wx.AcceleratorTable を作成する"""
        entries = []
        for feature in self.feature_store.all().values():
            if feature.shortcutKey is not None:
                entries.append(wx.AcceleratorEntry(feature.shortcutKey.modifierFlags, feature.shortcutKey.keyCode, self.ref_store.get_ref(feature.identifier)))
            # end shortcut key exists
        # end for feature
        return wx.AcceleratorTable(entries)
