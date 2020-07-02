#!/usr/bin/env python3
import sys, time, bisect
import lzma, json, subprocess
from datetime import datetime
from dateutil.relativedelta import FR, MO, SA, SU, TH, TU, WE
from dateutil.relativedelta import relativedelta
from enum import Enum
from os import path, getcwd, chdir, listdir, makedirs
from PyQt5.QtCore import Qt

class MF_RNG(Enum):
    DAY  = 0
    WEEK = 1
    MONTH= 2
    YEAR = 3
    pass

class TextStamp():
    def __init__(self, mf_type=0, mf_anchor=0, now=0):
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
    
    def update_type(self, mf_type, mf_anchor=0):
        if mf_type==MF_RNG.DAY:                        # from 00:00 to 24:00
            tmp = datetime(self.end.year, self.end.month, self.end.day)
            self.end   = tmp + relativedelta(days=mf_anchor)
            self.start = self.end + relativedelta(days=1)
            self.hint  = self.end.strftime('%Y-%m-%d')
        elif mf_type==MF_RNG.WEEK:                     # from MON to SUN
            tmp = datetime(self.end.year, self.end.month, self.end.day)
            mf_anchor  = -1 if mf_anchor==0 else mf_anchor #get last Monday when anchor==0
            self.end   = tmp + relativedelta(weekday=MO(mf_anchor))
            self.start = self.end + relativedelta(days=7)
            self.hint  = self.end.strftime('Week %U, %Y')
        elif mf_type==MF_RNG.MONTH:                    # from 1st to end-th
            tmp = datetime(self.end.year, self.end.month, 1)
            self.end   = tmp + relativedelta(months=mf_anchor)
            self.start = self.end + relativedelta(months=1)
            self.hint  = self.end.strftime('%B, %Y')
        elif mf_type==MF_RNG.YEAR:                     # from Jan to Dec
            self.end   = datetime(self.end.year, 1, 1) + relativedelta(years=mf_anchor)
            self.start = self.end + relativedelta(years=1)
            self.hint  = self.end.strftime('Year %Y')
        else:
            pass
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

    def __init__(self):
        self.key_list = [0x00]
        self.reactor = dict()
        pass
    
    def register(self, keys, hookfn):
        key_hash = [0x00]
        for tmp_key in keys:
            if tmp_key in self.keySpecsKeys: # for specific keys
                key_hash[0] = key_hash[0] | self.keySpecs[tmp_key]
            else:                          # for general keys
                key_hash.append(tmp_key)
            pass
        key_hash = '_'.join([str(x) for x in key_hash])
        self.reactor[key_hash] = hookfn
        pass
    
    def pressed(self, key):
        if key in self.keySpecsKeys:
            self.key_list[0] = self.key_list[0] | self.keySpecs[key] #append specific keys
        else:
            self.key_list.append(key)
        
        key_hash = '_'.join([str(x) for x in self.key_list])
        if key_hash in self.reactor:
            return self.reactor[key_hash] #return the hook function
        else:
            return None
        pass
    
    def released(self, key):
        if key in self.keySpecsKeys:
            self.key_list[0] = self.key_list[0] & (~self.keySpecs[key]) #remove specific keys
            if self.key_list[0]==0x00: # without specific keys present
                self.key_list = [0x00] #reset, if specific keys all released
        elif key in self.key_list:
            self.key_list.remove(key)
        pass

class workSpace:
    def __init__(self, p, *p_l, **kargs):
        self.wrk = expandPath(path.join(p, *p_l))
        self.pwd = getcwd()
        if 'forceUpdate' in kargs.keys():
            self.forceUpdate = True
        else:
            self.forceUpdate = False
        pass
    
    def __enter__(self):
        if not path.isdir(self.wrk):
            if self.forceUpdate:
                makedirs(self.wrk, mode=0o755, exist_ok=True)
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
        if path.exists(self.file):
            fd = open(self.file, 'r')
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
            fd = open(self.file, 'w')
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
        return list(zip(self.time_line, self.text_line, user_hint))

    pass

def isPrefix(sList, fList):
    sList, fList = list(sList), list(fList)
    return sList==fList[:len(sList)]

def listDirs(path_name):
    return [x for x in filter(lambda x:not path.isdir(x), listdir(path_name))]

def expandPath(path_name):
    return path.abspath(path.expanduser(path_name))
