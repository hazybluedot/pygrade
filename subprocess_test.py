#!/usr/bin/env python2

import subprocess
import os
from sys import stderr
import shlex
import fileinput
import pickle

def run_tests(t, **kwargs):
    verbose = True
    if "verbose" in kwargs:
        verbose = kwargs["verbose"]
    if "output_path" in  kwargs:
        output_path = kwargs["output_path"]
    else:
        output_path = "./"

    if "base_path" in  kwargs:
        base_path = kwargs["base_path"]
    else:
        output_path = "./"

    args = shlex.split(t['env'])
    args.append(os.path.join(base_path, t['path']))
    for (count,trial) in enumerate(t['trials']):
        myargs = args
        for arg in trial['args']:
            myargs.append(arg)

        (basedir,basefile) = os.path.split(t['path'])
        if verbose:
            stderr.write("basedir: {}, basename: {}\n".format(basedir,basefile))
        name = [basefile, '_trial{}'.format(count+1)]
        if verbose:
            stderr.write("name array: {}\n".format(name))
        of_name_array = name[:]
        ef_name_array = name[:]
        of_name_array.append('.stdout')
        ef_name_array.append('.stderr')
        of_name = os.path.join(output_path, "".join(of_name_array))
        ef_name = os.path.join(output_path, "".join(ef_name_array))
        if verbose:
            stderr.write("stdout file: {}, stderr file: {}\n".format(of_name,ef_name))

        with open(of_name, 'wb') as of, open(ef_name, 'wb') as ef:
            try:
                trial['status'] = subprocess.check_call(args, stdout=of, stderr=ef)
            except subprocess.CalledProcessError as e:
                pass
            except OSError as e:
                stderr.write("{}: {}\n".format(args[0],e))

            trial['stdout'] = of_name
            trial['stderr'] = ef_name
    return t


if __name__ == '__main__':
    import argparse
    verbose = False
    parser = argparse.ArgumentParser(description='Compare the output of a program to a reference program')
    parser.add_argument("files", metavar='FILE', nargs="*", help="Path to program to test")
    parser.add_argument("-f", help="Name of action file")
    parser.add_argument("-v","--verbose", help="Be verbose")
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
    t = run_tests(t,base_path=basedir,verbose=verbose)

    for path in fileinput.input(args.files):
        if verbose:
            stderr.write("Running tests on {}\n".format(path))
        (basedir,basefile) = os.path.split(path)

        t = run_tests(t, base_path=basedir, output_path=basedir, verbose=verbose)
        file_name = ".".join([basefile.rstrip(), 'test'])
        test_dump = os.path.join(basedir, file_name)
        with open(test_dump, 'wb') as f:
            pickle.dump(t,f)
            print f.name
