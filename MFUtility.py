import time, bisect
import lzma, json, subprocess
from datetime import datetime
from os import path, getcwd, chdir, makedirs

class TextStamp():
    def __init__(self):
        self.date = datetime.utcnow()
        self.weekno = self.date.strftime('%Y-%U')
        self.dayno = self.date.strftime('%m-%d')
        self.unixtime = str(int(time.time()))
        pass
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
                fd.write(tt[0] + '\n')
                fd.write(tt[1] + '\n')
                fd.write('\n')
                pass
            pass
        pass

    def write(self, unix, text):
        idx = bisect.bisect_right(self.time_line, unix)
        self.time_line.insert(idx, unix)
        self.text_line.insert(idx, text)
        self.updated = True
        pass

    def read(self, unix):
        idx = self.time_line.index(unix)
        return self.text_line[idx]
        pass

    pass

def isPrefix(sList, fList):
    sList, fList = list(sList), list(fList)
    return sList==fList[:len(sList)]

def expandPath(path_name):
    return path.abspath(path.expanduser(path_name))
