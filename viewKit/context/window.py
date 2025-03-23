from viewkit.menu import Menu
from viewkit.ref import RefStore


class WindowContext:
    def __init__(self):
        self.menu = Menu()
        self.ref_store = RefStore()
