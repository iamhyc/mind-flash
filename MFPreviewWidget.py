#!/usr/bin/env python3
import sys
from PyQt5.QtCore import (Qt, QRect, QSize)
from PyQt5.QtGui import (QFont, QFontMetrics, QIcon)
from PyQt5.QtWidgets import (QApplication, QWidget, QDesktopWidget, QLabel,
                        QLayout, QGridLayout, QPlainTextEdit, QSizePolicy)
from PyQt5.QtGui import (QFont, QFontMetrics, QPixmap, QPainter, QTextDocument)
from MFUtility import KeysReactor

class MFPreviewWidget(QWidget):
    def __init__(self, item):
        super().__init__()
        self.item = item
        pass
    pass

class MFImagePreviewer(QWidget):
    def __init__(self, parent=None, pixmap=None):
        super().__init__(parent, Qt.Dialog)
        self.parent = parent
        self.pixmap = pixmap
        #
        self.grid = QGridLayout()
        self.grid.setSpacing(0)
        self.grid.setContentsMargins(0,0,0,0)
        self.label = QLabel('ImagePreviewer', self)
        self.label.setPixmap(pixmap)
        self.grid.addWidget(self.label, 0, 0)
        self.grid.setSizeConstraint(QLayout.SetFixedSize)
        self.setLayout(self.grid)
        self.resize(self.sizeHint())
        #
        qr = self.frameGeometry()
        cp = QDesktopWidget().availableGeometry().center()
        qr.moveCenter(cp)
        self.move(qr.topLeft())
        #
        self.keysFn = KeysReactor(self)
        self.keysFn.register([Qt.Key_Return], lambda:self.close())
        self.keysFn.register([Qt.Key_Enter],  lambda:self.close())
        #
        self.styleHelper()
        self.setFocus()
        self.show()
        pass

    def styleHelper(self):
        self.setWindowTitle('Image Previewer')
        self.setWindowFlags( Qt.Dialog | Qt.FramelessWindowHint )
        # self.setWindowIcon( QIcon('./res/icons/pulse_heart.png') )
        # self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint)
        # self.setAttribute(Qt.WA_TranslucentBackground, True)
        self.setStyleSheet('''
            QWidget {
                background: rgba(255,254,249, 1.00);
            }
        ''')
        pass

    def mousePressEvent(self, e):
        if e.buttons() & Qt.LeftButton:
            self.press_pos = e.pos()
        elif e.buttons() & Qt.RightButton:
            self.close()
        pass

    def mouseMoveEvent(self, e):
        if e.buttons() & Qt.LeftButton:
            self.move( self.mapToParent(e.pos() - self.press_pos) )
            pass
        elif e.buttons() & Qt.RightButton:
            pass
        pass
    
    def focusOutEvent(self, e):
        self.close()
        pass

    pass

if __name__ == "__main__":
    app = QApplication(sys.argv)
    mf = MFImagePreviewer()
    sys.exit(app.exec_())