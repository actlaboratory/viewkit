import wx
from copy import copy
from viewkit import SubWindow
from viewkit.creator import ViewCreator


class KeyValueSettingKey:
    def __init__(self, key:str, display_name:str, format:int, width:int):
        self.key = key
        self.display_name = display_name
        self.format = format
        self.width = width


class KeyValueSettingCustomButton:
    def __init__(self, label:str, event_handler_method_name:str):
        self.label = label
        self.event_handler_method_name = event_handler_method_name


class KeyValueSettingCustomButtonEvent:
    def __init__(
            self,
            selected_index:int,
            selected_value_row:dict
    ):
        self.selected_index = selected_index
        self.selected_value_row = selected_value_row


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

    def findIndexByKey(self, key: str):
        for i, k in enumerate(self.keys):
            if k.key == key:
                return i
        return None


class KeyValueSettingWindow(SubWindow):
    def __init__(self, parent, ctx, title, parameters: KeyValueSettingConfig):
        super().__init__(parent, ctx, title, parameters)
        self.config = parameters
        self._value_rows = copy(parameters.values)
        lst, _ = self.creator.virtualListCtrl(self.config.listview_label, proportion=0, sizer_flag=wx.ALL |
                                              wx.ALIGN_CENTER_HORIZONTAL, size=(750, 300), style=wx.LC_REPORT | wx.LC_SINGLE_SEL)
        for i, key in enumerate(self.config.keys):
            lst.InsertColumn(i, key.display_name, format=key.format, width=key.width)
        for row in self.config.values:
            index = lst.InsertItem(lst.GetItemCount(), row.get(self.config.keys[0].display_name, ""))
            for i, key in enumerate(self.config.keys):
                lst.SetItem(index, i, row.get(key.key, ""))
        control_button_creator = ViewCreator(0, self.creator.getFont(), self.creator.getPanel(),
                                             self.creator.getSizer(), wx.HORIZONTAL, 20, "", wx.EXPAND)
        for btn in self.config.custom_buttons:
            control_button_creator.button(btn.label, lambda event, h=btn.event_handler_method_name: self._handleCustomButton(event, h))
        control_button_creator.button(self.config.add_button_label, None)
        control_button_creator.button(self.config.edit_button_label, None)
        control_button_creator.button(self.config.delete_button_label, self._delete)
        bottom_button_creator = ViewCreator(0, self.creator.getFont(), self.creator.getPanel(),
                                            self.creator.getSizer(), wx.HORIZONTAL, 20, "", wx.EXPAND)
        bottom_button_creator.okbutton("OK")
        bottom_button_creator.cancelbutton("Cancel")
        self._lst = lst

    def _handleCustomButton(self, event, handler_method_name:str):
        if not hasattr(self, handler_method_name):
            return
        method = getattr(self, handler_method_name)
        if not callable(method):
            return
        selected_index = self._lst.GetFirstSelected()
        selected_value_row = self._value_rows[selected_index] if selected_index >= 0 else None
        method(
            KeyValueSettingCustomButtonEvent(
                selected_index=selected_index,
                selected_value_row=selected_value_row
            )
        )

    def _delete(self, event):
        selected_index = self._lst.GetFirstSelected()
        if selected_index < 0:
            return
        self._lst.DeleteItem(selected_index)
        del self._value_rows[selected_index]
        adjusted_index = selected_index if selected_index < len(self._value_rows) else selected_index - 1
        if adjusted_index >= 0:
            self._lst.Select(adjusted_index)
            self._lst.Focus(adjusted_index)
            self._lst.SetFocus()
