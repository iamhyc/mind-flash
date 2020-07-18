#!/usr/bin/env python3
from pathlib import Path
from PyQt5.QtCore import (Qt, QSize, QTimer)
from PyQt5.QtGui import (QColor, QFont, QFontMetrics)
from PyQt5.QtWidgets import (QListWidget, QListWidgetItem)
from MFUtility import MF_HOSTNAME

MIN_TODO_SIZE       = (600, 70)
TODO_ITEM_FONT      = ('Noto Sans CJK SC',12)
TODO_TITLE_FONT     = ('Noto Sans CJK SC',8,QFont.Bold)
TODO_TITLE_FONT_ALT = ('Noto Sans CJK SC',8,-1,True)
TODO_BACKGROUND     = 'rgba(255,255,255, 0.25)'
TODO_BACKGROUND_ALT = 'rgba(255,255,255, 0.00)'

class TodoItemWrapper(QListWidgetItem):
    def __init__(self, parent, todo_item):
        super().__init__(parent, 0)
        self.parent = parent
        self.todo_item = todo_item
        self.updateItem(todo_item)
        pass

    def updateItem(self, todo_item):
        self.todo_item = todo_item
        stat, text = todo_item
        if stat=='title':
            self.setFlags(self.flags() & (not Qt.ItemIsSelectable))
            self.setFont(QFont(*TODO_TITLE_FONT))
            self.setText(text)
            pass
        elif stat=='+':
            self.setFont(QFont(*TODO_ITEM_FONT))
            _prefix = b'\xE2\x96\xA2'.decode('utf-8')
            self.setText('{}  {}'.format(_prefix, text))
            pass
        elif stat=='-':
            _font = QFont(*TODO_ITEM_FONT); _font.setStrikeOut(True)
            self.setFont(_font)
            _prefix = b'\xE2\x96\xA0'.decode('utf-8')
            self.setText('{}  {}'.format(_prefix, text))
            pass
        else:
            pass
        pass
    pass

class MFTodoWidget(QListWidget):
    def __init__(self, parent, base_path):
        super().__init__(parent)
        self.parent    = parent
        self.base_path = base_path
        self.todo_file = Path( self.base_path,MF_HOSTNAME,'todo' )
        self.todo_file.touch()
        self.todos     = self.loadTodoList()
        self.renderTodos()
        self.styleHelper()
        pass

    #FIXME: fix height hint, and minimum height
    def alterBackground(self):
        if self.count() > 1:
            background_color = TODO_BACKGROUND
            self.item(0).setFont( QFont(*TODO_TITLE_FONT) )
            self.item(0).setForeground(QColor('black'))
        else:
            background_color = TODO_BACKGROUND_ALT
            self.item(0).setFont( QFont(*TODO_TITLE_FONT_ALT) )
            self.item(0).setForeground(QColor('#BDC3C7'))
        
        self.setStyleSheet('''
            QListWidget {
                border: 0px;
                background: %s;
            }
        '''%(background_color))
        pass

    def styleHelper(self):
        # self.setFixedSize(*MIN_TODO_SIZE)
        self.setMinimumSize(*MIN_TODO_SIZE)
        self.setVisible(True)
        self.verticalScrollBar().setStyleSheet("""
            QScrollBar:vertical {
                border: none;
                background:palette(base);
                width:3px;
                margin: 0px 0px 0px 0px;
            }
            QScrollBar::handle:vertical {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                stop: 0 rgb(32, 47, 130), stop: 0.5 rgb(32, 47, 130), stop:1 rgb(32, 47, 130));
                min-height: 0px;
            }
            QScrollBar::add-line:vertical {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                stop: 0 rgb(32, 47, 130), stop: 0.5 rgb(32, 47, 130),  stop:1 rgb(32, 47, 130));
                height: 0px;
                subcontrol-position: bottom;
                subcontrol-origin: margin;
            }
            QScrollBar::sub-line:vertical {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                stop: 0  rgb(32, 47, 130), stop: 0.5 rgb(32, 47, 130),  stop:1 rgb(32, 47, 130));
                height: 0 px;
                subcontrol-position: top;
                subcontrol-origin: margin;
            }
        """)
        pass

    def renderTodos(self):
        self.clear()
        
        self.addItem( TodoItemWrapper(self, ['title','TODO LIST']) )
        for _todo in self.todos:
            _todo_item = (_todo[0], _todo[1])
            self.addItem( TodoItemWrapper(self, _todo_item) )

        self.alterBackground()
        self.resize(self.size())
        pass

    def saveTodoList(self, all_done=False):
        if all_done:
            _record = '\n'.join(['- '+x[1] for x in self.todos])
            _record = 'Completed Todo List:\n' + _record
            self.parent.mf_exec.mf_record( repr(_record) ) #record todo list
            open(str(self.todo_file), 'w').close() #erase todo file
            QTimer.singleShot(300, self.safe_close) #deferred exit
            pass
        else:
            #format: ('+/-', 'text')
            with open(str(self.todo_file), 'w') as fout:
                _tmp = [' '.join(x) for x in self.todos]
                fout.write( '\n'.join(_tmp) )
                pass
        pass

    def loadTodoList(self):
        #format: ('+/-', 'text')
        with open(str(self.todo_file), 'r') as fin:
            raw_text  = fin.read().strip()
            raw_todos = raw_text.splitlines()
            return [x.split(maxsplit=1) for x in raw_todos]
            pass
        pass

    def toggleItemStatus(self, item):
        _index = self.row(item)-1
        if _index<0: return False
        # toggle the item
        _status = item.font().strikeOut()
        self.todos[_index][0] = '+' if _status else '-' #update todo_list
        item.updateItem(self.todos[_index])  #update todo_item
        # check all items
        all_status = [x[0]=='-' for x in self.todos]
        all_done   = not (False in all_status)
        return all_done

    def mousePressEvent(self, e):
        if e.buttons() & Qt.RightButton:
            _item = self.itemAt(e.pos())
            if _item:
                all_done = self.toggleItemStatus(_item)
                self.saveTodoList(all_done)
            pass
        return super().mousePressEvent(e)
    
    def safe_close(self):
        all_status = [x[0]=='-' for x in self.todos]
        all_done   = not (False in all_status)
        if all_done:
            self.parent.close()
        pass
    pass
