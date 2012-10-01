#!/usr/bin/env python2

import argparse
import sys
import scholar
from itertools import imap

def update_grades(grades, fin):
    try:
        for (pid,grade) in imap(str.split, fin):
            try:
                grades.set(pid, grade)
            except scholar.ScholarError as e:
                sys.stderr.write("ERROR: {} {}, {}\n".format(pid,grade,e))
            except scholar.GradeError as e:
                sys.stderr.write("ERROR: {} {}, {}\n".format(pid,grade,e))
    except ValueError as e:
        sys.stderr.write("Input format should be 'PID GRADE' per line\n")

if __name__ == '__main__':
    from sys import stderr,stdin,stdout
    import re
    import argparse as ap
    verbose=False

    parser = ap.ArgumentParser(description="Update Scholar grade file")
    parser.add_argument('-v', '--verbose',action='store_true',help="Be verbose")
    parser.add_argument('file', nargs=1, help=("Grade file"))
    args = parser.parse_args()

    ## did we get a scholar archive, or a path to a grades.csv file?
    try:
        sc = scholar.ScholarArchive(args.file[0], 'w')
        with sc.grades('w') as grades:
            update_grades(grades, sys.stdin) ## doesn't work, can't write to file
    except scholar.ScholarError as e:
        ## Not a Scholar Archive
        with scholar.open_grades(args.file[0], 'w') as grades:
            update_grades(grades, sys.stdin) ## this works

