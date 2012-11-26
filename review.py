#!/usr/bin/env python2

from emacsclient import EmacsClient
from itertools import imap
import yaml
from utils import find_key
import shlex
import sys
import os

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
        for review in reviewstruct:
            if 'src' in review:
                for srcfile in review['src'].split('|'):
                    file_path = os.path.join(project_path, review['src'])
                    if os.path.isfile(file_path):
                        if args.verbose:
                            sys.stderr.write("Opening {0} for review\n".format(file_path))
                            ec.open_file(file_path)
                        else:
                            sys.stderr.write("{0}: file not found\n".format(file_path))
