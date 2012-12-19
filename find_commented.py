#!/usr/bin/env python2

import subprocess
import os

def find_commented(fpath, cexp):
    """Return a list of files in fpath containing comments matching cexp"""

    assert os.path.isdir(fpath), 'fpath is a real path'

    fargs = ['find', os.path.realpath(fpath), '-type', 'f', '-exec', 'grep', '-l', cexp, '{}', '+']

    try:
        filelist = subprocess.check_output(fargs)
    except subprocess.CalledProcessError as e:
        return None
    return filelist.split('\n')[:-1]

if __name__ == '__main__':
    import sys
    
    me, fpath, cexp = sys.argv

    filelist = find_commented(fpath,cexp)
    print filelist
