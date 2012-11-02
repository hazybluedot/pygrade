#!/usr/bin/env python2

import subprocess
import os
import sys
import shlex
import fileinput
import pickle
import pprint
import copy
import tempfile
import signal
from itertools import imap
import testloader as tl

class Alarm(Exception):
    pass

def alarm_handler(signum, frame):
    raise Alarm

def output_file_names(t, trial_num, output_path, **kwargs):
    verbose = False
    if 'verbose' in kwargs:
        verbose = True

    (basedir,basefile) = os.path.split(t['path'])
    if verbose:
        sys.stderr.write("basedir: {}, basename: {}\n".format(basedir,basefile))
    name = [basefile, '_trial{}'.format(trial_num)]
    if verbose:
        sys.stderr.write("name array: {}\n".format(name))
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
        base_path = "./"

    args = shlex.split(t['env'])

    if 'local-links' in t:
        for link in t['local-links']:
            dest = os.path.join(base_path,os.path.basename(link))
            if os.path.islink(dest):
                os.remove(dest)
            try:               
                if verbose:
                    sys.stderr.write("{} -> {}\n".format(link,dest))
                os.symlink(link,dest)
            except EnvironmentError as e:
                if verbose:
                    sys.stderr.write("{}: {}\n".format(os.path.basename(link), e))

    args.append(t['path'])
    t['cwd'] = base_path
    for (count,trial) in enumerate(t['trials']):
        myargs = args[:]

        for arg in trial['args']:
            myargs.append(arg)

        (of_name, ef_name) = output_file_names(t,count+1,output_path)

        if pretend:
            of_name = '/dev/null'
            ef_name = '/dev/null'

        if verbose:
            sys.stderr.write("stdout file: {}, stderr file: {}\n".format(of_name,ef_name))

        with open(of_name, 'wb') as of, open(ef_name, 'wb') as ef:
            stdin = None
            if 'stdin' in trial and not trial['stdin'] == None:
                stdin = open(trial['stdin'], 'r')

            signal.signal(signal.SIGALRM, alarm_handler)
            signal.alarm(2)  # 2 seconds

            header = "## Trial {}... stdin: {}, args: {}\n".format(count+1, trial['stdin'], trial['args'])
            for flo in [of,ef]:
                flo.write(header)
                if (verbose):
                     flo.write("{}\n".format(myargs))
                flo.flush()

            try:
                if verbose:
                    sys.stderr.write("Trial {}: calling subprocess with args: {}, stdin: {}, stdout: {}\n".format(count+1, myargs,trial['stdin'], of.name))
                trial['status'] = subprocess.call(myargs, stdin=stdin, stdout=of, stderr=ef, cwd=base_path)
                #(stdout_data, stderr_data) = subprocess.communicate(myargs, stdin=stdin, cwd=base_path)
                #trial['status'] = subprocess.wait()
                signal.alarm(0)
            except OSError as e:
                sys.stderr.write("{}: {}\n".format(args[0],e))
            except Alarm as e:
                sys.stderr.write("Timed out\n")
                ef.writelines("Timed out\n")

            signal.alarm(0)
            if hasattr(stdin,'close'):
                stdin.close()
            of.write("%%\n")
            ef.write("%%\n")
            #os.setuid(myuid)
            #for (real_file, temp_file) in zip([of, ef], [temp_of, temp_ef]):
            #    with open(real_file, 'wb') as f:
            #    stderr.write("Writing {} to {}\n".format(temp_file.name, real_file.name))
            #    real_file.writelines(line for line in temp_file)

            trial['args'] = myargs
            trial['stdout'] = of_name
            trial['stderr'] = ef_name
    return t


if __name__ == '__main__':
    import argparse
    verbose = False
    parser = argparse.ArgumentParser(description='Compare the output of a program to a reference program')
    parser.add_argument("files", metavar='FILE', nargs="*", help="Path to program to test")
    parser.add_argument("-v","--verbose", action='store_true', help="Be verbose")
    parser.add_argument("-p","--pretend", action='store_true', help="Run tests but don't write any data")
    parser.add_argument("--ref", type=argparse.FileType('r'), nargs='+', help="Path to reference file")
    parser.add_argument("-r","--raw", action='store_true', help="Read input as raw path to source file")
    parser.add_argument("--basedir", action='store', default=None, help="Base directory to use for reference files")

    args = parser.parse_args()
    if args.verbose:
        verbose=True

    if verbose:
        sys.stderr.write("args: {}\n".format(args))
    tests = tl.load_tests(args.ref,verbose=verbose, basedir=args.basedir)
    for (k,t) in tests.items():
        if verbose:
            sys.stderr.write("Running {} tests on reference program {}, output to {}...\n".format(k, t['path'], t['basedir']))            
            run_tests(t,base_path=t['basedir'],output_path=t['basedir'],verbose=verbose)

    for tokens in map(shlex.split, fileinput.input(args.files)):
        for path in tokens:
            if verbose:
                sys.stderr.write("Running tests on {}\n".format(path))
            
            (basedir,basefile) = os.path.split(path)

            if basefile == t['path']:
                if verbose:
                    sys.stderr.write("Using path as source {}\n".format(basefile))
                path = basedir

            for (k,t) in tests.items():
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
