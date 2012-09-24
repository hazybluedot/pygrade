#!/usr/bin/env python2

import argparse
import scholar
import shlex
import os
import fileinput
import sys

if __name__=='__main__':

   parser = argparse.ArgumentParser("Tally up grades for homework")
   parser.add_argument("files", metavar='FILE', nargs="*", help="Path to program to test")
   parser.add_argument("-v","--verbose", action='store_true', help="Be verbose")
   parser.add_argument("-f", type=argparse.FileType('r'), help="Path to homework data file")

   args = parser.parse_args()
   
   (homework,scholar) = scholar.open_homework(args.f)

   for (pid,path) in map(shlex.split, fileinput.input(args.files)):
       for problem in homework['problems']:
           src_path = os.path.join(path,problem['src'])
           if os.path.isfile(src_path):
               scholar.copy_to_feedback(pid,src_path)
               if args.verbose:
                   sys.stderr.write("Copying {} to {}'s feedback attachments\n".format(src_path,pid))
