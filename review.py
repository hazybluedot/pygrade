#!/usr/bin/env python2

from emacsclient import EmacsClient
from itertools import imap
import yaml
from utils import find_key
import shlex
import sys
import os
import subprocess
import urllib

def first_match(expression):
    for srcfile in expression.split('|'):
        file_path = os.path.join(project_path, srcfile)
        try:
            if os.path.isfile(file_path):
                return file_path
        except TypeError as e:
            sys.stderr.write("{0}: stupid TypeError: {1}\n".format(file_path, e))
            sys.exit(1)
    return None
 
if __name__ == '__main__':
    import argparse
    
    parser = argparse.ArgumentParser("Run tests on homework assignment")
    parser.add_argument("-v", "--verbose", action='store_true', help="Be Verbose")
    parser.add_argument("-f", "--file", type=argparse.FileType('r'), help="input file")
    parser.add_argument("-o", "--output-dir", default=".", help="output directory for reference output")
    parser.add_argument("-n", "--session-name", default="grading", help="Session name")
    args = parser.parse_args()

    myaml = yaml.load(args.file.read())
    reviewstruct = find_key('review', myaml)

    if args.verbose:
        sys.stderr.write("Found review struct: {0}\n".format(reviewstruct))

    ec = EmacsClient(servername=args.session_name)

    for (pid, project_path) in imap(shlex.split, sys.stdin):
        project_path = urllib.unquote(project_path)
        for review in reviewstruct:
            subprocess.call(['tmux', 'send-keys', '-t', 'grading:0.1', "cd \"{path}\"".format(path=os.path.realpath(project_path)), 'C-m'])
            subprocess.call(['tmux', 'send-keys', '-t', 'grading:0.1', "ls *", 'C-m'])
            if 'src' in review:
                actual_files = [ first_match(src_file) for src_file in review['src'] if first_match(src_file) ]
                for review_file in actual_files[:-1]:
                    if args.verbose:
                        sys.stderr.write("Opening {0} for review\n".format(review_file))
                    if review_file:
                        ec.open_file(review_file, nowait=True)
                    else:
                        sys.stderr.write("{0}: file not found\n".format(review['src']))
                ec.open_file(actual_files[-1])
                ec.kill_all()
