import wx
import _winxptheme
from viewkit.creator import ViewCreator

class SubWindow(wx.Dialog):
	"""viewkit では、メインウィンドウ以外のウィンドウをサブウィンドウと呼びます。現状では、これらは全て wx.Dialogのサブクラスとして実装されます。"""
	def __init__(self, parent,title,style=wx.CAPTION | wx.SYSTEM_MENU | wx.BORDER_DEFAULT):
		self.value=None
		wx.Dialog.__init__(self, parent,-1, title,style = style)
		_winxptheme.SetWindowTheme(self.wnd.GetHandle(),"","")
		self.SetEscapeId(wx.ID_NONE)
		self.Bind(wx.EVT_CLOSE,self.OnClose)
		self.panel = wx.Panel(self,wx.ID_ANY)
		self.creator = ViewCreator(0, self.panel, None, wx.VERTICAL, style=wx.ALL, space=0)

	#closeイベントで呼ばれる。Alt+F4対策
	def OnClose(self,event):
		if self.wnd.GetWindowStyleFlag() & wx.CLOSE_BOX==wx.CLOSE_BOX:
			event.Skip()
		else:
			event.Veto()
