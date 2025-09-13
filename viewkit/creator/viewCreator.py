# View Creator
# Copyright (C) 2019-2021 yamahubuki <itiro.ishino@gmail.com>
# Copyright (C) 2019-2020 Hiroki Fujii <hfujii@hisystron.com>

import ctypes
import importlib.resources
import os
import pywintypes
import win32api
import _winxptheme
import wx
import wx.lib.scrolledpanel


from .objects import button
from .objects import combobox
from .objects import checkbox
from .objects import radiobox
from .objects import radiobutton
from .objects import listbox
from .objects import treectrl
from .objects import normal_listctrl
from .objects import virtual_listctrl
from .objects import notebook
from .objects import textctrl
from .objects import spinctrl
from .objects import slider
from .objects import static_bitmap
from .objects import clear_slider
from .objects import grid_bag_sizer

dll_path = importlib.resources.files("viewkit").joinpath("viewHelper.dll")
viewHelper = ctypes.cdll.LoadLibrary(str(dll_path))

NORMAL = 0
BUTTON_COLOUR = 1
SKIP_COLOUR = 2

GridSizer = -1
FlexGridSizer = -2
GridBagSizer = -3

# テーマカラー
MODE_WHITE = 0
MODE_DARK = 1

# テキストの折り返し
MODE_NOWRAP = 0
MODE_WRAPPING = 2


class ViewCreator():
    def __init__(
            self,
            mode: int,
            font: wx.Font,
            parent,
            parent_sizer=None,
            orient=wx.HORIZONTAL,
            space=0,
            label="",
            style=0,
            proportion=0,
            margin=20):
        # wxオブジェクトを辞書に格納
        self.winObject = {
            "button": button.button,
            "staticText": wx.StaticText,
            "comboBox": combobox.comboBox,
            "checkBox": checkbox.checkBox,
            "radioBox": radiobox.radioBox,
            "radioButton": radiobutton.radioButton,
            "listBox": listbox.listBox,
            "treeCtrl": treectrl.treeCtrl,
            "listCtrl": normal_listctrl.listCtrl,
            "virtualListCtrl": virtual_listctrl.virtualListCtrl,
            "notebook": notebook.notebook,
            "textCtrl": textctrl.textCtrl,
            "gauge": wx.Gauge,
            "spinCtrl": spinctrl.spinCtrl,
            "slider": slider.slider,
            "clear_slider": clear_slider.clearSlider,
            "static_bitmap": static_bitmap.staticBitmap,
        }

        # 表示モード
        self.mode = mode

        self.font = font

        # 親ウィンドウ
        if type(parent) in [wx.Panel, wx.lib.scrolledpanel.ScrolledPanel]:
            self.parent = parent
            self._setFace(parent)
        elif isinstance(parent, wx.Notebook) or isinstance(parent, wx.Choicebook) or isinstance(parent, wx.Listbook):
            self._setFace(parent)
            self.parent = makePanel(parent)
            self._setFace(self.parent)
            parent.InsertPage(parent.GetPageCount(), self.parent, label)
            label = ""
            parent_sizer = self.BoxSizer(parent_sizer, wx.VERTICAL, "", margin, style, proportion)
        else:
            raise ValueError("ViewCreatorの親はパネルまたはブックコントロールである必要があります。これは %s です。" % type(parent))

        # サイザー作成
        if orient == FlexGridSizer:
            self.sizer = self.FlexGridSizer(parent_sizer, margin, style, label)
        elif orient == GridSizer:
            self.sizer = self.GridSizer(parent_sizer, margin, style, label)
        elif orient == GridBagSizer:
            self.sizer = self.GridBagSizer(parent_sizer, margin, style, label)
        else:
            self.sizer = self.BoxSizer(parent_sizer, orient, label, margin, style, proportion)

        self.space = space

    # BoxSizerの下にスペースを挿入
    def AddSpace(self, space=-2):
        if self.sizer.__class__ == wx.BoxSizer or self.sizer.__class__ == wx.StaticBoxSizer:
            if space == -2:
                space = self.space
            elif space == -1:
                return self.sizer.AddStretchSpacer(1)
            return self.sizer.AddSpacer(space)

    # グリッド系Sizerに空セルを挿入
    def AddEmptyCell(self):
        if self.sizer.__class__ == wx.BoxSizer or self.sizer.__class__ == wx.StaticBoxSizer:
            return
        return self.sizer.Add((0, 0))

    # parentで指定したsizerの下に、新たなBoxSizerを設置
    def BoxSizer(self, parent, orient=wx.VERTICAL, label="", space=0, style=0, proportion=0):
        if label == "":
            sizer = wx.BoxSizer(orient)
        else:
            sizer = wx.StaticBoxSizer(orient, self.parent, label)
            self._setFace(sizer.GetStaticBox())
        if type(parent) in (wx.Panel, wx.Window):
            parent.SetSizer(sizer)
        elif (parent is None):
            self.parent.SetSizer(sizer)
        else:
            Add(parent, sizer, proportion, style, space)
        return sizer

    def GridSizer(self, parent, space=0, style=0, x=2):
        if type(x) != int:
            x = 2
        sizer = wx.GridSizer(x, space, space)
        if type(parent) in (wx.Panel, wx.Window):
            parent.SetSizer(sizer)
        elif (parent is None):
            self.parent.SetSizer(sizer)
        else:
            parent.Add(sizer, 0, wx.ALL | style, space)
        return sizer

    def FlexGridSizer(self, parent, space=0, style=0, x=2):
        if type(x) != int:
            x = 2
        sizer = wx.FlexGridSizer(x, space, space)
        if type(parent) in (wx.Panel, wx.Window):
            parent.SetSizer(sizer)
        elif (parent is None):
            self.parent.SetSizer(sizer)
        else:
            parent.Add(sizer, 0, wx.ALL | style, space)
        return sizer

    def GridBagSizer(self, parent, space=0, style=0, x=2):
        if type(x) != int:
            x = 2
        sizer = grid_bag_sizer.GridBagSizer(x, space, space)
        if type(parent) in (wx.Panel, wx.Window):
            parent.SetSizer(sizer)
        elif (parent is None):
            self.parent.SetSizer(sizer)
        else:
            parent.Add(sizer, 0, wx.ALL | style, space)
        return sizer

    def button(self, text, event=None, style=wx.BORDER_RAISED, size=(-1, -1), sizer_flag=wx.ALL, proportion=0, margin=5, enable_tab_focus=True):
        hButton = self.winObject["button"](self.parent, wx.ID_ANY, label=text, name=text, style=style, size=size, enable_tab_focus=enable_tab_focus)
        hButton.Bind(wx.EVT_BUTTON, event)
        self._setFace(hButton, mode=BUTTON_COLOUR)
        Add(self.sizer, hButton, proportion, sizer_flag, margin)
        self.AddSpace()
        return hButton

    def okbutton(self, text, event=None, style=wx.BORDER_RAISED, size=(-1, -1),
                 sizer_flag=wx.ALIGN_BOTTOM | wx.ALIGN_RIGHT | wx.ALL, proportion=1, margin=5):
        hButton = self.winObject["button"](self.parent, wx.ID_OK, label=text, name=text, style=style, size=size)
        hButton.Bind(wx.EVT_BUTTON, event)
        self._setFace(hButton, mode=BUTTON_COLOUR)
        Add(self.sizer, hButton, proportion, sizer_flag, margin)
        hButton.SetDefault()
        self.AddSpace()
        return hButton

    def cancelbutton(self, text, event=None, style=wx.BORDER_RAISED, size=(-1, -1),
                     sizer_flag=wx.ALIGN_BOTTOM | wx.ALIGN_RIGHT | wx.ALL, proportion=1, margin=5):
        hButton = self.winObject["button"](self.parent, wx.ID_CANCEL, label=text, name=text, style=style, size=size)
        hButton.Bind(wx.EVT_BUTTON, event)
        self._setFace(hButton, mode=BUTTON_COLOUR)
        Add(self.sizer, hButton, proportion, sizer_flag, margin)
        self.AddSpace()
        self._setCloseable(hButton)
        return hButton

    def closebutton(self, text, event=None, style=wx.BORDER_RAISED, size=(-1, -1),
                    sizer_flag=wx.ALIGN_BOTTOM | wx.ALIGN_RIGHT | wx.ALL, proportion=1, margin=5):
        hButton = self.winObject["button"](self.parent, wx.ID_OK, label=text, name=text, style=style, size=size)
        hButton.Bind(wx.EVT_BUTTON, event)
        self._setFace(hButton, mode=BUTTON_COLOUR)
        Add(self.sizer, hButton, proportion, sizer_flag, margin)
        hButton.SetDefault()
        self.AddSpace()
        self._setCloseable(hButton)
        return hButton

    def _setCloseable(self, btn):
        gp = self.parent
        while (gp is not None):
            gp = gp.GetParent()
            if isinstance(gp, wx._core.Dialog):
                gp.EnableCloseButton(True)
                gp.SetWindowStyle(gp.GetWindowStyle() | wx.CLOSE_BOX)
                gp.SetEscapeId(btn.GetId())
                return

    def staticText(self, text, style=0, x=-1, sizer_flag=wx.ALIGN_CENTER_VERTICAL, proportion=0, margin=5):
        hStatic = self.winObject["staticText"](self.parent, wx.ID_ANY, label=text, name=text, size=(x, -1), style=style)
        self._setFace(hStatic)
        Add(self.sizer, hStatic, proportion, sizer_flag, margin)
        return hStatic

    def combobox(
            self,
            text,
            selection,
            event=None,
            state=-1,
            style=wx.CB_READONLY,
            x=-1,
            sizer_flag=wx.ALL | wx.ALIGN_CENTER_VERTICAL,
            proportion=0,
            margin=5,
            text_layout=wx.DEFAULT,
            enable_tab_focus=True):
        hStaticText, sizer, parent = self._addDescriptionText(text, text_layout, sizer_flag, proportion, margin)

        v = ""
        if state >= 0:
            v = selection[state]
        hCombo = self.winObject["comboBox"](parent, wx.ID_ANY, value=v, choices=selection, style=wx.BORDER_RAISED |
                                            style, name=text, size=(x, -1), enable_tab_focus=enable_tab_focus)
        hCombo.Bind(wx.EVT_TEXT, event)
        self._setFace(hCombo)
        Add(sizer, hCombo, proportion, sizer_flag, margin)
        self.AddSpace()
        return hCombo, hStaticText

    def comboEdit(
            self,
            text,
            selection,
            event=None,
            default_value="",
            style=wx.CB_DROPDOWN,
            x=-1,
            sizer_flag=wx.ALL | wx.ALIGN_CENTER_VERTICAL,
            proportion=0,
            margin=5,
            text_layout=wx.DEFAULT,
            enable_tab_focus=True):
        hStaticText, sizer, parent = self._addDescriptionText(text, text_layout, sizer_flag, proportion, margin)

        hCombo = self.winObject["comboBox"](parent, wx.ID_ANY, value=default_value, choices=selection,
                                            style=wx.BORDER_RAISED | style, name=text, size=(x, -1), enable_tab_focus=enable_tab_focus)
        hCombo.Bind(wx.EVT_TEXT, event)
        if default_value in selection:
            hCombo.SetSelection(selection.index(default_value))
        self._setFace(hCombo)
        if x == -1:  # 幅を拡張
            Add(sizer, hCombo, proportion, sizer_flag, margin, expand_flag=wx.HORIZONTAL)
        else:
            Add(sizer, hCombo, proportion, sizer_flag, margin)
        self.AddSpace()
        return hCombo, hStaticText

    def checkbox(
            self,
            text,
            event=None,
            state=False,
            style=0,
            x=-1,
            sizer_flag=wx.ALIGN_CENTER_VERTICAL,
            proportion=0,
            margin=5,
            enable_tab_focus=True):
        hPanel = wx.Panel(self.parent, wx.ID_ANY)
        self._setFace(hPanel, mode=SKIP_COLOUR)
        hSizer = self.BoxSizer(hPanel, self.getParentOrientation())

        if (isinstance(text, str)):  # 単純に一つを作成
            hCheckBox = self.winObject["checkBox"](
                hPanel, wx.ID_ANY, label=text, name=text, size=(
                    x, -1), style=style, enable_tab_focus=enable_tab_focus)
            hCheckBox.SetValue(state)
            hCheckBox.Bind(wx.EVT_CHECKBOX, event)
            self._setFace(hCheckBox, mode=SKIP_COLOUR)
            hSizer.Add(hCheckBox)
            Add(self.sizer, hPanel, proportion, sizer_flag, margin)
            if self.mode & MODE_DARK == MODE_DARK:
                viewHelper.ScCheckbox(hPanel.GetHandle())
            self.AddSpace()
            return hCheckBox
        elif (isinstance(text, list)):  # 複数同時作成
            hCheckBoxes = []
            for s in text:
                hCheckBox = self.winObject["checkBox"](
                    hPanel, wx.ID_ANY, label=s, name=s, size=(
                        x, -1), style=style, enable_tab_focus=enable_tab_focus)
                hCheckBox.SetValue(state)
                hCheckBox.Bind(wx.EVT_CHECKBOX, event)
                self._setFace(hCheckBox, mode=SKIP_COLOUR)
                hSizer.Add(hCheckBox)
                hCheckBoxes.append(hCheckBox)
            Add(self.sizer, hPanel, proportion, sizer_flag, margin)
            if self.mode & MODE_DARK == MODE_DARK:
                viewHelper.ScCheckbox(hPanel.GetHandle())
            self.AddSpace()
            return hCheckBoxes
        else:
            raise ValueError("ViewCreatorはCheckboxの作成に際し正しくない型の値を受け取りました。")

    # 3stateチェックボックス
    def checkbox3(
            self,
            text,
            event=None,
            state=None,
            style=0,
            x=-1,
            sizer_flag=wx.ALIGN_CENTER_VERTICAL,
            proportion=0,
            margin=0,
            enable_tab_focus=True):
        hPanel = wx.Panel(self.parent, wx.ID_ANY)
        self._setFace(hPanel, mode=SKIP_COLOUR)
        hSizer = self.BoxSizer(hPanel, self.getParentOrientation())

        if (isinstance(text, str)):  # 単純に一つを作成
            if (state is None):
                state = wx.CHK_UNCHECKED
            hCheckBox = self.winObject["checkBox"](
                hPanel, wx.ID_ANY, label=text, name=text, style=wx.CHK_3STATE | style, size=(
                    x, 0), enable_tab_focus=enable_tab_focus)
            hCheckBox.Set3StateValue(state)
            if state == wx.CHK_UNDETERMINED:
                hCheckBox.SetWindowStyleFlag(wx.CHK_ALLOW_3RD_STATE_FOR_USER)
            hCheckBox.Bind(wx.EVT_CHECKBOX, event)
            self._setFace(hCheckBox, mode=SKIP_COLOUR)
            hSizer.Add(hCheckBox)
            self.AddSpace()
            Add(self.sizer, hPanel, proportion, sizer_flag, margin)
            if self.mode & MODE_DARK == MODE_DARK:
                viewHelper.ScCheckbox(hPanel.GetHandle())
            self.AddSpace()
            return hCheckBox
        elif (isinstance(text, list)):  # 複数同時作成
            hCheckBoxes = []
            for i, s in enumerate(text):
                if (state is None):
                    hCheckBox = self.winObject["checkBox"](
                        hPanel, wx.ID_ANY, label=s, name=s, style=wx.CHK_3STATE | style, size=(
                            x, 0), enable_tab_focus=enable_tab_focus)
                elif (state[i] == wx.CHK_UNDETERMINED):
                    hCheckBox = self.winObject["checkBox"](
                        hPanel,
                        wx.ID_ANY,
                        label=s,
                        name=s,
                        style=wx.CHK_ALLOW_3RD_STATE_FOR_USER | wx.CHK_3STATE | style,
                        size=(
                            x,
                            0),
                        enable_tab_focus=enable_tab_focus)
                    hCheckBox.Set3StateValue(state[i])
                else:
                    hCheckBox = self.winObject["checkBox"](
                        hPanel, wx.ID_ANY, label=s, name=s, style=wx.CHK_3STATE | style, size=(
                            x, 0), enable_tab_focus=enable_tab_focus)
                    hCheckBox.Set3StateValue(state[i])
                hCheckBox.Bind(wx.EVT_CHECKBOX, event)
                self._setFace(hCheckBox, mode=SKIP_COLOUR)
                hSizer.Add(hCheckBox)
                hCheckBoxes.append(hCheckBox)
            Add(self.sizer, hPanel, proportion, sizer_flag, margin)
            if self.mode & MODE_DARK == MODE_DARK:
                viewHelper.ScCheckbox(hPanel.GetHandle())
            self.AddSpace()
            return hCheckBoxes
        else:
            raise ValueError("ViewCreatorはCheckboxの作成に際し正しくない型の値を受け取りました。")

    def radiobox(
            self,
            text,
            items,
            event=None,
            dimension=0,
            orient=wx.VERTICAL,
            style=0,
            x=-1,
            sizer_flag=wx.ALIGN_CENTER_VERTICAL | wx.ALL,
            proportion=0,
            margin=5,
            enable_tab_focus=True):
        if orient == wx.VERTICAL:
            style = wx.RA_SPECIFY_COLS | style
        else:
            style = wx.RA_SPECIFY_ROWS | style
        hRadioBox = self.winObject["radioBox"](
            self.parent, label=text, name=text, choices=items, majorDimension=dimension, style=style, size=(
                x, -1), enable_tab_focus=enable_tab_focus)
        hRadioBox.Bind(wx.EVT_RADIOBOX, event)
        self._setFace(hRadioBox)

        # ラジオボタンのウィンドウハンドルを使ってテーマを無効に変更する
        ptr = viewHelper.findRadioButtons(self.parent.GetHandle())
        s = ctypes.c_char_p(ptr).value.decode("UTF-8").split(",")
        for elem in s:
            _winxptheme.SetWindowTheme(int(elem), "", "")
        viewHelper.releasePtr(ptr)

        Add(self.sizer, hRadioBox, proportion, sizer_flag, margin)
        self.AddSpace()
        return hRadioBox

    def radio(self, text, event=None, state=False, style=0, x=-1, sizer_flag=wx.ALIGN_CENTER_VERTICAL, proportion=0, margin=5, enable_tab_focus=True):
        hPanel = wx.Panel(self.parent, wx.ID_ANY)
        self._setFace(hPanel, mode=SKIP_COLOUR)
        hSizer = self.BoxSizer(hPanel, self.getParentOrientation())

        if type(text) == str:
            hRadio = self.winObject["radioButton"](hPanel, id=wx.ID_ANY, label=text, style=style, name=text, enable_tab_focus=enable_tab_focus)
            hRadio.SetValue(state)
            hRadio.Bind(wx.EVT_RADIOBUTTON, event)
            self._setFace(hRadio, mode=SKIP_COLOUR)
            Add(self.sizer, hRadio)
            Add(self.sizer, hPanel, proportion, sizer_flag, margin)
            self.AddSpace()

            if self.mode & MODE_DARK == MODE_DARK:
                viewHelper.ScRadioButton(hPanel.GetHandle())

            return hRadio
        elif type(text) in (list, tuple):
            radios = []
            for s in text:
                if len(radios) == 0:  # 最初の１つのみ追加のスタイルが必要
                    hRadio = self.winObject["radioButton"](hPanel, id=wx.ID_ANY, label=s, style=wx.RB_GROUP |
                                                           style, name=s, enable_tab_focus=enable_tab_focus)
                else:
                    hRadio = self.winObject["radioButton"](hPanel, id=wx.ID_ANY, label=s, style=style, name=s, enable_tab_focus=enable_tab_focus)
                hRadio.Bind(wx.EVT_RADIOBUTTON, event)
                self._setFace(hRadio, mode=SKIP_COLOUR)
                Add(hSizer, hRadio)
                radios.append(hRadio)
            if type(state) == int:
                radios[state].SetValue(True)
            Add(self.sizer, hPanel, proportion, sizer_flag, margin)
            self.AddSpace()

            if self.mode & MODE_DARK == MODE_DARK:
                viewHelper.ScRadioButton(hPanel.GetHandle())

            return radios
        else:
            raise ValueError("ViewCreatorはRadioの作成に際し不正な型ののtextパラメータを受け取りました。")

    def listbox(self, text, choices=[], event=None, state=-1, style=0, size=(-1, -1),
                sizer_flag=wx.ALL, proportion=0, margin=5, text_layout=wx.DEFAULT, enable_tab_focus=True):
        hStaticText, sizer, parent = self._addDescriptionText(text, text_layout, sizer_flag, proportion, margin)

        hListBox = self.winObject["listBox"](parent, wx.ID_ANY, name=text, choices=choices, size=size, style=style, enable_tab_focus=enable_tab_focus)
        hListBox.Bind(wx.EVT_LISTBOX, event)
        hListBox.SetSelection(state)
        self._setFace(hListBox)
        Add(sizer, hListBox, proportion, sizer_flag, margin)
        self.AddSpace()
        return hListBox, hStaticText

    def treeCtrl(self, text, event=None, style=wx.TR_FULL_ROW_HIGHLIGHT | wx.TR_NO_BUTTONS, size=(200, 200),
                 sizer_flag=wx.ALL, proportion=0, margin=5, text_layout=wx.DEFAULT, enable_tab_focus=True):
        hStaticText, sizer, parent = self._addDescriptionText(text, text_layout, sizer_flag, proportion, margin)

        hTreeCtrl = self.winObject["treeCtrl"](parent, wx.ID_ANY, style=style | wx.BORDER_RAISED, size=size, enable_tab_focus=enable_tab_focus)
        hTreeCtrl.Bind(wx.EVT_TREE_SEL_CHANGED, event)
        self._setFace(hTreeCtrl)
        Add(sizer, hTreeCtrl, proportion, sizer_flag, margin)
        self.AddSpace()
        return hTreeCtrl, hStaticText

    def listCtrl(
            self,
            text,
            event=None,
            style=wx.LC_SINGLE_SEL | wx.LC_REPORT,
            size=(
                200,
                200),
            sizer_flag=wx.ALL,
            proportion=0,
            margin=5,
            text_layout=wx.DEFAULT,
            enable_tab_focus=True):
        hStaticText, sizer, parent = self._addDescriptionText(text, text_layout, sizer_flag, proportion, margin)

        hListCtrl = self.winObject["listCtrl"](parent, wx.ID_ANY, style=style | wx.BORDER_RAISED, size=size, enable_tab_focus=enable_tab_focus)
        hListCtrl.Bind(wx.EVT_LIST_ITEM_FOCUSED, event)
        self._setFace(hListCtrl)
        self._setFace(hListCtrl.GetMainWindow())
        try:
            _winxptheme.SetWindowTheme(win32api.SendMessage(hListCtrl.GetHandle(), 0x101F, 0, 0), "", "")  # ヘッダーのウィンドウテーマを引っぺがす
        except pywintypes.error:
            pass
        Add(sizer, hListCtrl, proportion, sizer_flag, margin)
        self.AddSpace()
        return hListCtrl, hStaticText

    def virtualListCtrl(
            self,
            text,
            event=None,
            style=wx.LC_SINGLE_SEL | wx.LC_REPORT,
            size=(
                200,
                200),
            sizer_flag=wx.ALL,
            proportion=0,
            margin=5,
            text_layout=wx.DEFAULT,
            enable_tab_focus=True):
        hStaticText, sizer, parent = self._addDescriptionText(text, text_layout, sizer_flag, proportion, margin)

        hListCtrl = self.winObject["virtualListCtrl"](parent, wx.ID_ANY, style=style | wx.BORDER_RAISED, size=size, enable_tab_focus=enable_tab_focus)
        hListCtrl.Bind(wx.EVT_LIST_ITEM_FOCUSED, event)
        self._setFace(hListCtrl)
        self._setFace(hListCtrl.GetMainWindow())
        _winxptheme.SetWindowTheme(win32api.SendMessage(hListCtrl.GetHandle(), 0x101F, 0, 0), "", "")  # ヘッダーのウィンドウテーマを引っぺがす
        Add(sizer, hListCtrl, proportion, sizer_flag, margin)
        self.AddSpace()
        return hListCtrl, hStaticText

    def tabCtrl(self, title, event=None, style=wx.NB_NOPAGETHEME, sizer_flag=0, proportion=0, margin=5, enable_tab_focus=True):
        htab = self.winObject["notebook"](self.parent, wx.ID_ANY, name=title, style=style, enable_tab_focus=enable_tab_focus)
        htab.Bind(wx.EVT_NOTEBOOK_PAGE_CHANGED, event)
        self._setFace(htab)
        Add(self.sizer, htab, proportion, sizer_flag, margin, expand_flag=wx.HORIZONTAL)
        self.sizer.Layout()
        return htab

    def inputbox(
            self,
            text,
            event=None,
            default_value="",
            style=wx.BORDER_RAISED,
            x=-1,
            sizer_flag=wx.ALL | wx.ALIGN_CENTER_VERTICAL,
            proportion=0,
            margin=5,
            text_layout=wx.DEFAULT,
            enable_tab_focus=True):
        if self.mode & MODE_WRAPPING == MODE_NOWRAP:
            style |= wx.TE_DONTWRAP
        hStaticText, sizer, parent = self._addDescriptionText(text, text_layout, sizer_flag, proportion, margin)

        hTextCtrl = self.winObject["textCtrl"](parent, wx.ID_ANY, size=(x, -1), name=text, value=default_value,
                                               style=style | wx.BORDER_RAISED, enable_tab_focus=enable_tab_focus)
        hTextCtrl.Bind(wx.EVT_TEXT, event)
        self._setFace(hTextCtrl)
        if x == -1:
            Add(sizer, hTextCtrl, proportion, sizer_flag, margin, expand_flag=wx.HORIZONTAL)
        else:
            Add(sizer, hTextCtrl, proportion, sizer_flag, margin)
        self.AddSpace()
        return hTextCtrl, hStaticText

    def gauge(self, text, max=0, default_value=0, style=wx.GA_HORIZONTAL | wx.GA_SMOOTH | wx.BORDER_RAISED, x=-
              1, sizer_flag=wx.ALL | wx.ALIGN_CENTER_VERTICAL, proportion=0, margin=5, text_layout=wx.DEFAULT):
        hStaticText, sizer, parent = self._addDescriptionText(text, text_layout, sizer_flag, proportion, margin)

        hGauge = self.winObject["gauge"](parent, wx.ID_ANY, size=(x, -1), style=style, name=text,)
        self._setFace(hGauge)
        if x == -1:
            Add(sizer, hGauge, proportion, sizer_flag, margin, expand_flag=wx.HORIZONTAL)
        else:
            Add(sizer, hGauge, proportion, sizer_flag, margin)
        self.AddSpace()
        return hGauge, hStaticText

    def spinCtrl(
            self,
            text,
            min=0,
            max=100,
            event=None,
            default_value=0,
            style=wx.SP_ARROW_KEYS,
            x=-1,
            sizer_flag=wx.ALL | wx.ALIGN_CENTER_VERTICAL,
            proportion=0,
            margin=5,
            text_layout=wx.DEFAULT,
            enable_tab_focus=True):
        hStaticText, sizer, parent = self._addDescriptionText(text, text_layout, sizer_flag, proportion, margin)

        hSpinCtrl = self.winObject["spinCtrl"](parent, wx.ID_ANY, min=min, max=max, initial=default_value,
                                               style=wx.BORDER_RAISED | style, size=(x, -1), enable_tab_focus=enable_tab_focus)
        hSpinCtrl.Bind(wx.EVT_TEXT, event)
        self._setFace(hSpinCtrl)
        Add(sizer, hSpinCtrl, proportion, sizer_flag, margin)
        self.AddSpace()
        return hSpinCtrl, hStaticText

    def slider(
            self,
            text,
            min=0,
            max=100,
            event=None,
            default_value=0,
            style=0,
            x=-1,
            sizer_flag=wx.ALL | wx.ALIGN_CENTER_VERTICAL,
            proportion=0,
            margin=5,
            text_layout=wx.DEFAULT,
            enable_tab_focus=True):
        hStaticText, sizer, parent = self._addDescriptionText(text, text_layout, sizer_flag, proportion, margin)

        hSlider = self.winObject["slider"](parent, wx.ID_ANY, size=(x, -1), value=default_value, minValue=min,
                                           maxValue=max, style=style, enable_tab_focus=enable_tab_focus)
        hSlider.Bind(wx.EVT_SCROLL_CHANGED, event)
        self._setFace(hSlider)
        if x == -1:  # 幅を拡張
            Add(sizer, hSlider, proportion, sizer_flag, margin, expand_flag=wx.HORIZONTAL)
        else:
            Add(sizer, hSlider, proportion, sizer_flag, margin)
        self.AddSpace()
        return hSlider, hStaticText

    def clearSlider(
            self,
            text,
            min=0,
            max=100,
            event=None,
            default_value=0,
            style=0,
            x=-1,
            sizer_flag=wx.ALL | wx.ALIGN_CENTER_VERTICAL,
            proportion=0,
            margin=5,
            text_layout=wx.DEFAULT,
            enable_tab_focus=True):
        hStaticText, sizer, parent = self._addDescriptionText(text, text_layout, sizer_flag, proportion, margin)

        hSlider = self.winObject["clear_slider"](parent, wx.ID_ANY, size=(x, -1), value=default_value,
                                                 minValue=min, maxValue=max, style=style, enable_tab_focus=enable_tab_focus)
        hSlider.SetBackgroundStyle(wx.BG_STYLE_PAINT)
        hSlider.Bind(wx.EVT_SCROLL_CHANGED, event)
        self._setFace(hSlider)
        if x == -1:  # 幅を拡張
            Add(sizer, hSlider, proportion, sizer_flag, margin, expand_flag=wx.HORIZONTAL)
        else:
            Add(sizer, hSlider, proportion, sizer_flag, margin)
        self.AddSpace()
        return hSlider, hStaticText

    def staticBitmap(self, text, bitmap=wx.NullBitmap, style=0, size=(-1, -1), sizer_flag=wx.ALL | wx.ALIGN_CENTER_VERTICAL, proportion=0, margin=5):
        staticBitmap = self.winObject["static_bitmap"](self.parent, wx.ID_ANY, size=size, style=style, name=text)
        self._setFace(staticBitmap)
        Add(self.sizer, staticBitmap, proportion, sizer_flag, margin)
        self.AddSpace()
        return staticBitmap

    def getPanel(self):
        return self.parent

    def getSizer(self):
        return self.sizer

    def getMode(self):
        return self.mode

    def _addDescriptionText(self, text, text_layout, sizer_flag=0, proportion=0, margin=0):
        if text_layout not in (None, wx.HORIZONTAL, wx.VERTICAL, wx.DEFAULT):
            raise ValueError("text_layout must be (None,wx.HORIZONTAL,wx.VIRTICAL,wx.DEFAULT)")
        if type(self.sizer) in (wx.BoxSizer, wx.StaticBoxSizer) and text_layout not in (None, self.sizer.GetOrientation(), wx.DEFAULT):
            panel = makePanel(self.parent)
            if text_layout is not None:
                hStaticText = wx.StaticText(panel, wx.ID_ANY, label=text, name=text)
            else:
                hStaticText = wx.StaticText(panel, wx.ID_ANY, label=text, name=text, size=(0, 0))
            self._setFace(hStaticText)
            sizer = self.BoxSizer(panel, orient=text_layout)
            Add(sizer, hStaticText, 0, wx.ALIGN_CENTER_VERTICAL)
            Add(self.sizer, panel, proportion, sizer_flag, margin)
            return hStaticText, sizer, panel
        elif isinstance(self.sizer, (wx.GridSizer, wx.FlexGridSizer, wx.GridBagSizer)) and text_layout is None:
            hStaticText = wx.StaticText(self.parent, wx.ID_ANY, label=text, name=text, size=(0, 0))
            self._setFace(hStaticText)
            sizer = self.BoxSizer(self.sizer, style=sizer_flag & (wx.ALIGN_LEFT | wx.ALIGN_RIGHT |
                                  wx.ALIGN_CENTER_VERTICAL | wx.ALIGN_TOP | wx.ALIGN_BOTTOM | wx.EXPAND))
            Add(sizer, hStaticText)
            return hStaticText, sizer, self.parent
        else:
            if text_layout is not None:
                hStaticText = wx.StaticText(self.parent, wx.ID_ANY, label=text, name=text)
            else:
                hStaticText = wx.StaticText(self.parent, wx.ID_ANY, label=text, name=text, size=(0, 0))
            self._setFace(hStaticText)
            Add(self.sizer, hStaticText, 0, sizer_flag & (wx.ALIGN_LEFT | wx.ALIGN_RIGHT |
                wx.ALIGN_CENTER_VERTICAL | wx.ALIGN_TOP | wx.ALIGN_BOTTOM | wx.EXPAND))
            return hStaticText, self.sizer, self.parent

    def _setFace(self, target, mode=NORMAL):
        if mode == NORMAL:
            if self.mode & MODE_DARK == MODE_DARK:
                target.SetBackgroundColour("#000000")  # 背景色＝黒
                target.SetForegroundColour("#ffffff")  # 文字色＝白
            else:
                target.SetBackgroundColour("#ffffff")  # 背景色＝白
                target.SetForegroundColour("#000000")  # 文字色＝黒
        elif (mode == BUTTON_COLOUR):
            if self.mode & MODE_DARK == MODE_DARK:
                target.SetBackgroundColour("#444444")  # 背景色＝灰色
                target.SetForegroundColour("#ffffff")  # 文字色＝白
        # end skip
        target.SetThemeEnabled(False)
        _winxptheme.SetWindowTheme(target.GetHandle(), "", "")
        target.SetFont(self.font)

    def getFont(self):
        return self.font

    def getParentOrientation(self, default=wx.VERTICAL):
        if type(self.sizer) in (wx.BoxSizer, wx.StaticBoxSizer):
            return self.sizer.GetOrientation()
        else:
            return default

    def SetItemSpan(self, col, row=1):
        assert (isinstance(self.sizer, wx.GridBagSizer))
        self.sizer.SetItemSpan(wx.GBSpan(row, col))

# parentで指定したsizerの下に、新たなBoxSizerを設置


def BoxSizer(parent, orient=wx.VERTICAL, flg=0, border=0):
    sizer = wx.BoxSizer(orient)
    if (parent is not None):
        parent.Add(sizer, 0, flg, border)
    return sizer


def Add(sizer, window, proportion=0, flag=0, border=0, expand_flag=None):
    if isinstance(sizer, wx.BoxSizer):
        if sizer.Orientation == wx.VERTICAL:
            for i in (wx.ALIGN_TOP, wx.ALIGN_BOTTOM, wx.ALIGN_CENTER_VERTICAL):
                if flag & i == i:
                    flag -= i
        else:
            for i in (wx.ALIGN_LEFT, wx.ALIGN_RIGHT, wx.ALIGN_CENTER_HORIZONTAL, wx.ALIGN_CENTER):
                if flag & i == i:
                    flag -= i
    if expand_flag == wx.HORIZONTAL:  # 幅を拡張
        if type(sizer) in (wx.BoxSizer, wx.StaticBoxSizer) and sizer.GetOrientation() == wx.VERTICAL:
            sizer.Add(window, proportion, flag | wx.EXPAND, border)
        else:
            sizer.Add(window, 1, flag, border)
    elif isinstance(sizer, wx.GridBagSizer):
        sizer.Add(window, flag=flag, border=border)
    else:
        sizer.Add(window, proportion, flag, border)

# parentで指定されたフレームにパネルを設置する


def makePanel(parent):
    hPanel = wx.Panel(parent, wx.ID_ANY, size=(-1, -1))
    return hPanel
