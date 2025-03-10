# listCtrlBase for ViewCreator
# Copyright (C) 2019-2020 Hiroki Fujii <hfujii@hisystron.com>
# Copyright (C) 2020 yamahubuki <itiro.ishino@gmail.com>

import json
import wx
from . import viewObjectUtil, listCtrlBase


class listCtrl(listCtrlBase.listCtrl):
    def __init__(self, *pArg, **kArg):
        self.focusFromKbd = viewObjectUtil.popArg(kArg, "enableTabFocus", True)  # キーボードフォーカスの初期値
        return super().__init__(*pArg, **kArg)
