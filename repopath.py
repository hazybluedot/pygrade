#!/usr/bin/env python2

import re
from itertools import imap
import sys
import os

## Usage example:
## find repos/ -name 'mult*.py' | repopath.py | sort | uniq

repo_path = re.compile(r'(.*)repos/(?P<pid>[^\s/]+)/(?P<path>.*)')

def split_path(path):
    m = repo_path.search(path)
    if m:
        if os.path.isfile(path):
            (path,filename) = os.path.split(path)
        return (m.group('pid'), os.path.realpath(path))

if __name__=='__main__':

    for (pid, path) in imap(split_path, imap(str.strip, sys.stdin)):
        print "{} \"{}\"".format(pid, path)
