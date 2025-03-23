# radioButtonBase for ViewCreator
# Copyright (C) 2019-2020 Hiroki Fujii <hfujii@hisystron.com>


import wx
from . import control, util


class radioButton(control.controlBase, wx.RadioButton):
    def __init__(self, *pArg, **kArg):
        self.focusFromKbd = util.popArg(kArg, "enableTabFocus", True)  # キーボードフォーカスの初期値
        return super().__init__(*pArg, **kArg)
