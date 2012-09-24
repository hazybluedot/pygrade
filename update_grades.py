#!/usr/bin/env python2

import fileinput
import argparse
import csv
import sys

if __name__ == '__main__':
    from sys import stderr,stdin,stdout
    import re
    import argparse as ap
    verbose=False

    parser = ap.ArgumentParser(description="Update grade file")
    parser.add_argument('-v', '--verbose',action='store_true',help="Be verbose")
    parser.add_argument('gradefile', nargs=1, type=argparse.FileType('r'), help=("Grade file"))
    args = parser.parse_args()

    gradefile = args.gradefile[0]
            
    line1 = gradefile.readline()
    line2 = gradefile.readline()
    
    reader = csv.DictReader(gradefile)
    fields = reader.fieldnames
    entries = []
    for line in reader:
        entries.append(line)
    gradefile.close()

    for (pid,grade) in map(str.split, sys.stdin):
        for record in entries:
            if record['ID'] == pid:
                record['grade'] = grade
                if args.verbose:
                    sys.stderr.write("Set grade to {} for {}\n".format(record['grade'],pid))

    #out_file = sys.stdout
    with open(gradefile.name, 'wb') as out_file:
        writer = csv.DictWriter(out_file,fields)
        out_file.write(line1)
        out_file.write(line2)
        writer.writeheader()
        writer.writerows(entries)
    
    #for gradeline in gradefile:
    #    for student in students:
    #        m = re.search(student, gradeline)
    #        if m:
    #            fields = gradeline.split(',')
    #            fields[-1] = students[student]
    #            print ",".join(fields)
    #            break
    #    if not m:
    #        stdout.write(gradeline)
