#!/usr/bin/env python2

from emacsclient import EmacsClient
from itertools import imap
from sys import stdin, stdout, stderr, exit
from os import path
import argparse
import subprocess
from maybe import maybe

def subprocess_args(script):
    args = [script]
    if path.isfile(script):
        with open(script, 'rb') as f:
            line = f.readline()
            if line.startswith('#!'):
                envargs = line.strip('#!').split()
                dargs = envargs + args
                args = dargs
    return args

def on_suggest(args, **kwargs):
    stderr.write("{}\n".format(args))

def on_review(args, **kwargs):
    stderr.write("reviewing file {}\n".format(args))
    if 'ec' in kwargs:
        kwargs['ec'].open_file(args, nowait=True, **kwargs)
    else:
        stderr.write("Error: on_review, no 'ec' EmacsClient object\n")

def parse_actions(actions, **kwargs): 
    stderr.write("kwargs keys: {}\n".format(kwargs.keys()))
    action_callers = {'review': on_review, 'suggest': on_suggest}
    verbose = maybe(kwargs,'verbose',False)
    if verbose:
        stderr.writelines("action -- {}\n".format(action) for action in actions)
    for (action, args) in imap(lambda x: x.split(':'), actions):
        try:
            action_callers[action](args.strip(), **kwargs)
        except KeyError as e:
            stderr.write("Action '{}' is not implemented\n".format(action))

def signal_handler(signal, frame):
        print 'You pressed Ctrl+C!'
        sys.exit(0)

if __name__=='__main__':

    parser = argparse.ArgumentParser()
    parser.add_argument("--file","-f", help="script file")
    parser.add_argument("-v","--verbose", action='store_true', help="Be verbose")

    args = parser.parse_args()

    #signal.signal(signal.SIGINT, signal_handler)

    if path.isfile(args.file):
        pargs = subprocess_args(args.file)

    ec = EmacsClient()

    for line in imap(lambda x: x.strip("\" \n"), stdin):
        if path.isfile(line):
            stderr.write("{}\n".format(line))
            if args.verbose:
                stderr.write("Running action {} with input {}\n".format(pargs, line))
            aprocess = subprocess.Popen(pargs, shell=False, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            (pout,perr) = aprocess.communicate(line)
            actions = [action for action in (action.strip() for action in pout.split('\n')) if action]
            parse_actions(actions, verbose=args.verbose, ec=ec)
            stderr.write("paction error: {}\n".format(perr))
            try:
                ec.open_file(line)
            except KeyboardInterrupt:
                stdout.write("\n")
                break
            ec.kill_all()
        else:
            stderr.write("{}: Invalid path\n".format(line))
    ec.kill_all()
    
