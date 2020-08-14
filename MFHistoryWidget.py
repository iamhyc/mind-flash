#!/usr/bin/env python3
import re, os
from pathlib import Path
from datetime import datetime
from dateutil.tz import tzlocal, tzutc
from MFUtility import MF_RNG
from PyQt5.QtCore import (Qt, QRect, QSize)
from PyQt5.QtGui import (QFont, QFontMetrics, QPixmap, QPainter, QTextDocument)
from PyQt5.QtWidgets import (QApplication, QWidget, QFrame, QLabel,
                            QListWidget, QListWidgetItem, QGridLayout)

COLOR_SPRING   = '#018749'
COLOR_SUMMER   = '#CC0000'
COLOR_AUTUMN   = '#9F2D20'
COLOR_WINTER   = '#1E90FF'
COLOR_WEEKDAY  = ['gold', 'deeppink', 'green', 'darkorange', 'blue', 'indigo', 'red']
COLOR_DAYTIME  = ['#B0C4DE', '#8BB271', '#F9F9F9', '#191970'] #midnight, morning, afternoon, night

MIN_HISTORY_SIZE = (600, 450)
MIN_ITEM_SIZE    = (600, 150)
MF_HINT_FONT     = ('Noto Sans CJK SC',10,QFont.Bold)
ITEM_HINT_FONT   = ('Noto Sans CJK SC',12)
ITEM_HINT_COLOR  = 'silver'
ITEM_TEXT_FONT   = ('Noto Sans CJK SC',14)
ITEM_TEXT_COLOR  = '#252526'
LIST_BACKGROUND  = '#FFFFFF'
ITEM_BACKGROUND  = '#ECF0F1'
ITEM_MARGIN      = 5#px
ITEM_RADIUS      = 10#px
OFFSET_FIX       = 2#px
img_filter   = re.compile('<-file://(.*?)->')
bold_filter  = re.compile('\*\*([^\*]+)\*\*')
italic_filter= re.compile('\*(.*?)\*')

class QLabelWrapper(QLabel):
    def __init__(self, type, text='', pixmap='', alt=''):
        super().__init__(text)
        self.type = type
        self.alt  = alt
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
                    background-color : %s;
                }
            '''%(LIST_BACKGROUND))
            # self.setAlignment(Qt.AlignHCenter | Qt.AlignVCenter)
            pass
        elif self.type=='item_hint':
            _user,_date,_time = self.text().split()
            _time_color = COLOR_DAYTIME[ int(_time.split(':')[0])//6 - 1 ] #for 24Hr timing
            _user_color = 'silver' if _user=='Myself' else 'black'
            _date_color = 'silver'
            self.setText('''<a style="color:{user_color}">{user}</a>
                        <a style="color:{date_color}">@ {date}</a>
                        <a style="color:{time_color}">{time}</a>
                        '''.format(
                            user_color=_user_color, user=_user,
                            date_color=_date_color, date=_date,
                            time_color=_time_color, time=_time
                        ))
            self.setFont(QFont(*ITEM_HINT_FONT))
            self.setStyleSheet('QLabel { background-color: %s; }'%(ITEM_BACKGROUND))
            self.setFixedHeight( QFontMetrics(self.font()).height()+5 )
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

    def mousePressEvent(self, ev):
        if ev.buttons() & Qt.RightButton and self.type=='img_label':
            _clipboard = QApplication.clipboard()
            if self.alt:
                _clipboard.setPixmap(self.alt)
            else:
                _clipboard.setPixmap(self.pixmap())
            try:
                os.system('notify-send -a "Mind Flash" -i "$PWD/res/icons/pulse_heart.png" -t 1000 "Image Copied."')
            except Exception:
                pass
            pass
        return super().mousePressEvent(ev)

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
        self.size_height = 0
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
        '''%(ITEM_BACKGROUND, ITEM_RADIUS))
        pass

    def getSizeHint(self, label_ref, pos):
        _doc  = QTextDocument(); _doc.setHtml(label_ref.text())
        _text = _doc.toPlainText()
        _size = QSize(590,0)
        if _text: #FIXME: sizeHint with 'mixed' layout
            fm    = QFontMetrics(label_ref.font())
            fm_rect = QRect(0,0,590,100)
            _height = fm.boundingRect(fm_rect, Qt.TextWordWrap, _text).size().height()
            _size  += QSize(0,_height)
        elif label_ref.pixmap():
            _size  += QSize(0, MIN_ITEM_SIZE[1])
        return _size

    def wrapWidget(self, ref, pos):
        self.layout.addWidget(ref, *pos)
        size_hint = self.getSizeHint(ref, pos)
        self.size_height += size_hint.height()
        return ref

    def updateItem(self, item):
        self.item = item
        (_user, _time, _text) = item
        _time = datetime.fromtimestamp(int(_time), tz=tzlocal()).strftime('%m-%d %H:%M') #%Y-%m-%d %H:%M:%S
        _text = bold_filter.sub(r'<b>\1</b>', _text)
        _text = italic_filter.sub(r'<i>\1</i>', _text)
        _text = img_filter.split(_text)
        # parse (hint, images, text)
        hint   = ' '.join([_user, _time])
        text   = eval( ''.join(_text[0:][::2]) ).strip()
        text   = text+'\n' if text else '' #NOTE: for QFontMetrics.boundingRect correction
        text   = text.replace('\n', '<br>')
        images = _text[1:][::2]
        # create widgets
        hint_label = QLabelWrapper('item_hint', hint)
        if text:
            text_label = QLabelWrapper('item_text', text)
        image_pixmaps = [QPixmap( str(Path(self.base_path, image)) ) for image in images]
        # adjust gridlayout
        self.wrapWidget(hint_label, [0,0, 1,3])
        if not images: #text only
            self.wrapWidget(text_label, [1,0, 1,3])
            pass
        elif not text: #images only
            CropRect = lambda x: QRect(0, 0, min(MIN_ITEM_SIZE[0]-ITEM_MARGIN*2,   x.width()), MIN_ITEM_SIZE[1])
            for (i,pixmap) in enumerate(image_pixmaps):
                cropped_pixmap = pixmap.copy( CropRect(pixmap) )
                image_label    = QLabelWrapper('img_label', pixmap=cropped_pixmap, alt=pixmap)
                self.wrapWidget(image_label, [i+1,0, 1,3])
                image_label.setFixedWidth(MIN_ITEM_SIZE[0]-ITEM_MARGIN*2-OFFSET_FIX)
                pass
            pass
        else:          #mixture
            CropRect = lambda x: QRect(0, 0, min(MIN_ITEM_SIZE[0]/3-ITEM_MARGIN*1, x.width()), MIN_ITEM_SIZE[1])
            for (i,pixmap) in enumerate(image_pixmaps):
                cropped_pixmap = pixmap.copy( CropRect(pixmap) )
                image_label    = QLabelWrapper('img_label', pixmap=cropped_pixmap, alt=pixmap)
                self.wrapWidget(image_label, [i+1,0, 1,1])
                image_label.setFixedWidth(MIN_ITEM_SIZE[0]/3-ITEM_MARGIN*1-OFFSET_FIX)
                pass
            self.wrapWidget(text_label, [1,1, -1,-1])
            pass
        pass

    def sizeHint(self):
        return QSize(-1, self.size_height)
    pass

class MFHistoryList(QListWidget):
    def __init__(self, parent):
        super().__init__(parent)
        self.parent = parent
        self.itemDoubleClicked.connect(self.itemDoubleClickEvent)
        self.styleHelper()
        pass

    def styleHelper(self):
        self.setStyleSheet('''
            QListWidget {
                border: 1px solid #5D6D7E;
                border-top: 0px;
            }
            QListView::item:selected {
                border: 1px solid #6a6ea9;
                border-radius: 10px;
            }
        ''')
        self.verticalScrollBar().setStyleSheet("""
            QScrollBar:vertical {
                border: none;
                background:palette(base);
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

    def itemDoubleClickEvent(self, item):
        raw_item = self.itemWidget(item).item
        self.parent.parent.w_editor.insertPlainText( eval(raw_item[2]) )
        self.parent.parent.w_editor.setFocus()
        #TODO: remove original record
        self.removeItemWidget(item)
        self.takeItem(self.row(item))
        pass
    pass

class MFHistory(QWidget):
    def __init__(self, parent, base_path):
        super().__init__(parent)
        self.parent = parent
        self.base_path = base_path
        self.styleHelper()
        pass
    
    def styleHelper(self):
        self.w_hint_label   = QLabelWrapper('mf_hint')
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
        self.setStyleSheet('''
            QWidget {
                border: 1px solid #5D6D7E;
                border-bottom: 0px solid white;
                background-color: white;
            }
        ''')
        pass

    def hideEvent(self, e):
        super().hideEvent(e)
        if not self.isVisible():
            self.w_history_list.clear()
        pass

    def setHintLabel(self, stp):
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
            self.w_hint_label.setStyleSheet("QLabel { color:%s }"%_color)
            pass
        elif stp.mf_type==MF_RNG.DAY:
            _color = COLOR_WEEKDAY[ stp.end.weekday() ]
            _hint  = stp.end.strftime('%Y-%m-%d <a style="color:{}">(%a)</a>'.format(_color))
            pass
        else:
            self.w_hint_label.setStyleSheet("QLabel { color:black }")
            pass
        self.w_hint_label.setText(_hint)
        pass

    def renderHistory(self, stp, items):
        self.w_history_list.clear()
        self.setHintLabel(stp)
        
        for item in items:
            w_item = QListWidgetItem(self.w_history_list)
            w_item_widget = MFHistoryItem(w_item, self.base_path, item)
            size_hint = QSize(0, w_item_widget.sizeHint().height()+ITEM_MARGIN) # do not adjust width
            w_item.setSizeHint(size_hint)
            self.w_history_list.addItem(w_item)
            self.w_history_list.setItemWidget(w_item, w_item_widget)
            pass
        pass
    
    pass