import wx
import ctypes
import sys
import _winxptheme


def simple(parent, title, message):
    dialog = wx.MessageDialog(parent, message, title, wx.OK)
    dialog.ShowModal()
    dialog.Destroy()


def yesNo(parent, title, message):
    dialog = wx.MessageDialog(parent, message, title, wx.YES_NO)
    result = dialog.ShowModal()
    dialog.Destroy()
    return result


def error(parent, message):
    dialog = wx.MessageDialog(parent, message, "error", wx.OK | wx.ICON_ERROR)
    dialog.ShowModal()
    dialog.Destroy()


def debug(message):
    if hasattr(sys, "frozen") == False:
        if type(message) != str:
            import pprint
            message = pprint.pformat(message)
        dialog = wx.MessageDialog(None, message, "debug", wx.OK)
        dialog.ShowModal()
        dialog.Destroy()


def win(title, message):
    ctypes.windll.user32.MessageBoxW(0, message, title, 0x00000040)
