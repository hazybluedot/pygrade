#!/usr/bin/env python2

import grade_tally as gt
import argparse as ap

if __name__ == "__main__":
    from sys import stdin,stderr,stdout,exit
    import csv
    import os
    import markdown

    verbose=False

    parser = ap.ArgumentParser(description='Read a list of comment files with basenames equal to github user names.  Write scholar comments files and updates grades.csv')
    parser.add_argument('csvfile', nargs='?', type=ap.FileType('r'),default=stdin,
                   help='filename of a comma deliminated file containing a list of usernames')
    parser.add_argument('--gradefile', type=ap.FileType('rw'), help='path to Scholar format grades file')
    parser.add_argument('--total-points', type=int, help='Total number of points this assignment has')
    parser.add_argument('--scholar-path', help='Path to Scholar Archive directory') 
    parser.add_argument('-v', '--verbose',action='store_true',help="Be verbose")
    args = parser.parse_args()

    if args.verbose:
        verbose=True

    if args.scholar_path:
        grades_fname = os.path.realpath(os.path.join(args.scholar_path,'grades.csv'))

    file_points = {}
    for line in stdin:
        fname = line.rstrip()
        with open(fname, 'r') as f:
            data = f.read()
            m = gt.bracket_points.findall(data)
            tally=0
            for number in m:
                tally += float(number)
            (gitname,ext) = os.path.splitext(os.path.basename(f.name))
            if (verbose):
                stderr.write("loaded %s: %0.2f\n" % (gitname, tally))
            file_points[gitname] = (data,tally)

    gitusers = {}
    if args.csvfile:
        gitusersFile = csv.reader(args.csvfile)
        for row in gitusersFile:
            if not row[-1]=="":
                gitusers[row[-1].lower()]=row[:-1]

    gradesFile = {}
    if os.path.isfile(grades_fname):
        stderr.write("Opening grades file %s\n" % grades_fname)
        with open(grades_fname,'r') as f:
            gradesFile['header'] = f.readline()
            f.readline()
            gradesFile['fields'] = f.readline()
            gradesFile['data'] = {}
            for row in f:
                fields = row.split(',')
                gradesFile['data'][fields[1]]=fields

    for gitname in file_points:
        points=file_points[gitname][1]
        comments=file_points[gitname][0]
        gitname = gitname.lower()
        try:
            vtpid = gitusers[gitname][2]
            final_points = args.total_points+points
            gradesFile['data'][vtpid][-1] = "%0.1f\n" % final_points
            name_data = gradesFile['data'][vtpid][1:]
            name_dir = "%s,%s(%s)" % (name_data[1], name_data[2], name_data[0])
            comments_file = os.path.join(args.scholar_path,name_dir,'comments.txt')
            if os.path.isfile(comments_file):
                with open(comments_file, 'w') as f:
                    f.write(markdown.markdown(comments))
        except KeyError,e:
            stderr.write("%s: not found in gitusers\n" % gitname)

    stdout.write(gradesFile['header'])
    stdout.write('\n')
    stdout.write(gradesFile['fields'])
    for vtpid in gradesFile['data']:
        stdout.write(','.join(gradesFile['data'][vtpid]))

