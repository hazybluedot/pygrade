#!/usr/bin/env python2

import yaml
import sys
import shlex
from itertools import imap
import os
from utils import find_key

import subprocess_test as sptest

if __name__=='__main__':
    import argparse
    
    parser = argparse.ArgumentParser("Run tests on homework assignment")
    parser.add_argument("-v", "--verbose", action='store_true', help="Be Verbose")
    parser.add_argument("-f", "--file", type=argparse.FileType('r'), help="input file")
    parser.add_argument("-o", "--output-dir", default=".", help="output directory for reference output")
    args = parser.parse_args()

    myaml = yaml.load(args.file.read())
    teststruct = find_key('tests', myaml)
    file_path = find_key('file_path', myaml)
    
    if args.verbose:
        sys.stderr.write("Found grading struct:\n{0}".format(yaml.dump(teststruct)))
        sys.stderr.write("Running tests in {0} to generate reference output\n".format(file_path))

    output_path = os.path.realpath(args.output_dir)
    if not os.path.isdir(output_path):
        std.stderr.write("{0}: output path must be a valid directory\n")
        sys.exit(1)

    sptest.run_tests(teststruct, base_path=file_path, output_path=output_path)
    #for (pid, project_path) in imap(shlex.split, sys.stdin):
        
