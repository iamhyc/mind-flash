#!/usr/bin/env python3
import re
from os import system as os_system
from pathlib import Path
from datetime import datetime
from dateutil.tz import tzlocal, tzutc
from MFUtility import POSIX, MF_RNG, MF_HOSTNAME, MimeDataManager
from MFPreviewWidget import MFImagePreviewer
from MFHistoryTopbar import TopbarManager
from PyQt5.QtCore import (Qt, QRect, QSize, QThread, pyqtSignal)
from PyQt5.QtGui import (QFont, QFontMetrics, QPixmap, QPainter, QTextDocument)
from PyQt5.QtWidgets import (QApplication, QWidget, QFrame, QLabel,
                            QListWidget, QListWidgetItem, QGridLayout)

COLOR_DAYTIME  = ['#856d72', '#83cbac', '#f1939c', '#93b5cf'] #00-06, 06-12, 12-18, 18-24
# color reference: http://zhongguose.com/, https://nipponcolors.com/
MIN_HISTORY_SIZE = (600, 450)
MIN_ITEM_SIZE    = (600, 150)
ITEM_HINT_FONT   = ('Noto Sans CJK SC',12)
ITEM_USER_COLOR  = 'silver'
ITEM_DATE_COLOR  = '#2b1216'
ITEM_TEXT_FONT   = ('Noto Sans CJK SC',14)
ITEM_TEXT_COLOR  = '#252526'
LIST_BACKGROUND  = '#FFFEF9' #xuebai
ITEM_BACKGROUND  = '#EEF7F2'
ITEM_BORDERCOLOR = '#DFECD5'
ITEM_MARGIN      = 5#px
ITEM_RADIUS      = 10#px
OFFSET_FIX       = 2#px
img_filter    = re.compile("\.(gif|jpe?g|tiff?|png|bmp)")
icon_filter   = re.compile("<-file://(.*?)->")
bold_filter   = re.compile("\*\*([^\*]+)\*\*")
italic_filter = re.compile("\*(.*?)\*")

class QLabelWrapper(QLabel):
    def __init__(self, type, text='', pixmap='', alt=''):
        super().__init__(text)
        self.type   = type
        self.alt    = alt
        if pixmap: self.setPixmap(pixmap)
        self.styleHelper()
        pass
    
    def styleHelper(self):
        self.setWordWrap(True)
        if self.type=='item_hint':
            self.setFont(QFont(*ITEM_HINT_FONT))
            self.setStyleSheet('QLabel { background-color: %s; }'%(ITEM_BACKGROUND))
            self.setFixedHeight( QFontMetrics(self.font()).height()+8 )

            _user,_date,_time = self.text().split()
            _time_color = COLOR_DAYTIME[ int(_time.split(':')[0])//6 ] #for 24Hr timing
            self.setText('''
                        <a style="color:{date_color}">{date}</a>
                        <a style="color:{time_color}">{time}</a>
                        <a style="color:{user_color}">@ {user}</a>
                        '''.format(
                            user_color=ITEM_USER_COLOR, user=_user,
                            date_color=ITEM_DATE_COLOR, date=_date,
                            time_color=_time_color, time=_time
                        ))
            pass
        elif self.type=='item_text':
            self.setFont(QFont(*ITEM_TEXT_FONT))
            self.setAlignment(Qt.AlignLeft | Qt.AlignTop)
            self.setTextFormat(Qt.RichText)
            self.setTextInteractionFlags(Qt.TextBrowserInteraction)
            self.setOpenExternalLinks(True)
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
        elif self.type=='file_label':
            _pixmap = self.pixmap().scaledToWidth(120, Qt.SmoothTransformation)
            #TODO: alter _pixmap with right-slide filename
            self.setPixmap(_pixmap)
            self.setAlignment(Qt.AlignHCenter | Qt.AlignVCenter)
            pass
        else:
            raise Exception
            pass
        pass

    def mousePressEvent(self, ev):
        if self.type=='img_label' and ev.buttons() & Qt.RightButton:
            _clipboard = QApplication.clipboard()
            if self.alt:
                _clipboard.setPixmap(self.alt)
            else:
                _clipboard.setPixmap(self.pixmap())
            try:
                os_system('notify-send -a "Mind Flash" -i "$PWD/res/icons/pulse_heart.png" -t 1000 "Image Copied."')
            except Exception:
                pass
            pass
        elif self.type=='img_label' and ev.buttons() & Qt.LeftButton:
            _pixmap = self.alt if self.alt else self.pixmap()
            w_preview = MFImagePreviewer(self, _pixmap)
            pass
        elif self.type=='file_label' and ev.buttons() & Qt.RightButton:
            #TODO: copy to clipboard mime data
            # os_system('notify-send -a "Mind Flash" -i "$PWD/res/icons/pulse_heart.png" -t 1000 "File %s Copied."'%self.alt.name)
            pass
        elif self.type=='file_label' and ev.buttons() & Qt.LeftButton:
            #TODO: open with QDesktopService
            pass
        return super().mousePressEvent(ev)

    pass

class MFHistoryItem(QFrame):
    def __init__(self, w_item, base_path, item):
        super().__init__(None)
        self.w_item = w_item
        self.base_path = base_path
        self.styleHelper()
        self.uri, self.item = item[0], item[1]
        self.double_clicked = 0
        self.updateItem()
        pass

    def styleHelper(self):
        self.size_height = QSize(0, 0) #two column, (image_height, text_height)
        self.layout = QGridLayout()
        self.setLayout(self.layout)
        self.layout.setSpacing(0)
        self.layout.setContentsMargins(0,0,0,0)
        self.setFixedWidth(MIN_ITEM_SIZE[0])
        self.setStyleSheet('''
            QFrame{
                background-color: %s;
                border: 1px solid %s;
                border-radius: %dpx;
                margin: 5px;
            }
            QLabel{
                border: 0px;
            }
        '''%(ITEM_BACKGROUND, ITEM_BORDERCOLOR, ITEM_RADIUS))
        pass

    def getHeightHint(self, label_ref, pos):
        if label_ref.text():
            _doc  = QTextDocument(); _doc.setHtml(label_ref.text())
            _text = _doc.toPlainText()
            fm    = QFontMetrics(label_ref.font())
            if label_ref.type=='item_hint':
                fm_rect = QRect(0,0,590,100)
                _height = fm.boundingRect(fm_rect, Qt.TextWordWrap, _text).size().height()
                size   = QSize(_height, _height)
            else:
                fm_rect = QRect(0,0,590,100) if len(self.item_icons)==0 else QRect(0,0,590/3*2,100)
                _height = fm.boundingRect(fm_rect, Qt.TextWordWrap, _text).size().height()
                size   = QSize(0, _height)
            pass
        else:
            size  = QSize(MIN_ITEM_SIZE[1], 0)
            pass
        return size

    def wrapWidget(self, ref, pos):
        self.layout.addWidget(ref, *pos)
        self.size_height += self.getHeightHint(ref, pos)
        return ref

    def getIconType(self, _path):
        _file = Path(self.base_path, _path)
        if img_filter.match(_file.suffix):
            return ('', POSIX(_file))
        else:
            return (_file, "./res/svg/archive.svg")
        pass

    def updateItem(self):
        (_user, _time, _text) = self.item
        _user = 'Myself' if _user==MF_HOSTNAME else _user
        _time = datetime.fromtimestamp(int(_time), tz=tzlocal()).strftime('%m-%d %H:%M') #%Y-%m-%d %H:%M:%S
        _text = eval( _text ).strip() #mod
        _text = bold_filter.sub(r'<b>\1</b>', _text)
        _text = italic_filter.sub(r'<i>\1</i>', _text)
        _text = icon_filter.split(_text)
        self.split_text = _text
        
        #NOTE: 1. parse (hint, images, text)
        hint   = ' '.join([_user, _time])
        self.item_icons = _text[1:][::2]
        _text  = ''.join(_text[0:][::2]).strip()
        _text  = _text+'\n' if _text else '' # for QFontMetrics.boundingRect correction
        self.item_text = _text.replace('\n', '<br>')
        
        #NOTE: 2. create widgets
        hint_label = QLabelWrapper('item_hint', hint)
        if self.item_text:
            text_label = QLabelWrapper('item_text', self.item_text)
        # not all item_icons are images, maybe files
        icon_pixmaps = list()
        for _icon in self.item_icons:
            _file, _pixmap = self.getIconType(_icon)
            icon_pixmaps.append( (_file, QPixmap(_pixmap)) )
            pass

        #NOTE: 3. adjust gridlayout
        self.wrapWidget(hint_label, [0,0, 1,3])
        if not self.item_icons:     #text only
            self.wrapWidget(text_label, [1,0, 1,3])
            pass
        elif not self.item_text:    #images only
            CropRect = lambda x: QRect(0, 0, min(MIN_ITEM_SIZE[0]-ITEM_MARGIN*2,   x.width()), MIN_ITEM_SIZE[1])
            for (i,pixmap) in enumerate(icon_pixmaps):
                #
                _file, _pixmap = pixmap
                if _file:
                    icon_label = QLabelWrapper('file_label', pixmap=_pixmap, alt=_file)
                    icon_label.setToolTip(_file.name)
                else:
                    cropped_pixmap = _pixmap.copy( CropRect(_pixmap) )
                    icon_label     = QLabelWrapper('img_label', pixmap=cropped_pixmap, alt=_pixmap)
                #
                self.wrapWidget(icon_label, [i+1,0, 1,3])
                icon_label.setFixedWidth(MIN_ITEM_SIZE[0]-ITEM_MARGIN*2-OFFSET_FIX)
                pass
            pass
        else:                       #mixture
            CropRect = lambda x: QRect(0, 0, min(MIN_ITEM_SIZE[0]/3-ITEM_MARGIN*1, x.width()), MIN_ITEM_SIZE[1])
            for (i,pixmap) in enumerate(icon_pixmaps):
                #
                _file, _pixmap = pixmap
                if _file:
                    icon_label = QLabelWrapper('file_label', pixmap=_pixmap, alt=_file)
                    icon_label.setToolTip(_file.name)
                else:
                    cropped_pixmap = _pixmap.copy( CropRect(_pixmap) )
                    icon_label     = QLabelWrapper('img_label', pixmap=cropped_pixmap, alt=_pixmap)
                #
                self.wrapWidget(icon_label, [i+1,0, 1,1])
                icon_label.setFixedWidth(MIN_ITEM_SIZE[0]/3-ITEM_MARGIN*1-OFFSET_FIX)
                pass
            self.wrapWidget(text_label, [1,1, -1,-1])
            pass
        pass

    def sizeHint(self):
        _height = max( self.size_height.height(), self.size_height.width() )
        return QSize(-1, _height)
    pass

class MFHistoryList(QListWidget):
    def __init__(self, parent, base_path):
        super().__init__(parent)
        self.parent = parent
        self.mdm    = MimeDataManager(base_path)
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
        w_item = self.itemWidget(item)
        raw_item, uri = w_item.item, w_item.uri

        if w_item.double_clicked==0:
            _text = raw_item[2]
            for icon in w_item.item_icons:
                _file, _image = w_item.getIconType(icon)
                if _file:
                    _fake_path = self.mdm.saveFiles([_file])[0]
                else:
                    _fake_path = self.mdm.savePixmap( QPixmap(_image) )
                _text = _text.replace(icon, _fake_path)
                pass
            self.parent.parent.w_editor.insertPlainText( eval(_text)+'\n' )
            self.parent.parent.w_editor.setFocus()
            w_item.double_clicked = 1
            pass
        else:
            self.removeItemWidget(item)
            self.takeItem(self.row(item))
            self.parent.setFocus()
            # remove the images temporarily
            for image in w_item.item_icons:
                self.mdm.remove(image)
                pass
            # remove the record
            _uri, _id = w_item.uri.rsplit(':', 1)
            with open(_uri, 'r+', encoding='utf-8') as f:
                _tmp = f.readlines()
                _idx = _tmp.index(_id)
                _tmp = _tmp[:_idx] + _tmp[_idx+3:]
                f.seek(0); f.writelines(_tmp); f.truncate()
                pass
            pass
        pass
    pass

class MFHistory(QWidget):
    on_lock  = pyqtSignal(object)
    off_lock = pyqtSignal(object)
    set_hint = pyqtSignal(object, str)
    set_progress = pyqtSignal(object, float)

    def __init__(self, parent, base_path, mf_exec):
        super().__init__(parent)
        self.parent    = parent
        self.base_path = base_path
        self.mf_exec   = mf_exec
        self.stp = None
        self.time_type, self.time_anchor = 0, 0
        self.styleHelper()
        pass
    
    def styleHelper(self):
        # set main window layout as grid
        self.grid = QGridLayout()
        self.grid.setSpacing(0)
        self.grid.setContentsMargins(0,0,0,0)
        # add widget into main layout
        self.w_topbar = TopbarManager(self)
        self.w_history_list = MFHistoryList(self, self.base_path)
        self.grid.addWidget(self.w_topbar,       0, 0)
        self.grid.addWidget(self.w_history_list, 1, 0)
        self.setLayout(self.grid)
        self.setFixedSize(*MIN_HISTORY_SIZE)
        self.setVisible(False)
        self.setStyleSheet('''
            QWidget {
                border: 1px solid #5D6D7E;
                border-bottom: 0px solid white;
                background-color: %s;
            }
        '''%(LIST_BACKGROUND))
        pass

    def hideEvent(self, e):
        super().hideEvent(e)
        if not self.isVisible():
            self.w_history_list.clear()
        pass

    def setFocus(self):
        self.parent.setFocus()

    def updateHistory(self, type_delta, anchor_delta, relative=False):
        if not self.isVisible(): return
        #
        mf_type   = (self.time_type+type_delta)     if type_delta is not None else 0
        mf_anchor = (self.time_anchor+anchor_delta) if anchor_delta is not None else 0
        if mf_type >= 4: #reset to today
            mf_type, mf_anchor = 0, 0
            relative = False
        if mf_anchor > 0: return #no future history
        #
        if relative: #relative to previous stp
            self.stp, items = self.mf_exec.mf_fetch(mf_type, mf_anchor, None, stp=self.stp, locate_flag=True)
            self.time_type, self.time_anchor = mf_type, self.stp.diff_time(mf_type) # relative update
        else:
            self.stp, items = self.mf_exec.mf_fetch(mf_type, mf_anchor, None, locate_flag=True)
            self.time_type, self.time_anchor = mf_type, mf_anchor # iteratively update
        #
        self.renderHistory(self.stp, items)
        return self.time_type

    def renderHistory(self, stp, items):
        self.stp = stp
        self.w_history_list.clear()
        self.w_topbar.hint_label.setDateHint(stp)
        
        for item in items:
            w_item = QListWidgetItem(self.w_history_list)
            w_item_widget = MFHistoryItem(w_item, self.base_path, item)
            size_hint = QSize(0, w_item_widget.sizeHint().height()+ITEM_MARGIN) # do not adjust width
            w_item.setSizeHint(size_hint)
            self.w_history_list.addItem(w_item)
            self.w_history_list.setItemWidget(w_item, w_item_widget)
            pass
        pass
    
    def dumpHistory(self, disp):
        self.on_lock.connect(disp.getLock)
        self.off_lock.connect(disp.releaseLock)
        self.set_hint.connect(disp.setHint)
        self.set_progress.connect(disp.setProgressHint)
        #
        self.on_lock.emit(self)
        self.set_progress.emit(self, 0.0)
        #
        _file = 'MFExport %s.md'%self.stp.hint
        if Path('~/Desktop').expanduser().is_dir():
            _path = Path('~/Desktop', _file).expanduser()
        else: #bypass some Windows OneDrive
            _path = Path('~/', _file).expanduser()
        _total = self.w_history_list.count()
        with open( str(_path), 'w+', encoding='utf-8' ) as f:
            f.write('# Mind Flash Export - %s\n'%self.stp.hint)
            for i in range(_total):
                w_item = self.w_history_list.itemWidget( self.w_history_list.item(i) )
                raw_item, uri = w_item.item, w_item.uri
                # dump the history item
                (_user, _time, _) = raw_item
                _date = datetime.fromtimestamp(int(_time), tz=tzlocal()).strftime('%Y-%m-%d %H:%M:%S')
                _text = ''
                for _idx,_raw in enumerate(w_item.split_text):
                    if _idx%2==0:
                        _text += _raw.strip()
                    else:
                        _text += '\n![](%s)\n'%(Path(self.base_path, _raw))
                    pass
                f.write("**`{user}`** `{date}`\n{text}\n\n------\n".format(
                        date=_date, user=_user, text=_text))
                self.set_progress.emit( self, (i+1)/_total )
            pass
        #
        QThread.msleep(1000)
        self.off_lock.emit(self)
        pass
    
    pass