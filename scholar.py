import shutil
import os
import re
import ast
import markdown
import codecs
from zipfile import ZipFile, BadZipfile
import sys
import csv
from itertools import imap
import tempfile

class ScholarError(Exception):
   pass

class GradeError(ValueError):
   pass

def open_grades(name, mode):
   class ScholarGrades:
      def __init__(self, f, mode):
         self.file = f
         self.mode = mode
         self.entries = []
         if hasattr(self.file, 'read'):
            self.isflo = True
         elif os.path.isfile(f):
            self.isflo = False
            self.file = open(f, 'r')
         else:
            raise ScholarException("Must supply a file-like-object or filename to a Scholar grades.csv file")
         
         self.__read_entries(self.file)

      def __enter__(self):
         return self

      def set(self, pid, grade):
         try:
            grade = float(grade)
            if grade < 0: 
               raise GradeError("Grade must be positive")

         except ValueError as e:
            raise GradeError("Grade must be a number")
         try:
            record = [ record for record in self.entries if record['ID'] == pid ][0]
            record['grade'] = grade
         except IndexError as e:
            raise ScholarError("{}: no such PID".format(pid))

      def __read_entries(self, f):
         sys.stderr.write("Reading entries from {}\n".format(self.file.name))
         self.head=[f.next() for x in xrange(2)]
         reader = csv.DictReader(f)
         self.fields = reader.fieldnames
         if not ('grade' in self.fields and 'ID' in self.fields):
            raise ScholarError("{}: Not a valid Scholar grades.csv file")

         def strip_dict(mydict):
            return dict((key.strip(), val.strip()) for (key,val) in mydict.items())

         self.entries = [ strip_dict(entry) for entry in reader ]

      def student_list(self):
         dict([('dmaczka', dict([('First Name', 'Darren'),('Last Name', 'Maczka')]))])
         return dict([ (entry['ID'], 
                          dict([('First Name', entry['First Name']), ('Last Name', entry['Last Name']) ]))
                          for entry in self.entries ] )
      
      def pid_list(self):
         return [ entry['PID'] for entry in self.entries ][:]

      def write(self):
         self.__write(self.file)

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
               with open(self.file.name, 'wb') as flow:
                  self.__write(flow)
         
   return ScholarGrades(name, mode)


class ScholarArchive:
   def __init__(self, path, mode):
      if os.path.isfile(path):
         try:
            with ZipFile(path, 'r') as myzip:
               contents = [info.filename for info in myzip.infolist()]
               self.prefix = os.path.commonprefix(contents)
               grades_csv = os.path.join(self.prefix,'grades.csv')
               with open_grades(myzip.open(grades_csv), 'r') as grades:
                  self.students = grades.student_list()
                  self.__construct_dict(contents)
               self.path = path
               self.grades_csv = grades_csv
               self.archive = os.path.realpath(path)
               self.unpacked = None

         except BadZipfile as e:
            raise ScholarError("{}: not a zip file".format(path))
         

   def __construct_dict(self, contents):
      for pid in self.students:
         #m = re.search(r'[\w, -]+\((\w+)\)', mdir)
         student = self.students[pid]
         prefix =  os.path.join(self.prefix, "{}, {}({})".format(student['Last Name'],student['First Name'],pid))
         comments_file = os.path.join(prefix, 'comments.txt')
         if not comments_file in contents:
            sys.stderr.write("Could not find {} in contents\n".format(comments_file))
         else:
            self.students[pid]['prefix'] = prefix

   def __write(self, filename, dest):
      with ZipFile(self.path, 'w') as zf:
         zf.write(filename, dest)

   def __enter__(self):
      self.unpacked = tempfile.mkdtemp()

   def __exit__(self, type, value, traceback):
      shutil.rmtree(self.unpacked)

   def grades(self, mode='r'):
      class GradeTemp:
         def __init__(self, sc):
            with ZipFile(sc.path, 'r') as myzip:
               self.tempdir = tempfile.mkdtemp()
               myzip.extract(sc.grades_csv, self.tempdir)
               self.tempfile = os.path.join(self.tempdir, sc.grades_csv)

         def __enter__(self):
            sys.stderr.write("Opening {} with mode {}\n".format(self.tempfile, mode))
            self.grades = open_grades(self.tempfile, mode)
            return self.grades
         
         def __exit__(self, type, value, traceback):
            if mode == 'w':
               try:
                  self.grades.write()
                  self.sc.__write(self.tempfile, sc.grades_csv)
               except Exception as e:
                  self.grades.close()
                  shutil.rmtree(self.tempdir)
                  raise e
            self.grades.close()
            shutil.rmtree(self.tempdir)

      return GradeTemp(self)

   def comments_file(self,pid):
      return os.path.join(self.students[pid], 'comments.txt')

   def feedback_attachments(self,pid):
      feedback_path = os.path.join(self.students[pid], 'Feedback Attachment(s)')
      archives = glob.glob(os.path.join(feedback_path, 'feedback_*.tar.gz'))
      self.temp_feedback_dir = tempfile.mkdtemp()
      #for archive in archives:

   def feedback_text(self,pid):
      return os.path.join(self.students[pid], 'feedbackText.html')

   def copy_to_feedback(self,pid,src):
      if os.path.isdir(src):
         shutil.copytree()
      else:
         shutil.copy(src, self.feedback_attachments(pid))

   def commit_feedback(self,pid):
      if self.temp_feedback_dir:
         shutil.make_archive(basename, 'gztar',root_dir=self.temp_feedback_dir)
         self.temp_feedback_dir = None

   #def write_feedback_text(self, pid, text):
   #   html = markdown.markdown(text)
   #   with codecs.open(self.feedback_text(pid), "w", encoding="utf8") as output_file:
   #      output_file.write(html)

   def write_comments(self, pid, text):
      html = markdown.markdown(text)
      with codecs.open(self.comments_file(pid), "w", encoding="utf8") as output_file:
         output_file.write(html)


def open_homework(f):
   try:
      homework = ast.literal_eval(f.read())
      f.close()
   except SyntaxError as e:
       f.close()
       sys.stderr.write("{}: Problem parsing file. {}\n".format(args.f.name, e))
       sys.exit(1)
   else:
       scholar_path = os.path.join(os.getcwd(), homework['name'])
       scholar = ScholarArchive(scholar_path)
       return (homework, scholar)

if __name__=='__main__':
    pass
