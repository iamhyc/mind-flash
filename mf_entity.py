#!/usr/bin/env python3
from os import path
from sys import argv
from time import ctime
# from getpass import getpass
# from termcolor import colored, cprint
from MFUtility import *

MF_CTIME   = ctime()
MF_HINT    = '>_<: '

class MFEntity:

    def __init__(self, base_path):
        self.base_path = base_path
        self.MF_ACTION={
            'dump': self.act_dump,
            'record': self.mf_record,
            'fetch': self.mf_fetch,
            'sync': self.mf_sync, # rsync archived files to/from cloud
            'import': self.mf_import, # import from lzma with private key
            'export': self.mf_export, # export to lzma with private key
        }
        pass

    def mf_save_pixmap(self, *args):
        pixmap = args[0]
        stp = TextStamp(now=1)
        ret = ''

        with workSpace(self.base_path, MF_HOSTNAME, stp.weekno, 'img', forceUpdate=True) as wrk:
            _fileName = 'pasted_%s.png'%(stp.unixtime)
            if pixmap.save(_fileName, 'PNG'):
                ret = '{}/{}/img/{}'.format(MF_HOSTNAME, stp.weekno, _fileName)
            pass
        
        return ret

    def mf_record(self, *args):
        text = args[0]
        stp = TextStamp(now=1)

        with workSpace(self.base_path, MF_HOSTNAME, stp.weekno, forceUpdate=True) as wrk:
            with MFRecord(stp.dayno) as rec:
                rec.write(stp.unixtime, text)
                pass
            pass
        pass

    def mf_fetch(self, *args, **kargs):
        mf_type, mf_anchor, mf_filter = args
        mf_type = MF_RNG(mf_type) if type(mf_type)==int else mf_type
        if 'stp' in kargs:
            stp = kargs['stp']
            stp.update_type(mf_type, mf_anchor)
        else:
            stp = TextStamp(mf_type, mf_anchor)

        items = list()
        while stp.next():
            for userDir in listDirs(self.base_path):
                userHint = 'Myself' if userDir==MF_HOSTNAME else userDir
                with workSpace(self.base_path, userDir, stp.weekno) as wrk:
                    with MFRecord(stp.dayno, userHint) as rec:
                        items += rec.readAll()
                    pass
                items.sort(key=lambda x:x[0])
                pass
            pass
        
        return stp, items

    def mf_sync(self, *args):
        print('Move the contents in %s to your sync folder! THX!'%(R_T(self.base_path)))
        pass

    # def mf_import(self, *args):
    #     file_path = args[0]
    #     passwd = getpass()
    #     pass

    # def mf_export(self, *args):
    #     file_path = args[0]
    #     passwd = getpass()
    #     pass

    def act_dump(self, *args):
        fd = open(path.join(self.base_path, 'mf_history'), 'r+')
        print(fd.read(), end='')
        pass

    def act(self, mf_cmd, *args):
        if mf_cmd in self.MF_ACTION.keys():
            self.MF_ACTION[mf_cmd](args)
        pass

    def interact(self):
        mf_txt = ''
        while True:
            mf_prefix = '[%s @ %s]\n'%(G_T(MF_HOSTNAME), Y_T(MF_CTIME))
            txt = input(MF_HINT)
            if txt=='':
                self.mf_record(mf_txt)
                break
            else:
                mf_txt += txt + '\n'
                pass
            pass
        pass

    pass

'''=================== Utility Function ==================='''
def R_T(text): return text #return colored(text, 'red')
def G_T(text): return text #return colored(text, 'green')
def B_T(text): return text #return colored(text, 'blue')
def C_T(text): return text #return colored(text, 'cyan')
def M_T(text): return text #return colored(text, 'magenta')
def Y_T(text): return text #return colored(text, 'yellow')

'''===================== Main Function ====================='''
if __name__ == '__main__':
    try:
        e = MFEntity(path.expanduser('~/.mf/'))
        if len(argv)>1:     # interact with parameters
            e.act(argv[1], argv[2:])
        else:
            e.interact()    # interact with console
    except Exception as e:
        pass
    finally:
        exit()