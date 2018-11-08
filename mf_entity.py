#!/usr/bin/python3
import platform
from os import path
from sys import argv
from time import ctime
from getpass import getpass
from termcolor import colored, cprint
from MFUtility import *

MF_HISTORY=path.expanduser('~/.mf/mf_history')
MF_HOSTNAME=platform.node()
MF_CTIME=ctime()
MF_HINT = '>_<: '

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

    def mf_record(self, *args):
        text = args[0]
        stp = TextStamp()
        with workSpace(self.base_path, MF_HOSTNAME, stp.weekno) as wrk:
            with MFRecord(stp.dayno) as rec:
                rec.write(stp.unixtime, text)
                pass
            pass
        pass

    def mf_fetch(self, *args):
        mf_type, mf_anchor, mf_filter = args
        if mf_type==int:
            mf_type = MFRetrieve(mf_type)
        #TODO: aggregate the records of multi-users

        if mf_type==MFRetrieve.DAY:
            stp = TextStamp()
            with workSpace(self.base_path, MF_HOSTNAME, stp.weekno) as wrk:
                with MFRecord(stp.dayno) as rec:
                    return rec.readAll()
                pass
            pass
        elif mf_type==MFRetrieve.WEEK:
            pass
        elif mf_type==MFRetrieve.MONTH:
            pass
        elif mf_type==MFRetrieve.YEAR:
            pass
        else: # retrieve all
            pass
        pass

    def mf_sync(self, *args):
        print('Move the contents in %s to your sync folder! THX!'%(R_T(self.base_path)))
        pass

    def mf_import(self, *args):
        filep = args[0]
        passwd = getpass()
        pass

    def mf_export(self, *args):
        filep = args[0]
        passwd = getpass()
        pass

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
def R_T(text): return colored(text, 'red')
def G_T(text): return colored(text, 'green')
def B_T(text): return colored(text, 'blue')
def C_T(text): return colored(text, 'cyan')
def M_T(text): return colored(text, 'magenta')
def Y_T(text): return colored(text, 'yellow')

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