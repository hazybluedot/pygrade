#!/usr/bin/env python2

import subprocess
import os
from sys import stderr,exit
import shlex
import fileinput
import pickle
import pprint
import copy

def output_file_names(t, trial_num, output_path, **kwargs):
    verbose = False
    if 'verbose' in kwargs:
        verbose = True

    (basedir,basefile) = os.path.split(t['path'])
    if verbose:
        stderr.write("basedir: {}, basename: {}\n".format(basedir,basefile))
    name = [basefile, '_trial{}'.format(trial_num)]
    if verbose:
        stderr.write("name array: {}\n".format(name))
    of_name_array = name[:]
    ef_name_array = name[:]
    of_name_array.append('.stdout')
    ef_name_array.append('.stderr')
    of_name = os.path.join(output_path, "".join(of_name_array))
    ef_name = os.path.join(output_path, "".join(ef_name_array))
    return (of_name, ef_name)

def run_tests(ref, **kwargs):
    t = copy.deepcopy(ref)
    verbose = True
    pretend = False
    if "verbose" in kwargs:
        verbose = kwargs["verbose"]
    if "pretend" in kwargs:
        pretend = kwargs["pretend"]
    if "output_path" in  kwargs:
        output_path = kwargs["output_path"]
    else:
        output_path = "./"
    
    if "base_path" in  kwargs:
        base_path = kwargs["base_path"]
    else:
        output_path = "./"

    args = shlex.split(t['env'])

    if 'local-links' in t:
        for link in t['local-links']:
            try:
                os.symlink(link,os.path.join(base_path,os.path.basename(link)))
            except EnvironmentError as e:
                pass 

    args.append(t['path'])
    t['cwd'] = base_path
    for (count,trial) in enumerate(t['trials']):
        myargs = args
        for arg in trial['args']:
            myargs.append(arg)

        (of_name, ef_name) = output_file_names(t,count+1,output_path)
        if pretend:
            of_name = '/dev/null'
            ef_name = '/dev/null'

        if verbose:
            stderr.write("stdout file: {}, stderr file: {}\n".format(of_name,ef_name))

        with open(of_name, 'wb') as of, open(ef_name, 'wb') as ef:
            try:
                trial['status'] = subprocess.check_call(myargs, stdout=of, stderr=ef, cwd=base_path)
            except subprocess.CalledProcessError as e:
                pass
            except OSError as e:
                stderr.write("{}: {}\n".format(args[0],e))
            trial['args'] = myargs
            trial['stdout'] = of_name
            trial['stderr'] = ef_name
    return t


if __name__ == '__main__':
    import argparse
    verbose = False
    parser = argparse.ArgumentParser(description='Compare the output of a program to a reference program')
    parser.add_argument("files", metavar='FILE', nargs="*", help="Path to program to test")
    parser.add_argument("-f", help="Name of action file")
    parser.add_argument("-v","--verbose", action='store_true', help="Be verbose")
    parser.add_argument("-p","--pretend", action='store_true', help="Run tests but don't write any data")
    parser.add_argument("--ref", type=argparse.FileType('r'), help="Path to reference file")

    args = parser.parse_args()
    if args.verbose:
        verbose=True

    if verbose:
        stderr.write("args: {}\n".format(args))
    (basedir,basefile) = os.path.split(args.ref.name)
    if verbose:
        stderr.write("basedir: {}, basename: {}\n".format(basedir,basefile))

    data = args.ref.read()
    t = eval(data,{"__builtins__":None})
    if verbose:
        stderr.write("Running tests on reference program...\n")
    run_tests(t,base_path=basedir,output_path=basedir,verbose=verbose)

    #for (pid,path) in map(shlex.split, fileinput.input(args.files)):
    for path in map(str.strip, fileinput.input(args.files)):
        if verbose:
            stderr.write("Running tests on {}\n".format(path))
        (basedir,basefile) = os.path.split(path)

        if basefile == t['path']:
            if verbose:
                stderr.write("Using path as source {}\n".format(basefile))
            path = basedir

        results = run_tests(t, base_path=path, output_path=path, verbose=verbose, pretend=args.pretend)
        file_name = ".".join([t['path'], 'test'])
        test_dump = os.path.join(path, file_name)
        if not args.pretend:
            with open(test_dump, 'wb') as f:
                pprint.pprint(results,f)
                print "{}".format(os.path.realpath(f.name))
                #return "'" + s.replace("'", "'\\''") + "'"
        else:
            print "Pretending to write to {}".format(test_dump)
