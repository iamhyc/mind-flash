#!/usr/bin/env python3
from pathlib import Path
from PyQt5.QtCore import (Qt, QSize, QTimer)
from PyQt5.QtGui import (QColor, QFont, QFontMetrics)
from PyQt5.QtWidgets import (QListWidget, QListWidgetItem)
from MFUtility import POSIX, MF_HOSTNAME

MIN_TODO_SIZE       = (600, 20)
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
        elif stat=='+': #https://www.compart.com/en/unicode/U+25A1
            self.setFont(QFont(*TODO_ITEM_FONT))
            _prefix = b'\xE2\x96\xA1'.decode('utf-8')
            self.setText('{}  {}'.format(_prefix, text))
            pass
        elif stat=='-': #https://www.compart.com/en/unicode/U+25A0
            _font = QFont(*TODO_ITEM_FONT); _font.setStrikeOut(True)
            self.setFont(_font)
            _prefix = b'\xE2\x96\xA0'.decode('utf-8')
            self.setText('{}  {}'.format(_prefix, text))
            pass
        else:
            pass
        
        size_hint = QSize( 0, QFontMetrics(self.font()).height() )
        self.setSizeHint(size_hint)
        pass
    pass

class MFTodoWidget(QListWidget):
    def __init__(self, parent, base_path, sync):
        super().__init__(parent)
        self.parent    = parent
        self.base_path = base_path
        if sync:
            self.todo_file = Path( self.base_path,'todo' )
        else:
            self.todo_file = Path( self.base_path,MF_HOSTNAME,'todo' )
        self.todo_count = 1 # default with title height
        self.todo_file.touch()
        self.todos     = self.loadTodoList()
        self.renderTodos()
        self.styleHelper()
        pass

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
        self.setMaximumHeight(105)
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
        #Reference: https://stackoverflow.com/questions/41517945/how-to-scroll-qlistwidget-to-selected-item
        self.clear(); self.todo_count = 1
        self.addItem( TodoItemWrapper(self, ['title','TODO LIST']) )
        for _todo in sorted(self.todos, key=lambda x:x[0]):
            self.todo_count += 1 if _todo[0]=='+' else 0
            _todo_item = (_todo[0], _todo[1])
            self.addItem( TodoItemWrapper(self, _todo_item) )

        self.alterBackground()
        # _height = sum( [self.sizeHintForRow(i) for i in range(self.todo_count)] ) #self.count()
        # self.setFixedHeight( min(_height,105) )
        pass

    def saveTodoList(self, all_done=False):
        if all_done:
            _record = '\n'.join(['- '+x[1] for x in self.todos])
            _record = 'Completed Todo List:\n' + _record
            self.parent.mf_exec.mf_record( repr(_record) ) #record todo list
            open(str(self.todo_file), 'w', encoding='utf-8').close() #erase todo file
            QTimer.singleShot(300, self.safe_close) #deferred exit
            pass
        else:
            #format: ('+/-', 'text')
            with open(str(self.todo_file), 'w', encoding='utf-8') as fout:
                _tmp = [' '.join(x) for x in self.todos]
                fout.write( '\n'.join(_tmp) )
                pass
        pass

    def loadTodoList(self):
        #format: ('+/-', 'text')
        with open(str(self.todo_file), 'r', encoding='utf-8') as fin:
            raw_text  = fin.read().strip()
            raw_todos = raw_text.splitlines()
            return [x.split(maxsplit=1) for x in raw_todos]
            pass
        pass

    def removeTodoItem(self, item):
        item_text = item.text().split(maxsplit=1)[1]
        try:
            index = list(zip(*self.todos))[1].index(item_text)
        except Exception:
            return False
        
        self.todos.pop(index)
        self.takeItem(self.row(item))
        self.renderTodos()
        pass

    def toggleTodoItem(self, item):
        item_text = item.text().split(maxsplit=1)[1]
        try:
            index = list(zip(*self.todos))[1].index(item_text)
        except Exception:
            return False
        # toggle the item
        _status = item.font().strikeOut()
        self.todos[index][0] = '+' if _status else '-' #update todo_list
        item.updateItem(self.todos[index])  #update todo_item
        # check all items
        all_status = [x[0]=='-' for x in self.todos]
        all_done   = not (False in all_status)
        return all_done

    def mouseDoubleClickEvent(self, e):
        if e.buttons() & Qt.LeftButton:
            _item = self.itemAt(e.pos())
            if _item:
                self.removeTodoItem(_item)
                self.saveTodoList()
                # if self.count()<=1:
                #     QTimer.singleShot(300, self.safe_close) #deferred exit
                self.parent.setFocus()
            pass
        return super().mouseDoubleClickEvent(e)

    def mousePressEvent(self, e):
        if e.buttons() & Qt.RightButton:
            _item = self.itemAt(e.pos())
            if _item:
                all_done = self.toggleTodoItem(_item)
                self.saveTodoList(all_done)
                self.parent.setFocus()
            pass
        return super().mousePressEvent(e)
    
    def sizeHint(self):
        height = sum( [self.sizeHintForRow(i) for i in range(self.todo_count)] ) #self.count()
        return QSize(600, height)

    def safe_close(self):
        all_status = [x[0]=='-' for x in self.todos]
        all_done   = not (False in all_status)
        if all_done:
            self.parent.close()
        pass
    pass
