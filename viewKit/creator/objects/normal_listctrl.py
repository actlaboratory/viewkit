# listCtrlBase for ViewCreator
# Copyright (C) 2019-2020 Hiroki Fujii <hfujii@hisystron.com>
# Copyright (C) 2020 yamahubuki <itiro.ishino@gmail.com>

import json
import wx
from . import listctrl, util


class listCtrl(listctrl.listCtrl):
    def __init__(self, *pArg, **kArg):
        self.focusFromKbd = util.popArg(kArg, "enableTabFocus", True)  # キーボードフォーカスの初期値
        return super().__init__(*pArg, **kArg)
