import wx
from copy import copy
from viewkit import SubWindow


class KeyValueSettingKey:
    def __init__(self, key: str, display_name: str, format: int, width: int):
        self.key = key
        self.display_name = display_name
        self.format = format
        self.width = width


class KeyValueSettingCustomButton:
    def __init__(self, label: str, event_handler_method_name: str):
        self.label = label
        self.event_handler_method_name = event_handler_method_name


class KeyValueSettingCustomButtonEvent:
    def __init__(
            self,
            selected_index: int,
            selected_value_row: dict
    ):
        self.selected_index = selected_index
        self.selected_value_row = selected_value_row


class KeyValueSettingEditEvent:
    def __init__(
            self,
            all_value_rows: list,
            is_add: bool,
            editing_index: int,
            original_value_row: dict
    ):
        self.all_value_rows = all_value_rows
        self.is_add = is_add
        self.editing_index = editing_index
        self.original_value_row = original_value_row


class KeyValueSettingConfig:
    def __init__(
        self,
        listview_label="keys",
        keys=[],
        values={},
        allow_edit_rows=True,
        custom_buttons=[],
        editor_window_class=None,
        add_button_label="Add",
        edit_button_label="Edit",
        delete_button_label="Delete"
    ):
        self.listview_label = listview_label
        self.keys = keys
        self.values = values
        self.allow_edit_rows = allow_edit_rows
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
        control_button_creator = self.creator.makeChild(wx.HORIZONTAL, 20, "", wx.EXPAND)
        for btn in self.config.custom_buttons:
            control_button_creator.button(btn.label, lambda event, h=btn.event_handler_method_name: self._handleCustomButton(event, h))
        add_button = control_button_creator.button(self.config.add_button_label, self._handleAdd)
        edit_button = control_button_creator.button(self.config.edit_button_label, self._handleEdit)
        delete_button = control_button_creator.button(self.config.delete_button_label, self._handleDelete)
        if not self.config.allow_edit_rows:
            add_button.Disable()
            delete_button.Disable()
        bottom_button_creator = self.creator.makeChild(wx.HORIZONTAL, 20, "", wx.EXPAND)
        bottom_button_creator.okbutton("OK")
        bottom_button_creator.cancelbutton("Cancel")
        self._lst = lst

    def _handleCustomButton(self, event, handler_method_name: str):
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

    def _handleAdd(self, event):
        if self.config.editor_window_class is None:
            return
        event = KeyValueSettingEditEvent(
            all_value_rows=self._value_rows,
            is_add=True,
            editing_index=-1,
            original_value_row=None
        )
        result = self.showSubWindow(self.config.editor_window_class, "Add", event, modal=True)
        print(result.code)
        if result.code != wx.ID_OK:
            return
        new_value_row = result.user_object
        if new_value_row is None:
            return
        index = self._lst.InsertItem(self._lst.GetItemCount(), new_value_row.get(self.config.keys[0].key, ""))
        for i, key in enumerate(self.config.keys):
            self._lst.SetItem(index, i, new_value_row.get(key.key, ""))
        self._value_rows.append(new_value_row)
        self._lst.Select(index)
        self._lst.Focus(index)
        self._lst.SetFocus()

    def _handleEdit(self, event):
        if self.config.editor_window_class is None:
            return
        selected_index = self._lst.GetFirstSelected()
        if selected_index < 0:
            return
        original_value_row = self._value_rows[selected_index]
        event = KeyValueSettingEditEvent(
            all_value_rows=self._value_rows,
            is_add=False,
            editing_index=selected_index,
            original_value_row=original_value_row
        )
        result = self.showSubWindow(self.config.editor_window_class, "Edit", event, modal=True)
        if result.code != wx.ID_OK:
            return
        new_value_row = result.user_object
        if new_value_row is None:
            return
        for i, key in enumerate(self.config.keys):
            self._lst.SetItem(selected_index, i, new_value_row.get(key.key, ""))
        self._value_rows[selected_index] = new_value_row
        self._lst.Select(selected_index)
        self._lst.Focus(selected_index)
        self._lst.SetFocus()

    def _handleDelete(self, event):
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
