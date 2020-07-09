#!/usr/bin/env python3
import re
from datetime import datetime
from dateutil.tz import tzlocal, tzutc
from PyQt5.QtGui import (QFont, QFontMetrics, QIcon)
from PyQt5.QtWidgets import (QWidget, QLabel, QTextEdit, QListWidget, QListWidgetItem, QGridLayout)

MIN_HISTORY_SIZE = (600, 450)
MIN_ITEM_SIZE    = (600, 150)
HINT_FONT        = ('Noto Sans CJK SC',10,QFont.Bold)

# [left-upper corner] [QLabel, 100% width, 12px, bold] (hint)
class MFHintLabel(QLabel):
    def __init__(self, parent, text=''):
        super().__init__(parent)
        self.setFont(QFont(*HINT_FONT))
        self.setFixedWidth(MIN_HISTORY_SIZE[0])
        self.setStyleSheet("QLabel { background-color : white; }");
        self.setText(text)
        pass
    pass

class MFHistoryItem(QListWidgetItem):
    def __init__(self, parent, item):
        super().__init__(parent, 0)
        self.updateItem(item)
        pass

    def updateItem(self, item):
        (_user, _time, _text) = item
        _time = datetime.fromtimestamp(int(_time), tz=tzlocal()).strftime('%Y-%m-%d %H:%M:%S')
        hint  = '%s @ %s'%(_user, _time)
        #FIXME: item redering with ListWidgetItem
        # [item_css] ('background-color: #8c8c8c;')
        # [time_css] ('color: #B4B5B8; font-size: 12px;')
        # [text_css] ('color: #252526; font-size: 16px;')
        # re.sub(r'<-file://(\S+)->',r'\1">'; QSize( min(MIN_ITEM_SIZE[0], img.width), 150 )
        # replace('\\n', '<br>')
        pass
    pass

class MFHistoryList(QListWidget):
    def __init__(self, parent):
        super().__init__(parent)
        self.styleHelper()
        pass

    def styleHelper(self):
        self.setStyleSheet(
            '''
            QListWidget {
                border-bottom: 1px solid #5D6D7E;
            }
            QScrollBar:vertical {
                border: none;
                background: rgba(0,0,0,0);
                width: 10px;
                margin: 5px 0px 5px 0px;
            }
            '''
        )
        self.setContentsMargins(5,5,5,5)
        self.setFixedWidth(MIN_HISTORY_SIZE[0])
        pass
    pass

class MFHistory(QWidget):
    def __init__(self, parent, basePath):
        super().__init__(parent)
        self.basePath = basePath
        self.styleHelper()
        pass
    
    def styleHelper(self):
        self.setStyleSheet('background-color: white; border: 1px solid white;')
        self.w_hint_label   = MFHintLabel(self)
        self.w_history_list = MFHistoryList(self)
        # set main window layout as grid
        grid = QGridLayout()
        grid.setSpacing(0)
        grid.setContentsMargins(0,0,0,0)
        grid.addWidget(self.w_hint_label,   0, 0)
        grid.addWidget(self.w_history_list, 1, 0)
        self.setLayout(grid)
        self.setFixedSize(*MIN_HISTORY_SIZE)
        self.setVisible(False)
        pass

    def hideEvent(self, e):
        super().hideEvent(e)
        self.w_history_list.clear()
        pass

    def render(self, hint, items):
        self.w_hint_label.setText(hint)
        for item in items:
            w_item = MFHistoryItem(self.w_history_list, item)
            self.w_history_list.addItem(w_item)
            pass
        pass
    
    pass