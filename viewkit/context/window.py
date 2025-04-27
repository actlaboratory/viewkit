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
            if feature.shortcut_key is not None:
                entries.append(
                    wx.AcceleratorEntry(
                        feature.shortcut_key.modifier_flags,
                        feature.shortcut_key.key_code,
                        self.ref_store.getRef(
                            feature.identifier)))
            # end shortcut key exists
        # end for feature
        return wx.AcceleratorTable(entries)
