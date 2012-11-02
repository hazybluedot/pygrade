#!/usr/bin/env python2

from sys import stdin, stderr, stdout, exit
import testloader as tl
import argparse
import os
import subprocess

if __name__=='__main__':
    parser = argparse.ArgumentParser(description='Compare the output of a program to a reference program')
    parser.add_argument("-v","--verbose", action='store_true', help="Be verbose")
    parser.add_argument("-p","--pretend", action='store_true', help="Run tests but don't write any data")
    parser.add_argument("--ref", type=argparse.FileType('r'), help="Path to reference file")
    parser.add_argument("basedir", nargs=1, help="Base path to search")

    args = parser.parse_args()

    problem_set = tl.load_set(args.ref,verbose=args.verbose, basedir=args.basedir)
    tests = problem_set['problems']
    basedir = args.basedir[0].rstrip("/") + "/"

    if not os.path.isdir(basedir):
        stderr("{}: not a valid directory\n".format(basedir))
        exit(1)

    if args.verbose:
        stderr.writelines("{}: {}\n".format(name, test['path']) for (name,test) in tests.items())

    for (name,test) in tests:
        find_args = ['find', basedir, '-name', test['path'] ]
        if args.verbose:
            stderr.write("{}\n".format(find_args))
        found = subprocess.check_output(find_args).split("\n")
        stdout.writelines(item+"\n" for item in found if len(item) > 1)
