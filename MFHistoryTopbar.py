#!/usr/bin/env python3
from pathlib import Path
from MFUtility import MF_RNG
from PyQt5.QtCore import (Qt, QSize)
from PyQt5.QtGui import (QFont, QFontMetrics, QPixmap)
from PyQt5.QtWidgets import (QWidget, QLabel, QPlainTextEdit, QGridLayout)

COLOR_SPRING   = '#018749'
COLOR_SUMMER   = '#CC0000'
COLOR_AUTUMN   = '#9F2D20'
COLOR_WINTER   = '#1E90FF'
COLOR_WEEKDAY  = ['gold', 'deeppink', 'green', 'darkorange', 'blue', 'indigo', 'red']

MF_HINT_FONT     = ('Noto Sans CJK SC',10,QFont.Bold)
MIN_HISTORY_SIZE = (600, 450)
LIST_BACKGROUND  = '#FFFEF9' #xuebai

class HintLabel(QLabel):
    def __init__(self, text=''):
        super().__init__(text)
        self.styleHelper()
        pass

    def styleHelper(self):
        self.setWordWrap(True)
        self.setFont(QFont(*MF_HINT_FONT))
        self.setFixedWidth(MIN_HISTORY_SIZE[0])
        self.setFont(QFont(*MF_HINT_FONT))
        self.setFixedWidth(MIN_HISTORY_SIZE[0])
        self.setStyleSheet('''
            QLabel {
                background-color : %s;
            }
        '''%(LIST_BACKGROUND))
        # self.setAlignment(Qt.AlignHCenter | Qt.AlignVCenter)
        pass

    def setDateHint(self, stp):
        _hint = stp.hint
        if stp.mf_type==MF_RNG.WEEK or stp.mf_type==MF_RNG.MONTH:
            _month = stp.end.month
            if _month in range(2,5):
                _color = COLOR_SPRING
            elif _month in range(5,8):
                _color = COLOR_SUMMER
            elif _month in range(8,11):
                _color = COLOR_AUTUMN
            else:
                _color = COLOR_WINTER
            self.setStyleSheet("QLabel { color:%s }"%_color)
            pass
        elif stp.mf_type==MF_RNG.DAY:
            _color = COLOR_WEEKDAY[ stp.end.weekday() ]
            _hint  = stp.end.strftime('%Y-%m-%d <a style="color:{}">(%a)</a>'.format(_color))
            pass
        else:
            self.setStyleSheet("QLabel { color:black }")
            pass
        self.setText(_hint)
        pass
    pass

class InputBox(QPlainTextEdit):
    def __init__(self, parent):
        super().__init__(parent)
        self.parent = parent
        pass
    pass

class ToolBar(QWidget):
    def __init__(self, parent):
        super().__init__(parent)
        self.parent = parent
        pass
    pass

class TopbarManager:
    def __init__(self, parent):
        self.parent = parent
        self.tool_bar = ToolBar(None)
        self.hint_label = HintLabel('mf_hint')
        self.input_box = InputBox(None)
        self.w_display = self.hint_label
        self.parent.grid.addWidget(self.w_display, 0, 0)
        pass

    def switchWidget(self, widget):
        self.parent.grid.replaceWidget(self.w_display, widget)
        self.w_display = widget
        self.parent.adjustSize()
        pass

    pass
