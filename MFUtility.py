#!/usr/bin/env python3
import locale
import sys, bisect, platform
import tempfile, shutil
from os import chdir
from pathlib import Path
from enum import Enum
from PyQt5.QtCore import (Qt, QObject, QThread, pyqtSignal, pyqtSlot)
from datetime import datetime
from dateutil.relativedelta import FR, MO, SA, SU, TH, TU, WE
from dateutil.relativedelta import relativedelta

MF_HOSTNAME= platform.node().split('-')[0]
# locale.setlocale(locale.LC_ALL, "en_GB.utf8")

class MF_RNG(Enum):
    DAY  = 0
    WEEK = 1
    MONTH= 2
    YEAR = 3
    pass

class TextStamp():
    def __init__(self, mf_type=0, mf_anchor=0, now=0):
        self.mf_type = mf_type
        self.start,  self.end,   self.hint     = None, None, None
        self.weekno, self.dayno, self.unixtime = None, None, None
        self.end = datetime.now()
        self.back_stepper = relativedelta(days=-1)
        
        if not now:
            self.update_type(mf_type, mf_anchor)
            self.update_hint()
        else:
            self.start = self.end
            self.update_hint()
        pass

    def diff_time(self, mf_type):
        _diff = relativedelta(self.end, datetime.now())
        mf_type = MF_RNG(mf_type) if type(mf_type)==int else mf_type
        if mf_type==MF_RNG.DAY:
            return _diff.days
        elif mf_type==MF_RNG.WEEK:
            return _diff.weeks
        elif mf_type==MF_RNG.MONTH:
            return _diff.months
        elif mf_type==MF_RNG.YEAR:
            return _diff.years
        else:
            return _diff
        pass

    def update_type(self, mf_type, mf_anchor=0):
        if mf_type==MF_RNG.DAY:                        # from 00:00 to 24:00
            tmp = datetime(self.end.year, self.end.month, self.end.day)
            self.end   = tmp + relativedelta(days=mf_anchor)
            self.start = self.end + relativedelta(days=1)
            self.hint  = self.end.strftime('%Y-%m-%d (%a)')
        elif mf_type==MF_RNG.WEEK:                     # from MON to SUN
            tmp = datetime(self.end.year, self.end.month, self.end.day)
            mf_anchor  = -1 if mf_anchor==0 else mf_anchor #FIXME: get last Monday when anchor==0
            self.end   = tmp + relativedelta(weekday=MO(mf_anchor))
            self.start = self.end + relativedelta(days=7)
            self.hint  = self.end.strftime('Week %U (%b), %Y')
        elif mf_type==MF_RNG.MONTH:                    # from 1st to end-th
            tmp = datetime(self.end.year, self.end.month, 1)
            self.end   = tmp + relativedelta(months=mf_anchor)
            self.start = self.end + relativedelta(months=1)
            self.hint  = self.end.strftime('%b, %Y')
        elif mf_type==MF_RNG.YEAR:                     # from Jan to Dec
            self.end   = datetime(self.end.year, 1, 1) + relativedelta(years=mf_anchor)
            self.start = self.end + relativedelta(years=1)
            self.hint  = self.end.strftime('Year %Y')
        else:
            return
        self.mf_type = mf_type
        pass

    def next(self):
        if self.start + self.back_stepper < self.end:
            return False
        self.start += self.back_stepper
        self.update_hint()
        return True

    def update_hint(self):
        self.weekno   = self.start.strftime('%Y-%U')
        self.dayno    = self.start.strftime('%m-%d')
        self.unixtime = str(int( self.start.timestamp() ))
        pass

    pass

class KeysReactor():

    keySpecs = {
        Qt.Key_Control: 0x01,
        Qt.Key_Alt:     0x02,
        Qt.Key_Shift:   0x04
    }
    keySpecsKeys = keySpecs.keys()

    def __init__(self, parent, name='Default'):
        self.name = name
        self.key_list = [0x00]
        self.reactor  = dict()
        self.press_hook_pre    = None
        self.press_hook_post   = None
        self.release_hook_pre  = None
        self.release_hook_post = None

        if parent:
            self.parent = parent
            self.super  = super(type(parent), parent)
            parent.keyPressEvent   = lambda e: self.pressed(e.key(), e)
            parent.keyReleaseEvent = lambda e: self.released(e.key(), e)
        pass
    
    def __str__(self):
        ret = []
        ret.append('Ctrl')  if self.key_list[0]&0x01 else None
        ret.append('Alt')   if self.key_list[0]&0x02 else None
        ret.append('Shift') if self.key_list[0]&0x04 else None
        ret += [str(x) for x in self.key_list[1:]]
        return '[%s] %s'%(self.name, '+'.join(ret))
    
    def register(self, keys, hookfn):
        key_hash = [0x00]
        for tmp_key in keys:
            if tmp_key in self.keySpecsKeys: # for specific keys
                key_hash[0] = key_hash[0] | self.keySpecs[tmp_key]
            else:                            # for general keys
                key_hash.append(tmp_key)
            pass
        key_hash = '_'.join([str(x) for x in key_hash])
        self.reactor[key_hash] = hookfn
        pass
    
    def pressed(self, key, e=None):
        #NOTE: pre hook
        if self.press_hook_pre:
            self.press_hook_pre(e)

        #NOTE: press keys
        if key in self.keySpecsKeys:
            self.key_list[0] = self.key_list[0] | self.keySpecs[key] #append specific keys
        else:
            self.key_list.append(key)
        key_hash = '_'.join([str(x) for x in self.key_list])
        if key_hash in self.reactor:
            ret = self.reactor[key_hash]() #unused ret code
        else:
            self.super.keyPressEvent(e)
        
        #NOTE: post hook
        if self.press_hook_post:
            self.press_hook_post(e)
        pass
    
    def released(self, key, e=None):
        #NOTE: pre hook
        if self.release_hook_pre:
            self.release_hook_pre(e)
        
        #NOTE: remove keys
        if key in self.keySpecsKeys:    # remove a special key
            self.key_list[0] = self.key_list[0] & (~self.keySpecs[key]) #remove specific keys
        elif key in self.key_list:      # remove a common key
            self.key_list.remove(key)
        self.super.keyReleaseEvent(e)
        if self.key_list[0]==0x00: #reset, if no specific keys presented
            self.key_list = [0x00]

        #NOTE: post hook
        if self.release_hook_post:
            self.release_hook_post(e)
        pass

    def hasSpecsKeys(self):
        return self.key_list[0] != 0x00

    def clear(self):
        self.key_list = [0x00]
        pass

    def setKeyPressHook(self, press_hook, post=True):
        if post:
            self.press_hook_post = press_hook
        else:
            self.press_hook_pre  = press_hook
        pass

    def setKeyReleaseHook(self, release_hook, post=True):
        if post:
            self.release_hook_post = release_hook
        else:
            self.release_hook_pre  = release_hook
        pass

    pass

class MouseReactor(object):

    MOVEWINDOW_EVENT  = 0x01
    LEFTCLICK_EVENT   = 0x02
    RIGHTCLICK_EVENT  = 0x04
    DOUBLECLICK_EVENT = 0x08
    LEFTLONGPRESS_EVENT  = 0x10
    RIGHTLONGPRESS_EVENT = 0X20

    def __init__(self, parent):
        left_clicked,    right_clicked    =  0,  0
        left_clicked_ts, right_clicked_ts = -1, -1
        pass

    #def LeftDoubleClickEvent(self, e):
    #def RightClickEvent(self, e):
    #def LeftLongPressEvent(self, e):
    #def RightLongPressEvent(self, e):

    pass

class workSpace:
    def __init__(self, p, *p_l, **kargs):
        self.wrk = Path(p, *p_l).expanduser().resolve()
        self.pwd = Path.cwd()
        if 'forceUpdate' in kargs.keys():
            self.forceUpdate = True
        else:
            self.forceUpdate = False
        pass
    
    def __enter__(self):
        if not Path(self.wrk).is_dir():
            if self.forceUpdate:
                Path(self.wrk).mkdir(mode=0o755, exist_ok=True)
            else:
                return self.__exit__(*sys.exc_info())
        else:
            pass
        chdir(self.wrk)
        return self

    def __exit__(self, exc_type, exc_value, exc_tb):
        chdir(self.pwd)
        if exc_tb: pass
        pass
    pass

class MFRecord:
    def __init__(self, file, hint=''):
        self.updated = False
        self.file = file
        self.hint = hint
        pass

    def __enter__(self):
        if Path(self.file).exists():
            fd = open(self.file, 'r', encoding='utf-8')
            lines = fd.readlines()
            fd.close()

            self.time_line = lines[0::3]
            self.text_line = lines[1::3]
            pass
        else:
            self.time_line, self.text_line = list(), list()
            pass
        
        return self
    
    def __exit__(self, exc_type, exc_value, exc_tb):
        if exc_value: raise
        if self.updated:
            fd = open(self.file, 'w', encoding='utf-8')
            for tt in zip(self.time_line, self.text_line):
                fd.write(tt[0])
                fd.write(tt[1])
                fd.write('\n')
                pass
            pass
        pass

    def write(self, unix, text):
        idx = bisect.bisect_right(self.time_line, unix)
        self.time_line.insert(idx, unix+'\n')
        self.text_line.insert(idx, text+'\n')
        self.updated = True
        pass

    def read(self, unix):
        idx = self.time_line.index(unix)
        return self.text_line[idx]

    def readAll(self):
        user_hint = [self.hint] * len(self.time_line)
        return list( zip(user_hint, self.time_line, self.text_line) )

    pass

class MimeDataManager:
    def __init__(self, base_path):
        self.temp = tempfile.gettempdir()
        self.home = base_path
        pass

    def savePixmap(self, pixmap):
        _stp  = TextStamp(now=1)
        _file = 'pasted_%s.png'%_stp.unixtime
        _path = str( Path(self.temp, _file) )
        pixmap.save(_path, 'PNG')
        _fake_path = Path(MF_HOSTNAME, _stp.weekno, 'img', _file)
        return _fake_path

    def saveFiles(self, files):
        _stp = TextStamp(now=1)
        # _folder = 'archived_%s'%_stp.unixtime
        
        _fake_path = Path(MF_HOSTNAME, _stp.weekno, 'files')
        _temp_path = Path(self.temp)
        ret = list()
        for _url in files:
            _file = Path( _url.toLocalFile() )
            shutil.copy( str(_file), _temp_path )
            ret.append( str(Path(_fake_path, _file.name)) )
            pass
        return ret

    def save(self, real_path):
        temp_path = Path(self.temp, Path(real_path).name)
        home_path = Path(self.home, real_path)
        if temp_path.is_file():
            Path(home_path.parent).mkdir(mode=0o755, exist_ok=True)
            shutil.copy2( str(temp_path), str(home_path) )
            return True
        else:
            return False
        pass
    
    def remove(self, real_path):
        # temp_path = Path(self.temp, Path(real_path).name)
        # home_path = Path(self.home, real_path)
        # try:
        #     shutil.move( str(home_path), str(temp_path) )
        #     return True
        # except:
        #     return False
        #FIXME: need to keep track of reference, so not delete for now
        return False
    pass

class MFWorker(QObject):
    def __init__(self, func, args=None):
        super().__init__(None)
        self.func = func
        self.args = args
        self.thread = QThread()
        self.moveToThread(self.thread)
        self.thread.started.connect(self.run)
        pass

    def isRunning(self):
        return self.thread.isRunning()

    def start(self):
        self.thread.start()
        pass
    
    def terminate(self):
        self.thread.exit(0)
        pass

    def run(self):
        if self.args:
            self.func(*self.args)
        else:
            self.func()
        self.thread.exit(0)
        pass
    pass