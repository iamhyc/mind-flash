#!/usr/bin/env python3
import re
from pathlib import Path
from MFUtility import (CFG, MF_RNG, KeysReactor, MFWorker)
from PyQt5.QtCore import (Qt, QSize, QPoint, QEvent, pyqtSlot)
from PyQt5.QtGui import (QIcon, QFont)
from PyQt5.QtWidgets import (QWidget, QLabel, QPlainTextEdit, QBoxLayout, QGridLayout)

COLOR_WEEKDAY  = ['gold', 'deeppink', 'green', 'darkorange', 'blue', 'indigo', 'red']
TOOL_ICON_NUM     = 3
TOOL_ICONS        = {
    'filter':   {'pos':-1, 'hint':'Filter (Ctrl+F)', 'func':'filterIconEvent'},
    'export':   {'pos':0,  'hint':'Export', 'func':'exportIconEvent'},
    'history':  {'pos':0,  'hint':'History (Alt+V)', 'func':'historyIconEvent'},
    '_'     :   {'pos':0,  'hint':'__space__'},
    'collapse': {'pos':+1, 'hint':'Collapse (Alt+H)', 'func':'collapseIconEvent'}
    }

class HintLabel(QLabel):
    def __init__(self, parent, text=''):
        super().__init__(text, parent)
        self.parent = parent
        self.hint = text
        self.lock = None
        self.styleHelper()
        pass

    def styleHelper(self):
        self.setWordWrap(True)
        self.setFont( CFG.FONT_DEFAULT(self) )
        self.setFixedSize(*CFG.SIZE_TOPBAR_MAIN())
        # self.setAlignment(Qt.AlignHCenter | Qt.AlignCenter)
        pass

    @pyqtSlot(object, str)
    def setHint(self, owner, hint):
        if owner is not self.lock: return
        self.setText(hint)
        pass

    @pyqtSlot(object, str)
    def setDateHint(self, stp=None, postfix=''):
        if stp is None:
            self.hint = self.hint #not change
        elif stp.mf_type==MF_RNG.WEEK or stp.mf_type==MF_RNG.MONTH:
            _month = stp.end.month
            if _month in range(2,5):
                _color = CFG.COLOR_SPRING()
            elif _month in range(5,8):
                _color = CFG.COLOR_SUMMER()
            elif _month in range(8,11):
                _color = CFG.COLOR_AUTUMN()
            else:
                _color = CFG.COLOR_WINTER()
            self.hint = '<a style="color:%s">%s</a>'%(_color, stp.hint)
        elif stp.mf_type==MF_RNG.DAY:
            _color = COLOR_WEEKDAY[ stp.end.weekday() ]
            self.hint = stp.end.strftime('%Y-%m-%d <a style="color:{}">(%a)</a>'.format(_color))
        else:
            self.hint = '<a style="color:black">%s</a>'%(stp.hint)
        
        if self.lock is None:
            self.setText(self.hint + ' ' + postfix)
        pass

    @pyqtSlot(object, float)
    def setProgressHint(self, owner, percentage):
        if owner is not self.lock: return
        
        percentage = max(min(percentage, 1.0), 0.0)
        _text = 'Progress: %.2f'%( percentage*100 )
        if percentage == 1.0:
            _text = 'Done.'
        self.setText(_text)
        pass

    @pyqtSlot(object)
    def getLock(self, owner):
        if self.lock is None:
            self.lock = owner
            return True
        else:
            return False

    @pyqtSlot(object)
    def releaseLock(self, owner):
        if self.lock==owner or self.lock is None:
            self.lock = None
            self.setText(self.hint)
            return True
        else:
            return False
    pass

class InputBox(QPlainTextEdit):
    def __init__(self, parent):
        super().__init__(parent)
        self.parent    = parent
        self.w_history = parent.parent
        self.keysFn = KeysReactor(self)
        self.registerKeys()
        self.styleHelper()
        pass

    def styleHelper(self):
        self.setFont( CFG.FONT_DEFAULT(self) )
        self.setPlaceholderText("Search with Regex ...")
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.setFixedSize(*CFG.SIZE_TOPBAR_MAIN())
        self.setVisible(False)
        pass

    def registerKeys(self):
        self.keysFn.register(CFG.KEYS_EDIT(self), lambda:self.setFilter())
        self.keysFn.register(CFG.KEYS_CLOSE(), lambda:self.focusOut())
        pass

    def setFilter(self):
        _regex = self.toPlainText()
        if len(_regex)>0:
            # _regex = re.sub(r'(?<!\\)\*', "(.*)", _regex)
            _regex = re.compile(_regex, re.IGNORECASE)
            self.w_history.setFilter(_regex)
        else:
            self.w_history.setFilter(None)
        self.focusOut()
        pass

    def focusOut(self):
        self.parent.switch()
        self.w_history.setFocus()
        pass

    def focusOutEvent(self, e):
        if len(self.toPlainText())==0:
            self.w_history.setFilter(None)
        return super().focusOutEvent(e)
    pass

class ToolBarIcon(QLabel):

    def __init__(self, parent, item):
        super().__init__('', parent)
        self.parent = parent
        self.topbar = parent.parent
        self.name   = item[0]
        self.attr   = item[1]
        self.press_pos = QPoint(0, 0)
        self.styleHelper()
        pass

    def styleHelper(self):
        if self.name=='_':
            _width = CFG.SIZE_TOPBAR_MAIN()[0] - CFG.SIZE_TOPBAR_ICON()[0]*TOOL_ICON_NUM - 33 #33 for one rightmost icon
            self.setFixedSize( _width, CFG.SIZE_TOPBAR_MAIN()[1] )
            self.setStyleSheet('QLabel { border-width: 1px 0px 1px 0px; }')
            self.setTextFormat(Qt.RichText)
            self.setTextInteractionFlags(Qt.TextBrowserInteraction)
            self.setOpenExternalLinks(True)
            self.callback = None #TODO: impl. MouseReactor
            return
        
        self.icon_name = self.name
        _icon = QIcon( './res/svg/{}.svg'.format(self.icon_name) ).pixmap( QSize(32,32) )
        self.setPixmap(_icon)
        self.setToolTip(self.attr['hint'])
        self.callback = self.__getattribute__( self.attr['func'] )
        self.setAlignment(Qt.AlignHCenter | Qt.AlignVCenter)

        if self.attr['pos']<0:      #leftmost position
            self.setFixedSize(*CFG.SIZE_TOPBAR_ICON())
            self.setStyleSheet('QLabel { border-width: 1px 1px 1px 1px; }')
        elif self.attr['pos']>0:    #rightmost position
            self.setAlignment(Qt.AlignRight | Qt.AlignTop)
            self.setStyleSheet('QLabel { border-width: 1px 1px 1px 0px; }')
        else:                       #middle position
            self.setFixedSize(*CFG.SIZE_TOPBAR_ICON())
            self.setStyleSheet('QLabel { border-width: 1px 1px 1px 0px; }')
        pass

    def mousePressEvent(self, e):
        self.press_pos = e.pos()
        if e.buttons() & Qt.LeftButton:
            if self.callback: self.callback()
        return super().mousePressEvent(e)
    
    def mouseMoveEvent(self, e):
        if (self.callback is None) and (e.buttons()&Qt.LeftButton):
            _main_body = self.topbar.parent.parent
            _main_body.move( _main_body.mapToParent(e.pos() - self.press_pos) )
            # print(self.parent.pos() - self.init_pos)
            pass
        elif e.buttons() & Qt.RightButton:
            pass
        pass

    def filterIconEvent(self):
        self.topbar.switch( self.topbar.input_box )
        self.topbar.input_box.setFocus()
        pass

    def exportIconEvent(self):
        self.topbar.switch( self.topbar.hint_label )
        self.worker = MFWorker(self.topbar.parent.dumpHistory,
                                args=(self.topbar.hint_label, ))
        self.worker.start()
        pass

    def historyIconEvent(self):
        _icons = ['history', 'history-week', 'history-month', 'history-year']
        #
        _idx = self.topbar.parent.updateHistory(+1, None, True)
        self.icon_name = _icons[_idx]
        _icon = QIcon( './res/svg/{}.svg'.format(self.icon_name) ).pixmap( QSize(32,32) )
        self.setPixmap(_icon)
        pass

    def collapseIconEvent(self):
        self.topbar.parent.parent.w_editor.toggleHistoryWidget()
        pass

    pass

class ToolBar(QWidget):
    def __init__(self, parent):
        super().__init__(parent)
        self.parent = parent
        self.keys   = TOOL_ICONS.keys()
        self.items  = dict()
        self.styleHelper()
        pass

    def styleHelper(self):
        layout = QBoxLayout(QBoxLayout.LeftToRight)
        layout.setSpacing(0)
        layout.setContentsMargins(0,0,0,0)
        for item in TOOL_ICONS.items():
            _name, _attr = item
            self.items[_name] = ToolBarIcon(self, item)
            layout.addWidget( self.items[_name], 0, Qt.AlignJustify )
            pass
        self.setLayout(layout)
        #
        self.setFixedSize(*CFG.SIZE_TOPBAR_MAIN())
        self.setVisible(False)
        self.setStyleSheet( CFG.STYLESHEET(self) )
        pass
    pass

class TopbarManager(QWidget):
    def __init__(self, parent):
        super().__init__(parent)
        self.parent = parent
        self.hint_label = HintLabel(self)
        self.tool_bar   = ToolBar(self)
        self.input_box  = InputBox(self)
        self.w_display  = self.hint_label
        self.styleHelper()
        self.installEventFilter(self)
        pass

    def styleHelper(self):
        self.grid = QGridLayout()
        self.grid.setSpacing(0)
        self.grid.setContentsMargins(0,0,0,0)
        self.grid.addWidget(self.w_display, 0, 0)
        self.setLayout(self.grid)
        self.setFixedSize(*CFG.SIZE_TOPBAR_MAIN())
        self.setStyleSheet( CFG.STYLESHEET(self) )
        pass

    def switch(self, widget=None):
        if widget is None: widget = self.hint_label
        if self.w_display == widget: return

        self.w_display.setVisible(False); widget.setVisible(True)
        self.grid.replaceWidget(self.w_display, widget)
        self.w_display = widget
        pass

    def eventFilter(self, object, event):
        if event.type() == QEvent.Enter:
            self.switch(self.tool_bar)
        elif event.type() == QEvent.Leave:
            self.switch(self.hint_label)
            self.parent.setFocus()
            pass
        return super().eventFilter(object, event)
    pass
