#!/usr/bin/env python3
import re
from pathlib import Path
from datetime import datetime
from dateutil.tz import tzlocal, tzutc
from MFUtility import (POSIX, MF_HOSTNAME, signal_emit,
                        TextStamp, MimeDataManager, MFWorker)
from MFUtility import (icon_filter, link_filter)
from MFPreviewWidget import MFImagePreviewer
from MFHistoryTopbar import TopbarManager
from PyQt5.QtCore import (Qt, QUrl, QMimeData, QRect, QSize, QThread, pyqtSignal, pyqtSlot)
from PyQt5.QtGui import (QColor, QPen, QFont, QFontMetrics,
                        QPainter, QPixmap, QTextDocument, QDesktopServices)
from PyQt5.QtWidgets import (QApplication, QWidget, QFrame, QLabel, QAbstractItemView,
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
FILE_ICON_FONT   = ('Noto Sans CJK SC',11,QFont.Bold)
ICON_HINT_FONT   = ('Noto Sans CJK SC',12,0,1)
LIST_BACKGROUND  = '#FFFEF9' #xuebai
ITEM_BACKGROUND  = '#EEF7F2'
ITEM_BORDERCOLOR = '#DFECD5'
ITEM_MARGIN      = 5#px
ITEM_RADIUS      = 10#px
OFFSET_FIX       = 2#px
MAX_NUM_SCROLL   = 7#wheel

img_filter    = re.compile("\.(gif|jpe?g|tiff?|png|bmp)")
bold_filter   = re.compile("\*\*([^\*]+)\*\*")
italic_filter = re.compile("\*(.*?)\*")

class QLabelWrapper(QLabel):
    def __init__(self, type, text='', pixmap='', alt='', parent=None):
        super().__init__(text)
        self.parent = parent
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
            self.setToolTip(self.alt)
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
            self.setToolTip("View: Left-Click\nCopy: Right-Click")
            pass
        elif self.type=='file_label':
            _pixmap = self.getFileIcon()
            self.setPixmap( _pixmap.scaledToWidth(75, Qt.SmoothTransformation) )
            self.setAlignment(Qt.AlignHCenter | Qt.AlignVCenter)
            pass
        else:
            raise Exception
            pass
        pass

    def getFileIcon(self):
        #
        _text   = Path(self.alt).name
        _suffix = Path(self.alt).suffix.upper()
        _suffix = _suffix[1:] if _suffix else "(Unknown)"
        _pixmap = QPixmap(120, 120); _pixmap.fill(QColor(0,0,0,0))
        _painter= QPainter(_pixmap)
        _painter.setRenderHints(QPainter.Antialiasing|QPainter.TextAntialiasing)
        # draw rounded rect
        _pen = _painter.pen(); _pen.setWidth(2)
        _painter.setPen(_pen)
        _painter.drawRoundedRect(QRect(1,1,118,118), 15, 15)
        # draw suffix text
        _rect = QRect(8, 10, 108, 35)  #100*25
        _painter.setPen(QPen(QColor("#0f59a4")))
        _painter.setFont(QFont(*ICON_HINT_FONT))
        _painter.drawText(_rect, Qt.AlignHCenter|Qt.TextSingleLine, _suffix )
        _painter.setPen(_pen)
        # draw splitter
        _painter.drawLine(1, 40, 118, 40)
        # draw suffix text
        _rect = QRect(8, 45, 108, 110) #100*65
        _painter.setFont(QFont(*FILE_ICON_FONT))
        _fm   = QFontMetrics( _painter.font() )
        # _elided_text = _fm.elidedText(_text, Qt.ElideMiddle, _rect.width(), Qt.TextWrapAnywhere)
        _painter.drawText(_rect, Qt.AlignHCenter|Qt.TextWrapAnywhere, _text )
        del _painter
        return _pixmap

    def mousePressEvent(self, ev):
        if self.type=='img_label' and ev.buttons() & Qt.RightButton:
            _clipboard = QApplication.clipboard()
            if self.alt:
                _clipboard.setPixmap(self.alt)
            else:
                _clipboard.setPixmap(self.pixmap())
            try:
                w_history = self.parent.parent
                _text     = "Image copied."
                self.worker = MFWorker(w_history.showHint,
                                        args=(_text, 1000))
                self.worker.start()
            except Exception:
                pass
            pass
        elif self.type=='img_label' and ev.buttons() & Qt.LeftButton:
            _pixmap = self.alt if self.alt else self.pixmap()
            w_preview = MFImagePreviewer(self, _pixmap)
            pass
        elif self.type=='file_label' and ev.buttons() & Qt.RightButton:
            _clipboard = QApplication.clipboard()
            _mimeData  = QMimeData(); _mimeData.setUrls([ QUrl.fromLocalFile(str(self.alt)) ])
            _clipboard.setMimeData(_mimeData)
            try:
                w_history = self.parent.parent
                _text     = "File <u>%s</u> copied."%self.alt.name
                self.worker = MFWorker(w_history.showHint,
                                        args=(_text, 1600))
                self.worker.start()
            except:
                pass
            pass
        elif self.type=='file_label' and ev.buttons() & Qt.LeftButton:
            QDesktopServices.openUrl(QUrl.fromLocalFile( POSIX(self.alt.parent) ))
            pass
        return super().mousePressEvent(ev)

    pass

class MFHistoryItem(QFrame):
    def __init__(self, parent, w_item, base_path, item):
        super().__init__(None)
        self.parent = parent
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
        _text =''
        if label_ref.text():
            _doc  = QTextDocument(); _doc.setHtml(label_ref.text())
            _text = _doc.toPlainText()
            fm    = QFontMetrics(label_ref.font())
            if label_ref.type=='item_hint':
                fm_rect = QRect(0,0,590,100)
                _height = fm.boundingRect(fm_rect, Qt.TextWordWrap, _text).size().height()
                size   = QSize(_height, _height)
            else:
                fm_rect = QRect(0,0,590,100) if not self.draw_image else QRect(0,0,590/3*2,100)
                _height = fm.boundingRect(fm_rect, Qt.TextWordWrap, _text).size().height()
                size   = QSize(0, _height)
            pass
        else:
            _height = min(label_ref.pixmap().height()+25, MIN_ITEM_SIZE[1])
            size  = QSize(_height, 0)
            pass
        return size

    def wrapWidget(self, ref, pos):
        self.layout.addWidget(ref, *pos)
        self.size_height += self.getHeightHint(ref, pos)
        return ref

    def updateItem(self):
        (_user, _stp, _text) = self.item
        _user = 'Myself' if _user==MF_HOSTNAME else _user
        _time = datetime.fromtimestamp(int(_stp), tz=tzlocal()).strftime('%m-%d %H:%M') #%Y-%m-%d %H:%M:%S
        _text = eval( _text ).strip() #mod
        _text = bold_filter.sub(r'<b>\1</b>', _text)
        _text = italic_filter.sub(r'<i>\1</i>', _text)

        #NOTE: 1. get rich text with regex
        self.draw_image = False
        self.rich_text = list()
        icon_iter = icon_filter.finditer(_text)
        for _icon in icon_iter:
            _path = Path( _icon.groups()[0] )
            if img_filter.match(_path.suffix):
                self.draw_image = True
                self.rich_text.append( (_icon.span(), 'img', POSIX(_path)) )
            else:
                self.draw_image = True
                self.rich_text.append( (_icon.span(), 'file',POSIX(_path)) )
            pass
        link_iter = link_filter.finditer(_text)
        for _link in link_iter:
            _tag, _alt, _path = _link.groups()
            if _tag=='!' or _alt=='img':
                self.draw_image = True
                self.rich_text.append( (_link.span(), 'img', _path) )
            elif _alt=='file':
                self.draw_image = True
                self.rich_text.append( (_link.span(), 'file',_path) )
            else:
                self.rich_text.append( (_link.span(), _alt, _path) )
            pass
        self.rich_text.sort(key=lambda x:x[0][0]) #sort by start of span
        
        #NOTE: 2. get plain text with segment tree
        self.plain_text = list()
        draw_text       = str()
        last_span       = (0, 0)
        for _item in self.rich_text:
            this_span = _item[0]
            self.plain_text.append( _text[last_span[1]:this_span[0]] )
            last_span = this_span
            draw_text += self.plain_text[-1]
            if _item[1] not in ['img','file']:
                _alt = _item[2] if (_item[1] in ['','url']) else _item[1]
                draw_text += '<a href={path}>{alt}</a>'.format(alt=_alt, path=_item[2])
            pass
        self.plain_text.append( _text[last_span[1]:] )
        draw_text += self.plain_text[-1]
        #
        draw_text = draw_text.strip()
        draw_text += '\n' if draw_text else '' # for QFontMetrics.boundingRect correction
        draw_text = draw_text.replace('\n', '<br>')
        
        #NOTE: 3. create hint_label and text_label
        hint_alt   = datetime.fromtimestamp(int(_stp), tz=tzlocal()).strftime('%Y-%m-%d %H:%M:%S')
        hint_label = QLabelWrapper('item_hint', '%s %s'%(_user, _time), alt=hint_alt)
        text_label = QLabelWrapper('item_text', draw_text)

        #NOTE: 4. adjust gridlayout
        self.wrapWidget(hint_label, [0,0, 1,3])
        if not self.draw_image: #text only
            self.wrapWidget(text_label, [1,0, 1,3])
            pass
        else:
            if not draw_text:
                CropRect = lambda x: QRect(0, 0, min(MIN_ITEM_SIZE[0]-ITEM_MARGIN*2,   x.width()), MIN_ITEM_SIZE[1])
                IconSize = (1, 3)
                ImgWidth = MIN_ITEM_SIZE[0]-ITEM_MARGIN*2-OFFSET_FIX
            else:
                CropRect = lambda x: QRect(0, 0, min(MIN_ITEM_SIZE[0]/3-ITEM_MARGIN*1, x.width()), MIN_ITEM_SIZE[1])
                IconSize = (1, 1)
                ImgWidth = MIN_ITEM_SIZE[0]/3-ITEM_MARGIN*1-OFFSET_FIX
            #
            for (i,_item) in enumerate(self.rich_text):
                if _item[1]=='img':
                    _file = Path(self.base_path, _item[2]).as_posix()
                    _pixmap = QPixmap( POSIX(_file) )
                    cropped_pixmap = _pixmap.copy( CropRect(_pixmap) )
                    icon_label     = QLabelWrapper('img_label', pixmap=cropped_pixmap, alt=_pixmap, parent=self)
                elif _item[1]=='file':
                    _file = Path(self.base_path, _item[2])
                    icon_label = QLabelWrapper('file_label', alt=_file, parent=self)
                    icon_label.setToolTip(_file.name)
                else:
                    icon_label = None
                    pass
                #
                self.wrapWidget(icon_label, [*(i+1,0), *IconSize])
                icon_label.setFixedWidth(ImgWidth)
                pass
            #
            if draw_text: self.wrapWidget(text_label, [1,1, -1,-1])
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
        self.base_path = base_path
        self.mdm    = MimeDataManager(base_path)
        self.offset = 0
        self.to_bound = 0
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
        self.setVerticalScrollMode(QAbstractItemView.ScrollPerPixel)
        pass

    def itemDoubleClickEvent(self, item):
        w_item = self.itemWidget(item)
        raw_item, uri = w_item.item, w_item.uri

        if w_item.double_clicked==0:
            _text = raw_item[2]
            for _item in w_item.rich_text:
                if _item[1]=='file':
                    _file = Path(self.base_path, _item[2])
                    _ret = self.mdm.saveFiles([_file])
                    fake_path = _ret[0] if len(_ret)>0 else ''
                    _text = _text.replace(_item[2], fake_path)
                    pass
                elif _item[1]=='img':
                    _file = Path(self.base_path, _item[2]).as_posix()
                    try:
                        fake_path = self.mdm.savePixmap( QPixmap(_file) )
                    except:
                        fake_path = ''
                    finally:
                        _text = _text.replace(_item[2], fake_path)
                    pass
                else:
                    pass
                pass
            _text += '\n' if _text else ''
            self.parent.parent.w_editor.insertPlainText( eval(_text)+'\n' )
            self.parent.parent.w_editor.setFocus()
            w_item.double_clicked = 1
            pass
        else:
            self.removeItemWidget(item)
            self.takeItem(self.row(item))
            self.parent.setFocus()
            # remove the images temporarily
            for _item in w_item.rich_text:
                if _item[1]=='img' or _item[1]=='file':
                    self.mdm.remove(_item[2])
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
    
    def wheelEvent(self, e):
        _offset = self.verticalOffset()
        _move_up = e.angleDelta().y()>0
        if (_move_up and self.offset==0) or (not _move_up and self.offset==_offset):
            self.to_bound += 1
        else:
            self.to_bound = 0
        self.offset = _offset
        #
        if self.to_bound>=MAX_NUM_SCROLL:
            self.to_bound = 0
            _direction = -1 if _move_up else +1
            self.parent.updateHistory(0, _direction)
            pass
        return super().wheelEvent(e)
    pass

class MFHistory(QWidget):
    _signal0 = pyqtSignal()
    _signal1 = pyqtSignal(object)
    _signal2 = pyqtSignal(object,str)
    on_lock  = pyqtSignal(object)
    off_lock = pyqtSignal(object)
    set_hint = pyqtSignal(object, str)
    set_progress = pyqtSignal(object, float)

    def __init__(self, parent, base_path, mf_exec):
        super().__init__(parent)
        self.parent    = parent
        self.base_path = base_path
        self.mf_exec   = mf_exec
        #
        self.filter = None
        self.worker = None
        self.stp    = None
        self.time_type, self.time_anchor = 0, 0
        self.styleHelper()
        #
        _disp = self.w_topbar.hint_label
        self.on_lock.connect(_disp.getLock)
        self.off_lock.connect(_disp.releaseLock)
        self.set_hint.connect(_disp.setHint)
        self.set_progress.connect(_disp.setProgressHint)
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

    def setFilter(self, _filter):
        self.filter = _filter
        self.updateHistory(0, 0)
        pass

    def updateHistory(self, type_delta, anchor_delta, relative=False):
        if not self.isVisible(): return
        if self.worker and self.worker.isRunning():
            self.worker.terminate()
            self.worker.thread.wait()
        #
        mf_type   = (self.time_type+type_delta)     if type_delta is not None else 0
        mf_anchor = (self.time_anchor+anchor_delta) if anchor_delta is not None else 0
        if mf_type >= 4: #reset to today
            mf_type, mf_anchor = 0, 0
            relative = False
        if mf_anchor > 0: return #no future history
        if relative:
            self.stp.update_type(mf_type, mf_anchor)
        else:
            self.stp = TextStamp(mf_type, mf_anchor)
        #
        self.w_topbar.hint_label.setDateHint(self.stp, "(Loading...)")
        self.worker = MFWorker(self._updateHistory,
                                args=(mf_type, mf_anchor, relative))
        self.worker.start()
        return mf_type

    def _updateHistory(self, mf_type, mf_anchor, relative):
        self.items = self.mf_exec.mf_fetch(mf_type, mf_anchor, None, stp=self.stp, locate_flag=True)
        if relative:
            self.time_type, self.time_anchor = mf_type, self.stp.diff_time(mf_type) # relative update
        else:
            self.time_type, self.time_anchor = mf_type, mf_anchor                   # iteratively update
        _postfix = '(filtered)' if self.filter is not None else ''
        signal_emit(self._signal2, self.w_topbar.hint_label.setDateHint, (self.stp, _postfix))
        signal_emit(self._signal1, self.renderHistory, (self.items, ))
        pass

    @pyqtSlot(object)
    def renderHistory(self, items):
        self.w_history_list.clear()
        
        for item in items:
            (_user, _stp, _text) = item[1] #TODO: match user/timestamp/content/<theme>
            if (self.filter is None) or self.filter.search(_text):
                w_item = QListWidgetItem(self.w_history_list)
                w_item_widget = MFHistoryItem(self, w_item, self.base_path, item)
                size_hint = QSize(0, w_item_widget.sizeHint().height()+ITEM_MARGIN) # do not adjust width
                w_item.setSizeHint(size_hint)
                self.w_history_list.addItem(w_item)
                self.w_history_list.setItemWidget(w_item, w_item_widget)
            pass
        pass
    
    def showHint(self, hint, show_ms):
        self.on_lock.emit(self)
        self.set_hint.emit(self, hint)
        if show_ms>=0:
            QThread.msleep(show_ms)
            self.off_lock.emit(self)
        pass

    def dumpHistory(self, disp):
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
                _rich_text = w_item.rich_text.copy()
                for _idx in range(len(w_item.plain_text)):
                    if w_item.plain_text[_idx]=='':
                        if len(_rich_text)==0: continue
                        _item = _rich_text.pop(0)
                        if _item[1]=='img':
                            _file = Path(self.base_path,_item[2])
                            _text += '\n![](%s)\n'%( POSIX(_file) )
                        elif _item[1]=='file':
                            _file = Path(self.base_path,_item[2])
                            _text += '\n[%s](%s)\n'%( _file.name, POSIX(_file) )
                        else:
                            _text += '[%s](%s)'%( _item[1],_item[2] )
                    else:
                        _text += '\n'+w_item.plain_text[_idx].strip()
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