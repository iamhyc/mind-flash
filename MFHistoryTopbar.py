#!/usr/bin/env python3
from pathlib import Path
from MFUtility import MF_RNG, KeysReactor, Worker
from PyQt5.QtCore import (Qt, QSize, QEvent, QThread, pyqtSlot)
from PyQt5.QtGui import (QIcon, QFont, QFontMetrics, QPixmap)
from PyQt5.QtWidgets import (QWidget, QLabel, QPlainTextEdit, QBoxLayout, QGridLayout)

COLOR_SPRING   = '#018749'
COLOR_SUMMER   = '#CC0000'
COLOR_AUTUMN   = '#9F2D20'
COLOR_WINTER   = '#1E90FF'
COLOR_WEEKDAY  = ['gold', 'deeppink', 'green', 'darkorange', 'blue', 'indigo', 'red']

MF_HINT_FONT      = ('Noto Sans CJK SC',10,QFont.Bold)
INPUTBOX_FONT     = ('Noto Sans CJK SC',14)
MIN_TOPBAR_SIZE   = (600, 40)
MIN_TOOLICON_SIZE = (72, 40)
TOOLICON_NUM      = 2
TOPBAR_BACKGROUND = '#FFFEF9' #xuebai

class HintLabel(QLabel):
    def __init__(self, parent, text=''):
        super().__init__(text, parent)
        self.parent = parent
        self.hint = text
        self.lock = None
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
            self.hint = '<a style="color:%s">%s</a>'%(_color, _hint)
        elif stp.mf_type==MF_RNG.DAY:
            _color = COLOR_WEEKDAY[ stp.end.weekday() ]
            self.hint = stp.end.strftime('%Y-%m-%d <a style="color:{}">(%a)</a>'.format(_color))
        else:
            self.hint = '<a style="color:black">%s</a>'%(_hint)
        
        if self.lock is None:
            self.setText(self.hint)
        pass

    @pyqtSlot(float)
    def setProgressHint(self, percentage):
        percentage = max(min(percentage, 1.0), 0.0)
        self.setText('Progress: %.2f'%(percentage*100))
        pass

    @pyqtSlot(object)
    def getLock(self, owner):
        if self.lock is None:
            self.lock = owner
            return True
        else:
            return False

    @pyqtSlot(object)
    def releaseLock(self, owner):
        if self.lock and self.lock==owner:
            self.lock = None
            self.setText(self.hint)
            return True
        else:
            return False
    pass

class InputBox(QPlainTextEdit):
    def __init__(self, parent):
        super().__init__(parent)
        self.parent = parent
        self.keysFn = KeysReactor(self)
        self.registerKeys()
        self.styleHelper()
        pass

    def styleHelper(self):
        self.setFont( QFont(*INPUTBOX_FONT) )
        self.setPlaceholderText("Press ENTER to search ...")
        self.setFixedSize(*MIN_TOPBAR_SIZE)
        self.setVisible(False)
        pass

    def registerKeys(self):
        self.keysFn.register([Qt.Key_Return], lambda:self.clear())
        pass
    pass

class ToolBarIcon(QLabel):

    def __init__(self, parent, type=None, pos=0):
        super().__init__('', parent)
        self.parent = parent
        self.topbar = parent.parent
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
            if self.pos<0:      #leftmost position
                self.setFixedSize(*MIN_TOOLICON_SIZE)
                self.setStyleSheet('QLabel { border-width: 1px 1px 1px 1px; }')
            elif self.pos>0:    #rightmost position
                self.setAlignment(Qt.AlignRight | Qt.AlignTop)
                self.setStyleSheet('QLabel { border-width: 1px 1px 1px 0px; }')
            else:               #middle position
                self.setFixedSize(*MIN_TOOLICON_SIZE)
                self.setStyleSheet('QLabel { border-width: 1px 1px 1px 0px; }')
        else: #spacing
            _width = MIN_TOPBAR_SIZE[0] - MIN_TOOLICON_SIZE[0]*TOOLICON_NUM - 33 #33 for one rightmost icon
            self.setFixedSize( _width, MIN_TOPBAR_SIZE[1] )
            self.setStyleSheet('QLabel { border-width: 1px 0px 1px 0px; }')
        pass

    def mousePressEvent(self, e):
        if e.buttons() & Qt.LeftButton:
            if self.type == 'search':
                self.topbar.switch( self.topbar.input_box )
                self.topbar.input_box.setFocus()
                pass
            elif self.type == 'export':
                self.topbar.switch( self.topbar.hint_label )
                #
                self.worker = Worker(self.topbar.parent.dumpHistory,
                                        args=(self.topbar.hint_label, ))
                self.worker.start()
                pass
            elif self.type == 'collapse':
                self.topbar.parent.parent.w_editor.toggleHistoryWidget()
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
        layout.addWidget( ToolBarIcon(self),                   0, Qt.AlignJustify )
        layout.addWidget( ToolBarIcon(self, 'collapse',   1),  0, Qt.AlignJustify )
        self.setLayout(layout)
        self.setStyleSheet('''
            QWidget {
                border: 1px solid #5D6D7E;
            }
        ''')
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
