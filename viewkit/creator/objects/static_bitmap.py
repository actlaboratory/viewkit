# staticBitmapBase for ViewCreator
# Copyright (C) 2023 yamahubuki <itiro.ishino@gmail.com>

import wx
from . import control, util


class staticBitmap(control.controlBase, wx.StaticBitmap):
    def __init__(self, *pArg, **kArg):
        self.focusFromKbd = False
        return super().__init__(*pArg, **kArg)
