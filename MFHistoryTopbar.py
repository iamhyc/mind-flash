#!/usr/bin/env python3
from pathlib import Path
from MFUtility import MF_RNG
from PyQt5.QtCore import (Qt, QSize, QEvent)
from PyQt5.QtGui import (QIcon, QFont, QFontMetrics, QPixmap)
from PyQt5.QtWidgets import (QWidget, QLabel, QPlainTextEdit, QBoxLayout, QGridLayout)

COLOR_SPRING   = '#018749'
COLOR_SUMMER   = '#CC0000'
COLOR_AUTUMN   = '#9F2D20'
COLOR_WINTER   = '#1E90FF'
COLOR_WEEKDAY  = ['gold', 'deeppink', 'green', 'darkorange', 'blue', 'indigo', 'red']

MF_HINT_FONT      = ('Noto Sans CJK SC',10,QFont.Bold)
MIN_TOPBAR_SIZE   = (600, 40)
MIN_TOOLICON_SIZE = (70, 40)
TOPBAR_BACKGROUND = '#FFFEF9' #xuebai

class HintLabel(QLabel):
    def __init__(self, parent, text=''):
        super().__init__(text, parent)
        self.parent = parent
        self.styleHelper()
        pass

    def styleHelper(self):
        self.setWordWrap(True)
        self.setFont(QFont(*MF_HINT_FONT))
        self.setFixedSize(*MIN_TOPBAR_SIZE)
        # self.setAlignment(Qt.AlignHCenter | Qt.AlignCenter)
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
        self.styleHelper()
        pass

    def styleHelper(self):
        self.setFixedSize(*MIN_TOPBAR_SIZE)
        self.setVisible(False)
        pass
    pass

class ToolBarIcon(QLabel):
    def __init__(self, parent, type, pos=0):
        super().__init__('', parent)
        self.parent = parent
        self.type = type
        self.pos = pos
        self.styleHelper()
        pass

    def styleHelper(self):
        if type(self.type)==str:
            _icon = QIcon( './res/svg/{}.svg'.format(self.type) ).pixmap( QSize(32,32) )
            self.setPixmap(_icon)
            self.setToolTip(self.type)
            
            self.setAlignment(Qt.AlignHCenter | Qt.AlignVCenter)
            if self.pos<0: #leftmost position
                self.setFixedSize(*MIN_TOOLICON_SIZE)
                self.setStyleSheet('QLabel { border-width: 1px 0px 0px 1px; }')
            elif self.pos>0: #rightmost position
                self.setAlignment(Qt.AlignRight | Qt.AlignTop)
                self.setStyleSheet('QLabel { border-width: 1px 1px 0px 0px; }')
            else: #middle position
                self.setFixedSize(*MIN_TOOLICON_SIZE)
                self.setStyleSheet('QLabel { border-width: 1px 0px 0px 0px; }')
        else: #spacing
            self.setFixedSize( int(self.type), MIN_TOPBAR_SIZE[1] )
            self.setStyleSheet('QLabel { border-width: 1px 0px 0px 0px; }')
        pass

    def mousePressEvent(self, e):
        if self.type == 'search':
            pass
        elif self.type == 'export':
            pass
        elif self.type == 'collapse':
            self.parent.parent.parent.parent.w_editor.toggleHistoryWidget()
            pass
        else:
            pass
        return super().mousePressEvent(e)
    pass

class ToolBar(QWidget):
    def __init__(self, parent):
        super().__init__(parent)
        self.parent = parent
        self.styleHelper()
        pass

    def styleHelper(self):
        layout = QBoxLayout(QBoxLayout.LeftToRight)
        layout.setSpacing(0)
        layout.setContentsMargins(0,0,0,0)
        layout.addWidget( ToolBarIcon(self, 'search',    -1),  0, Qt.AlignJustify )
        layout.addWidget( ToolBarIcon(self, 'export',     0),  0, Qt.AlignJustify )
        layout.addWidget( ToolBarIcon(self, 600-32*3),         0, Qt.AlignJustify )
        layout.addWidget( ToolBarIcon(self, 'collapse',      1),  0, Qt.AlignJustify )
        self.setLayout(layout)
        self.setFixedSize(*MIN_TOPBAR_SIZE)
        self.setVisible(False)
        pass
    pass

class TopbarManager(QWidget):
    def __init__(self, parent):
        super().__init__(parent)
        self.parent = parent
        self.hint_label = HintLabel(self)
        self.tool_bar   = ToolBar(self)
        self.input_box  = InputBox(self)
        self.w_display  = self.hint_label
        self.styleHelper()
        self.installEventFilter(self)
        pass

    def styleHelper(self):
        self.grid = QGridLayout()
        self.grid.setSpacing(0)
        self.grid.setContentsMargins(0,0,0,0)
        self.grid.addWidget(self.w_display, 0, 0)
        self.setLayout(self.grid)
        self.setFixedSize(*MIN_TOPBAR_SIZE)
        self.setStyleSheet('''
            QWidget {
                background-color : %s;
            }
        '''%(TOPBAR_BACKGROUND))
        pass

    def switch(self, widget=None):
        if widget is None: widget = self.hint_label
        if self.w_display == widget: return

        self.w_display.setVisible(False); widget.setVisible(True)
        self.grid.replaceWidget(self.w_display, widget)
        self.w_display = widget
        pass

    def eventFilter(self, object, event):
        if event.type() == QEvent.Enter:
            self.switch(self.tool_bar)
        elif event.type() == QEvent.Leave:
            self.switch(self.hint_label)
            pass
        return super().eventFilter(object, event)
    pass
