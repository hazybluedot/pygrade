#!/usr/bin/env python2

import os
import sys
import csv 
from errors import *

default_args={ 'idfield': 'Student Id', 'headerlines': 0, 'gradefield': 'iotest part 1' }

letter_grade = { 'A': 100,
                  'A-': 95,
                  'B+': 90,
                  'B': 85,
                  'B-': 80
                  }
def open_grades(name, mode, margs=default_args):
   mmargs=default_args
   if 'name' in margs:
       mmargs['gradefield'] = margs['name']

   class ScholarGrades:
      def __init__(self, f, mode):
         self.file = f
         self.idfield = mmargs['idfield']
         self.gradefield = mmargs['gradefield']
         self.mode = mode
         self.entries = []
         if hasattr(self.file, 'read'):
            self.isflo = True
         else:
            #try:
             self.isflo = False
             self.file = open(f, 'r')
         #else:
         #   raise ScholarError("{0}: Must supply a file-like-object or filename to a Scholar grades.csv file".format(f))
         
         self.__read_entries(self.file)

      def __enter__(self):
         return self

      def set(self, pid, grade):
         try:
            grade = float(grade)
            if grade < 0: 
               raise GradeError("Grade must be positive")

         except ValueError as e:
            grade = letter_grade[grade]
            #raise GradeError("Grade must be a number")
         try:
            record = [ record for record in self.entries if record[self.idfield] == pid ][0]
            record[self.gradefield] = grade
         except IndexError as e:
            raise ScholarError("{}: no such PID".format(pid))

      def __read_entries(self, f):
         sys.stderr.write("Reading entries from {}\n".format(self.file.name))
         self.head=[f.next() for x in xrange(mmargs['headerlines'])]
         reader = csv.DictReader(f)
         self.fields = reader.fieldnames
         if not (self.gradefield in self.fields and self.idfield in self.fields):
            raise ScholarError("{0}: either no '{1}' or '{3}' in fields {2}".format(self.file.name, self.idfield, self.fields, self.gradefield))

         def strip_dict(mydict):
             try:
                 return dict((key.strip(), val.strip()) for (key,val) in mydict.items())
             except AttributeError as e:
                 sys.stderr.write("{0}: {1}\n".format(e,mydict.items()))
                 raise e

         #for entry in reader:
         #    sys.stderr.write("entry: {0}\n".format(strip_dict(entry)))
         self.entries = [ entry for entry in reader ]#[ strip_dict(entry) for entry in reader ]

      def student_list(self):
         return dict([ (entry[self.idfield], 
                          dict([('First Name', entry['First Name']), ('Last Name', entry['Last Name']) ]))
                          for entry in self.entries ] )
      
      def pid_list(self):
         return [ entry['PID'] for entry in self.entries ][:]

      def write(self):
         self.__write(self.file.name)

      def __write(self, flo):
         if mode == 'w':
            writer = csv.DictWriter(flo,self.fields)
            try:
               flo.writelines(self.head)
               writer.writeheader()
               writer.writerows(self.entries)
            except IOError as e:
               raise GradeError("{}: {}".format(flo.name, e))

      def close(self):
         self.file.close()

      def __exit__(self,type,value,traceback):
         if self.mode == 'w':
            if self.isflo:
               self.write()
               self.close()
            else:
               self.__write(sys.stdout)
               #with open(self.file.name, 'wb') as flow:
               #   self.__write(flow)
         
   return ScholarGrades(name, mode)
