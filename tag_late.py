#!/usr/bin/env python2

from sys import stdin, stderr, stdout
import testloader as tl
import argparse
from itertools import imap
import os
import subprocess
import StringIO
from datetime import datetime, timedelta

if __name__=='__main__':
    parser = argparse.ArgumentParser(description='Compare the output of a program to a reference program')
    parser.add_argument("-v","--verbose", action='store_true', help="Be verbose")
    parser.add_argument("-p","--pretend", action='store_true', help="Run tests but don't write any data")
    parser.add_argument("--ref", type=argparse.FileType('r'), help="Path to reference file")
    parser.add_argument("--basedir", action='store', default=None, help="Base directory to use for reference files")
    
    args = parser.parse_args()

    problem_set = tl.load_set(args.ref,verbose=args.verbose, basedir=args.basedir)
    tests = problem_set['problems']
    duedate = datetime.strptime(problem_set['due'], "%B %d, %Y %I:%M%p")

    if args.verbose:
        stderr.writelines("{}: {}\n".format(name, test['path']) for (name,test) in tests.items())

    for line in imap(str.strip, stdin):
        if not os.path.isfile(line):
            stderr.write("{}: expected a source file\n".format(line))
        (basedir,path) = os.path.split(line)
        pid = basedir.split('/')[1]
        git_args = ['git','log','-1',r'--format="%ad"', r'--date=local', r'--', path]
        #git_args = ['git','log','-1', r'--', path]
        try:
            mdate = subprocess.check_output(git_args, stderr=stderr, cwd=basedir)
        except subprocess.CalledProcessError as e:
            stderr.write("{}: {}\n".format(line,e))
        try:
            subdate = datetime.strptime(mdate.strip("\"\n"), "%a %b %d %H:%M:%S %Y")  
            pastdue = subdate-duedate
            if pastdue > timedelta():
                print "{}: {} ({})".format(pid, path, pastdue)
        except ValueError as e:
            stderr.write("{}: {}\n".format(path, e))
