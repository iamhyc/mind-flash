#!/usr/bin/env python3
from PyQt5.QtCore import (Qt, QSize)
from PyQt5.QtGui import (QFont, QFontMetrics)
from PyQt5.QtWidgets import (QListWidget, )

MIN_TODO_SIZE = (600, 200)

class MFTodoWidget(QListWidget):
    def __init__(self, parent, base_path):
        super().__init__(parent)
        self.parent    = parent
        self.base_path = base_path
        self.todos     = self.loadTodoList()
        self.clicked.connect(self.addItem)
        self.itemDoubleClicked.connect(self.onItemDoubleClicked)
        self.styleHelper()
        pass

    def styleHelper(self):
        self.setFixedSize(*MIN_TODO_SIZE)
        self.setVisible(False)
        self.setStyleSheet('''
            QListWidget {
                border: 0px;
                background: transparent;
            }
        ''')
        pass

    def saveTodoList(self, clear=False):
        #format: ('+/-', 'text')
        pass

    def loadTodoList(self):
        #format: ('+/-', 'text')
        pass

    def addItem(self, index):
        _text = self.parent.w_editor.toPlainText()
        if _text:
            self.parent.w_editor.clear()
            #TODO: add _text in todo-list
            self.saveTodoList()
            pass
        pass

    def onItemDoubleClicked(self, item):
        #TODO: toggle item strikeline style
        self.saveTodoList()
        pass

    def onAllCompletion(self):
        #TODO: join all list item, and call self.parent.mf_exec.record()
        self.saveTodoList(clear=True)
        pass
    pass

    