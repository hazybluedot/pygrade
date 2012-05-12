#!/usr/bin/env python2

import fileinput,re
from sys import stdout, stderr

paren_points = re.compile(r'\(([+-][\d]+)\)')
bracket_points = re.compile(r'\[([+-][\d]+)\]')

if __name__ == "__main__":
   verbose=False
   students = {}
   student=None
   for line in fileinput.input():
      if fileinput.isfirstline():
         m = re.search(r'/([\w, -]+\(\w+\))/', fileinput.filename())
         if m:
            student = m.groups(0)
         else:
            stderr.write("Skipping %s: Could not determine student\n" % fileinput.filename())
            fileinput.nextfile()
            next

         if verbose:
            stderr.write("Student: %s\n" % student)
         students[student] = 0
      m = paren_points.findall(line)
      if m:
         if verbose:
            stderr.write("\t%s: found %r\n" % (fileinput.filename(), m))
         for number in m:
            if verbose:
               stderr.write("\tAdding %f to tally for %s\n" % (float(number), student))
            students[student] += float(number)
      
      
   for student in sorted(students.iterkeys()):
      stdout.write("%s: %f\n" % (student[0], students[student]))
