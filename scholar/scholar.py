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
import glob
import time
import grade
from errors import *

def get_full_list(path):
   tree = []
   for root, dirs, files in os.walk(path):
      tree.extend([ os.path.join(root,file) for file in files])
   return tree

class ScholarArchive:
   def __init__(self, path, mode):
      if os.path.isfile(path):
         try:
            with ZipFile(path, 'r') as myzip:
               contents = [info.filename for info in myzip.infolist()]
               self.prefix = os.path.commonprefix(contents)
               self.__populate(self.prefix)
         except BadZipfile as e:            
            raise ScholarError("{}: not a zip file".format(path))
         else:
            self.archive = os.path.realpath(path)
            self.unpacked = None

      else:
         self.__populate(path)
      self.temp_feedback_dir = None

   def __populate(self,prefix):
      grades_csv = os.path.join(prefix,'grades.csv')
      with open_grades(grades_csv, 'r') as grades:
         self.students = grades.student_list()
         contents = get_full_list(prefix)
         self.__construct_dict(prefix,contents)
      self.grades_csv = grades_csv
      
   def __construct_dict(self, prefix, contents):
      for pid in self.students:
         #m = re.search(r'[\w, -]+\((\w+)\)', mdir)
         student = self.students[pid]
         sprefix =  os.path.join(prefix, "{}, {}({})".format(student['Last Name'],student['First Name'],pid))
         comments_file = os.path.join(sprefix, 'comments.txt')
         if not comments_file in contents:
            sys.stderr.write("Could not find {} in contents of {}\n".format(comments_file, prefix))
            sys.stderr.writelines("{}\n".format(path) for path in contents)
            quit(1)
         else:
            self.students[pid]['prefix'] = sprefix

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
      return os.path.join(self.students[pid]['prefix'], 'comments.txt')

   def feedback_attachments(self,pid):
      feedback_path = os.path.join(self.students[pid]['prefix'], 'Feedback Attachment(s)')
      if not self.temp_feedback_dir:
         self.temp_feedback_dir = tempfile.mkdtemp()
      return os.path.join(self.temp_feedback_dir, pid)
      #for archive in archives:

   def feedback_text(self,pid):
      return os.path.join(self.students[pid], 'feedbackText.html')

   def copy_to_feedback(self,pid,src):
      if os.path.isdir(src):
         sys.stderr.write("Copying {} to Feedback Attachments\n".format(src))
         shutil.copytree(src, self.feedback_attachments(pid), symlinks=True)
         self.commit_feedback(pid)
      else:
         shutil.copy(src, self.feedback_attachments(pid))

   def pids(self):
      return self.students.keys()

   def commit_feedback(self,pid):
      feedback_dir = self.feedback_attachments(pid)
      if feedback_dir:
         basename = "feedback_{:d}".format(int(time.time()))
         basedir = os.path.join(self.students[pid]['prefix'], 'Feedback Attachment(s)')
         old_archives = glob.glob(os.path.join(basedir, 'feedback_*.tar.gz'))
         sys.stderr.write("Writing {} to {}\n".format(basename, basedir))
         shutil.make_archive(os.path.join(basedir,basename), 'gztar',root_dir=feedback_dir)
         shutil.rmtree(self.temp_feedback_dir)
         for archive in old_archives:
            sys.stderr.write("Removing old archive {}\n".format(archive))
            os.remove(archive)
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
       sys.stderr.write("{}: Problem parsing file. {}\n".format(f.name, e))
       sys.exit(1)
   else:
       scholar_path = os.path.join(os.getcwd(), homework['name'])
       sys.stderr.write("Using Scholar Path: {}\n".format(scholar_path))
       scholar = ScholarArchive(scholar_path, 'w')
       return (homework, scholar)

if __name__=='__main__':
    pass
