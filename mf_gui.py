#!/usr/bin/python3
'''Mind Flash
This is *mf*, a flash pass your mind.
You Write, You Listen.
'''
import sys, signal, socket
from os import path, getcwd, chdir
from PyQt5.QtCore import Qt, QPoint, QTimer, QMargins
from PyQt5.QtGui import QFont, QIcon, QTextOption
from PyQt5.QtWidgets import (QApplication, QWidget, QDesktopWidget,
                    QGridLayout, QTextEdit, QPlainTextEdit, QSizePolicy)
from mf_entity import MFEntity
from MFUtility import MFRetrieve, KeysReactor

MF_NAME="Mind Flash"
MF_DIR=path.expanduser('~/.mf/')

class MFTextEdit(QPlainTextEdit):
    def __init__(self, parent, w_history):
        super().__init__(parent)
        self.parent = parent
        self.w_history = w_history
        self.press_pos = QPoint(0, 0)
        self.init_pos = self.parent.pos()
        self.styleHelper()
        self.defaultHistory()

        self.keysFn = KeysReactor()
        self.registerKeys()
        pass

    def registerKeys(self):
        ### insert newline ###
        def mf_edit_binding():
            self.setReadOnly(False)
            self.insertPlainText('\n')
            pass
        self.keysFn.register([Qt.Key_Return], mf_edit_binding)

        ### flash recording ###
        def mf_flash_binding():
            mf_text = self.toPlainText()
            if mf_text:
                mf_exec.mf_record( repr(mf_text) )
            self.parent.close()
            pass
        self.keysFn.register([Qt.Key_Control, Qt.Key_Return], mf_flash_binding)

        self.keysFn.register([Qt.Key_Alt, Qt.Key_V], exit)
        self.keysFn.register([Qt.Key_Alt, Qt.Key_V, Qt.Key_V], exit)
        self.keysFn.register([Qt.Key_Alt, Qt.Key_V, Qt.Key_V, Qt.Key_V], exit)
        self.keysFn.register([Qt.Key_Alt, Qt.Key_K], exit)
        self.keysFn.register([Qt.Key_Alt, Qt.Key_J], exit)
        pass

    def defaultHistory(self):
        items = mf_exec.mf_fetch(MFRetrieve.DAY, 0, None)
        #TODO: update the render logic
        for item in items:
            self.w_history.appendItem(item)
        pass

    def styleHelper(self):
        # Basic Style
        self.setStyleSheet("""
            border: 0px solid white;
            border-top: 1px solid #CCCCCC 
        """)
        # self.setStyleSheet("border: 1px solid #CCCCCC")
        self.setFixedSize(600, 70)
        self.setTabChangesFocus(True)
        self.setWordWrapMode(QTextOption.WrapAtWordBoundaryOrAnywhere)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        # Font Style
        self.setFont( QFont('Noto Sans CJK SC',14) )
        # Cursor Style
        QApplication.setOverrideCursor(Qt.ArrowCursor)
        self.setReadOnly(True)
        QTimer.singleShot(500, self.hideCaret)
        pass

    def hideCaret(self):
        self.setReadOnly(True)
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
            # TODO: toggle history widget, remember to cache the dump content
            pass
        pass

    def mouseDoubleClickEvent(self, e):
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
            pass
        self.setFocus() # for convinience
        pass

    def keyPressEvent(self, e):
        returnFn = self.keysFn.pressed(e.key())

        if returnFn:
            returnFn()
        else: #ascii keys
            self.setReadOnly(False)
            super().keyPressEvent(e)
            pass
        pass

    def keyReleaseEvent(self, e):
        self.keysFn.released(e.key())
        pass
    
    pass

class MFHistory(QTextEdit):

    mf_text_wrapper = """
        <div style="{item_css}">
            <a style="{time_css}">{0}</a><br>
            <a style="{text_css}">{1}</a>
        </div>
    """.format(
        '{}', '{}',
        item_css="""
            margin: 5px 5px 5px 5px;
            padding: 1px 1px 1px 1px;
            background-color: #F6F6F6;
        """,
        time_css="""
            color: #B4B5B8;
            font-size: 12px;
        """,
        text_css="""
            color: #252526;
            font-size: 16px;
        """
    )

    def __init__(self, parent):
        super().__init__(parent)
        self.styleHelper()
        pass
    
    def styleHelper(self):
        self.setStyleSheet("""
            border: 0px solid black;
        """)
        self.setReadOnly(True)
        self.setFixedSize(600, 450)
        self.setVisible(False)
        pass

    def appendItem(self, item):
        self.append(self.mf_text_wrapper.format(item[0], item[1]))
        pass

    pass

class MFGui(QWidget):
    def __init__(self):
        super().__init__()

        w_history = MFHistory(self)
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
    # singleton instance using local socket
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