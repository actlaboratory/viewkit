# listCtrlBase for ViewCreator
# Copyright (C) 2019-2020 Hiroki Fujii <hfujii@hisystron.com>
# Copyright (C) 2020 yamahubuki <itiro.ishino@gmail.com>

import json
import wx
from . import control, listctrl, util


class listCtrl(control.controlBase, wx.ListCtrl):
    def __init__(self, *pArg, **kArg):
        self._needSaveColumnInfo = False
        self.sectionName = ""
        self.keyName = ""
        return super().__init__(*pArg, **kArg)

    # ポップアップメニューの表示位置をクライアント座標のwx.Pointで返す
    def getPopupMenuPosition(self):
        if self.GetFocusedItem() >= 0:
            rect = self.GetItemRect(self.GetFocusedItem(), wx.LIST_RECT_LABEL)
            return rect.GetBottomRight()
        else:
            return super().getPopupMenuPosition()

    # todo loadColumnInfo and saveColumnInfo

    def getItemSelections(self):
        """
        現在選択されている項目のインデックスを取得
        :returns: 選択中インデックスのリスト
        :rtype: list
        """
        ret = []
        i = self.GetFirstSelected()
        if i >= 0:
            ret.append(i)
        else:
            return ret
        while True:
            iTmp = i
            i = self.GetNextSelected(iTmp)
            if i >= 0:
                ret.append(i)
            else:
                return ret
