#!/usr/bin/python3
'''Mind Flash
This is *mf*, a flash pass your mind.
You Write, You Listen.
'''
import sys
import signal, platform
from os import path
from PyQt5 import QtCore
from PyQt5.QtCore import Qt, QPoint, QTimer
from PyQt5.QtGui import QFont, QIcon, QTextOption
from PyQt5.QtWidgets import (QApplication, QWidget, QDesktopWidget, 
                    QLineEdit, QPlainTextEdit, QSizePolicy)

MF_NAME="Mind Flash"
MF_DIR=path.expanduser('~/.mf/')
MF_HOSTNAME=platform.node()

class MFEditor(QPlainTextEdit):

    def __init__(self, parent):
        super().__init__(parent)
        self.parent = parent
        self.press_pos = QPoint(0, 0)
        self.init_pos = self.parent.pos()
        self.styleHelper()
        pass

    def styleHelper(self):
        # Basic Style
        self.setTabChangesFocus(True)
        self.setWordWrapMode(QTextOption.WrapAnywhere)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Expanding)
        self.resize( self.parent.size() )
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

    def keyPressEvent(self, e):
        if e.key()==Qt.Key_Return or e.key()==Qt.Key_Enter:
            self.parent.close()
            pass
        else:
            self.setReadOnly(False)
            super().keyPressEvent(e)
            pass
        pass
    pass

class MFGui(QWidget):
    def __init__(self):
        super().__init__()
        self.resize(600, 70)

        qr = self.frameGeometry()
        cp = QDesktopWidget().availableGeometry().center()
        qr.moveCenter(cp)
        self.move(qr.topLeft())

        self.setWindowTitle(MF_NAME)
        self.setWindowIcon( QIcon('./icons/pulse_heart.png') )
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint)

        editor = MFEditor(self)
        # history = MFWidget(self)
        
        self.show()
        pass

    pass

if __name__ == '__main__':
    signal.signal(signal.SIGINT, signal.SIG_IGN)
    app = QApplication(sys.argv)
    mf = MFGui()
    sys.exit(app.exec_())
    pass