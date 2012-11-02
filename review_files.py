#!/usr/bin/env python2

from emacsclient import EmacsClient
from itertools import imap
from sys import stdin, stdout, stderr, exit
from os import path
import argparse
import subprocess
from maybe import maybe
import imp

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

def on_test(args, **kwargs):
    stderr.write("running test: {}\n".format(args))
    

def on_suggest(args, **kwargs):
    stderr.write("{}\n".format(args))

def on_review(args, **kwargs):
    #stderr.write("reviewing file {}\n".format(args))
    if 'ec' in kwargs:
        kwargs['ec'].open_file(args, **kwargs)
    else:
        stderr.write("Error: on_review, no 'ec' EmacsClient object\n")

def parse_actions(actions, **kwargs): 
    stderr.write("kwargs keys: {}\n".format(kwargs.keys()))
    to_review = []
    action_callers = {'review': lambda x,**k: to_review.append(x), 'suggest': on_suggest, 'test': on_test}
    verbose = maybe(kwargs,'verbose',False)
    if verbose:
        stderr.writelines("action -- {}\n".format(action) for action in actions)
    for (action, args) in imap(lambda x: x.split(':'), actions):
        try:
            action_callers[action](args.strip(), **kwargs)
        except KeyError as e:
            stderr.write("Action '{}' is not implemented\n".format(action))

    stderr.write("Reviewing: {}\n".format(to_review))
    kwargs['nowait']=True
    for review in to_review[:-1]:
        on_review(review, **kwargs)
    kwargs['nowait']=False
    on_review(to_review[-1], **kwargs)
        
if __name__=='__main__':

    parser = argparse.ArgumentParser()
    parser.add_argument("--file","-f", help="script file")
    parser.add_argument("-v","--verbose", action='store_true', help="Be verbose")

    args = parser.parse_args()

    #signal.signal(signal.SIGINT, signal_handler)

    if path.isfile(args.file):
        pargs = subprocess_args(args.file)
        (module_name,dot,ext) = args.file.partition('.')
        action = imp.load_source(module_name, args.file)
    else:
        stderr.write("{}: could not find action file\n".format(args.file))
        exit(1)
    ec = EmacsClient(servername=action.session_name())

    for line in imap(lambda x: x.strip("\" \n"), stdin):
        if path.isfile(line) or path.isdir(line):
            stderr.write("{}\n".format(line))
            if args.verbose:
                stderr.write("Running action {} with input {}\n".format(pargs, line))
            aprocess = subprocess.Popen(pargs, shell=False, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            (pout,perr) = aprocess.communicate(line)
            actions = [action for action in (action.strip() for action in pout.split('\n')) if action]
            parse_actions(actions, verbose=args.verbose, ec=ec)
            stderr.write("paction error: {}\n".format(perr))
            ec.kill_all()
        else:
            stderr.write("{}: Invalid path\n".format(line))
    ec.kill_all()
    
