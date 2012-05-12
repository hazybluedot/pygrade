#!/usr/bin/env python2

import fileinput, argparse

if __name__ == '__main__':
    from sys import stderr,stdin,stdout
    import re
    import argparse as ap
    verbose=False

    parser = ap.ArgumentParser(description="Update grade file")
    parser.add_argument('-t', '--total',help="Total number of points to deduct from") 
    parser.add_argument('-v', '--verbose',action='store_true',help="Be verbose")
    parser.add_argument('gradefile', nargs=1, type=argparse.FileType('r'), help=("Grade file"))
    args = parser.parse_args()

    total = float(args.total)
    gradefile = args.gradefile[0]
    if args.verbose:
        verbose = args.verbose

            
    students={}
    for line in stdin:
        (student, diff) = line.split(':')
        if verbose:
            stderr.write("Looking at %s\n" % student)
        try:
            m = re.match(r'([\w-]+), ([\w -]+)\((\w+)\)',student)
            (lastname, firstname, pid) = m.groups(0)
            diff = float(diff)
            if verbose:
                stderr.write("split line into %s, %s and %f\n" % (lastname,firstname, diff))
            students["%s, %s" % (lastname, firstname)]="%.1f" % (total+diff)
        except ValueError,e:
            stderr.write("%s: Could not split\n" % student)

    for gradeline in gradefile:
        for student in students:
            m = re.search(student, gradeline)
            if m:
                fields = gradeline.split(',')
                fields[-1] = students[student]
                print ",".join(fields)
                break
        if not m:
            stdout.write(gradeline)
