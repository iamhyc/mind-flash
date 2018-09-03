#!/usr/bin/python3
import time, bisect
import lzma, json, subprocess
from datetime import datetime
from enum import Enum
from os import path, getcwd, chdir, listdir, makedirs
from PyQt5.QtCore import Qt

class MFRetrieve(Enum):
    DAY  = 1
    WEEK = 2
    MONTH= 3
    YEAR = 4
    ALL  = 5
    pass

class TextStamp():
    def __init__(self):
        self.date = datetime.utcnow()
        self.weekno = self.date.strftime('%Y-%U')
        self.dayno = self.date.strftime('%m-%d')
        self.unixtime = str(int(time.time()))
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
        self.keyL = list(0x00)
        self.reactor = dict()
        pass
    
    def register(self, keys, hookfn):
        a_key = [0x00]
        for tmp in keys:
            if tmp_key in self.keySpecsKeys: # for specific keys
                a_key[0] = a_key[0] | self.keySpecs[tmp_key]
            else:                          # for general keys
                a_key.append(tmp_key)
            pass
        self.reactor[a_key] = hookfn
        pass
    
    def pressed(self, key):
        if key in self.keySpecsKeys:
            self.keyL[0] = self.keyL[0] | self.keySpecs[key] #append specific keys
        else:
            self.keyL.append[key]
        
        if self.keyL in self.reactor:
            return self.reactor[self.keyL] #return the hook function
        else:
            return NULL
        pass
    
    def released(self, key):
        if key in self.keySpecsKeys:
            self.keyL[0] = self.keyL[0] & (~self.keySpecs[key]) #remove specific keys
            if self.keyL[0]==0x00: # without specific keys present
                self.keyL = list(0x00) #reset, if specific keys all released
        pass

class workSpace:
    def __init__(self, p, *p_l):
        self.wrk = expandPath(path.join(p, *p_l))
        makedirs(self.wrk, mode=0o755, exist_ok=True)
        self.pwd = getcwd()
        pass
    
    def __enter__(self):
        chdir(self.wrk)
        return self

    def __exit__(self, exc_type, exc_value, exc_tb):
        chdir(self.pwd)
        if exc_tb: pass
        pass
    pass

class MFRecord:
    def __init__(self, file):
        self.updated = False
        self.file = file
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
        pass

    def readAll(self):
        return zip(self.time_line, self.text_line)
        pass

    pass

def isPrefix(sList, fList):
    sList, fList = list(sList), list(fList)
    return sList==fList[:len(sList)]

def listDirs(path_name):
    filter(path.isdir, listdir(path_name))
    pass

def expandPath(path_name):
    return path.abspath(path.expanduser(path_name))
