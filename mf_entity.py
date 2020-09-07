#!/usr/bin/env python3
from pathlib import Path
from sys import argv
from time import ctime
from os import system as os_system
# from getpass import getpass
# from termcolor import colored, cprint
from MFUtility import *

MF_CTIME   = ctime()
MF_HINT    = '>_<: '

class MFEntity:

    def __init__(self, base_path):
        self.base_path = base_path
        _path = Path(self.base_path, MF_HOSTNAME)
        self.first_run  = not _path.is_dir()
        try: #NOTE: execute `msh-userfix` for linux users
            if self.first_run: os_system('/usr/bin/msh-userfix')
        except:
            pass
        _path.mkdir(parents=True, exist_ok=True)
        self.no_record  = len( list(_path.glob("*-*")) ) == 0
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
        stp = TextStamp(now=1)

        with workSpace(self.base_path, MF_HOSTNAME, stp.weekno, forceUpdate=True) as wrk:
            with MFRecord(stp.dayno) as rec:
                rec.write(stp.unixtime, text)
                pass
            pass
        pass

    #FIXME: I/O is bottleneck now.
    def mf_fetch(self, *args, **kargs):
        mf_type, mf_anchor, mf_filter = args

        if 'stp' in kargs:
            stp = kargs['stp']
            # stp.update_type(mf_type, mf_anchor)
        else:
            stp = TextStamp(mf_type, mf_anchor)

        if 'locate_flag' in kargs and kargs['locate_flag']:
            locate_flag = True
        else:
            locate_flag = False

        items = list()
        while stp.next():
            for userDir in Path(self.base_path).iterdir():
                userHint = userDir.stem
                # userHint = 'Myself' if userDir.stem==MF_HOSTNAME else userDir.stem
                with workSpace(self.base_path, userDir, stp.weekno) as wrk:
                    with MFRecord(stp.dayno, userHint) as rec:
                        these_items = rec.readAll()
                        if locate_flag:
                            # uri: <userDir>/<weekno>/<stp.dayno>:<unixtime_line>
                            for _item in these_items:
                                _uri = '{path}:{id}'.format(
                                        path=POSIX(Path(userDir, stp.weekno, stp.dayno)), id=_item[1])
                                items.append( (_uri, _item) )
                            pass
                        else:
                            items += these_items
                    pass
                pass
            
            if locate_flag:
                items.sort(key=lambda x:x[1][1])
            else:
                items.sort(key=lambda x:x[1])
            pass
        return items

    def mf_sync(self, *args):
        print('Move the contents in %s to your sync folder! THX!'%(R_T(self.base_path)))
        pass

    def mf_import(self, *args):
        file_path = args[0]
        # passwd = getpass()
        pass

    def mf_export(self, *args):
        file_path = args[0]
        # passwd = getpass()
        pass

    def act_dump(self, *args):
        fd = Path(self.base_path, 'mf_history').open('r+', encoding='utf-8')
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
        e = MFEntity( Path('~/.mf/').expanduser() )
        if len(argv)>1:     # interact with parameters
            e.act(argv[1], argv[2:])
        else:
            e.interact()    # interact with console
    except Exception as e:
        pass
    finally:
        exit()