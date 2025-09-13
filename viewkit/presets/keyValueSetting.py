import wx
from viewkit import SubWindow
from viewkit.creator import ViewCreator


class KeyValueSettingKey:
    def __init__(self, key, format, width):
        self.key = key
        self.format = format
        self.width = width


class KeyValueSettingCustomButton:
    def __init__(self, label, event_handler):
        self.label = label
        self.event_handler = event_handler

class KeyValueSettingConfig:
    def __init__(
        self,
        listview_label="keys",
        keys=[],
        values={},
        allow_edit_keys=True,
        custom_buttons=[],
        editor_window_class=None,
        add_button_label="Add",
        edit_button_label="Edit",
        delete_button_label="Delete"
    ):
        self.listview_label = listview_label
        self.keys = keys
        self.values = values
        self.allow_edit_keys = allow_edit_keys
        self.custom_buttons = custom_buttons
        self.editor_window_class = editor_window_class
        self.add_button_label = add_button_label
        self.edit_button_label = edit_button_label
        self.delete_button_label = delete_button_label

    def findIndexByKey(self, key:str):
        for i,k in enumerate(self.keys):
            if k.key == key:
                return i
        return None


class KeyValueSettingWindow(SubWindow):
    def __init__(self, parent, ctx, title, parameters: KeyValueSettingConfig):
        super().__init__(parent, ctx, title, parameters)
        self.config = parameters
        lst, _ = self.creator.virtualListCtrl(self.config.listview_label, proportion=0, sizer_flag=wx.ALL|wx.ALIGN_CENTER_HORIZONTAL,size=(750,300),style=wx.LC_REPORT | wx.LC_SINGLE_SEL)
        for i,key in enumerate(self.config.keys):
            lst.InsertColumn(i,key.key,format=key.format,width=key.width)
        for row in self.config.values:
            index = lst.InsertItem(lst.GetItemCount(), row.get(self.config.keys[0].key, ""))
            for i,key in enumerate(self.config.keys):
                lst.SetItem(index, i, row.get(key.key, ""))
        control_button_creator = ViewCreator(0,self.creator.getFont(), self.creator.getPanel(),self.creator.getSizer(),wx.HORIZONTAL,20,"",wx.EXPAND)
        for btn in self.config.custom_buttons:
            control_button_creator.button(btn.label,btn.event_handler)
        control_button_creator.button(self.config.add_button_label,None)
        control_button_creator.button(self.config.edit_button_label,None)
        control_button_creator.button(self.config.delete_button_label,None)
        bottom_button_creator = ViewCreator(0,self.creator.getFont(), self.creator.getPanel(),self.creator.getSizer(),wx.HORIZONTAL,20,"",wx.EXPAND)
        bottom_button_creator.okbutton("OK")
        bottom_button_creator.cancelbutton("Cancel")
