#!/usr/bin/env python3
'''Mind Flash
This is *mf*, a flash pass your mind.
You Write, You Listen.
'''
import sys, signal, socket, time
import re
from os import chdir
from pathlib import Path
from PyQt5.QtCore import Qt, QObject, QPoint, QTimer, QMargins, QRect, QSize
from PyQt5.QtGui import (QFont, QFontMetrics, QIcon, QTextOption, QTextDocument)
from PyQt5.QtWidgets import (QApplication, QWidget, QDesktopWidget,
                    QLayout, QGridLayout, QPlainTextEdit, QSizePolicy,
                    QGraphicsDropShadowEffect)
from mf_entity import MFEntity
from MFHistoryWidget import MFHistory
from MFTodoWidget import MFTodoWidget
from MFUtility import MF_RNG, KeysReactor, MimeDataManager

MF_NAME     = 'Mind Flash'
MF_DIR      = Path('~/.mf/').expanduser()
INPUTBOX_FONT  = ('Noto Sans CJK SC',14)
MIN_INPUTBOX_SIZE = (600, 70)
INPUTBOX_RESIZE   = (0,0,0,1,2,3)

mdm = MimeDataManager(MF_DIR)

class MFTextEdit(QPlainTextEdit):
    def __init__(self, parent, w_history, w_todo):
        super().__init__(parent)
        self.parent = parent
        self.w_history = w_history
        self.w_todo = w_todo
        self.clipboard = QApplication.clipboard()
        #
        self.pressed = False
        self.press_pos = QPoint(0, 0)
        self.init_pos = self.parent.pos()
        self.font_style = QFont(*INPUTBOX_FONT)
        self.font_metric= QFontMetrics(self.font_style)
        self.styleHelper()
        #
        self.setAcceptDrops(True)
        self.textChanged.connect(self.textChangedEvent)
        self.keysFn = KeysReactor(self, 'MFTextEdit')
        self.keysFn.setKeyPressHook(self.showCaret)
        self.registerKeys()
        pass
    
    def styleHelper(self):
        # Basic Style
        self.setStyleSheet("""
            QPlainTextEdit {
                border: 1px solid #D7DBDD;
                background: rgba(255,254,249, 0.88)
            }
        """) #background color: #xuebai 
        self.setFixedSize(*MIN_INPUTBOX_SIZE)
        self.setTabChangesFocus(True)
        self.setWordWrapMode(QTextOption.WrapAtWordBoundaryOrAnywhere)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        # Font Style
        self.setFont(self.font_style)
        # Cursor Style
        QApplication.setOverrideCursor(Qt.ArrowCursor)
        self.ensureCursorVisible()
        self.lastKeyStroke = time.time() - 1.0
        self.hideCaret()
        # Placeholder Text
        self.showHelpText()
        pass

    def registerKeys(self):
        #NOTE: Ctrl+Return; insert newline
        def mf_edit_binding():
            self.showCaret()
            self.insertPlainText('\n')
            pass
        self.keysFn.register([Qt.Key_Control, Qt.Key_Return], mf_edit_binding)

        #NOTE: Return; flash recording
        def mf_flash_binding():
            mf_text = self.toPlainText().encode('utf-8').decode('utf-8')
            self.saveFileCache()
            if mf_text:
                mf_exec.mf_record( repr(mf_text.strip()) )
            self.parent.close()
            pass
        self.keysFn.register([Qt.Key_Return], mf_flash_binding)

        #NOTE: Ctrl+V; paste pixmaps
        def mf_paste_pixmap():
            if self.canPaste():
                self.paste()
            else:
                pixmap = self.clipboard.mimeData().imageData()
                if pixmap:
                    fake_path = mdm.savePixmap(pixmap)
                    _text = "<-file://{}->".format(fake_path)
                    self.insertPlainText(_text)
                pass
            pass
        self.keysFn.register([Qt.Key_Control, Qt.Key_V], mf_paste_pixmap)

        #NOTE: Alt+Q; add to todo list
        def mf_add_todo():
            todo_text = self.toPlainText().encode('utf-8').decode('utf-8')
            if todo_text:
                self.clear()
                self.w_todo.todos.append( ['+', todo_text] )
                self.w_todo.saveTodoList()
                self.w_todo.renderTodos()
                pass
            pass
        self.keysFn.register([Qt.Key_Alt, Qt.Key_Q], mf_add_todo)

        ### Alt+V ###
        self.keysFn.register(
            [Qt.Key_Alt, Qt.Key_V],
            lambda:self.w_history.updateHistory(+1, None, True)
        )
        ### Alt+J ###
        self.keysFn.register(
            [Qt.Key_Alt, Qt.Key_J], 
            lambda:self.w_history.updateHistory(0, +1)
        )
        ### Alt+K ###
        self.keysFn.register(
            [Qt.Key_Alt, Qt.Key_K], 
            lambda:self.w_history.updateHistory(0, -1)
        )
        ### Alt+H ###
        self.keysFn.register(
            [Qt.Key_Alt, Qt.Key_H], 
            lambda:self.toggleHistoryWidget()
        )
        pass

    def showHelpText(self):
        if mf_exec.first_run:
            self.setPlaceholderText('Try double click on me!')
        elif mf_exec.no_record:
            self.setPlaceholderText('press ENTER to flush it!')
        else:
            pass
        pass

    def toggleHistoryWidget(self):
        size_half = int( self.w_history.height()/2 )
        if self.w_history.isVisible():  #hide history widget
            self.showHelpText()
            self.parent.grid.replaceWidget(self.w_history, self.w_todo)
            self.w_history.setVisible(False); self.w_todo.setVisible(True)
            self.parent.adjustSize()
            self.parent.resize(self.size())
            self.parent.move(self.parent.pos() + QPoint(0, size_half))
            pass
        else:                           #show history widget
            self.parent.grid.replaceWidget(self.w_todo, self.w_history)
            self.w_todo.setVisible(False); self.w_history.setVisible(True)
            self.parent.adjustSize()
            self.parent.move(self.parent.pos() - QPoint(0, size_half))
            self.w_history.updateHistory(0, 0) #refresh, default history for today
            pass
        self.setFocus() # for convenience
        pass

    def saveFileCache(self):
        icon_filter = re.compile("<-file://(.*?)->")
        _text = icon_filter.split(self.toPlainText())
        image_path = _text[1:][::2]
        for _path in image_path:
            mdm.save(_path)
        pass

    def hideCaret(self):
        if time.time() - self.lastKeyStroke > 1.0:
            # QApplication.setCursorFlashTime(0)
            self.setCursorWidth(0)
        QTimer.singleShot(250, self.hideCaret)
        pass

    def showCaret(self, e=None, force=False):
        # QApplication.setCursorFlashTime(1000)
        self.setCursorWidth(1)
        if force or not self.keysFn.hasSpecsKeys():
            self.lastKeyStroke = time.time()
        pass

    def getLineCount(self):
        _count = 0
        _doc = self.document()
        _it = _doc.begin()
        while _it != _doc.end():
            _count += _it.layout().lineCount()
            _it = _it.next()
        return _count

    def mousePressEvent(self, e):
        self.pressed = True
        self.press_pos = e.pos()
        pass

    def mouseMoveEvent(self, e):
        if (e.buttons()&Qt.LeftButton) and self.pressed:
            self.parent.move( self.parent.mapToParent(e.pos() - self.press_pos) )
            # print(self.parent.pos() - self.init_pos)
            pass
        elif e.buttons() & Qt.RightButton:
            pass
        pass

    def mouseReleaseEvent(self, e):
        self.pressed = False
        return super().mouseReleaseEvent(e)

    def mouseDoubleClickEvent(self, e):
        self.toggleHistoryWidget()
        pass
    
    def textChangedEvent(self):
        _lines = min(self.getLineCount(), len(INPUTBOX_RESIZE)-1)
        _size  = QSize(MIN_INPUTBOX_SIZE[0], 70+35*INPUTBOX_RESIZE[_lines])
        if _size!=self.size():
            self.setFixedSize(MIN_INPUTBOX_SIZE[0], 70+35*INPUTBOX_RESIZE[_lines])
            self.parent.adjustSize()
            self.parent.resize(self.size())
        pass

    def focusInEvent(self, e):
        self.keysFn.clear()
        return super().focusInEvent(e)

    def focusOutEvent(self, e):
        self.keysFn.clear()
        return super().focusOutEvent(e)

    #Reference: https://www.qtcentre.org/threads/33513-QTextEdit-Drag-and-Drop
    def dragEnterEvent(self, e):
        e.accept()
        pass

    def dragMoveEvent(self, e):
        e.accept()
        pass

    def dropEvent(self, e):
        _mime = e.mimeData()
        if _mime.hasUrls():
            url_list = _mime.urls()
            #
            local_urls = list( filter(lambda x:x.isLocalFile(), url_list) )
            if len(local_urls)>0:
                ret = mdm.saveFiles(local_urls)
                ret = ["<-file://{}->".format(_path) for _path in ret]
                _text = '\n'.join(ret)
                self.insertPlainText(_text)
                pass
            #
            web_urls = list( filter(lambda x:not x.isLocalFile(), url_list) )
            if len(web_urls)>0:
                for _url in url_list:
                    _text = '<a href="{url}">{url}</a>\n'.format(url=_url.toString())
                    self.insertPlainText(_text)
                pass
            pass
        elif _mime.hasHtml():
            _doc  = QTextDocument(); _doc.setHtml(_mime.html())
            _text = _doc.toPlainText()
            self.insertPlainText(_text)
            pass
        elif _mime.hasText():
            _text = self.text().strip()
            self.insertPlainText(_text)
            pass
        self.textChangedEvent()
        self.showCaret(force=True)
        self.setFocus()
        pass

    pass

class MFGui(QWidget):
    def __init__(self):
        super().__init__()
        self.mf_exec   = mf_exec
        self.w_todo    = MFTodoWidget(self, MF_DIR, sync=False)
        self.w_history = MFHistory(self,  MF_DIR, mf_exec)
        self.w_editor  = MFTextEdit(self, self.w_history, self.w_todo)
        # set main window layout as grid
        self.grid = QGridLayout()
        self.grid.setSpacing(0)
        self.grid.setContentsMargins(0,0,0,0)
        self.grid.addWidget(self.w_todo, 0, 0)
        self.grid.addWidget(self.w_editor,  1, 0)
        self.grid.setSizeConstraint(QLayout.SetFixedSize)
        self.setLayout(self.grid)
        self.resize(self.sizeHint())
        # register global shortcuts
        self.keysFn = KeysReactor(self, 'MFGui')
        self.registerGlobalKeys()
        # move window to desktop center
        qr = self.frameGeometry()
        cp = QDesktopWidget().availableGeometry().center()
        qr.moveCenter(cp)
        self.move(qr.topLeft())
        # set window style
        self.setWindowTitle(MF_NAME)
        self.setWindowIcon( QIcon('./res/icons/pulse_heart.png') )
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint)
        self.setAttribute(Qt.WA_InputMethodEnabled)
        self.setAttribute(Qt.WA_TranslucentBackground, True)
        self.setContentsMargins(5,5,5,5)
        self.setGraphicsEffect(
            QGraphicsDropShadowEffect(blurRadius=5, xOffset=3, yOffset=3)
        )
        self.setFocus()
        self.show()
        pass

    def registerGlobalKeys(self):
        ### Ctrl+W / Escape ###
        self.keysFn.register([Qt.Key_Control, Qt.Key_W], lambda:self.close())
        self.keysFn.register([Qt.Key_Escape],            lambda:self.close())
        ### Ctrl+L ###
        self.keysFn.register([Qt.Key_Control, Qt.Key_L], lambda:self.setFocus())
        ### Alt+V ###
        self.keysFn.register(
            [Qt.Key_Alt, Qt.Key_V],
            lambda:self.w_history.updateHistory(+1, None, True)
        )
        ### Alt+J ###
        self.keysFn.register(
            [Qt.Key_Alt, Qt.Key_J], 
            lambda:self.w_history.updateHistory(0, +1)
        )
        ### Alt+K ###
        self.keysFn.register(
            [Qt.Key_Alt, Qt.Key_K], 
            lambda:self.w_history.updateHistory(0, -1)
        )
        ### Alt+H ###
        self.keysFn.register(
            [Qt.Key_Alt, Qt.Key_H], 
            lambda:self.w_history.toggleHistoryWidget()
        )
        pass

    def setFocus(self):
        self.w_editor.showCaret(force=True)
        self.w_editor.setFocus()
        pass

    pass

if __name__ == '__main__':
    global mf_exec, mf_sock
    # singleton instance restriction using local socket
    try:
        mf_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        mf_sock.bind(('', 19216))
    except:
        exit()
    # ignore interrupt signal
    signal.signal(signal.SIGINT, signal.SIG_IGN)
    # change workspace root
    chdir( Path(__file__).resolve().parent )
    # init MF Entity
    mf_exec = MFEntity(MF_DIR)
    # init MF GUI
    app = QApplication(sys.argv)
    app.setStyle('Fusion')
    mf = MFGui()
    sys.exit(app.exec_())
    pass