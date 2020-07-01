
import re
from datetime import datetime
from dateutil.tz import tzlocal, tzutc
from PyQt5.QtWidgets import (QTextEdit, )

mf_text_hint = """
        <div style="width:100%;font-weight:bold;padding: 1px 1px 1px 1px">
            <div style="width:100%;font-size:12px;">{}</div>
        </div>
"""

mf_text_wrapper = """
        <div style="{item_css}">
            <a style="{time_css}">{0}</a><br>
            <a style="{text_css}">{1}</a>
        </div>
    """.format(
        '{}', '{}',
        item_css="""
            width:70px;
            display: inline-block;
            margin: 5px 5px 5px 5px;
            background-color: #8c8c8c;
        """,
        time_css="""
            color: #B4B5B8;
            font-size: 14px;
        """,
        text_css="""
            color: #252526;
            font-size: 20px;
        """
    )

class MFHistory(QTextEdit):

    def __init__(self, parent, basePath):
        super().__init__(parent)
        self.basePath = basePath
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

    def render(self, hint, items):
        #TODO: update the render logic
        _textBuffer = [ mf_text_hint.format(hint) ]
        for item in items:
            itime = datetime.fromtimestamp(int(item[0]), tz=tzlocal()).strftime('%Y-%m-%d %H:%M:%S')
            ihint = '%s&nbsp;&nbsp;@&nbsp;&nbsp;%s'%(item[2], itime)
            #FIXME: fix the image style, please!
            itext = re.sub(r'<-file://(\S+)->',r'<img height="100" src="{}\1">'.format(self.basePath), item[1])
            itext = eval( itext.replace('\\n', '<br>') )

            _textBuffer.append(mf_text_wrapper.format(ihint, itext))
        self.setHtml(''.join(_textBuffer))
        pass
    
    pass