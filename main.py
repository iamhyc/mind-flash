#!/usr/bin/python3
'''Mind Flash
This is *mf*, a flash pass your mind.
You Write, You Listen.
'''
from os import path
from sys import argv
from time import ctime
from termcolor import colored, cprint

MF_HISTORY=path.expanduser('~/.mf/mf_history')
MF_HINT = '> '

'''=================== Utility Function ==================='''
def R_T(text): return colored(text, 'red')
def G_T(text): return colored(text, 'green')
def B_T(text): return colored(text, 'blue')
def C_T(text): return colored(text, 'cyan')
def M_T(text): return colored(text, 'magenta')
def Y_T(text): return colored(text, 'yellow')

'''=================== Private Function ==================='''
def mf_dump():
    fd = open(MF_HISTORY, 'r+')
    print(fd.read())
    pass

MF_ACTION={
    'dump':mf_dump,
    'backup':exit,
}

'''=================== Main Function ==================='''
def mf_main():
    fd = open(MF_HISTORY, 'a+')
    mf_txt = ''
    while True:
        mf_prefix = '[%s]\n'%(Y_T(ctime()))
        txt = input(MF_HINT)
        if txt=='':
            fd.write(mf_prefix + mf_txt + '\n')
            break
        else:
            mf_txt += txt + '\n'
            pass
        pass
    pass

if __name__ == '__main__':
    try:
        if len(argv)>1 and argv[1] in MF_ACTION.keys():
            MF_ACTION[argv[1]]()
        else:
            mf_main()
            pass
    except Exception as e:
        print(e)
    finally:
        exit()