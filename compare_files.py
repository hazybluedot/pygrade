#!/usr/bin/env python2

import sys
import difflib
import os
import shlex
import ast
import subprocess_test as spt
import pprint 
from itertools import imap
import testloader as tl

def do_refs(ref_test, do):
    for test in ref_test:
        (basedir,filename) = os.path.split(test)
        for (count, trial) in enumerate(ref_test[test]['trials']):
            path = ref_test[test]['path']
            (of_name, ef_name) = spt.output_file_names(ref_test[test],count+1,basedir)
            try:
                do(trial['stdout'])
                do(trial['stderr'])
            except KeyError as e:
                trial['stdout'] = do(of_name)
                trial['stderr'] = do(ef_name)

def open_refs(ref_test):
    do_refs(ref_test, lambda n: open(n,'rd'))

def close_refs(ref_test):
    do_refs(ref_test, lambda s: s.close())

def generate_diff(trial,ref,what): 
    diff_name = ".".join([trial[what],'diff'])
    with open(trial[what], 'rb') as of:
        ref[what].seek(0)
        diff = difflib.context_diff([line for line in of], [line for line in ref[what]], fromfile=of.name, tofile='reference')
        #sys.stderr.write("Comparing {} to reference {}\n".format(of.name,ref[what].name))
        return (diff),

def run_trials(test, path):
    test_file = ".".join([test['path'], "test"])
    test_file = os.path.join(path, test_file)
    try:
        tests = {}
        with open(test_file, 'rb') as f:
            try:
                tests = ast.literal_eval(f.read())
            except SyntaxError as e:
                sys.stderr.write("Syntax error reading {}\n".format(f.name))
                sys.exit(1)

            diff = []
            for (count,(trial,ref)) in enumerate(zip(tests['trials'],test['trials'])):
                try:
                    trial['status'] = (trial['status'],ref['status'])
                except KeyError as e:
                    pass

                diff += generate_diff(trial,ref,'stdout')
                diff += generate_diff(trial,ref,'stderr')

            diff_path = os.path.join(tests['cwd'],"_".join([tests['path'],'trials.diff']))
            with open(diff_path,'wb') as df:
                for item in diff:
                    df.writelines("{}".format(line) for line in item)
                tests['diff'] = df.name

        with open(test_file, 'wb') as f:
            print f.name
            pprint.pprint(tests,f)

    except EnvironmentError as e:
        sys.stderr.write("{}: environment error\n".format(test_file))


if __name__ == '__main__':
    import argparse
    import fileinput

    parser = argparse.ArgumentParser(description='Compare a list of files to reference files')
    
    parser.add_argument("files", metavar='FILE', nargs="*", help="File name to read paths to source files from")
    parser.add_argument("--ref", type=argparse.FileType('r'), nargs='+', help="Path to reference file (.test)")
    parser.add_argument("--verbose","-v", action="store_true", help="Be verbose")

    args = parser.parse_args()

    tl.ref_test = load_tests(args.ref)
    open_refs(ref_test)

    #for (pid,path) in map(shlex.split, fileinput.input(args.files)):
    for path in imap(str.strip, fileinput.input(args.files)):
        if os.path.isfile(path):
            (path,filename) = os.path.split(path)
        for test in ref_test:
            (basedir,filename) = os.path.split(path)
            if filename == ref_test[test]['path']:
                path = basedir
            run_trials(ref_test[test],path)

    close_refs(ref_test)
