
from PyQt5.QtWidgets import (QTextEdit, )

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