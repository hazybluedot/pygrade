#!/usr/bin/env python2
import scholar
import argparse
import subprocess
import sys
import os

parser = argparse.ArgumentParser("Try to deduce base directory for student by searching for source files")
parser.add_argument("-v","--verbose", action='store_true', help="Be verbose")
parser.add_argument("-f", type=argparse.FileType('r'), help="Path to homework data file")
parser.add_argument("--base-dir", help="Base directory to search in")

args = parser.parse_args()

if __name__=='__main__':
    (homework,scholar) = scholar.open_homework(args.f)
    
    if not os.path.isdir(args.base_dir):
        sys.stderr.write("{}: not a valid directory\n".format(args.base_dir))
        sys.exit(1)
        
    dirs = []
    for problem in homework['problems']:
        (pbase,pfile) = os.path.split(problem['src'])
        find_cmd = ['find', args.base_dir, '-name', pfile ]
        results = subprocess.check_output(find_cmd)
        dirs.extend([ os.path.split(path)[0] for path in results.split("\n") ])

    dirs = list(set(dirs))
    for pid in scholar.pids():
        path = os.path.commonprefix([ entry for entry in dirs if entry.find("{}/".format(pid)) >= 0 ])
        if path:
            print "{} \"{}\"".format(pid, path)
        else:
            sys.stderr.write("No directory found for {}\n".format(pid))
        #for path in results.split("\n"):
        #    print path
