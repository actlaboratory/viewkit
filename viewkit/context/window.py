import wx
from viewkit.menu import Menu
from viewkit.ref import RefStore
from viewkit.feature import FeatureStore


class WindowContext:
    def __init__(self):
        self.menu = Menu()
        self.ref_store = RefStore()
        self.feature_store = FeatureStore()
