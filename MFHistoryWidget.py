#!/usr/bin/env python3
import re
from os import path
from datetime import datetime
from dateutil.tz import tzlocal, tzutc
from PyQt5.QtCore import (Qt, QRect, QSize)
from PyQt5.QtGui import (QFont, QFontMetrics, QPixmap, QPainter)
from PyQt5.QtWidgets import (QWidget, QFrame,QLabel, QTextEdit, QListWidget, QListWidgetItem,
                            QGridLayout, QStyle, QStyleOption)

MIN_HISTORY_SIZE = (600, 450)
MIN_ITEM_SIZE    = (600, 150)
MF_HINT_FONT     = ('Noto Sans CJK SC',10,QFont.Bold)
ITEM_HINT_FONT   = ('Noto Sans CJK SC',12)
ITEM_HINT_COLOR  = 'blue'
ITEM_TEXT_FONT   = ('Noto Sans CJK SC',14)
ITEM_TEXT_COLOR  = '#252526'
LIST_BACKGROUND  = '#FFFFFF'
ITEM_BACKGROUND  = '#ECF0F1'
ITEM_MARGIN      = 5#px
OFFSET_FIX       = 2#px
img_filter   = re.compile('<-file://(.*?)->')
bold_filter  = re.compile('\*\*([^\*]+)\*\*')
italic_filter= re.compile('\*(.*?)\*')

class QLabelWrap(QLabel):
    def __init__(self, type, text='', pixmap=''):
        super().__init__(text)
        self.type = type
        if pixmap: self.setPixmap(pixmap)
        self.styleHelper()
        pass
    
    def styleHelper(self):
        self.setWordWrap(True)
        if self.type=='mf_hint':
            self.setFont(QFont(*MF_HINT_FONT))
            self.setFixedWidth(MIN_HISTORY_SIZE[0])
            self.setStyleSheet('''
                QLabel {
                    background-color : %r;
                }
            '''%(LIST_BACKGROUND))
            pass
        elif self.type=='item_hint':
            self.setFont(QFont(*ITEM_HINT_FONT))
            self.setFixedHeight( QFontMetrics(self.font()).height()+5 )
            self.setStyleSheet('''
                QLabel {
                    background-color: %r;
                    color: %r;
                }
            '''%(ITEM_BACKGROUND, ITEM_HINT_COLOR))
            pass
        elif self.type=='item_text':
            self.setFont(QFont(*ITEM_TEXT_FONT))
            self.setAlignment(Qt.AlignLeft | Qt.AlignTop)
            self.setTextFormat(Qt.RichText)
            self.setStyleSheet('''
                QLabel {
                    background-color: %r;
                    color: %r;
                }
            '''%(ITEM_BACKGROUND, ITEM_TEXT_COLOR))
            pass
        elif self.type=='img_label':
            self.setAlignment(Qt.AlignHCenter | Qt.AlignVCenter)
            pass
        else:
            raise Exception
            pass
        pass
    pass

class MFHistoryItem(QFrame):
    def __init__(self, w_item, base_path, item):
        super().__init__(None)
        self.w_item = w_item
        self.base_path = base_path
        self.styleHelper()
        self.updateItem(item)
        pass

    def styleHelper(self):
        self.layout = QGridLayout()
        self.setLayout(self.layout)
        self.layout.setSpacing(0)
        self.layout.setContentsMargins(0,0,0,0)
        self.setFixedWidth(MIN_ITEM_SIZE[0])
        self.setStyleSheet('''
            QFrame{
                background-color: %r;
                border: 1px solid black;
                border-radius: %rpx;
                margin: 5px;
            }
            QLabel{
                border: 0px;
            }
        '''%(ITEM_BACKGROUND, ITEM_MARGIN*2))
        pass

    def updateItem(self, item):
        (_user, _time, _text) = item
        _time = datetime.fromtimestamp(int(_time), tz=tzlocal()).strftime('%Y-%m-%d %H:%M:%S')
        _text = bold_filter.sub(r'<b>\1</b>', _text)
        _text = italic_filter.sub(r'<i>\1</i>', _text)
        _text = img_filter.split(_text)
        # parse (hint, images, text)
        hint   = '%s @ %s'%(_user, _time)
        text   = eval( ''.join(_text[0:][::2]) ).strip()
        text   = text.replace('\n', '<br>')
        images = _text[1:][::2]
        # create widgets
        hint_label = QLabelWrap('item_hint', hint)
        if text:
            text_label = QLabelWrap('item_text', text)
        image_pixmaps = [QPixmap(path.join(self.base_path, image)) for image in images]
        # adjust gridlayout
        self.layout.addWidget(hint_label, 0, 0, 1, 3)
        if not images: #text only
            self.layout.addWidget(text_label, 1, 0, 1, 3)
            pass
        elif not text: #images only
            CropRect = lambda x: QRect(0, 0, min(MIN_ITEM_SIZE[0]-ITEM_MARGIN*2,   x.width()), MIN_ITEM_SIZE[1])
            for (i,pixmap) in enumerate(image_pixmaps):
                cropped_pixmap = pixmap.copy( CropRect(pixmap) )
                image_label    = QLabelWrap('img_label', pixmap=cropped_pixmap)
                self.layout.addWidget(image_label, i+1, 0, 1, 3)
                image_label.setFixedWidth(MIN_ITEM_SIZE[0]-ITEM_MARGIN*2-OFFSET_FIX)
                pass
            pass
        else:
            CropRect = lambda x: QRect(0, 0, min(MIN_ITEM_SIZE[0]/3-ITEM_MARGIN*1, x.width()), MIN_ITEM_SIZE[1])
            for (i,pixmap) in enumerate(image_pixmaps):
                cropped_pixmap = pixmap.copy( CropRect(pixmap) )
                image_label    = QLabelWrap('img_label', pixmap=cropped_pixmap)
                self.layout.addWidget(image_label, i+1, 0, 1, 1)
                image_label.setFixedWidth(MIN_ITEM_SIZE[0]/3-ITEM_MARGIN*1-OFFSET_FIX)
                pass
            self.layout.addWidget(text_label, 1, 1, -1, -1)
            pass
        pass
    pass

class MFHistoryList(QListWidget):
    def __init__(self, parent):
        super().__init__(parent)
        self.styleHelper()
        pass

    def styleHelper(self):
        self.setStyleSheet('''
            QListWidget {
                border-bottom: 1px solid #5D6D7E;
            }
            QListView::item:selected {
                border: 1px solid #6a6ea9;
                border-radius: 10px;
            }
        ''')
        self.verticalScrollBar().setStyleSheet("""
            QScrollBar:vertical {
                border: none;
                background:white;
                width:3px;
                margin: 0px 0px 0px 0px;
            }
            QScrollBar::handle:vertical {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                stop: 0 rgb(32, 47, 130), stop: 0.5 rgb(32, 47, 130), stop:1 rgb(32, 47, 130));
                min-height: 0px;
            }
            QScrollBar::add-line:vertical {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                stop: 0 rgb(32, 47, 130), stop: 0.5 rgb(32, 47, 130),  stop:1 rgb(32, 47, 130));
                height: 0px;
                subcontrol-position: bottom;
                subcontrol-origin: margin;
            }
            QScrollBar::sub-line:vertical {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                stop: 0  rgb(32, 47, 130), stop: 0.5 rgb(32, 47, 130),  stop:1 rgb(32, 47, 130));
                height: 0 px;
                subcontrol-position: top;
                subcontrol-origin: margin;
            }
        """)
        self.setSpacing(0)
        self.setContentsMargins(0,0,0,0)
        self.setFixedWidth(MIN_HISTORY_SIZE[0])
        pass
    pass

class MFHistory(QWidget):
    def __init__(self, parent, base_path):
        super().__init__(parent)
        self.base_path = base_path
        self.styleHelper()
        pass
    
    def styleHelper(self):
        self.setStyleSheet('''
            QWidget {
                border: 0px;
                background-color: white;
            }
        ''')
        self.w_hint_label   = QLabelWrap('mf_hint')
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
        self.w_history_list.clear()
        self.w_hint_label.setText(hint)
        for item in items:
            w_item = QListWidgetItem(self.w_history_list)
            w_item_widget = MFHistoryItem(w_item, self.base_path, item)
            size_hint = QSize(0, w_item_widget.sizeHint().height()+ITEM_MARGIN) #NOTE: do not adjust width
            w_item.setSizeHint(size_hint)
            self.w_history_list.addItem(w_item)
            self.w_history_list.setItemWidget(w_item, w_item_widget)
            pass
        pass
    
    pass