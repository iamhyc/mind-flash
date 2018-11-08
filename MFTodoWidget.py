
from PyQt5.QtWidgets import (QTextEdit, )

class MFTodoWidget():
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