import wx
import logging


class toolTip():
    def __init__(self, parent, cursorPos, label, bgColor, fgColor, font):
        cursorPos.x += 10
        cursorPos.y += 10
        self.parent = parent
        self.dialog = wx.Dialog(parent.GetTopLevelParent(), style=wx.BORDER_RAISED, pos=cursorPos)
        self.dialog.SetBackgroundColour(bgColor)
        self.dialog.SetForegroundColour(fgColor)
        self.dialog.SetFont(font)
        self.staticText = wx.StaticText(self.dialog, wx.ID_ANY, label=label)
        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add(self.staticText, 0, wx.ALIGN_CENTER | wx.ALL, border=5)
        self.dialog.SetSizer(sizer)
        self.dialog.Fit()
        self.dialog.Disable()
        pos = self._fixPos()
        if pos:
            self.dialog.SetPosition(pos)
            self.dialog.Show()

    def refresh(self, cursorPos=None, label=None):
        if label is not None:
            self.staticText.SetLabel(label)
        self.dialog.Fit()
        if cursorPos is not None:
            pos = self._fixPos(cursorPos)
            if pos:
                self.dialog.Move(pos)
                self.dialog.Show()
            else:
                self.dialog.Show(False)

    def destroy(self):
        self.dialog.Destroy()
        self.dialog = None

    def __del__(self):
        if self.dialog is not None:
            self.destroy()

    def _fixPos(self, cursorPos=None):
        borderW = (int)((self.parent.GetTopLevelParent().GetScreenRect().GetWidth() - self.parent.GetTopLevelParent().GetClientSize()[0] + 2) / 2)
        borderT = (int)((self.parent.GetTopLevelParent().GetScreenRect().GetHeight() -
                         self.parent.GetTopLevelParent().GetClientSize()[1] - borderW - 1))
        clientRect = self.dialog.GetScreenRect()
        if cursorPos is not None:
            clientRect.SetPosition(wx.Point(cursorPos.x + 10, cursorPos.y + 10))
        clientBR = clientRect.GetBottomRight()
        clientH = (int)(clientRect.GetHeight())
        maxBR = self.parent.GetTopLevelParent().GetScreenRect().GetBottomRight()
        x = maxBR.x - clientBR.x - borderW
        if x < 0:
            if clientRect.GetPosition().x + x < borderW:
                return False
            else:
                pos = clientRect.GetPosition()
                pos.x += x
        else:
            pos = clientRect.GetPosition()
        y = maxBR.y - clientBR.y - borderW
        if y < 0:
            if clientRect.GetPosition().y - 20 - clientH < borderT:
                return False
            else:
                pos.y -= (20 + clientH)
        return pos
