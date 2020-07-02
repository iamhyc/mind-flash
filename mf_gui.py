#!/usr/bin/python3
'''Mind Flash
This is *mf*, a flash pass your mind.
You Write, You Listen.
'''
import sys, signal, socket, time
from os import path, getcwd, chdir
from PyQt5.QtCore import Qt, QObject, QPoint, QTimer, QMargins, QRect
from PyQt5.QtGui import QFont, QFontMetrics, QIcon, QTextOption
from PyQt5.QtWidgets import (QApplication, QWidget, QDesktopWidget,
                    QGridLayout, QPlainTextEdit, QSizePolicy)
from mf_entity import MFEntity
from MFHistoryWidget import MFHistory
from MFTodoWidget import MFTodoWidget
from MFUtility import MF_RNG, KeysReactor

MF_NAME     = 'Mind Flash'
MF_DIR      = path.expanduser('~/.mf/')
FONT_STYLE  = ('Noto Sans CJK SC',14)
MIN_INPUTBOX_SIZE = (600, 70)

class MFTextEdit(QPlainTextEdit):
    def __init__(self, parent, w_history):
        super().__init__(parent)
        self.parent = parent
        self.w_history = w_history
        self.clipboard = QApplication.clipboard()

        self.stp = None
        self.time_type, self.time_anchor = 0, 0
        self.press_pos = QPoint(0, 0)
        self.init_pos = self.parent.pos()
        self.font_style = QFont(*FONT_STYLE)
        self.font_metric= QFontMetrics(self.font_style)
        self.styleHelper()

        self.keysFn = KeysReactor()
        self.registerKeys()
        pass

    def registerKeys(self):
        #NOTE: Ctrl+Return; insert newline
        def mf_edit_binding():
            self.setCursorWidth(1)
            self.insertPlainText('\n')
            pass
        self.keysFn.register([Qt.Key_Control, Qt.Key_Return], mf_edit_binding)

        #NOTE: Return; flash recording
        def mf_flash_binding():
            mf_text = self.toPlainText()
            if mf_text:
                mf_exec.mf_record( repr(mf_text) )
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
                    imagePath = mf_exec.mf_save_pixmap(pixmap)
                    mf_text = "<-file://{}->".format(imagePath)
                    pasteText = self.toPlainText()
                    if pasteText:
                        mf_text = pasteText + '\n' + mf_text
                    mf_exec.mf_record( repr(mf_text) )
                    self.parent.close()
            pass
        self.keysFn.register([Qt.Key_Control, Qt.Key_V], mf_paste_pixmap)

        ### Alt+V ###
        self.keysFn.register(
            [Qt.Key_Alt, Qt.Key_V],
            lambda:self.updateHistory(self.time_type+1, 0, True) if self.time_type+1<4 else self.updateHistory(0, 0)
        )
        ### Alt+J ###
        self.keysFn.register(
            [Qt.Key_Alt, Qt.Key_K], 
            lambda:self.updateHistory(self.time_type, self.time_anchor-1)
        )
        ### Alt+K ###
        self.keysFn.register(
            [Qt.Key_Alt, Qt.Key_J], 
            lambda:self.updateHistory(self.time_type, self.time_anchor+1)
        )
        ### Alt+H ###
        self.keysFn.register(
            [Qt.Key_Alt, Qt.Key_H], 
            lambda:self.toggleHistoryWidget()
        )
        pass

    def updateHistory(self, mf_type, mf_anchor, relative=False):
        if not self.w_history.isVisible(): return
        if mf_anchor > 0: return #no future history
        if relative: #relative to previous stp
            self.stp, items = mf_exec.mf_fetch(mf_type, mf_anchor, None, stp=self.stp)
        else:
            self.stp, items = mf_exec.mf_fetch(mf_type, mf_anchor, None)

        self.time_type, self.time_anchor = mf_type, mf_anchor # iteratively update 
        self.w_history.render(self.stp.hint, items)
        pass

    def styleHelper(self):
        # Basic Style
        self.setStyleSheet("""
            border: 0px solid white;
            border-top: 1px solid #CCCCCC 
        """)
        # self.setStyleSheet("border: 1px solid #CCCCCC")
        self.setFixedSize(*MIN_INPUTBOX_SIZE)
        self.setTabChangesFocus(True)
        self.setWordWrapMode(QTextOption.WrapAtWordBoundaryOrAnywhere)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        # Font Style
        self.setFont(self.font_style)
        # Cursor Style
        QApplication.setOverrideCursor(Qt.ArrowCursor)
        self.setCursorWidth(0)
        self.lastKeyStroke = time.time()
        QTimer.singleShot(500, self.hideCaret)
        pass

    def toggleHistoryWidget(self):
        size_half = self.w_history.height()/2
        if self.w_history.isVisible():
            self.w_history.setVisible(False)
            self.parent.adjustSize()
            self.parent.resize(self.size())
            self.parent.move(self.parent.pos() + QPoint(0, size_half))
            pass
        else:
            self.w_history.setVisible(True)
            self.parent.adjustSize()
            self.parent.move(self.parent.pos() - QPoint(0, size_half))
            self.updateHistory(0, 0) #default history for today
            pass
        self.setFocus() # for convenience
        pass

    def hideCaret(self):
        if time.time() - self.lastKeyStroke > 1.0:
            self.setCursorWidth(0)
        QTimer.singleShot(500, self.hideCaret)
        pass

    def mousePressEvent(self, e):
        self.press_pos = e.pos()
        pass

    def mouseMoveEvent(self, e):
        if e.buttons() & Qt.LeftButton:
            self.parent.move( self.parent.mapToParent(e.pos() - self.press_pos) )
            # print(self.parent.pos() - self.init_pos)
            pass
        elif e.buttons() & Qt.RightButton:
            #TODO: toggle history widget, remember to cache the dump content
            pass
        pass

    def mouseDoubleClickEvent(self, e):
        self.toggleHistoryWidget()
        pass

    def keyPressEvent(self, e):
        returnFn = self.keysFn.pressed(e.key())
        self.setCursorWidth(1)
        self.lastKeyStroke = time.time()

        returnFn() if returnFn else super().keyPressEvent(e)
        pass

    def keyReleaseEvent(self, e):
        self.keysFn.released(e.key())
        pass
    
    pass

class MFGui(QWidget):
    def __init__(self):
        super().__init__()
        self.setAttribute(Qt.WA_InputMethodEnabled)

        w_history = MFHistory(self, MF_DIR)
        w_editor = MFTextEdit(self, w_history)

        grid = QGridLayout()
        grid.setSpacing(0)
        grid.setContentsMargins(0,0,0,0)
        grid.addWidget(w_history, 0, 0)
        grid.addWidget(w_editor, 1, 0)
        self.setLayout(grid)
        self.resize(self.sizeHint())

        qr = self.frameGeometry()
        cp = QDesktopWidget().availableGeometry().center()
        qr.moveCenter(cp)
        self.move(qr.topLeft())

        self.setWindowTitle(MF_NAME)
        self.setWindowIcon( QIcon('./icons/pulse_heart.png') )
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint)
        self.show()
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
    chdir(path.dirname(path.realpath(__file__)))
    # init MF Entity
    mf_exec = MFEntity(MF_DIR)
    # init MF GUI
    app = QApplication(sys.argv)
    mf = MFGui()
    sys.exit(app.exec_())
    pass