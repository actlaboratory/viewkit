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
    def __init__(self, mode, parent, parentSizer=None, orient=wx.HORIZONTAL, space=0, label="", style=0, proportion=0, margin=20):
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
        if type(mode) == int:
            self.mode = mode
        elif type(mode) == str:
            if mode.lower() == "dark":
                self.mode = MODE_DARK
            else:
                self.mode = MODE_WHITE
        else:
            raise ValueError("モードは整数値またはwhiteかdarkの文字列で指定してください。")

        # 初期設定フォント
        # todo fontManager

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
            parentSizer = self.BoxSizer(parentSizer, wx.VERTICAL, "", margin, style, proportion)
        else:
            raise ValueError("ViewCreatorの親はパネルまたはブックコントロールである必要があります。")

        # サイザー作成
        if orient == FlexGridSizer:
            self.sizer = self.FlexGridSizer(parentSizer, margin, style, label)
        elif orient == GridSizer:
            self.sizer = self.GridSizer(parentSizer, margin, style, label)
        elif orient == GridBagSizer:
            self.sizer = self.GridBagSizer(parentSizer, margin, style, label)
        else:
            self.sizer = self.BoxSizer(parentSizer, orient, label, margin, style, proportion)

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

    def button(self, text, event=None, style=wx.BORDER_RAISED, size=(-1, -1), sizerFlag=wx.ALL, proportion=0, margin=5, enableTabFocus=True):
        hButton = self.winObject["button"](self.parent, wx.ID_ANY, label=text, name=text, style=style, size=size, enableTabFocus=enableTabFocus)
        hButton.Bind(wx.EVT_BUTTON, event)
        self._setFace(hButton, mode=BUTTON_COLOUR)
        Add(self.sizer, hButton, proportion, sizerFlag, margin)
        self.AddSpace()
        return hButton

    def okbutton(self, text, event=None, style=wx.BORDER_RAISED, size=(-1, -1),
                 sizerFlag=wx.ALIGN_BOTTOM | wx.ALIGN_RIGHT | wx.ALL, proportion=1, margin=5):
        hButton = self.winObject["button"](self.parent, wx.ID_OK, label=text, name=text, style=style, size=size)
        hButton.Bind(wx.EVT_BUTTON, event)
        self._setFace(hButton, mode=BUTTON_COLOUR)
        Add(self.sizer, hButton, proportion, sizerFlag, margin)
        hButton.SetDefault()
        self.AddSpace()
        return hButton

    def cancelbutton(self, text, event=None, style=wx.BORDER_RAISED, size=(-1, -1),
                     sizerFlag=wx.ALIGN_BOTTOM | wx.ALIGN_RIGHT | wx.ALL, proportion=1, margin=5):
        hButton = self.winObject["button"](self.parent, wx.ID_CANCEL, label=text, name=text, style=style, size=size)
        hButton.Bind(wx.EVT_BUTTON, event)
        self._setFace(hButton, mode=BUTTON_COLOUR)
        Add(self.sizer, hButton, proportion, sizerFlag, margin)
        self.AddSpace()
        self._setCloseable(hButton)
        return hButton

    def closebutton(self, text, event=None, style=wx.BORDER_RAISED, size=(-1, -1),
                    sizerFlag=wx.ALIGN_BOTTOM | wx.ALIGN_RIGHT | wx.ALL, proportion=1, margin=5):
        hButton = self.winObject["button"](self.parent, wx.ID_OK, label=text, name=text, style=style, size=size)
        hButton.Bind(wx.EVT_BUTTON, event)
        self._setFace(hButton, mode=BUTTON_COLOUR)
        Add(self.sizer, hButton, proportion, sizerFlag, margin)
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

    def staticText(self, text, style=0, x=-1, sizerFlag=wx.ALIGN_CENTER_VERTICAL, proportion=0, margin=5):
        hStatic = self.winObject["staticText"](self.parent, wx.ID_ANY, label=text, name=text, size=(x, -1), style=style)
        self._setFace(hStatic)
        Add(self.sizer, hStatic, proportion, sizerFlag, margin)
        return hStatic

    def combobox(
            self,
            text,
            selection,
            event=None,
            state=-1,
            style=wx.CB_READONLY,
            x=-1,
            sizerFlag=wx.ALL | wx.ALIGN_CENTER_VERTICAL,
            proportion=0,
            margin=5,
            textLayout=wx.DEFAULT,
            enableTabFocus=True):
        hStaticText, sizer, parent = self._addDescriptionText(text, textLayout, sizerFlag, proportion, margin)

        v = ""
        if state >= 0:
            v = selection[state]
        hCombo = self.winObject["comboBox"](parent, wx.ID_ANY, value=v, choices=selection, style=wx.BORDER_RAISED |
                                            style, name=text, size=(x, -1), enableTabFocus=enableTabFocus)
        hCombo.Bind(wx.EVT_TEXT, event)
        self._setFace(hCombo)
        Add(sizer, hCombo, proportion, sizerFlag, margin)
        self.AddSpace()
        return hCombo, hStaticText

    def comboEdit(
            self,
            text,
            selection,
            event=None,
            defaultValue="",
            style=wx.CB_DROPDOWN,
            x=-1,
            sizerFlag=wx.ALL | wx.ALIGN_CENTER_VERTICAL,
            proportion=0,
            margin=5,
            textLayout=wx.DEFAULT,
            enableTabFocus=True):
        hStaticText, sizer, parent = self._addDescriptionText(text, textLayout, sizerFlag, proportion, margin)

        hCombo = self.winObject["comboBox"](parent, wx.ID_ANY, value=defaultValue, choices=selection,
                                            style=wx.BORDER_RAISED | style, name=text, size=(x, -1), enableTabFocus=enableTabFocus)
        hCombo.Bind(wx.EVT_TEXT, event)
        if defaultValue in selection:
            hCombo.SetSelection(selection.index(defaultValue))
        self._setFace(hCombo)
        if x == -1:  # 幅を拡張
            Add(sizer, hCombo, proportion, sizerFlag, margin, expandFlag=wx.HORIZONTAL)
        else:
            Add(sizer, hCombo, proportion, sizerFlag, margin)
        self.AddSpace()
        return hCombo, hStaticText

    def checkbox(self, text, event=None, state=False, style=0, x=-1, sizerFlag=wx.ALIGN_CENTER_VERTICAL, proportion=0, margin=5, enableTabFocus=True):
        hPanel = wx.Panel(self.parent, wx.ID_ANY)
        self._setFace(hPanel, mode=SKIP_COLOUR)
        hSizer = self.BoxSizer(hPanel, self.getParentOrientation())

        if (isinstance(text, str)):  # 単純に一つを作成
            hCheckBox = self.winObject["checkBox"](hPanel, wx.ID_ANY, label=text, name=text, size=(x, -1), style=style, enableTabFocus=enableTabFocus)
            hCheckBox.SetValue(state)
            hCheckBox.Bind(wx.EVT_CHECKBOX, event)
            self._setFace(hCheckBox, mode=SKIP_COLOUR)
            hSizer.Add(hCheckBox)
            Add(self.sizer, hPanel, proportion, sizerFlag, margin)
            if self.mode & MODE_DARK == MODE_DARK:
                viewHelper.ScCheckbox(hPanel.GetHandle())
            self.AddSpace()
            return hCheckBox
        elif (isinstance(text, list)):  # 複数同時作成
            hCheckBoxes = []
            for s in text:
                hCheckBox = self.winObject["checkBox"](hPanel, wx.ID_ANY, label=s, name=s, size=(x, -1), style=style, enableTabFocus=enableTabFocus)
                hCheckBox.SetValue(state)
                hCheckBox.Bind(wx.EVT_CHECKBOX, event)
                self._setFace(hCheckBox, mode=SKIP_COLOUR)
                hSizer.Add(hCheckBox)
                hCheckBoxes.append(hCheckBox)
            Add(self.sizer, hPanel, proportion, sizerFlag, margin)
            if self.mode & MODE_DARK == MODE_DARK:
                viewHelper.ScCheckbox(hPanel.GetHandle())
            self.AddSpace()
            return hCheckBoxes
        else:
            raise ValueError("ViewCreatorはCheckboxの作成に際し正しくない型の値を受け取りました。")

    # 3stateチェックボックス
    def checkbox3(self, text, event=None, state=None, style=0, x=-1, sizerFlag=wx.ALIGN_CENTER_VERTICAL, proportion=0, margin=0, enableTabFocus=True):
        hPanel = wx.Panel(self.parent, wx.ID_ANY)
        self._setFace(hPanel, mode=SKIP_COLOUR)
        hSizer = self.BoxSizer(hPanel, self.getParentOrientation())

        if (isinstance(text, str)):  # 単純に一つを作成
            if (state is None):
                state = wx.CHK_UNCHECKED
            hCheckBox = self.winObject["checkBox"](
                hPanel, wx.ID_ANY, label=text, name=text, style=wx.CHK_3STATE | style, size=(
                    x, 0), enableTabFocus=enableTabFocus)
            hCheckBox.Set3StateValue(state)
            if state == wx.CHK_UNDETERMINED:
                hCheckBox.SetWindowStyleFlag(wx.CHK_ALLOW_3RD_STATE_FOR_USER)
            hCheckBox.Bind(wx.EVT_CHECKBOX, event)
            self._setFace(hCheckBox, mode=SKIP_COLOUR)
            hSizer.Add(hCheckBox)
            self.AddSpace()
            Add(self.sizer, hPanel, proportion, sizerFlag, margin)
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
                            x, 0), enableTabFocus=enableTabFocus)
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
                        enableTabFocus=enableTabFocus)
                    hCheckBox.Set3StateValue(state[i])
                else:
                    hCheckBox = self.winObject["checkBox"](
                        hPanel, wx.ID_ANY, label=s, name=s, style=wx.CHK_3STATE | style, size=(
                            x, 0), enableTabFocus=enableTabFocus)
                    hCheckBox.Set3StateValue(state[i])
                hCheckBox.Bind(wx.EVT_CHECKBOX, event)
                self._setFace(hCheckBox, mode=SKIP_COLOUR)
                hSizer.Add(hCheckBox)
                hCheckBoxes.append(hCheckBox)
            Add(self.sizer, hPanel, proportion, sizerFlag, margin)
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
            sizerFlag=wx.ALIGN_CENTER_VERTICAL | wx.ALL,
            proportion=0,
            margin=5,
            enableTabFocus=True):
        if orient == wx.VERTICAL:
            style = wx.RA_SPECIFY_COLS | style
        else:
            style = wx.RA_SPECIFY_ROWS | style
        hRadioBox = self.winObject["radioBox"](
            self.parent, label=text, name=text, choices=items, majorDimension=dimension, style=style, size=(
                x, -1), enableTabFocus=enableTabFocus)
        hRadioBox.Bind(wx.EVT_RADIOBOX, event)
        self._setFace(hRadioBox)

        # ラジオボタンのウィンドウハンドルを使ってテーマを無効に変更する
        ptr = viewHelper.findRadioButtons(self.parent.GetHandle())
        s = ctypes.c_char_p(ptr).value.decode("UTF-8").split(",")
        for elem in s:
            _winxptheme.SetWindowTheme(int(elem), "", "")
        viewHelper.releasePtr(ptr)

        Add(self.sizer, hRadioBox, proportion, sizerFlag, margin)
        self.AddSpace()
        return hRadioBox

    def radio(self, text, event=None, state=False, style=0, x=-1, sizerFlag=wx.ALIGN_CENTER_VERTICAL, proportion=0, margin=5, enableTabFocus=True):
        hPanel = wx.Panel(self.parent, wx.ID_ANY)
        self._setFace(hPanel, mode=SKIP_COLOUR)
        hSizer = self.BoxSizer(hPanel, self.getParentOrientation())

        if type(text) == str:
            hRadio = self.winObject["radioButton"](hPanel, id=wx.ID_ANY, label=text, style=style, name=text, enableTabFocus=enableTabFocus)
            hRadio.SetValue(state)
            hRadio.Bind(wx.EVT_RADIOBUTTON, event)
            self._setFace(hRadio, mode=SKIP_COLOUR)
            Add(self.sizer, hRadio)
            Add(self.sizer, hPanel, proportion, sizerFlag, margin)
            self.AddSpace()

            if self.mode & MODE_DARK == MODE_DARK:
                viewHelper.ScRadioButton(hPanel.GetHandle())

            return hRadio
        elif type(text) in (list, tuple):
            radios = []
            for s in text:
                if len(radios) == 0:  # 最初の１つのみ追加のスタイルが必要
                    hRadio = self.winObject["radioButton"](hPanel, id=wx.ID_ANY, label=s, style=wx.RB_GROUP |
                                                           style, name=s, enableTabFocus=enableTabFocus)
                else:
                    hRadio = self.winObject["radioButton"](hPanel, id=wx.ID_ANY, label=s, style=style, name=s, enableTabFocus=enableTabFocus)
                hRadio.Bind(wx.EVT_RADIOBUTTON, event)
                self._setFace(hRadio, mode=SKIP_COLOUR)
                Add(hSizer, hRadio)
                radios.append(hRadio)
            if type(state) == int:
                radios[state].SetValue(True)
            Add(self.sizer, hPanel, proportion, sizerFlag, margin)
            self.AddSpace()

            if self.mode & MODE_DARK == MODE_DARK:
                viewHelper.ScRadioButton(hPanel.GetHandle())

            return radios
        else:
            raise ValueError("ViewCreatorはRadioの作成に際し不正な型ののtextパラメータを受け取りました。")

    def listbox(self, text, choices=[], event=None, state=-1, style=0, size=(-1, -1),
                sizerFlag=wx.ALL, proportion=0, margin=5, textLayout=wx.DEFAULT, enableTabFocus=True):
        hStaticText, sizer, parent = self._addDescriptionText(text, textLayout, sizerFlag, proportion, margin)

        hListBox = self.winObject["listBox"](parent, wx.ID_ANY, name=text, choices=choices, size=size, style=style, enableTabFocus=enableTabFocus)
        hListBox.Bind(wx.EVT_LISTBOX, event)
        hListBox.SetSelection(state)
        self._setFace(hListBox)
        Add(sizer, hListBox, proportion, sizerFlag, margin)
        self.AddSpace()
        return hListBox, hStaticText

    def treeCtrl(self, text, event=None, style=wx.TR_FULL_ROW_HIGHLIGHT | wx.TR_NO_BUTTONS, size=(200, 200),
                 sizerFlag=wx.ALL, proportion=0, margin=5, textLayout=wx.DEFAULT, enableTabFocus=True):
        hStaticText, sizer, parent = self._addDescriptionText(text, textLayout, sizerFlag, proportion, margin)

        hTreeCtrl = self.winObject["treeCtrl"](parent, wx.ID_ANY, style=style | wx.BORDER_RAISED, size=size, enableTabFocus=enableTabFocus)
        hTreeCtrl.Bind(wx.EVT_TREE_SEL_CHANGED, event)
        self._setFace(hTreeCtrl)
        Add(sizer, hTreeCtrl, proportion, sizerFlag, margin)
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
            sizerFlag=wx.ALL,
            proportion=0,
            margin=5,
            textLayout=wx.DEFAULT,
            enableTabFocus=True):
        hStaticText, sizer, parent = self._addDescriptionText(text, textLayout, sizerFlag, proportion, margin)

        hListCtrl = self.winObject["listCtrl"](parent, wx.ID_ANY, style=style | wx.BORDER_RAISED, size=size, enableTabFocus=enableTabFocus)
        hListCtrl.Bind(wx.EVT_LIST_ITEM_FOCUSED, event)
        self._setFace(hListCtrl)
        self._setFace(hListCtrl.GetMainWindow())
        try:
            _winxptheme.SetWindowTheme(win32api.SendMessage(hListCtrl.GetHandle(), 0x101F, 0, 0), "", "")  # ヘッダーのウィンドウテーマを引っぺがす
        except pywintypes.error:
            pass
        Add(sizer, hListCtrl, proportion, sizerFlag, margin)
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
            sizerFlag=wx.ALL,
            proportion=0,
            margin=5,
            textLayout=wx.DEFAULT,
            enableTabFocus=True):
        hStaticText, sizer, parent = self._addDescriptionText(text, textLayout, sizerFlag, proportion, margin)

        hListCtrl = self.winObject["virtualListCtrl"](parent, wx.ID_ANY, style=style | wx.BORDER_RAISED, size=size, enableTabFocus=enableTabFocus)
        hListCtrl.Bind(wx.EVT_LIST_ITEM_FOCUSED, event)
        self._setFace(hListCtrl)
        self._setFace(hListCtrl.GetMainWindow())
        _winxptheme.SetWindowTheme(win32api.SendMessage(hListCtrl.GetHandle(), 0x101F, 0, 0), "", "")  # ヘッダーのウィンドウテーマを引っぺがす
        Add(sizer, hListCtrl, proportion, sizerFlag, margin)
        self.AddSpace()
        return hListCtrl, hStaticText

    def tabCtrl(self, title, event=None, style=wx.NB_NOPAGETHEME, sizerFlag=0, proportion=0, margin=5, enableTabFocus=True):
        htab = self.winObject["notebook"](self.parent, wx.ID_ANY, name=title, style=style, enableTabFocus=enableTabFocus)
        htab.Bind(wx.EVT_NOTEBOOK_PAGE_CHANGED, event)
        self._setFace(htab)
        Add(self.sizer, htab, proportion, sizerFlag, margin, expandFlag=wx.HORIZONTAL)
        self.sizer.Layout()
        return htab

    def inputbox(
            self,
            text,
            event=None,
            defaultValue="",
            style=wx.BORDER_RAISED,
            x=-1,
            sizerFlag=wx.ALL | wx.ALIGN_CENTER_VERTICAL,
            proportion=0,
            margin=5,
            textLayout=wx.DEFAULT,
            enableTabFocus=True):
        if self.mode & MODE_WRAPPING == MODE_NOWRAP:
            style |= wx.TE_DONTWRAP
        hStaticText, sizer, parent = self._addDescriptionText(text, textLayout, sizerFlag, proportion, margin)

        hTextCtrl = self.winObject["textCtrl"](parent, wx.ID_ANY, size=(x, -1), name=text, value=defaultValue,
                                               style=style | wx.BORDER_RAISED, enableTabFocus=enableTabFocus)
        hTextCtrl.Bind(wx.EVT_TEXT, event)
        self._setFace(hTextCtrl)
        if x == -1:
            Add(sizer, hTextCtrl, proportion, sizerFlag, margin, expandFlag=wx.HORIZONTAL)
        else:
            Add(sizer, hTextCtrl, proportion, sizerFlag, margin)
        self.AddSpace()
        return hTextCtrl, hStaticText

    def gauge(self, text, max=0, defaultValue=0, style=wx.GA_HORIZONTAL | wx.GA_SMOOTH | wx.BORDER_RAISED, x=-
              1, sizerFlag=wx.ALL | wx.ALIGN_CENTER_VERTICAL, proportion=0, margin=5, textLayout=wx.DEFAULT):
        hStaticText, sizer, parent = self._addDescriptionText(text, textLayout, sizerFlag, proportion, margin)

        hGauge = self.winObject["gauge"](parent, wx.ID_ANY, size=(x, -1), style=style, name=text,)
        self._setFace(hGauge)
        if x == -1:
            Add(sizer, hGauge, proportion, sizerFlag, margin, expandFlag=wx.HORIZONTAL)
        else:
            Add(sizer, hGauge, proportion, sizerFlag, margin)
        self.AddSpace()
        return hGauge, hStaticText

    def spinCtrl(
            self,
            text,
            min=0,
            max=100,
            event=None,
            defaultValue=0,
            style=wx.SP_ARROW_KEYS,
            x=-1,
            sizerFlag=wx.ALL | wx.ALIGN_CENTER_VERTICAL,
            proportion=0,
            margin=5,
            textLayout=wx.DEFAULT,
            enableTabFocus=True):
        hStaticText, sizer, parent = self._addDescriptionText(text, textLayout, sizerFlag, proportion, margin)

        hSpinCtrl = self.winObject["spinCtrl"](parent, wx.ID_ANY, min=min, max=max, initial=defaultValue,
                                               style=wx.BORDER_RAISED | style, size=(x, -1), enableTabFocus=enableTabFocus)
        hSpinCtrl.Bind(wx.EVT_TEXT, event)
        self._setFace(hSpinCtrl)
        Add(sizer, hSpinCtrl, proportion, sizerFlag, margin)
        self.AddSpace()
        return hSpinCtrl, hStaticText

    def slider(
            self,
            text,
            min=0,
            max=100,
            event=None,
            defaultValue=0,
            style=0,
            x=-1,
            sizerFlag=wx.ALL | wx.ALIGN_CENTER_VERTICAL,
            proportion=0,
            margin=5,
            textLayout=wx.DEFAULT,
            enableTabFocus=True):
        hStaticText, sizer, parent = self._addDescriptionText(text, textLayout, sizerFlag, proportion, margin)

        hSlider = self.winObject["slider"](parent, wx.ID_ANY, size=(x, -1), value=defaultValue, minValue=min,
                                           maxValue=max, style=style, enableTabFocus=enableTabFocus)
        hSlider.Bind(wx.EVT_SCROLL_CHANGED, event)
        self._setFace(hSlider)
        if x == -1:  # 幅を拡張
            Add(sizer, hSlider, proportion, sizerFlag, margin, expandFlag=wx.HORIZONTAL)
        else:
            Add(sizer, hSlider, proportion, sizerFlag, margin)
        self.AddSpace()
        return hSlider, hStaticText

    def clearSlider(
            self,
            text,
            min=0,
            max=100,
            event=None,
            defaultValue=0,
            style=0,
            x=-1,
            sizerFlag=wx.ALL | wx.ALIGN_CENTER_VERTICAL,
            proportion=0,
            margin=5,
            textLayout=wx.DEFAULT,
            enableTabFocus=True):
        hStaticText, sizer, parent = self._addDescriptionText(text, textLayout, sizerFlag, proportion, margin)

        hSlider = self.winObject["clear_slider"](parent, wx.ID_ANY, size=(x, -1), value=defaultValue,
                                                 minValue=min, maxValue=max, style=style, enableTabFocus=enableTabFocus)
        hSlider.SetBackgroundStyle(wx.BG_STYLE_PAINT)
        hSlider.Bind(wx.EVT_SCROLL_CHANGED, event)
        self._setFace(hSlider)
        if x == -1:  # 幅を拡張
            Add(sizer, hSlider, proportion, sizerFlag, margin, expandFlag=wx.HORIZONTAL)
        else:
            Add(sizer, hSlider, proportion, sizerFlag, margin)
        self.AddSpace()
        return hSlider, hStaticText

    def staticBitmap(self, text, bitmap=wx.NullBitmap, style=0, size=(-1, -1), sizerFlag=wx.ALL | wx.ALIGN_CENTER_VERTICAL, proportion=0, margin=5):
        staticBitmap = self.winObject["static_bitmap"](self.parent, wx.ID_ANY, size=size, style=style, name=text)
        self._setFace(staticBitmap)
        Add(self.sizer, staticBitmap, proportion, sizerFlag, margin)
        self.AddSpace()
        return staticBitmap

    def GetPanel(self):
        return self.parent

    def GetSizer(self):
        return self.sizer

    def GetMode(self):
        return self.mode

    def _addDescriptionText(self, text, textLayout, sizerFlag=0, proportion=0, margin=0):
        if textLayout not in (None, wx.HORIZONTAL, wx.VERTICAL, wx.DEFAULT):
            raise ValueError("textLayout must be (None,wx.HORIZONTAL,wx.VIRTICAL,wx.DEFAULT)")
        if type(self.sizer) in (wx.BoxSizer, wx.StaticBoxSizer) and textLayout not in (None, self.sizer.GetOrientation(), wx.DEFAULT):
            panel = makePanel(self.parent)
            if textLayout is not None:
                hStaticText = wx.StaticText(panel, wx.ID_ANY, label=text, name=text)
            else:
                hStaticText = wx.StaticText(panel, wx.ID_ANY, label=text, name=text, size=(0, 0))
            self._setFace(hStaticText)
            sizer = self.BoxSizer(panel, orient=textLayout)
            Add(sizer, hStaticText, 0, wx.ALIGN_CENTER_VERTICAL)
            Add(self.sizer, panel, proportion, sizerFlag, margin)
            return hStaticText, sizer, panel
        elif isinstance(self.sizer, (wx.GridSizer, wx.FlexGridSizer, wx.GridBagSizer)) and textLayout is None:
            hStaticText = wx.StaticText(self.parent, wx.ID_ANY, label=text, name=text, size=(0, 0))
            self._setFace(hStaticText)
            sizer = self.BoxSizer(self.sizer, style=sizerFlag & (wx.ALIGN_LEFT | wx.ALIGN_RIGHT |
                                  wx.ALIGN_CENTER_VERTICAL | wx.ALIGN_TOP | wx.ALIGN_BOTTOM | wx.EXPAND))
            Add(sizer, hStaticText)
            return hStaticText, sizer, self.parent
        else:
            if textLayout is not None:
                hStaticText = wx.StaticText(self.parent, wx.ID_ANY, label=text, name=text)
            else:
                hStaticText = wx.StaticText(self.parent, wx.ID_ANY, label=text, name=text, size=(0, 0))
            self._setFace(hStaticText)
            Add(self.sizer, hStaticText, 0, sizerFlag & (wx.ALIGN_LEFT | wx.ALIGN_RIGHT |
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
        target.SetFont(wx.Font())

    def getParentOrientation(self, default=wx.VERTICAL):
        if type(self.sizer) in (wx.BoxSizer, wx.StaticBoxSizer):
            return self.sizer.GetOrientation()
        else:
            return default

    def SetItemSpan(self, col, row=1):
        assert (isinstance(self.sizer, wx.GridBagSizer))
        self.sizer.SetItemSpan(wx.GBSpan(row, col))

    # configから読み取った値からmodeの整数値を生成して返す
    def config2modeValue(color="white", wrapping="off"):
        if type(color) != str or type(wrapping) != str:
            raise ValueError
        mode = 0
        if color.lower() == "dark":
            mode += MODE_DARK
        if wrapping.lower() == "on":
            mode += MODE_WRAPPING
        return mode

# parentで指定したsizerの下に、新たなBoxSizerを設置


def BoxSizer(parent, orient=wx.VERTICAL, flg=0, border=0):
    sizer = wx.BoxSizer(orient)
    if (parent is not None):
        parent.Add(sizer, 0, flg, border)
    return sizer


def Add(sizer, window, proportion=0, flag=0, border=0, expandFlag=None):
    if isinstance(sizer, wx.BoxSizer):
        if sizer.Orientation == wx.VERTICAL:
            for i in (wx.ALIGN_TOP, wx.ALIGN_BOTTOM, wx.ALIGN_CENTER_VERTICAL):
                if flag & i == i:
                    flag -= i
        else:
            for i in (wx.ALIGN_LEFT, wx.ALIGN_RIGHT, wx.ALIGN_CENTER_HORIZONTAL, wx.ALIGN_CENTER):
                if flag & i == i:
                    flag -= i
    if expandFlag == wx.HORIZONTAL:  # 幅を拡張
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
