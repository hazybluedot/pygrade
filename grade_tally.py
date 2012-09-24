#!/usr/bin/env python2

import fileinput
import re
import argparse
import sys
import ast
import os
import shlex
import scholar

paren_points = re.compile(r'\(([+-][\d]+)\)')
bracket_points = re.compile(r'\[([+-][\d]+)\]')
comments_match = re.compile(r'##.*$')

def collect_points(f):
   tally = 0
   comments = []
   fname = os.path.basename(f.name)
   for (lineno,line) in enumerate(f):
      m = bracket_points.findall(line)
      if m:
         for number in m:
            tally += float(number)
      m = comments_match.search(line)
      if m:
         comments.append((fname, lineno, line))
   return (tally,comments)

def collect_problem(path, problem, **kwargs):
   verbose = False
   if 'verbose' in kwargs:
      verbose = kwargs['verbose']

   points=0
   comments = []
   try:
      with open(os.path.join(path,problem['src']), 'r') as f:
         (points,comments) = collect_points(f)
   except IOError as e:
      points = -int(problem['points'])
      comments.append((problem['src'],0,'Could not find source file\n'))

   subtotal = problem['points']+points
   if verbose:
      sys.stderr.write("\tpoints for {}: {}/{}\n".format(problem['src'],subtotal,problem['points']))
      sys.stderr.writelines("\t{}:{} {}".format(fname,lineno,line) for (fname,lineno,line) in comments if not line.strip() == '###DKM')
   return (subtotal, problem['points'], comments)


if __name__ == "__main__":
   
   parser = argparse.ArgumentParser("Tally up grades for homework")
   parser.add_argument("files", metavar='FILE', nargs="*", help="Path to program to test")
   parser.add_argument("-v","--verbose", action='store_true', help="Be verbose")
   parser.add_argument("-f", type=argparse.FileType('r'), help="Path to homework data file")

   args = parser.parse_args()

   (homework,scholar) = scholar.open_homework(args.f)

   for (pid,path) in map(shlex.split, fileinput.input(args.files)):
      if args.verbose:
         sys.stderr.write("Student: %s\n" % pid)
      
      #for problem in homework['problems']:
      results = [ collect_problem(path,problem,verbose=args.verbose) for problem in homework['problems'] ]
      
      comments_file = scholar.comments_file(pid)

      if args.verbose:
         sys.stderr.write("Writing comments to {}\n".format(comments_file))
         
      student_total = 0
      with open(comments_file, 'w') as f:
         for (problem, (subtotal, outof, comments)) in zip(homework['problems'], results):
            f.write("{}: {}/{}\n".format(problem['src'], subtotal, outof))
            f.writelines("\tline {}: {}".format(lineno, comment) for (fname,lineno,comment) in comments if not comment.strip() == '###DKM' )
            student_total += subtotal
         f.write("\nsubtotal: {}/{}\n".format(student_total, sum(x['points'] for x in homework['problems']))) 
      print "{} {}".format(pid,student_total)
